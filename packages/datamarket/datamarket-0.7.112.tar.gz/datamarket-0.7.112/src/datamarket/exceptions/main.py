########################################################################################################################
# CLASSES


import requests


class RedirectionDetectedError(Exception):
    def __init__(self, message="Redirection detected!"):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    def __init__(self, message="Not found!"):
        self.message = message
        super().__init__(self.message)


class BadRequestError(Exception):
    def __init__(self, message="Bad request!"):
        self.message = message
        super().__init__(self.message)


class EmptyResponseError(Exception):
    def __init__(self, message="Empty response!"):
        self.message = message
        super().__init__(self.message)


class ManagedHTTPError(Exception):
    """Signal that this HTTP status was handled and should not be retried."""

    def __init__(self, response: requests.Response, *, url: str | None = None, message: str | None = None):
        self.response = response
        self.request = getattr(response, "request", None)
        self.status_code = getattr(response, "status_code", None)
        self.url = url or (self.request.url if self.request is not None else None)
        self.message = message
        super().__init__(message or f"HTTP {self.status_code} for {self.url}")


class NoWorkingProxiesError(Exception):
    def __init__(self, message="No working proxies available"):
        self.message = message
        super().__init__(self.message)


class EnsureNewIPTimeoutError(Exception):
    def __init__(self, message="Timed out waiting for new IP"):
        self.message = message
        super().__init__(self.message)
