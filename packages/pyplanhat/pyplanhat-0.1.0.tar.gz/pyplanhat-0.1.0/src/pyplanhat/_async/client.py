"""Planhat API client."""

import os

import httpx

from pyplanhat._async.resources import Companies


class AsyncPyPlanhat:
    """Planhat API client."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
    ) -> None:
        self.api_key = api_key or os.getenv("PLANHAT_API_KEY")
        url = base_url or os.getenv("PLANHAT_API_BASE_URL") or "https://api.planhat.com"
        self.base_url = url.rstrip("/")

        if not self.api_key:
            raise ValueError(
                "API key required. Set PLANHAT_API_KEY environment variable "
                "or pass api_key parameter."
            )

        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=30.0,
        )

        # Initialize resources
        self.companies = Companies(self._client)

    async def __aenter__(self) -> "AsyncPyPlanhat":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()
