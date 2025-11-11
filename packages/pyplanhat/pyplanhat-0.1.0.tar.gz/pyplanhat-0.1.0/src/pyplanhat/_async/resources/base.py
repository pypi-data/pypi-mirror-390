"""Base resource class for API resources."""

from typing import Any

import httpx

from pyplanhat._exceptions import (
    APIError,
    AuthenticationError,
    InvalidRequestError,
    RateLimitError,
    ServerError,
)


class BaseResource:
    """Base class for all API resources."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        self._client = client

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any] | None:
        """Handle HTTP response with proper error handling."""
        if response.status_code == 401 or response.status_code == 403:
            raise AuthenticationError(
                response.text or "Authentication failed", response.status_code, response.text
            )
        elif response.status_code == 404:
            raise InvalidRequestError(
                response.text or "Resource not found", response.status_code, response.text
            )
        elif response.status_code == 429:
            raise RateLimitError(
                response.text or "Rate limit exceeded", response.status_code, response.text
            )
        elif response.status_code >= 500:
            raise ServerError(
                response.text or "Server error",
                response.status_code,
                response.text,
            )
        elif response.status_code >= 400:
            raise APIError(response.text or "API error", response.status_code, response.text)

        response.raise_for_status()

        # Handle 204 No Content responses
        if response.status_code == 204:
            return None

        return response.json()  # type: ignore[no-any-return]
