"""Custom exceptions for PyPlanhat SDK."""


class PyPlanhatError(Exception):
    """Base exception for all PyPlanhat errors."""

    pass


class APIConnectionError(PyPlanhatError):
    """Raised when network/timeout issues occur."""

    pass


class APIError(PyPlanhatError):
    """Base for HTTP errors with status_code and response_body."""

    def __init__(self, message: str, status_code: int, response_body: str):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(APIError):
    """Raised for 401/403 errors."""

    pass


class InvalidRequestError(APIError):
    """Raised for 400/404 errors."""

    pass


class RateLimitError(APIError):
    """Raised for 429 errors."""

    pass


class ServerError(APIError):
    """Raised for 5xx errors."""

    pass
