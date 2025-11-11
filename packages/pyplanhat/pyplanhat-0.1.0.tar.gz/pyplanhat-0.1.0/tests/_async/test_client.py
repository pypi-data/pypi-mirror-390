"""Basic tests for PyPlanhat client."""

import pytest

from pyplanhat._async.client import AsyncPyPlanhat


@pytest.mark.asyncio
async def test_client_initialization() -> None:
    """Test that client initializes correctly."""
    client = AsyncPyPlanhat(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.planhat.com"
    await client.close()


@pytest.mark.asyncio
async def test_client_initialization_with_base_url() -> None:
    """Test that client initializes with custom base URL."""
    client = AsyncPyPlanhat(api_key="test-key", base_url="https://custom.api.com/")
    assert client.api_key == "test-key"
    assert client.base_url == "https://custom.api.com"
    await client.close()


@pytest.mark.asyncio
async def test_client_context_manager() -> None:
    """Test that client works as context manager."""
    async with AsyncPyPlanhat(api_key="test-key") as client:
        assert client.api_key == "test-key"


@pytest.mark.asyncio
async def test_client_missing_api_key() -> None:
    """Test that client raises error without API key."""
    with pytest.raises(ValueError, match="API key required"):
        AsyncPyPlanhat()
