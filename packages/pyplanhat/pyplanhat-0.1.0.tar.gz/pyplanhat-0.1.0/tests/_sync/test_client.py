"""Basic tests for PyPlanhat client."""

import pytest

from pyplanhat._sync.client import PyPlanhat


def test_client_initialization() -> None:
    """Test that client initializes correctly."""
    client = PyPlanhat(api_key="test-key")
    assert client.api_key == "test-key"
    assert client.base_url == "https://api.planhat.com"
    client.close()


def test_client_initialization_with_base_url() -> None:
    """Test that client initializes with custom base URL."""
    client = PyPlanhat(api_key="test-key", base_url="https://custom.api.com/")
    assert client.api_key == "test-key"
    assert client.base_url == "https://custom.api.com"
    client.close()


def test_client_context_manager() -> None:
    """Test that client works as context manager."""
    with PyPlanhat(api_key="test-key") as client:
        assert client.api_key == "test-key"


def test_client_missing_api_key() -> None:
    """Test that client raises error without API key."""
    with pytest.raises(ValueError, match="API key required"):
        PyPlanhat()
