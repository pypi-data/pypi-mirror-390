########################################################################################################################
# IMPORTS

import logging
import random
import time
from datetime import timedelta
from functools import partial

import requests
import tenacity
from stem import Signal
from stem.control import Controller

from datamarket.exceptions import EnsureNewIPTimeoutError, NoWorkingProxiesError

########################################################################################################################
# SETUP

logger = logging.getLogger(__name__)
logging.getLogger("stem").setLevel(logging.WARNING)

PROXY_ROTATION_INTERVAL = timedelta(minutes=10)
PROXY_ROTATION_TIMEOUT_SECONDS = int(PROXY_ROTATION_INTERVAL.total_seconds())

########################################################################################################################
# CLASSES


class ProxyInterface:
    """
    Manage HTTP, HTTPS, and SOCKS5 proxies configured in the [proxy] section.
    """

    CHECK_IP_URL = "https://wtfismyip.com/json"

    def __init__(self, config):
        self._load_from_config(config)
        self.current_index = -2  # -2 means no selection made yet, -1 means Tor selected
        self._health = {}  # {entry: {"ok": bool, "last_checked": time.time(), "last_error": str}}
        self._traversal_queue = []  # Queue of indices left to test in current traversal
        self._traversal_start = None  # Timestamp when current traversal started
        self._last_ip_wait = {}  # {entry: (timestamp, traversal_cycle)} - last time we attempted to wait for IP change
        self._traversal_cycle = 0  # Counter of full traversals of the queue

    def _load_from_config(self, cfg):
        # Tor password (optional)
        self.tor_password = cfg.get("proxy", "tor_password", fallback=None)

        # Comma-separated list of hosts
        hosts_raw = cfg.get("proxy", "hosts", fallback="")
        if not hosts_raw:
            raise RuntimeError("[proxy] hosts list is empty")

        entries = []
        for host_entry in (h.strip() for h in hosts_raw.split(",") if h.strip()):
            host, port, user, password = self._parse_host_entry(host_entry)
            entries.append((host, port, user, password))

        self.entries = entries

    def _parse_host_entry(self, host_entry):
        if "@" in host_entry:
            auth_part, host_part = host_entry.rsplit("@", 1)
            host, port = host_part.split(":")
            user, password = auth_part.split(":", 1)
            return host, port, user, password
        else:
            host, port = host_entry.split(":")
            return host, port, None, None

    @property
    def proxies(self):
        return self.get_proxies(use_tor=bool(self.tor_password))

    @staticmethod
    def get_proxy_url(host, port, user=None, password=None, schema="http"):
        auth = f"{user}:{password}@" if user and password else ""
        return f"{schema}://{auth}{host}:{port}"

    def get_proxies(
        self,
        use_tor=False,
        randomize=False,
        raw=False,
        use_auth=False,
        use_socks=False,
        check_timeout=5,
        cooldown_seconds=30,
        proxy_rotation_interval=PROXY_ROTATION_INTERVAL,
    ):
        """
        Return parsed proxy URLs or raw entry tuple for a working proxy.

        :param use_tor: route via local Tor SOCKS5 if True
        :param randomize: select a random proxy if True, otherwise round-robin
        :param raw: return raw (host, port, user, password) tuple if True
        :param use_auth: include proxies that require authentication if True; otherwise only credential-free
        :param check_timeout: timeout in seconds for health check requests
        :param cooldown_seconds: how long to cache health status before re-checking
        :param proxy_rotation_interval: max time to retry finding working proxies (timedelta or seconds, 0 to disable)
        """
        # Tor handling (skip health check for tor)
        if use_tor:
            self.current_index = -1  # Indicate Tor is selected
            if raw:
                return ("127.0.0.1", "9050", None, None)
            return {"socks5": self.get_proxy_url("127.0.0.1", 9050, schema="socks5")}

        # Get a working entry (with health checks if enabled)
        host, port, user, password = self._get_working_entry(
            use_auth=use_auth,
            randomize=randomize,
            check_timeout=check_timeout,
            cooldown_seconds=cooldown_seconds,
            proxy_rotation_interval=proxy_rotation_interval,
        )

        if raw:
            return host, port, user, password

        # Build mapping of proxy URLs
        if use_socks:
            return {
                "socks5": self.get_proxy_url(host, port, user, password, "socks5"),
            }
        else:
            return {
                "http": self.get_proxy_url(host, port, user, password, "http"),
                "https": self.get_proxy_url(host, port, user, password, "http"),
            }

    def check_current_ip(self, proxies=None):
        try:
            proxies_arg = proxies or {"http": self.proxies["http"]}
            resp = requests.get(self.CHECK_IP_URL, proxies=proxies_arg, timeout=30)
            return resp.json().get("YourFuckingIPAddress")
        except Exception as ex:
            logger.error(ex)

    def renew_tor_ip(self):
        if not self.tor_password:
            logger.error("Tor password not configured")
            return

        try:
            logger.debug(f"Current IP: {self.check_current_ip()}")
            with Controller.from_port(port=9051) as controller:
                controller.authenticate(password=self.tor_password)
                controller.signal(Signal.NEWNYM)

            time.sleep(5)
            logger.debug(f"New IP: {self.check_current_ip()}")
        except Exception as ex:
            logger.error("Failed to renew Tor IP")
            logger.error(ex)

    def wait_for_new_ip(self, timeout=PROXY_ROTATION_TIMEOUT_SECONDS, interval=30, check_timeout=5):
        """
        Ensures that the IP address of the selected proxy differs from any other proxy chosen within the proxy rotation interval.

        :param timeout: Max seconds to wait for IP change
        :param interval: Seconds between IP checks
        :param check_timeout: Timeout for individual IP check requests
        :return: The selected entry (unchanged)
        :raises RuntimeError: If no proxy is available or baseline cannot be determined
        :raises EnsureNewIPTimeoutError: If IP doesn't change within timeout
        """
        # Use currently selected proxy
        if self.current_index == -1:
            # Tor is selected
            entry = ("127.0.0.1", "9050", None, None)
        elif self.current_index >= 0 and self.current_index < len(self.entries):
            # current_index points to the selected entry
            entry = self.entries[self.current_index]
        else:
            # No valid selection, select one
            logger.debug("No proxy currently selected, selecting one for IP waiting")
            self.get_proxies(raw=True)
            if self.current_index == -1:
                entry = ("127.0.0.1", "9050", None, None)
            elif self.current_index >= 0 and self.current_index < len(self.entries):
                entry = self.entries[self.current_index]
            else:
                raise RuntimeError("Could not select a proxy for IP waiting")

        # Check if we should skip waiting based on global cooldown and traversal cycle
        now = time.time()
        interval_seconds = PROXY_ROTATION_INTERVAL.total_seconds()
        for last_wait in self._last_ip_wait.values():
            last_ts, last_cycle = last_wait

            time_recent = last_ts is not None and (now - last_ts) <= interval_seconds
            no_full_rotation = self._traversal_cycle <= last_cycle

            # Skip only if both conditions are true: recent wait AND no full traversal cycle since
            if time_recent and no_full_rotation:
                logger.debug(
                    "Skipping wait_for_new_ip: last wait %.1fs ago and no full traversal since (last_cycle=%s current=%s)",
                    now - last_ts,
                    last_cycle,
                    self._traversal_cycle,
                )
                return

        # Mark we are now attempting to wait for this entry
        self._last_ip_wait[entry] = (now, self._traversal_cycle)

        # Try to use cached baseline IP from health check
        health = self._health.get(entry, {})
        baseline = health.get("last_ip")
        if baseline is None:
            raise RuntimeError(f"Could not determine baseline IP for entry {entry[0]}:{entry[1]}")
        return self._wait_for_new_ip(entry, baseline, timeout, interval, check_timeout)

    def _mark_entry_status(self, entry, ok, error=None, last_ip=None):
        """Update health cache for an entry."""
        self._health[entry] = {
            "ok": ok,
            "last_checked": time.time(),
            "last_error": error,
            "last_ip": last_ip,
        }

    def _is_entry_alive(self, entry, timeout=5):
        """Check if a proxy entry is working by making a test request."""
        host, port, user, pwd = entry
        try:
            proxies = {
                "http": self.get_proxy_url(host, port, user, pwd, "http"),
                "https": self.get_proxy_url(host, port, user, pwd, "http"),
            }
            resp = requests.get(self.CHECK_IP_URL, proxies=proxies, timeout=timeout)
            ok = resp.status_code == 200
            last_ip = resp.json().get("YourFuckingIPAddress") if ok else None
            self._mark_entry_status(entry, ok, last_ip=last_ip)
            return ok
        except Exception as ex:
            self._mark_entry_status(entry, False, str(ex))
            return False

    def _get_working_entry(
        self,
        use_auth=False,
        randomize=False,
        check_timeout=5,
        cooldown_seconds=30,
        proxy_rotation_interval=PROXY_ROTATION_INTERVAL,
    ):
        """Get a working proxy entry, performing health checks as needed.

        - Fails fast if there are no entries.
        - Optionally retries for up to `proxy_rotation_interval`,
        refreshing the traversal queue before each attempt.
        """

        if not self.entries:
            raise NoWorkingProxiesError("No proxies available")

        pool = self._build_pool(use_auth)
        self._refresh_traversal_queue(pool, randomize)

        find_once = partial(self._find_working_entry_once, check_timeout, cooldown_seconds)

        if not proxy_rotation_interval:
            return find_once()

        def before_sleep(retry_state):
            tenacity.before_sleep_log(logger, logging.INFO)(retry_state)
            self._refresh_traversal_queue(pool, randomize)

        retrying = tenacity.Retrying(
            wait=tenacity.wait_fixed(cooldown_seconds),
            stop=tenacity.stop_after_delay(proxy_rotation_interval),
            before_sleep=before_sleep,
            retry=tenacity.retry_if_exception_type(NoWorkingProxiesError),
            reraise=True,
        )
        return retrying(find_once)

    def _get_round_robin_candidates(self, pool):
        """Get candidates in round-robin order starting from current_index."""
        candidates = []
        start_idx = (self.current_index + 1) % len(self.entries) if self.current_index >= 0 else 0
        for i in range(len(self.entries)):
            idx = (start_idx + i) % len(self.entries)
            entry = self.entries[idx]
            if entry in pool:
                candidates.append(idx)
        return candidates

    def _build_pool(self, use_auth):
        pool = self.entries if use_auth else [e for e in self.entries if not e[2] and not e[3]]
        if not pool:
            pool = self.entries
        return pool

    def _refresh_traversal_queue(self, pool, randomize):
        # Build current pool indices
        current_pool_indices = [idx for idx, entry in enumerate(self.entries) if entry in pool]

        # Check if we need to refill the traversal queue
        if not self._traversal_queue and current_pool_indices:
            if randomize:
                self._traversal_queue = current_pool_indices.copy()
                random.shuffle(self._traversal_queue)
            else:
                # Round-robin: start from next after current_index
                self._traversal_queue = []
                start_idx = (self.current_index + 1) % len(self.entries) if self.current_index >= 0 else 0
                for i in range(len(self.entries)):
                    idx = (start_idx + i) % len(self.entries)
                    if idx in current_pool_indices:
                        self._traversal_queue.append(idx)
            self._traversal_start = time.time()
            self._traversal_cycle += 1

    def _find_working_entry_once(self, check_timeout, cooldown_seconds):
        # Consume from traversal queue for cached checks
        for idx in self._traversal_queue:
            entry = self.entries[idx]
            health = self._health.get(entry, {})
            last_checked = health.get("last_checked", 0)
            ok = health.get("ok", False)
            now = time.time()

            if ok and (now - last_checked) < cooldown_seconds:
                logger.debug(f"Using cached working proxy: {entry[0]}:{entry[1]}")
                self.current_index = idx
                self._traversal_queue.remove(idx)
                return entry
            elif not ok and (now - last_checked) < cooldown_seconds:
                continue
            else:
                logger.debug(f"Checking proxy health: {entry[0]}:{entry[1]}")
                if self._is_entry_alive(entry, timeout=check_timeout):
                    self.current_index = idx
                    self._traversal_queue.remove(idx)
                    return entry

        self._traversal_queue = []
        raise NoWorkingProxiesError("No working proxies available")

    def _wait_for_new_ip(self, entry, baseline, timeout, interval, check_timeout):
        logger.info("Refreshing proxy IP...")
        start = time.time()
        while time.time() - start < timeout:
            host, port, user, pwd = entry
            proxies_map = {
                "http": self.get_proxy_url(host, port, user, pwd, "http"),
                "https": self.get_proxy_url(host, port, user, pwd, "http"),
            }
            try:
                resp = requests.get(self.CHECK_IP_URL, proxies=proxies_map, timeout=check_timeout)
                current_ip = resp.json().get("YourFuckingIPAddress")
            except Exception:
                current_ip = None

            if current_ip and current_ip != baseline:
                self._mark_entry_status(entry, True, last_ip=current_ip)
                logger.info(f"IP changed from {baseline} to {current_ip}")
                return

            time.sleep(interval)

        raise EnsureNewIPTimeoutError(f"Timed out waiting for new IP after {timeout}s")
