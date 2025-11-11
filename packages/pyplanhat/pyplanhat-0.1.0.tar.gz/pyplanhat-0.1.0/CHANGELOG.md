# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2025-11-10

### Added

#### Core SDK
- **AsyncPyPlanhat** client with async-first architecture
- **PyPlanhat** synchronous client (auto-generated from async source)
- Context manager support for both clients (`async with` / `with`)
- Bearer token authentication via `api_key` parameter
- Configurable base URL for API endpoint customization

#### Resources
- **Companies** resource with full CRUD operations:
  - `list()` - Retrieve all companies with pagination support
  - `get(id)` - Fetch single company by ID
  - `create(company)` - Create new company
  - `update(id, company)` - Update existing company
  - `delete(id)` - Delete company by ID
- Pydantic-based `Company` model with comprehensive field validation

#### Error Handling
- Custom exception hierarchy for precise error handling:
  - `PyPlanhatError` - Base exception for all SDK errors
  - `APIConnectionError` - Network/timeout issues
  - `APIError` - Base for HTTP errors (includes status_code and response_body)
  - `AuthenticationError` - 401/403 authentication failures
  - `InvalidRequestError` - 400/404 bad requests
  - `RateLimitError` - 429 rate limit exceeded
  - `ServerError` - 5xx server errors

#### Architecture
- **Async-first DRY architecture** using `unasync` for code generation
- Zero duplication of business logic between async and sync implementations
- Single source of truth in `src/pyplanhat/_async/` directory
- Automated sync code generation via `scripts/generate_sync.py`

#### Type Safety
- Full mypy type checking support with strict mode
- Type hints throughout codebase
- Pydantic models for runtime validation

#### Testing
- Comprehensive test suite with 97% code coverage
- 52 tests covering both async and sync implementations
- Parallel test structure (`tests/_async/` and `tests/_sync/`)
- HTTP mocking with `pytest-httpx`
- Error scenario coverage (400, 401, 403, 404, 429, 5xx)

### Documentation

- Comprehensive README with installation and quick start guides
- Async and sync usage examples
- Development setup and workflow documentation
- Architecture overview and design principles
- Contribution guidelines
- Phase-based development plan (PLAN.md)
- Detailed architecture documentation (ARCHITECTURE.md)
- PyPI publication strategy (PYPI.md)

### Infrastructure

- Modern Python packaging with `pyproject.toml` (PEP 621)
- MIT License
- Python 3.10+ support (3.10, 3.11, 3.12, 3.13)
- GitHub Actions CI/CD:
  - Automated testing on push/PR
  - Linting with `ruff`
  - Type checking with `mypy`
  - Code coverage reporting with Codecov
- Automated PyPI publishing via GitHub Actions and Trusted Publishing
- uv package manager integration

### Dependencies

- `httpx>=0.27.0` - Modern async HTTP client
- `pydantic>=2.0.0` - Data validation and settings management

---

*Note: Version 0.1.0 represents the initial public release. The SDK is in Alpha status with a stable API for the Companies resource. Additional resources (EndUsers, Conversations) will be added in future releases.*
