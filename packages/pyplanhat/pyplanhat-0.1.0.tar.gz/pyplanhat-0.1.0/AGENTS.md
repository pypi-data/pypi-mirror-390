# PyPlanhat SDK Development Rules

This document contains project-specific instructions for OpenCode agents working on the PyPlanhat SDK development.

## Project Context

**PyPlanhat SDK** is a modern Python SDK for the Planhat API, built using the Astral stack (uv, ruff) with async-first architecture.

### Key Architectural Decisions

1. **Async-First DRY Architecture**: All business logic written once in `_async/` source
2. **Generated Sync Code**: Synchronous code generated via `unasync`, never manual
3. **Astral Stack**: Use `uv` for package management, `ruff` for linting/formatting
4. **Test-Driven**: Comprehensive coverage for both async and sync versions
5. **Generated Code Committed**: Sync code is in version control, not .gitignored

## Development Standards

### Python Environment
- **Target**: Python 3.10+
- **Build Backend**: hatchling (preferred over uv_build)
- **Package Manager**: uv for all workflows
- **Virtual Environment**: uv sync for dependency management

### Core Dependencies
```toml
[project.dependencies]
httpx>=0.27.0          # HTTP client (async-first)
pydantic>=2.0.0         # Data validation and models

[project.optional-dependencies]
test = [
    pytest>=7.0.0,
    pytest-httpx>=0.30.0,  # Replace responses library
    pytest-asyncio>=0.21.0,
    pytest-cov>=4.0.0,
]

dev = [
    unasync>=0.15.0,       # Code generation
    ruff>=0.1.0,          # Linting and formatting
    mypy>=1.0.0,          # Type checking
]
```

### Project Structure
```
src/
├── pyplanhat/
│   ├── _async/          # Async source code (write here only)
│   │   ├── client.py
│   │   └── resources/
│   │       ├── companies.py
│   │       ├── endusers.py
│   │       └── conversations.py
│   ├── _sync/           # Generated sync code (never edit)
│   │   ├── client.py
│   │   └── resources/
│   ├── _exceptions.py   # Custom exception hierarchy
│   └── __init__.py     # Public API exports
tests/
├── _async/             # Async tests (write here only)
│   ├── test_client.py
│   ├── test_companies.py
│   ├── test_endusers.py
│   └── test_conversations.py
└── _sync/              # Generated sync tests (never edit)
    ├── test_client.py
    ├── test_companies.py
    ├── test_endusers.py
    └── test_conversations.py
scripts/
└── generate_sync.py     # unasync generation script
```

## Critical Rules

### 1. Async-First Development
- **ALL business logic** must be written in `src/pyplanhat/_async/`
- **NEVER write sync code manually** - always generate via unasync
- **Test async first**, then generate sync tests
- **Commit both async source and generated sync code**

### 2. Generated Code Management
- **Generated sync code MUST be committed** to version control
- **DO NOT add** `src/pyplanhat/_sync/` or `tests/_sync/` to .gitignore
- **Use .gitattributes** to mark generated files: `*.py linguist-generated=true`
- **NEVER manually edit** files in `_sync/` directories

### 3. Exception Hierarchy
Follow this exact hierarchy for all error handling:

```python
# Base exception
class PyPlanhatError(Exception):
    """Base exception for all PyPlanhat errors."""
    pass

# Network/connection issues
class APIConnectionError(PyPlanhatError):
    """Raised when network/timeout issues occur."""
    pass

# HTTP errors (base class with attributes)
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

### 4. Testing Standards
- **Use pytest-httpx** for mocking (NOT responses library)
- **Test both async and sync versions** identically
- **Test all error conditions** with custom exceptions
- **Maintain test parity** - both suites must be equivalent
- **Use `@pytest.mark.asyncio`** for async test functions only

**Fixture Configuration (CRITICAL - Phase 1 Lesson)**:
- ✅ **Async fixtures**: Use `@pytest_asyncio.fixture` decorator
- ✅ **Sync fixtures**: Use `@pytest.fixture` decorator (NOT pytest_asyncio)
- ✅ **Keep fixtures in conftest.py** - Don't duplicate in test files
- ⚠️ **After code generation**: Verify sync conftest uses `@pytest.fixture`
- ⚠️ **Common bug**: unasync copies `@pytest_asyncio.fixture` to sync code (incorrect)

**Type-Safe Response Handling**:
```python
# Correct pattern for create/update operations
data = await self._handle_response(response)
assert data is not None  # POST/PUT should never return 204
return Model(**data)

# WRONG: Don't raise status 500 for defensive checks
# if data is None:
#     raise InvalidRequestError("Failed", 500, "")  # ❌
```

### 5. API Integration Patterns
- **Use httpx.AsyncClient** for async implementation
- **Use httpx.Client** for sync implementation (generated)
- **Handle all HTTP status codes** with custom exceptions
- **Parse responses with Pydantic models**
- **Support custom fields** with `Dict[str, Any] = {}` default

### 6. Docstring Guidelines
**CRITICAL**: Docstrings in async source are copied to sync code during generation.

**DO**:
- Use generic, implementation-agnostic docstrings
- Example: "PyPlanhat client" (not "Async PyPlanhat client")
- Example: "Tests for PyPlanhat SDK" (not "Async tests")
- Example: "Fixture providing a PyPlanhat client" (not "async client")

**DON'T**:
- Use "async" or "sync" specifiers in docstrings
- Reference implementation details that won't translate
- Write docstrings that only make sense for async or sync variant

**Why**: The `generate_sync.py` script transforms code tokens but preserves string content. Generic docstrings ensure both variants have accurate documentation and avoid false positives in code reviews.

## Phase-Based Development

### Phase 0: Foundation (P0-0 to P0-9)
Critical setup tasks that must be completed before feature development:
- **P0-0**: Research Planhat API specification (authentication, endpoints, schemas)
- **P0-1**: Update project configuration (dependencies, Python version, tools)
- **P0-2**: Establish directory structure with src/ layout
- **P0-3**: Configure version control for generated code
- **P0-4**: Implement unasync integration with token replacements
- **P0-5**: Define custom exception hierarchy
- **P0-6**: Build core client shell with authentication
- **P0-7**: Generate initial sync code and verify
- **P0-8**: Create top-level package imports
- **P0-9**: Set up CI workflow with all quality gates

### Phase 1: Companies (P1-1 to P1-5)
First vertical slice to validate architecture:
- **P1-1**: Create Company Pydantic model with exact API schema
- **P1-2**: Implement AsyncCompanies resource with full CRUD
- **P1-3**: Write comprehensive async tests with error scenarios
- **P1-4**: Generate and verify sync code
- **P1-5**: Run full test suite and validate parity

### Phase 2: Resources (P2-1 to P2-3)
Expand to remaining v1.0 resources:
- **P2-1**: Implement End Users resource (follow P1 pattern)
- **P2-2**: Implement Conversations resource (follow P1 pattern)
- **P2-3**: Wire resources to main client with namespace pattern

### Phase 3: Documentation (P3-1 to P3-5)
Professional documentation and release automation:
- **P3-1**: Set up mkdocs with Material theme
- **P3-2**: Write user-facing documentation
- **P3-3**: Configure mkdocstrings for API reference
- **P3-4**: Implement release workflow
- **P3-5**: Configure trusted publishing

### Phase 4: Release (P4-1 to P4-3)
Final release to PyPI:
- **P4-1**: Final review and merge
- **P4-2**: Trigger release with semantic versioning
- **P4-3**: Monitor and verify PyPI publication

## Quality Gates

### Before Any Task Completion
1. ✅ **Tests Pass**: Both async and sync test suites pass
2. ✅ **Linting Clean**: `ruff check .` shows no issues
3. ✅ **Formatted**: `ruff format --check .` passes
4. ✅ **Type Checked**: `mypy src/` passes without errors
5. ✅ **Generated Code**: Sync code regenerated and committed
6. ✅ **Fixture Decorators**: Sync conftest uses `@pytest.fixture` (not `@pytest_asyncio.fixture`)
7. ✅ **No Duplicate Fixtures**: Test files don't redefine conftest fixtures
8. ✅ **Documentation**: Updated if API changes made

### Before Phase Completion
1. ✅ **All Tasks Complete**: Every task in phase meets criteria
2. ✅ **CI Pipeline**: All checks passing on main branch
3. ✅ **No TODOs**: No outstanding TODO or FIXME comments
4. ✅ **Architecture Compliance**: No deviations from documented patterns
5. ✅ **Scope Validation**: No features beyond documented scope

## Scope Creep Prevention

### Forbidden Changes
- **Build Backend**: Do not change from hatchling
- **Python Version**: Do not support < 3.10
- **Test Library**: Do not use responses (use pytest-httpx)
- **HTTP Library**: Do not use requests (use httpx)
- **Generated Code**: Do not .gitignore generated files
- **Architecture**: Do not break async-first pattern

### Required Justifications
- **New Dependencies**: Must be documented in PLAN.md
- **Architecture Changes**: Must update documentation first
- **Additional Resources**: Must be approved for v1.0+ scope
- **Custom Patterns**: Must follow established conventions

## Agent-Specific Instructions

### Architect Agent
- **Read-only analysis** - No code editing
- **Research focused** - API docs, architecture validation
- **Planning output** - Detailed implementation plans
- **Dependency checking** - Identify prerequisites and blockers

### Builder Agent
- **Implementation focused** - Write code following patterns
- **Test-driven** - Write tests alongside implementation
- **Quality gates** - Ensure all checks pass
- **Generated code** - Regenerate and commit sync code

### Reviewer Agent
- **Quality validation** - Check all gates and standards
- **Scope enforcement** - Prevent architectural drift
- **Test parity** - Verify async/sync equivalence
- **Documentation review** - Ensure completeness and accuracy

## External References

When working on specific tasks, reference these documents:

### For API Research (P0-0)
- Planhat API Documentation: https://docs.planhat.com
- Authentication methods and headers
- JSON schemas for Companies, End Users, Conversations
- Custom fields handling patterns

### For Implementation Patterns
- Python Async/Await Best Practices
- httpx Documentation for async client usage
- Pydantic Documentation for model definitions
- pytest-httpx Documentation for mocking patterns

### For Release Process
- Python Packaging Authority Guidelines
- PyPI Trusted Publishing Documentation
- GitHub Actions Documentation for workflows
- Semantic Release Documentation

## Success Metrics

### Development Quality
- **Test Coverage**: > 90% for both async and sync
- **Linting**: Zero ruff issues
- **Type Checking**: Zero mypy errors
- **Documentation**: 100% public API covered

### Architecture Compliance
- **DRY**: Zero duplicated business logic
- **Generated Code**: 100% generated, 0% manual edits
- **Exception Handling**: 100% custom exceptions used
- **Pattern Consistency**: All resources follow same pattern

### Process Efficiency
- **CI/CD**: All gates automated and passing
- **Release**: Fully automated with semantic versioning
- **Documentation**: Auto-generated API reference
- **Quality**: Zero manual quality checks required

---

**Remember**: The goal is to build a high-quality Python SDK while maintaining strict architectural discipline. Every change should serve the SDK's users and follow established patterns.