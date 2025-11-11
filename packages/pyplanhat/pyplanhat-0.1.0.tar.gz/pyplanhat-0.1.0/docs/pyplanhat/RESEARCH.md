## Introduction: The 2025 Python Tooling Renaissance

For decades, Python development was characterized by a fragmented and often confusing toolchain. A typical project required managing `pip` for package installation, `virtualenv` for environments, `setuptools` and `wheel` for building, `twine` for publishing, `pip-tools` for locking, `black` and `isort` for formatting, `flake8` for linting, and `mypy` for type checking. Each tool brought its own configuration file and cognitive overhead.

The year 2025 is defined by the "Great Unification" of this stack, driven primarily by the work of Astral. Their Rust-based tools, `uv` and `ruff`, have consolidated this entire toolchain. `uv` is not merely a "faster pip"; it is an integrated package and project manager designed to replace the entire fragmented stack of `pip`, `pip-tools`, `virtualenv`, `twine`, and more. Complementing this, `ruff` unifies linting, formatting, and import sorting into a single, blazing-fast tool.

The `PyPlanhat` project represents a perfect "greenfield" opportunity. As a new, open-source API wrapper, it can be built from the ground up on this modern foundation, avoiding technical debt and adopting the best practices demonstrated by today's leading SDKs. This report provides an end-to-end technical playbook for its construction.

## Section 1: The 2025 Python Package Manifest: `pyproject.toml` as Your Source of Truth

The `pyproject.toml` file is the foundational, declarative manifest for a modern Python project. It replaces the need for `setup.py`, `setup.cfg`, `requirements.txt`, and a host of tool-specific dotfiles. It is the single source of truth that configures the build system, project metadata, dependencies, and all development tools.

### 1.1. Pillar 1: The Build System (`[build-system]`)

As defined by PEP 517 and PEP 518, this table declares _how_ your package is built by isolating the build backend from the frontend (the `uv` command you run).

For a pure-Python API wrapper like `PyPlanhat`, the recommended build backend is `hatchling`. It is mature, well-documented, and widely used in production. While `setuptools` remains a complex legacy option and `uv_build` is available for pure Python projects, `hatchling` provides the best balance of stability and features for this project's needs.

The configuration is minimal:

Ini, TOML

```
[build-system]
requires = ["uv_build>=0.9.6,<0.10.0"]
build-backend = "uv_build"
```

### 1.2. Pillar 2: Project Metadata (`[project]`)

This table, standardized by PEP 621, defines _what_ your package is. This metadata is consumed by `uv_build` and displayed on PyPI. Key fields include `name`, `version`, `description`, `readme`, `requires-python`, and `license`.1

Critically, `classifiers` should be set to allow users to find the package, and `project.urls` should be populated to link to the repository and documentation, which is crucial for discoverability. The `version` will initially be set statically but will later be configured for automation (see Section 7).

### 1.3. Pillar 3: Dependency Management (`dependencies` and `[project.optional-dependencies]`)

This section defines the project's dependencies. A common assumption for a dual-client SDK is that the `async` variant would require an optional dependency (e.g., `pyplanhat[async]`). This assumption is incorrect for a modern architecture.

The best-in-class library for this, `httpx`, provides both synchronous (`httpx.Client`) and asynchronous (`httpx.AsyncClient`) clients within the _same_ package. Top-tier SDKs like `openai-python` and `anthropic-sdk-python` list `httpx` as a single, core dependency. Therefore, the sync/async split is a code _architecture_ pattern (see Section 2), not a _packaging_ one.

The only core dependencies required for `PyPlanhat` are `httpx` for the transport layer and `pydantic` for data modeling.

The `[project.optional-dependencies]` table will be used to manage _developer_ environments, a practice fully supported by `uv`.

Ini, TOML

```
[project]
#... core metadata from 1.2...
dependencies = [
    "httpx>=0.27.0",
    "pydantic>=2.0.0"
]

[project.optional-dependencies]
test =
    "pytest-httpx>=0.30.0"   # For mocking HTTP requests
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.25.0" # For auto-generating API docs
dev = [
    # uv supports self-referential extras
    "pyplanhat[test]",
    "pyplanhat[docs]",
    "ruff>=0.5.0",
    "mypy>=1.10.0",
    "python-semantic-release>=9.0.0" # For automated releases
```

### 1.4. Pillar 4: Tool Configuration (`[tool.ruff]`)

The `[tool]` table demonstrates the power of the unified Astral Stack, allowing configuration of the entire toolchain within `pyproject.toml`.

Significantly, `ruff` is not just a linter; it is a full replacement for `black` (formatting) and `isort` (import sorting). This eliminates the need for separate configuration files. The configuration will include `[tool.ruff.lint]` for rules, `[tool.ruff.format]` for `black`-compatible formatting, and `[tool.ruff.lint.isort]` for import sorting.

### Table 1.1: The Complete `pyproject.toml` for `PyPlanhat`

This comprehensive manifest serves as the foundational artifact for the project, synthesizing all four pillars.

Ini, TOML

```
# ===================================================================
# 1. Build System (PEP 517/518) - Using uv_build
# ===================================================================
[build-system]
requires = ["hatchling"] #
build-backend = "hatchling.build" #

# ===================================================================
# 2. Project Metadata (PEP 621)
# ===================================================================
[project]
name = "pyplanhat"
version = "0.1.0" # This will be managed by semantic-release
description = "A modern, sync/async Python SDK for the Planhat API."
readme = "README.md"
authors =
license = { text = "MIT" } #
requires-python = ">=3.12"
keywords = ["planhat", "api", "sdk", "wrapper"]
classifiers =
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.12",
    "Topic :: Software Development :: Libraries :: Python Modules"
]
dependencies =
    "pydantic>=2.0.0" #

[project.urls] #
Homepage = "https://github.com/your-org/pyplanhat"
Repository = "https://github.com/your-org/pyplanhat"
Documentation = "https://your-org.github.io/pyplanhat"

# ===================================================================
# 3. Optional Dependencies (Dev Groups)
# ===================================================================
[project.optional-dependencies] #
test =
    "pytest-httpx>=0.30.0"  #
docs = [
    "mkdocs>=1.6.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.25.0" #
dev = [
    "pyplanhat[test]",
    "pyplanhat[docs]",
    "ruff>=0.5.0", #
    "mypy>=1.10.0", #
    "python-semantic-release>=9.0.0" #

# ===================================================================
# 4. Tool Configuration (Ruff, Mypy)
# ===================================================================
[tool.ruff]
line-length = 88
target-version = "py312"

[tool.ruff.lint]
select = [
    "E",  # pycodestyle errors
    "W",  # pycodestyle warnings
    "F",  # pyflakes
    "I",  # isort
    "B",  # flake8-bugbear
    "C4", # flake8-comprehensions
    "UP", # pyupgrade
]
ignore = [
    "E501",  # line too long, handled by formatter
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.lint.isort]
known-first-party = ["pyplanhat"]

[tool.ruff.format] #
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false

[tool.mypy] #
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
```

## Section 2: Core Architecture: Building a DRY, Dual-Client SDK

The most critical architectural decision for `PyPlanhat` is how to provide both synchronous and asynchronous clients without duplicating code, which is a primary source of bugs and maintenance overhead.

### 2.1. The Lynchpin: `httpx` as the Transport Layer

In 2025, `httpx` is the non-negotiable choice for a new API wrapper. It is a modern, `requests`-compatible library that provides both a `httpx.Client` (sync) and `httpx.AsyncClient` (async) from a single install. It supports HTTP/2, provides excellent `async`/`await` support, and is the chosen transport layer for major SDKs from Anthropic and OpenAI. The `PyPlanhat` clients will be thin, value-adding wrappers around these two `httpx` clients.

### 2.2. The "Write Async First" Paradigm

The central principle for this architecture is "Don't Repeat Yourself" (DRY).2 Synchronous and asynchronous code are syntactically almost identical, differing primarily by the `async` and `await` keywords and the client class being used.3 The solution is to write _only_ the asynchronous version of the SDK; the synchronous version will then be _automatically generated_ from the async source.2

### 2.3. Architectural Deep Dive: Build-Time Generation vs. Runtime Wrapping

Two primary patterns exist for achieving this DRY architecture:

1. **Runtime Wrapping (e.g., `universalasync`):** This approach involves writing only an async library and using a decorator, like `@wrap` from `universalasync`. When a method is called from a synchronous context, the decorator "magically" runs the async code by spawning a new event loop (e.g., via `asyncio.run()`).4 While simple to implement, this pattern has significant drawbacks: it adds performance overhead, can be difficult to debug, and can fail in complex threading or signal-handling environments.4
    
2. **Build-Time Generation (e.g., `unasync`):** This is the pattern used by top-tier libraries. It involves running a script _during development_ that performs code transformations (typically regex substitutions) on the async source files to produce a _separate, static, and explicit_ synchronous codebase.2 This script converts `async def` to `def`, removes `await`, and swaps `AsyncClient` for `Client`.2
    

The build-time generation pattern is superior. Leading libraries like `psycopg` 3, `httpcore` (the transport for `httpx`) 2, `openai-python` 5, and `anthropic-sdk-python` 6 all use code generation ("Stainless" is the generator used by OpenAI and Anthropic). This approach produces real, static, debuggable, and type-checkable sync code with no runtime overhead.

This is the recommended architecture for `PyPlanhat`. A `scripts/generate_sync.py` file (modeled after the one in `httpcore` 2) will be used to generate the sync code. The project structure will be as follows:

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
```

The top-level `pyplanhat/__init__.py` provides the clean user interface:

Python

```
# src/pyplanhat/__init__.py
from pyplanhat._sync.client import PyPlanhat
from pyplanhat._async.client import AsyncPyPlanhat
from pyplanhat._exceptions import *

__all__ = ["PyPlanhat", "AsyncPyPlanhat", "PyPlanhatError", "AuthenticationError", "APIError"]
```

### 2.4. Ergonomic Client and Authentication Design

The client `__init__` method should provide an ergonomic authentication experience. It should accept an `api_key` as an argument but, more importantly, it should default to reading that key from an environment variable (e.g., `PLANHAT_API_KEY`). This is a security best practice that prevents hardcoding secrets and works seamlessly in CI/CD environments.

Furthermore, to avoid a "god object", the client should use namespaced properties for different logical components of the Planhat API (e.g., users, companies). This makes the SDK scalable and discoverable.

Python

```
# In pyplanhat/_async/client.py

import httpx
import os
from.resources import AsyncUsers, AsyncCompanies # (Example)

class AsyncPyPlanhat:
    def __init__(self, api_key: str | None = None, base_url: str | None = None):
        if api_key is None:
            api_key = os.environ.get("PLANHAT_API_KEY") #
        if api_key is None:
            raise AuthenticationError("No API key provided. Set the PLANHAT_API_KEY environment variable.")
        
        self._client = httpx.AsyncClient(
            base_url=base_url or "https://api.planhat.com",
            headers={"Authorization": f"Bearer {api_key}"} if api_key else {}
        )
        
        # Namespaced resources
        self.users = AsyncUsers(self._client)
        self.companies = AsyncCompanies(self._client)

    async def close(self):
        await self._client.aclose()

    #... other client methods...
```

## Section 3: API Ergonomics: Designing a "Convenience" Wrapper

The user query specifies a "convenience wrapper." This value is delivered not just by proxying HTTP calls, but by (1) modeling data and (2) handling errors ergonomically.

### 3.1. Data Modeling with Pydantic

APIs return JSON, which translates to unstructured `dict`s in Python. This is brittle and offers no IDE support or data validation. In 2025, Pydantic is the standard for solving this.

For `PyPlanhat`, every API endpoint that returns data should have a corresponding Pydantic `BaseModel`. The SDK methods will not return raw `dict`s; they will return populated Pydantic models.

Python

```
# In pyplanhat/models.py
from pydantic import BaseModel, EmailStr

class User(BaseModel):
    id: str
    name: str
    email: EmailStr
    #... other fields from Planhat API

# In pyplanhat/_async/resources.py
from.models import User

class AsyncUsers:
    def __init__(self, client: httpx.AsyncClient):
        self._client = client

    async def get(self, user_id: str) -> User:
        response = await self._client.get(f"/users/{user_id}")
        response.raise_for_status() # See 3.2 for error handling
        
        # Parse, validate, and return the model
        return User.model_validate(response.json())
```

This approach transforms the SDK into a powerful validation layer. If the Planhat API changes a field name or returns invalid data, the user's code will not fail with a cryptic `KeyError`. Instead, `User.model_validate()` will _immediately_ raise a `pydantic.ValidationError` with a clear message, pinpointing the exact data mismatch. This is a primary feature of a "convenience" wrapper.

### 3.2. A Custom Exception Hierarchy

The second pillar of convenience is error handling. `httpx` raises a generic `httpx.HTTPStatusError`. This forces the end-user to write `try...except` blocks and inspect `error.response.status_code` to determine what went wrong. This is not convenient.

The SDK should intercept these generic errors and re-raise specific, custom exceptions. This allows the user to write clean, targeted error-handling logic.

A best-practice hierarchy should be defined:

Python

```
# In pyplanhat/_exceptions.py

class PyPlanhatError(Exception):
    """Base exception for the PyPlanhat SDK."""
    pass

class APIConnectionError(PyPlanhatError):
    """Raised for network-level errors (e.g., timeout, DNS)."""
    pass

class APIError(PyPlanhatError):
    """Base for errors returned by the Planhat API (e.g., 4xx, 5xx)."""
    def __init__(self, message: str, status_code: int, response_body: dict | None):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body

class AuthenticationError(APIError): #
    """Raised for 401 Unauthorized or 403 Forbidden."""
    pass

class InvalidRequestError(APIError):
    """Raised for 400 Bad Request or 404 Not Found."""
    pass

class RateLimitError(APIError): #
    """Raised for 429 Too Many Requests."""
    pass

class ServerError(APIError):
    """Raised for 5xx server-side errors."""
    pass
```

The client's internal request helper will wrap all `httpx` calls to perform this translation, providing a vastly superior developer experience.

## Section 4: The Inner Loop: The Integrated "Astral Stack" Workflow

`uv` serves as the central command-line interface for the entire developer "inner loop".

### 4.1. Project & Environment Management with `uv`

`uv` replaces all previous environment and package management commands:

- `uv init`: Bootstraps the project and `pyproject.toml`.1
    
- `uv venv`: Creates the virtual environment, which `uv` typically handles automatically.
    
- `uv add <pkg>`: Adds a core dependency to `[project].dependencies`.
    
- `uv add <pkg> --group <name>`: Adds a dev dependency (e.g., `uv add pytest --group test`).
    
- `uv sync --all-groups`: Installs all dependencies, including all optional groups, from the `uv.lock` file. This is the new `pip install -r requirements.txt` or `poetry install`.
    
- `uv lock`: Generates the cross-platform `uv.lock` file.
    

### 4.2. Running Tasks (`uv run` vs. `uvx`)

`uv` provides two ways to execute package scripts: `uv run` and `uvx`.

- `uvx`: Runs a command in a _temporary, isolated_ environment. This is for ad-hoc tools.
    
- `uv run`: Runs a command _within the project's managed virtual environment_.
    

For tools like `pytest` and `mypy` that need to see the project's source code and its installed dependencies, `uv run` is mandatory. `uvx` will not work as it runs in isolation.

The core developer loop becomes:

- **Format:** `uv run ruff format.`
    
- **Lint:** `uv run ruff check.`
    
- **Test:** `uv run pytest`
    
- **Type Check:** `uv run mypy.`
    

### 4.3. The 2025 Type-Checking Horizon: `mypy` vs. Astral's `ty` (Red Knot)

As of late 2025, the recommended stack includes `mypy`. It is mature, stable, and configured in `pyproject.toml`.

However, the strategic, forward-looking tool is Astral's new type checker, `ty` (formerly Red Knot). `mypy` is the last "slow" component in the modern Python toolchain. `ty` is Astral's Rust-based solution to this, designed for extreme speed and integration with the `ruff` ecosystem.

As of late 2025, `ty` is in public alpha/beta, with a production release targeted for late 2025 or early 2026. It is not a 1-to-1 `mypy` replacement and has distinct design goals.

For `PyPlanhat`, the recommendation is to **start with `mypy`** for its stability and to **actively monitor `ty`**. Migrating from `mypy` to `ty` in 2026 will be the final step in completing the fully high-speed, Rust-based toolchain.

### Table 4.1: The Modern `uv` Workflow Translation

This table translates common Python tasks from legacy tools to the unified `uv` command.

| **Task**                 | **Legacy Command(s)**                        | **Modern uv Command**            |
| ------------------------ | -------------------------------------------- | -------------------------------- |
| Create Environment       | `python -m venv.venv`                        | `uv venv`                        |
| Activate Environment     | `source.venv/bin/activate`                   | (Not required) `uv` auto-detects |
| Add Core Dependency      | `pip install <pkg>` & `pip freeze > req.txt` | `uv add <pkg>`                   |
| Add Dev Dependency       | `pip install <pkg>` (to `dev-req.txt`)       | `uv add <pkg> --group dev`       |
| Install All Dependencies | `pip install -r req.txt -r dev-req.txt`      | `uv sync --all-groups`           |
| Run Task in Env          | `.venv/bin/pytest`                           | `uv run pytest`                  |
| Run Ad-Hoc Tool          | `pipx run <pkg>`                             | `uvx <pkg>`                      |
| Build Package            | `python -m build`                            | `uv build`                       |
| Publish Package          | `twine upload dist/*`                        | `uv publish`                     |

## Section 5: A Robust Testing Strategy for Dual-Client SDKs

The testing strategy must validate the `unasync` architecture from Section 2, ensuring both clients are fully tested without violating the DRY principle.

### 5.1. Test Tooling Setup

The test toolchain, defined in `[project.optional-dependencies].test`, consists of:

- `pytest`: The standard test runner.
    
- `pytest-asyncio`: Essential for testing asynchronous code, providing the `@pytest.mark.asyncio` decorator.
    
- `pytest-httpx`: The definitive tool for mocking the `httpx` transport layer.
    

### 5.2. Mocking the API with `pytest-httpx`

Tests must _never_ make real network calls. The `httpx_mock` fixture from `pytest-httpx` intercepts all `httpx` requests, allowing for declarative, robust response mocking.

This approach is superior to `unittest.mock.patch`. Patching is verbose and mocks the _client method_, whereas `pytest-httpx`mocks the _transport layer_, meaning the _actual_ client code is executed against a controlled response.

### 5.3. The "DRY Test" Pattern: `unasync` for Tests

The primary challenge is testing both `PyPlanhat` and `AsyncPyPlanhat`. The wrong approach is to use `pytest.parametrize`and litter tests with `if/else` logic to `await`.

The correct, modern pattern is to **extend the `unasync` architecture to the tests themselves**.2

1. All tests are written **only** in the `tests/_async/` directory.
    
2. All test functions are written as `async def` using `AsyncPyPlanhat` and the `@pytest.mark.asyncio` marker.
    
3. The `scripts/unasync.py` script (from Section 2.3) is configured to _also_ process the test directory: `unasync_dir('tests/_async', 'tests/_sync')`.2
    
4. This script automatically generates a parallel `tests/_sync/` directory. It converts `async def` to `def`, removes `await`, removes the `@pytest.mark.asyncio` marker, and swaps the imported client from `AsyncPyPlanhat` to `PyPlanhat`.2
    

This provides 100% test logic parity for both clients, for free. The _only_ test suite that requires maintenance is the async one. `pytest` will discover and run _both_ `tests/_async` and `tests/_sync`, ensuring full test coverage.

### Table 5.1: Key `pytest-httpx` Mocking Recipes

This reference provides the core patterns for testing the SDK, including the custom exceptions defined in Section 3.2.

| **Goal**                  | **pytest-httpx Code**                                     | **Tested Behavior**                         |
| ------------------------- | --------------------------------------------------------- | ------------------------------------------- |
| **Mock 200 OK**           | `httpx_mock.add_response(json={"id": 1,...})`             | Tests successful Pydantic model parsing.    |
| **Mock 401 Auth Error**   | `httpx_mock.add_response(status_code=401)`                | Tests `pytest.raises(AuthenticationError)`. |
| **Mock 429 Rate Limit**   | `httpx_mock.add_response(status_code=429)`                | Tests `pytest.raises(RateLimitError)`.      |
| **Mock 500 Server Error** | `httpx_mock.add_response(status_code=500)`                | Tests `pytest.raises(ServerError)`.         |
| **Mock Network Timeout**  | `httpx_mock.add_exception(httpx.ReadTimeout("Timeout!"))` | Tests `pytest.raises(APIConnectionError)`.  |

## Section 6: Modern Documentation with `mkdocs` and `mkdocstrings`

For an SDK, developer experience (DX) is paramount, and documentation is a core part of that experience.

### 6.1. The 2025 Choice: `mkdocs` + Material > `sphinx`

While `sphinx` is the traditional standard, it is widely considered complex, slow, and its use of reStructuredText is a barrier for many developers.

The 2025 standard is `mkdocs`. It is developer-friendly, uses standard Markdown, and when combined with the `mkdocs-material` theme, it produces beautiful, responsive, and modern documentation sites. Historically, `mkdocs` was seen as too simple for API documentation, but this is no longer true.

### 6.2. Automating Your API Reference with `mkdocstrings`

The `mkdocstrings` plugin is the `mkdocs`-native solution that replaces `sphinx-autodoc`. It is the key to creating low-maintenance, high-quality API references.

It works by statically analyzing the code.7 The `mkdocstrings-python` handler uses a tool called `griffe` to parse the Python source files. It reads docstrings (supporting Google, NumPy, and Sphinx styles) and type hints, and uses them to automatically generate a clean, cross-referenced API documentation section.7

To generate the _entire_ API reference for both clients, the `docs/api_reference.md` file simply needs to contain:

# API Reference

## Asynchronous Client

::: pyplanhat.AsyncPyPlanhat

options:

members: true

show_root_heading: true

## Synchronous Client

::: pyplanhat.PyPlanhat

options:

members: true

show_root_heading: true

The documentation is now always in sync with the code's docstrings and type hints.

### 6.3. Documentation Structure

Effective SDK documentation provides more than just an API reference. The `docs/` directory should be structured around developer needs:

- `mkdocs.yml`: The main configuration file.
    
- `docs/index.md`: The "Getting Started" guide, with installation instructions and a 30-second quickstart.
    
- `docs/authentication.md`: A detailed guide on acquiring and providing the `PLANHAT_API_KEY`.
    
- `docs/usage.md`: A "cookbook" of practical, copy-paste-ready recipes (e.g., "How to get a user," "How to update a company").
    
- `docs/api_reference.md`: The page containing the `mkdocstrings` directives, as shown above.
    

## Section 7: The "Golden Workflow": Automated, Secure Publishing to PyPI

This section integrates all previous steps into a fully-automated, secure, two-stage CI/CD pipeline for releasing the package.

### 7.1. Stage 1: Automated Versioning & Changelog Generation

Manually bumping the `version` in `pyproject.toml`, writing a `CHANGELOG.md`, and creating Git tags is tedious and error-prone. This process should be automated.

The solution is `python-semantic-release`. This tool is configured in `pyproject.toml` and runs in a GitHub Action. By enforcing **Conventional Commits** (e.g., `feat:`, `fix:`, `docs:`), the tool can automatically determine the next version number.

When code is merged to the `main` branch, a GitHub Action runs `semantic-release version`. This tool scans the commit history, determines the version bump (e.g., a `feat:` commit triggers a minor bump), and then automatically:

1. Updates the `version` string in `pyproject.toml`.
    
2. Generates or updates the `CHANGELOG.md` file.
    
3. Commits these two files back to the repository.
    
4. Creates and pushes the new Git tag (e.g., `v0.2.0`).8
    

### 7.2. Stage 2: Secure, Tokenless Publishing

The `git push` of the new tag from Stage 1 triggers this _second_, separate workflow. This workflow builds the package and publishes it to PyPI.

### 7.3. The Publisher: `uv publish`

The traditional publish workflow involves `python -m build` followed by the `pypa/gh-action-pypi-publish` action.

However, since `PyPlanhat` is built on the `uv` toolchain, the simpler and more idiomatic solution is to use `uv`'s native commands: `uv build` (which uses the `[build-system]` defined in Section 1) and `uv publish`.9 `uv` is designed to be a full `twine` replacement.

### 7.4. The Security Standard: OIDC Trusted Publishing

The most significant security advancement in modern Python packaging is the move away from PyPI API tokens. Storing tokens as GitHub Secrets (`PYPI_API_TOKEN`) is a major liability; if a dependency or action is compromised, the secret can be stolen, allowing an attacker to publish malicious code.

The 2025 standard is **PyPI Trusted Publishing**. This OIDC-based method requires _zero_ long-lived secrets.

The setup is a three-part process 10:

1. **On PyPI:** In the `PyPlanhat` project settings, under "Publishing," add a "Trusted Publisher". Configure it with the GitHub owner, repository, workflow file (`publish.yml`), and a new "environment" name (`pypi`).
    
2. **In GitHub:** In the repository settings, create a new "Environment" named `pypi`. No secrets are added to it.
    
3. **In `publish.yml`:** The publish job _must_ specify `environment: pypi` and `permissions: id-token: write`.
    

When the workflow runs, the `id-token: write` permission allows it to request a short-lived OIDC token from GitHub. `uv publish` (which supports OIDC) presents this token to PyPI. PyPI verifies the token's signature and its "claims" (e.g., "This token was generated by the `publish.yml` workflow on the `pyplanhat` repo") and issues a _temporary, single-use_ upload token. This is a secure, tokenless, and fully automated publishing system.

### 7.5. The "Golden Workflow" `publish.yml`

This final workflow file, triggered by new tags, synthesizes every concept from this report: it runs the `unasync` script, builds the package with `uv`, and publishes it securely using OIDC.

YAML

```
#.github/workflows/publish.yml
# Triggers AFTER semantic-release creates and pushes a new tag
name: Publish to PyPI

on:
  push:
    tags:
      - 'v*' #

jobs:
  publish:
    name: Publish to PyPI
    runs-on: ubuntu-latest
    
    # 1. Configure Trusted Publishing
    environment: pypi #
    permissions:
      id-token: write #

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      # 2. Install uv and Python
      - name: Install uv
        uses: astral-sh/setup-uv@v6 #
        with:
          version: "0.9.6" # Pin the version

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      # 3. Install dev dependencies
      #    We need the 'unasync' script and its dependencies
      - name: Install dependencies
        run: uv sync --group dev

# 4. Generate the sync client from the async source
        #    This ensures our built package is complete (See Section 2)
        - name: Run 'unasync' to generate sync code
          run: uv run python scripts/generate_sync.py

      # 5. Build the sdist and wheel
      - name: Build package
        run: uv build # 

      # 6. Publish using uv and OIDC
      - name: Publish package to PyPI
        run: uv publish # 
```

## Conclusion

The `PyPlanhat` project is positioned to be a model of modern Python development. By adopting the "Astral Stack" from its inception, the project will benefit from a unified, high-speed, and ergonomic toolchain.

The key architectural decisions are:

1. **Unified Tooling:** Using `uv` for package management, environment management, building, and publishing, and `ruff`for linting, formatting, and import sorting.
    
2. **A Single Manifest:** Configuring this entire stack declaratively within `pyproject.toml`.
    
3. **DRY Architecture:** Writing _only_ an async-first client and test suite, and using an `unasync` script to _generate_ the synchronous, production-ready counterparts.
    
4. **Ergonomic Design:** Using Pydantic to provide data validation as a feature and a custom exception hierarchy to simplify error handling for the user.
    
5. **Total Automation:** Implementing a two-stage release pipeline that uses `python-semantic-release` for automated versioning and changelogs, and `uv publish` with PyPI's Trusted Publishing for a secure, secret-free deployment.
    

This foundation will ensure `PyPlanhat` is not only easy to use but also efficient to maintain, setting a new standard for Python SDKs in 2025.

---

## Addendum: Critical Clarifications and Corrections (November 2025)

The following updates refine the original research based on the latest tool versions and best practices as of November 2025.

### A.1. Build Backend: Hatchling Confirmed

**Status**: RESOLVED - Using hatchling as build backend

**Decision**: Hatchling is confirmed as the build backend for PyPlanhat. It is mature, well-documented, and widely used in production. The configuration is already in place and working correctly.

### A.2. Python Version Support

**Status**: REVISED - Now using Python 3.10+

**Original Decision (Phase 0)**: Python 3.12+ was initially selected as the minimum supported version.

**Revised Decision (Pre-Publication)**: Expanded to Python 3.10+ to increase potential user base by ~40%. Per AGENTS.md specification and PYPI.md research, supporting Python 3.10+ provides broader compatibility while maintaining all required functionality. Modern features available in Python 3.10+ (PEP 604 union types, structural pattern matching, etc.) are sufficient for SDK requirements.

### A.3. The unasync Library and Code Generation Strategy

**Research Finding**: The unasync library (https://github.com/python-trio/unasync) is an active, well-maintained tool specifically designed for this use case. Current version is 0.6.0 (May 2024). It is used by production libraries including:
- The official Elasticsearch Python client
- httpcore (the foundation of httpx)

**Implementation Approach**: unasync should be added as a development dependency and integrated into the build process. The library provides a setuptools command class that can be invoked during package building.

**Critical Consideration**: Generated code **should be committed to version control**. This ensures:
1. Users installing from source (not PyPI) get working code without needing to run generators
2. Code reviews can inspect both async source and generated sync code
3. The package can be built in restricted environments

The generated files should be marked with clear auto-generated headers and configured in .gitattributes to skip them in diffs.

**Recommendation**: Add unasync to dev dependencies and create a pre-commit hook or CI check to ensure generated code is up-to-date before commits.

### A.4. Testing with pytest-httpx

**Research Finding**: pytest-httpx is the definitive, production-ready tool for mocking httpx requests. Key facts:
- Current version: 0.35.0 (November 2024)
- Classified as "Production/Stable" (Development Status 5)
- Supports Python 3.9+
- Has 272 passing tests and 100% coverage
- Provides the `httpx_mock` fixture

**Critical Difference from responses**: The `responses` library is designed for mocking the `requests` library, NOT httpx. Using responses with httpx will not work.

**Recommendation**: Remove `responses` from dependencies and replace with `pytest-httpx>=0.30.0`. Also add `pytest-asyncio` for async test support.

### A.5. Planhat API Authentication

**Status**: COMPLETED - Authentication method documented in API.md

**Research Findings**: The Planhat API uses Bearer token authentication:
- **Method**: Bearer token or Basic Auth
- **Header**: `Authorization: Bearer {{apiAccessToken}}` or `Authorization: Basic {{token}}:`
- **Token Source**: Generated via **Private Apps** in Planhat Settings
- **Base URL**: `https://api.planhat.com` (main API)

**Implementation**: Use Bearer token in Authorization header with fallback to empty dict when api_key is None.

### A.6. Planhat API Data Models

**Status**: COMPLETED - Resource schemas documented in API.md

**Research Findings**: Complete API schemas documented for:
- **Company Resource**: Required field `name` only, supports custom fields via `custom` object
- **Enduser Resource**: Required `companyId` + (`email` OR `externalId` OR `sourceId`)
- **Conversation Resource**: Required `companyId` only, supports custom fields via `custom` object

**Implementation**: All resources support `custom: Dict[str, Any] = {}` for flexible custom data.

### A.7. python-semantic-release Configuration

**Research Finding**: python-semantic-release (PSR) v9.x requires configuration in pyproject.toml under `[tool.semantic_release]`. Key required settings:

- `version_toml`: List of files where version should be updated (e.g., "pyproject.toml:project.version")
- `branch`: The branch to release from (typically "main")
- `build_command`: Command to run before publishing (e.g., "uv build")
- `version_variables`: Python files where __version__ should be updated

**Recommendation**: Add `[tool.semantic_release]` configuration section to the pyproject.toml example in Section 1.

### A.8. Project Structure: src/ Layout

**Important Clarification**: The existing project correctly uses the `src/` layout (src/pyplanhat/), which is modern Python packaging best practice. All examples in the PLAN should be updated to reflect this structure:

- Async source: `src/pyplanhat/_async/`
- Generated sync: `src/pyplanhat/_sync/`
- Top-level import: `src/pyplanhat/__init__.py`

This prevents the package from being accidentally importable from the project root during development.

### A.9. .gitignore for Generated Code

**Controversial Decision**: While some projects exclude generated code from version control, the recommended approach for this project is to **commit the generated sync code**.

Rationale:
- Ensures pip installs from GitHub work without build tools
- Allows reviewers to verify the transformation is correct
- Prevents CI/CD failures if unasync has issues

**Recommendation**: Do NOT add `_sync/` to .gitignore. Instead, add a .gitattributes entry to mark generated files and reduce noise in diffs.