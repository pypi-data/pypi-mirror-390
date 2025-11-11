# PyPlanhat SDK Development Guide

## Development Environment Setup

### Prerequisites

- Python 3.10+
- uv (Astral package manager)
- Git with GitHub CLI
- Make (optional, for convenience scripts)

### Initial Setup

```bash
# Clone repository
git clone https://github.com/your-org/pyplanhat.git
cd pyplanhat

# Install dependencies
uv sync --all-groups

# Set up pre-commit hooks (if configured)
uv run pre-commit install
```

## Development Workflow

### Daily Development Cycle

```bash
# Sync dependencies (run daily)
uv sync

# Run tests during development
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src/pyplanhat --cov-report=term-missing

# Lint and format code
uv run ruff format .
uv run ruff check .

# Type checking
uv run mypy src/

# Generate sync code after async changes
python scripts/generate_sync.py
```

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/P0-1-task-name

# Check status
git status

# Stage and commit changes
git add .
git commit -m "feat: implement P0-1 - update project configuration"

# Push to remote
git push origin feature/P0-1-task-name

# Switch back to main
git checkout main
git pull origin main
```

## Quality Gates

### Before Committing

1. **Tests Pass**: Both async and sync test suites
2. **Linting Clean**: `ruff check .` shows no issues
3. **Formatted**: `ruff format --check .` passes
4. **Type Checked**: `mypy src/` passes without errors
5. **Generated Code**: Sync code regenerated and committed
6. **Documentation**: Updated if API changes made

### Before Phase Completion

1. **All Tasks Complete**: Every task in phase meets criteria
2. **CI Pipeline**: All checks passing on main branch
3. **No TODOs**: No outstanding TODO or FIXME comments
4. **Architecture Compliance**: No deviations from documented patterns
5. **Scope Validation**: No features beyond documented scope

## Testing Strategy

### Test Structure

```
tests/
├── _async/                 # Async tests (write here)
│   ├── test_client.py      # Client tests
│   ├── test_companies.py   # Companies resource tests
│   ├── test_endusers.py    # End users resource tests
│   └── test_conversations.py # Conversations resource tests
└── _sync/                  # Generated sync tests (don't edit)
    ├── test_client.py
    ├── test_companies.py
    ├── test_endusers.py
    └── test_conversations.py
```

### Test Writing Guidelines

#### Async Test Example

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
    httpx_mock.add_response(
        json=[
            {"id": "1", "name": "Company A", "domain": "company-a.com"},
            {"id": "2", "name": "Company B", "domain": "company-b.com"}
        ]
    )
    
    companies = await async_client.companies.list()
    
    assert len(companies) == 2
    assert companies[0].id == "1"
    assert companies[0].name == "Company A"
    assert companies[0].domain == "company-a.com"

@pytest.mark.asyncio
async def test_get_company_success(async_client, httpx_mock):
    """Test getting a specific company successfully."""
    httpx_mock.add_response(
        json={
            "id": "1", 
            "name": "Company A", 
            "domain": "company-a.com"
        }
    )
    
    company = await async_client.companies.get("1")
    
    assert company.id == "1"
    assert company.name == "Company A"

@pytest.mark.asyncio
async def test_get_company_not_found(async_client, httpx_mock):
    """Test getting a non-existent company raises error."""
    httpx_mock.add_response(
        status_code=404,
        text="Company not found"
    )
    
    with pytest.raises(InvalidRequestError) as exc_info:
        await async_client.companies.get("nonexistent")
    
    assert exc_info.value.status_code == 404
    assert "Company not found" in str(exc_info.value)

@pytest.mark.asyncio
async def test_create_company_success(async_client, httpx_mock):
    """Test creating a new company successfully."""
    new_company = Company(name="New Company", domain="new-company.com")
    
    httpx_mock.add_response(
        status_code=201,
        json={
            "id": "3", 
            "name": "New Company", 
            "domain": "new-company.com"
        }
    )
    
    created_company = await async_client.companies.create(new_company)
    
    assert created_company.id == "3"
    assert created_company.name == "New Company"

@pytest.mark.asyncio
async def test_authentication_error(async_client, httpx_mock):
    """Test authentication error handling."""
    httpx_mock.add_response(
        status_code=401,
        text="Invalid API key"
    )
    
    with pytest.raises(AuthenticationError) as exc_info:
        await async_client.companies.list()
    
    assert exc_info.value.status_code == 401
    assert "Invalid API key" in str(exc_info.value)

@pytest.fixture
async def async_client():
    """Fixture for async client."""
    client = AsyncPyPlanhat(api_key="test-key")
    yield client
    await client.close()
```

#### Test Coverage Requirements

- **Happy Path**: All successful operations
- **Error Cases**: All HTTP error codes (400, 401, 403, 404, 429, 5xx)
- **Edge Cases**: Empty responses, malformed data, network issues
- **Validation**: Invalid input data handling
- **Custom Fields**: Test custom field serialization/deserialization

### Running Tests

```bash
# Run all tests
uv run pytest -v

# Run specific test file
uv run pytest tests/_async/test_companies.py -v

# Run specific test
uv run pytest tests/_async/test_companies.py::test_list_companies -v

# Run with coverage
uv run pytest --cov=src/pyplanhat --cov-report=html

# Run async tests only
uv run pytest tests/_async/ -v

# Run sync tests only
uv run pytest tests/_sync/ -v

# Compare test coverage between async and sync
uv run pytest tests/_async/ --cov=src/pyplanhat --cov-report=term-missing
uv run pytest tests/_sync/ --cov=src/pyplanhat --cov-report=term-missing
```

## Code Generation Workflow

### After Async Changes

```bash
# 1. Regenerate sync code
python scripts/generate_sync.py

# 2. Apply formatting to generated code
uv run ruff format src/pyplanhat/_sync/ tests/_sync/

# 3. Fix any linting issues
uv run ruff check src/pyplanhat/_sync/ tests/_sync/ --fix

# 4. Type check generated code
uv run mypy src/pyplanhat/_sync/

# 5. Run sync tests to verify parity
uv run pytest tests/_sync/ -v

# 6. Commit generated code
git add src/pyplanhat/_sync/ tests/_sync/
git commit -m "build: regenerate sync code from async source"
```

### Validation Script

```bash
#!/bin/bash
# scripts/validate_sync_generation.sh

echo "🔄 Regenerating sync code..."
python scripts/generate_sync.py

echo "🎨 Formatting generated code..."
uv run ruff format src/pyplanhat/_sync/ tests/_sync/

echo "🔧 Fixing linting issues..."
uv run ruff check src/pyplanhat/_sync/ tests/_sync/ --fix

echo "🔍 Type checking generated code..."
uv run mypy src/pyplanhat/_sync/

echo "🧪 Running sync tests..."
uv run pytest tests/_sync/ -v

echo "📊 Comparing test coverage..."
echo "Async tests:"
uv run pytest tests/_async/ --cov=src/pyplanhat --cov-report=term-missing | grep "TOTAL"
echo "Sync tests:"
uv run pytest tests/_sync/ --cov=src/pyplanhat --cov-report=term-missing | grep "TOTAL"

echo "✅ Sync code generation validation complete!"
```

## Tooling Configuration

### ruff Configuration

```toml
# pyproject.toml
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
    "E501",  # line too long, handled by black
    "B008",  # do not perform function calls in argument defaults
    "C901",  # too complex
]

[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]
"tests/*" = ["B011"]  # assert False in tests is fine
```

### mypy Configuration

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
check_untyped_defs = true
disallow_any_generics = true
disallow_incomplete_defs = true
disallow_untyped_defs = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_ignores = true

[[tool.mypy.overrides]]
module = "tests.*"
disallow_untyped_defs = false
```

### pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
minversion = "7.0"
addopts = "-ra -q --strict-markers --strict-config"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
]
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.12"]

    steps:
    - uses: actions/checkout@v5

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install uv
      uses: astral-sh/setup-uv@v2
    
    - name: Install dependencies
      run: uv sync --all-groups
    
    - name: Run linting
      run: uv run ruff check .
    
    - name: Check formatting
      run: uv run ruff format --check .
    
    - name: Run type checking
      run: uv run mypy src/
    
    - name: Run tests
      run: uv run pytest --cov=src/pyplanhat --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella
```

## Debugging Guide

### Common Issues

#### 1. unasync Generation Failures

```bash
# Check for remaining async keywords
grep -r "async def" src/pyplanhat/_sync/
grep -r "await " src/pyplanhat/_sync/

# Check for incorrect imports
grep -r "from.*_async" src/pyplanhat/_sync/

# Check for remaining pytest decorators
grep -r "@pytest.mark.asyncio" tests/_sync/
```

#### 2. Test Parity Issues

```bash
# Compare test counts
echo "Async test count:"
find tests/_async/ -name "test_*.py" -exec grep -l "def test_" {} \; | wc -l
echo "Sync test count:"
find tests/_sync/ -name "test_*.py" -exec grep -l "def test_" {} \; | wc -l

# Compare test content (should be identical except for async/await)
diff -u tests/_async/test_companies.py tests/_sync/test_companies.py
```

#### 3. Import Issues

```bash
# Check for circular imports
uv run python -c "import src.pyplanhat._async.client"

# Check for missing imports
uv run mypy src/ --show-error-codes
```

### Debugging Tools

```bash
# Install debugging dependencies
uv add --group dev ipdb pdbpp

# Use in code
import ipdb; ipdb.set_trace()  # IPython debugger
import pdb; pdb.set_trace()    # Standard debugger
```

## Performance Optimization

### Development Performance

```bash
# Use uv's fast installation
uv sync --frozen  # Skip dependency resolution if lockfile unchanged

# Run tests in parallel
uv run pytest -n auto

# Use mypy daemon for faster type checking
uv run mypy src/ --daemon
```

### Runtime Performance

- Use connection pooling for HTTP clients
- Implement proper caching for API responses
- Optimize Pydantic model serialization
- Use async context managers properly

## Release Process

### Pre-release Checklist

1. **All Tests Pass**: Both async and sync suites
2. **Documentation Updated**: API docs and user guide
3. **Version Bumped**: Update version in pyproject.toml
4. **Changelog Updated**: Document all changes
5. **CI/CD Green**: All checks passing on main branch

### Release Commands

```bash
# Build package
uv build

# Check package
uv run twine check dist/*

# Upload to test PyPI
uv run twine upload --repository testpypi dist/*

# Upload to PyPI (after testing)
uv run twine upload dist/*
```

This development guide ensures consistent, high-quality development across the PyPlanhat SDK team.