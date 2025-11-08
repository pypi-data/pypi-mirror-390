########################################################################################################################
# IMPORTS

import logging
from datetime import timedelta
from typing import Optional, Sequence

import requests
from bs4 import BeautifulSoup
from requests.exceptions import ProxyError
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    retry_if_not_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_exponential,
)

from datamarket.exceptions.main import ManagedHTTPError

from ..exceptions import BadRequestError, EmptyResponseError, NotFoundError, RedirectionDetectedError
from ..interfaces.proxy import ProxyInterface
from .main import ban_sleep

########################################################################################################################
# SETUP LOGGER

logger = logging.getLogger(__name__)


########################################################################################################################
# CLASSES


class RequestsClient:
    """A robust, proxy-enabled HTTP client with retry logic and flexible output formats."""

    def __init__(self, proxy_interface: Optional[ProxyInterface] = None):
        """
        Initializes the HTTP client.

        Args:
            proxy_interface (Optional[ProxyInterface], optional): Proxy provider. If None, no proxy is used. Defaults to None.
        """
        self.proxy_interface = proxy_interface

    @retry(
        retry=retry_if_exception_type(ProxyError),
        wait=wait_exponential(exp_base=3, multiplier=3, max=60),
        stop=stop_after_delay(timedelta(minutes=10)),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _request_with_proxy_retry(self, url: str, method: str, use_auth: bool, **params):
        """
        Performs an HTTP request with proxy retry logic.

        Args:
            url (str): The target URL to fetch data from.
            method (str): HTTP method to use (e.g., 'GET', 'POST').
            use_auth (bool): Whether to use authenticated proxies.
            **params: Additional arguments passed to the requests method.

        Returns:
            requests.Response: The HTTP response object.
        """
        logger.info(f"Fetching data from {url} ...")
        proxy_cfg = None
        if self.proxy_interface:
            host, port, user, pwd = self.proxy_interface.get_proxies(raw=True, use_auth=use_auth)
            if host and port:
                proxy_url = f"http://{host}:{port}"
                proxy_auth_url = f"http://{user}:{pwd}@{host}:{port}"
                proxy_cfg = {"http": proxy_url, "https": proxy_url}
                if user and pwd:
                    proxy_cfg = {"http": proxy_auth_url, "https": proxy_auth_url}
                logger.info(f"Using proxy: {proxy_url}")
        response = getattr(requests, method.lower())(url, proxies=proxy_cfg, **params)

        return response

    @retry(
        retry=retry_if_not_exception_type(
            (NotFoundError, BadRequestError, RedirectionDetectedError, ProxyError, ManagedHTTPError)
        ),
        wait=wait_exponential(exp_base=3, multiplier=3, max=60),
        stop=stop_after_attempt(5),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def get_data(
        self,
        url: str,
        method: str = "GET",
        output: str = "json",
        sleep: tuple = (6, 3),
        use_auth_proxies: bool = False,
        max_proxy_delay: timedelta = timedelta(minutes=10),
        ignored_status_codes: Sequence[int] = (),
        **kwargs,
    ):
        """
        Fetches data from a given URL using HTTP requests, with support for proxy configuration, retries, and flexible output formats.

        Args:
            url (str): The target URL to fetch data from.
            method (str, optional): HTTP method to use (e.g., 'GET', 'POST'). Defaults to 'GET'.
            output (str, optional): Output format ('json', 'text', 'soup', 'response'). Defaults to 'json'.
            sleep (tuple, optional): Tuple specifying max and min sleep times (seconds) after request. Defaults to (6, 3).
            use_auth_proxies (bool, optional): Whether to use authenticated proxies. Defaults to False.
            max_proxy_delay (timedelta, optional): Maximum delay for proxy retry logic. Defaults to 10 minutes.
            ignored_status_codes (Sequence[int], optional): Status codes to ignore and return response for. Defaults to ().
            **kwargs: Additional arguments passed to the requests method (timeout defaults to 30 seconds if not specified).

        Returns:
            Depends on the 'output' argument:
                - 'json': Parsed JSON response.
                - 'text': Response text.
                - 'soup': BeautifulSoup-parsed HTML.
                - 'response': Raw requests.Response object.

        Raises:
            ManagedHTTPError: If a response status code is in `ignored_status_codes`.
            NotFoundError: If a 404 status code is returned and not in `ignored_status_codes`.
            BadRequestError: If a 400 status code is returned and not in `ignored_status_codes`.
            EmptyResponseError: If the response has no content.
            ProxyError: On proxy-related errors.
            requests.HTTPError: For other HTTP errors if not ignored.
        """

        params = {"timeout": 30} | kwargs
        r = self._request_with_proxy_retry.retry_with(stop=stop_after_delay(max_proxy_delay))(
            self, url, method, use_auth_proxies, **params
        )

        ban_sleep(*sleep)

        if r.status_code in ignored_status_codes:
            raise ManagedHTTPError(r, url=url, message=f"Status {r.status_code} in ignored_status_codes for URL {url}")

        error_handlers = {
            404: lambda: NotFoundError(f"404 Not Found error for {url}"),
            400: lambda: BadRequestError(f"400 Bad Request error for {url}"),
        }

        if (code := r.status_code) in error_handlers:
            raise error_handlers[code]()

        r.raise_for_status()

        if not r.content:
            raise EmptyResponseError(f"Empty response received from {url} (status {r.status_code})")

        r.encoding = "utf-8"
        output_format = {
            "json": lambda: r.json(),
            "text": lambda: r.text,
            "soup": lambda: BeautifulSoup(r.content, "html.parser"),
            "response": lambda: r,
        }

        if output in output_format:
            return output_format[output]()
