# PyPlanhat SDK Architecture

## Core Architectural Decisions

### 1. Async-First DRY Architecture

**Principle**: Write business logic once, generate synchronous version automatically.

**Implementation**:
- All source code written in `src/pyplanhat/_async/`
- Synchronous code generated to `src/pyplanhat/_sync/` via `unasync`
- Never manually edit generated sync code
- Both versions tested identically for parity

**Benefits**:
- Zero duplication of business logic
- Consistent behavior between async and sync
- Single source of truth for API interactions
- Reduced maintenance burden

### 2. Generated Code Management

**Principle**: Generated code is first-class, committed to version control.

**Implementation**:
- `src/pyplanhat/_sync/` and `tests/_sync/` committed to git
- `.gitattributes` marks generated files: `*.py linguist-generated=true`
- Generation script `scripts/generate_sync.py` run after async changes
- CI validates that sync code is up-to-date

**Benefits**:
- No build-time generation required for users
- Easy code review of generated output
- Clear diff history of sync changes
- Immediate feedback on async changes

### 3. Astral Stack Integration

**Principle**: Use modern Python tooling for optimal developer experience.

**Implementation**:
- `uv` for package management and scripting
- `ruff` for linting and formatting
- `mypy` for type checking
- `hatchling` as build backend

**Benefits**:
- Fast dependency resolution
- Consistent code quality
- Excellent IDE support
- Industry-standard tooling

## Exception Hierarchy

### Design Philosophy

**Principle**: Structured error handling with context preservation.

**Implementation**:
```python
# Base exception for all PyPlanhat errors
class PyPlanhatError(Exception):
    """Base exception for all PyPlanhat errors."""
    pass

# Network and connection issues
class APIConnectionError(PyPlanhatError):
    """Raised when network/timeout issues occur."""
    pass

# HTTP errors with context
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
```

**Benefits**:
- Clear error categorization
- Rich context for debugging
- Easy error handling patterns
- Consistent error interface

## Project Structure

### Directory Layout

```
src/
├── pyplanhat/
│   ├── _async/              # Async source code (write here only)
│   │   ├── client.py        # Main async client
│   │   └── resources/       # Async resource implementations
│   │       ├── companies.py
│   │       ├── endusers.py
│   │       └── conversations.py
│   ├── _sync/               # Generated sync code (never edit)
│   │   ├── client.py        # Generated sync client
│   │   └── resources/       # Generated sync resources
│   ├── _exceptions.py       # Custom exception hierarchy
│   └── __init__.py         # Public API exports
tests/
├── _async/                 # Async tests (write here only)
│   ├── test_client.py
│   ├── test_companies.py
│   ├── test_endusers.py
│   └── test_conversations.py
└── _sync/                  # Generated sync tests (never edit)
    ├── test_client.py
    ├── test_companies.py
    ├── test_endusers.py
    └── test_conversations.py
scripts/
└── generate_sync.py        # unasync generation script
```

### Import Patterns

**Async Source**:
```python
# src/pyplanhat/_async/resources/companies.py
from pyplanhat._async.client import AsyncPyPlanhat
from pyplanhat._exceptions import APIError, AuthenticationError
```

**Generated Sync**:
```python
# src/pyplanhat/_sync/resources/companies.py (generated)
from pyplanhat._sync.client import PyPlanhat
from pyplanhat._exceptions import APIError, AuthenticationError
```

**Public API**:
```python
# src/pyplanhat/__init__.py
from pyplanhat._async.client import AsyncPyPlanhat
from pyplanhat._sync.client import PyPlanhat
from pyplanhat._exceptions import *
```

## Resource Implementation Patterns

### Base Resource Class

**Async Implementation**:
```python
# src/pyplanhat/_async/resources/base.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import httpx

from pyplanhat._exceptions import APIError, AuthenticationError

class BaseResource(ABC):
    def __init__(self, client: httpx.AsyncClient):
        self._client = client
    
    async def _handle_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Handle HTTP response with proper error handling."""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed", response.status_code, response.text)
        elif response.status_code == 404:
            raise InvalidRequestError("Resource not found", response.status_code, response.text)
        elif response.status_code >= 400:
            raise APIError(f"API error: {response.text}", response.status_code, response.text)
        
        response.raise_for_status()
        return response.json()
```

### CRUD Operations Pattern

**Companies Resource Example**:
```python
# src/pyplanhat/_async/resources/companies.py
from typing import List, Optional
from pydantic import BaseModel
import httpx

from pyplanhat._async.resources.base import BaseResource
from pyplanhat._exceptions import APIError

class Company(BaseModel):
    id: str
    name: str
    domain: Optional[str] = None
    custom_fields: Dict[str, Any] = {}

class Companies(BaseResource):
    async def list(self) -> List[Company]:
        """List all companies."""
        response = await self._client.get("/companies")
        data = await self._handle_response(response)
        return [Company(**item) for item in data]
    
    async def get(self, company_id: str) -> Company:
        """Get a specific company by ID."""
        response = await self._client.get(f"/companies/{company_id}")
        data = await self._handle_response(response)
        return Company(**data)
    
    async def create(self, company: Company) -> Company:
        """Create a new company."""
        response = await self._client.post("/companies", json=company.dict())
        data = await self._handle_response(response)
        return Company(**data)
    
    async def update(self, company_id: str, company: Company) -> Company:
        """Update an existing company."""
        response = await self._client.put(f"/companies/{company_id}", json=company.dict())
        data = await self._handle_response(response)
        return Company(**data)
    
    async def delete(self, company_id: str) -> None:
        """Delete a company."""
        response = await self._client.delete(f"/companies/{company_id}")
        await self._handle_response(response)
```

## Client Architecture

### Async Client

```python
# src/pyplanhat/_async/client.py
import httpx
from typing import Optional

from pyplanhat._async.resources.companies import Companies
from pyplanhat._async.resources.endusers import EndUsers
from pyplanhat._async.resources.conversations import Conversations
from pyplanhat._exceptions import APIConnectionError

class AsyncPyPlanhat:
    """Async client for Planhat API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.planhat.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=30.0
        )
        
        # Initialize resources
        self.companies = Companies(self._client)
        self.endusers = EndUsers(self._client)
        self.conversations = Conversations(self._client)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
    
    async def close(self):
        """Close the HTTP client."""
        try:
            await self._client.aclose()
        except Exception as e:
            raise APIConnectionError(f"Failed to close client: {e}")
```

### Generated Sync Client

```python
# src/pyplanhat/_sync/client.py (generated)
import httpx
from typing import Optional

from pyplanhat._sync.resources.companies import Companies
from pyplanhat._sync.resources.endusers import EndUsers
from pyplanhat._sync.resources.conversations import Conversations
from pyplanhat._exceptions import APIConnectionError

class PyPlanhat:
    """Sync client for Planhat API."""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.planhat.com"):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
            timeout=30.0
        )
        
        # Initialize resources
        self.companies = Companies(self._client)
        self.endusers = EndUsers(self._client)
        self.conversations = Conversations(self._client)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def close(self):
        """Close the HTTP client."""
        try:
            self._client.close()
        except Exception as e:
            raise APIConnectionError(f"Failed to close client: {e}")
```

## Testing Architecture

### Test Parity Principle

**Principle**: Async and sync tests must be identical in structure and coverage.

**Implementation**:
- Write tests once in `tests/_async/`
- Generate sync tests via unasync
- Validate test coverage parity
- Ensure identical test scenarios

### Test Structure Example

```python
# tests/_async/test_companies.py
import pytest
import httpx

from pyplanhat._async.client import AsyncPyPlanhat
from pyplanhat._async.resources.companies import Company
from pyplanhat._exceptions import AuthenticationError, InvalidRequestError

@pytest.mark.asyncio
async def test_list_companies(async_client, httpx_mock):
    """Test listing all companies."""
    # Mock response
    httpx_mock.add_response(
        json=[
            {"id": "1", "name": "Company A"},
            {"id": "2", "name": "Company B"}
        ]
    )
    
    companies = await async_client.companies.list()
    
    assert len(companies) == 2
    assert companies[0].name == "Company A"
    assert companies[1].name == "Company B"

@pytest.mark.asyncio
async def test_get_company_not_found(async_client, httpx_mock):
    """Test getting a non-existent company raises error."""
    httpx_mock.add_response(
        status_code=404,
        text="Company not found"
    )
    
    with pytest.raises(InvalidRequestError):
        await async_client.companies.get("nonexistent")

@pytest.fixture
async def async_client():
    """Fixture for async client."""
    client = AsyncPyPlanhat(api_key="test-key")
    yield client
    await client.close()
```

## Code Generation Configuration

### unasync Settings

```python
# scripts/generate_sync.py
import unasync
import os

def main():
    settings = [
        unasync.FileReplacement(
            from_pattern="/_async/",
            to_pattern="/_sync/",
        ),
        unasync.FunctionReplacement(
            from_pattern="async def ",
            to_pattern="def ",
        ),
        unasync.FunctionReplacement(
            from_pattern="await ",
            to_pattern="",
        ),
        unasync.FunctionReplacement(
            from_pattern="AsyncClient",
            to_pattern="Client",
        ),
        unasync.FunctionReplacement(
            from_pattern="AsyncPyPlanhat",
            to_pattern="PyPlanhat",
        ),
        unasync.FunctionReplacement(
            from_pattern="@pytest.mark.asyncio",
            to_pattern="",
        ),
    ]
    
    # Generate source code
    unasync.main([
        "src/pyplanhat/_async/",
        "--unasync-file-replacements", "/_async/:/_sync/",
        "--unasync-function-replacements", "async def :def",
        "--unasync-function-replacements", "await :",
        "--unasync-function-replacements", "AsyncClient:Client",
        "--unasync-function-replacements", "AsyncPyPlanhat:PyPlanhat",
        "--unasync-function-replacements", "@pytest.mark.asyncio:",
    ])
    
    # Generate test code
    unasync.main([
        "tests/_async/",
        "--unasync-file-replacements", "/_async/:/_sync/",
        "--unasync-function-replacements", "async def :def",
        "--unasync-function-replacements", "await :",
        "--unasync-function-replacements", "AsyncClient:Client",
        "--unasync-function-replacements", "AsyncPyPlanhat:PyPlanhat",
        "--unasync-function-replacements", "@pytest.mark.asyncio:",
    ])

if __name__ == "__main__":
    main()
```

This architecture ensures maintainability, consistency, and excellent developer experience while following modern Python best practices.