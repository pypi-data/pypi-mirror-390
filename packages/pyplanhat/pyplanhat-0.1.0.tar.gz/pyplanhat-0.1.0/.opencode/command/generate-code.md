---
description: Run unasync transformation and validate output
---

Execute unasync transformation, run ruff fixes, validate test parity, and commit generated code.

## Unasync Transformation

1. **Run Generation Script**:
   ```bash
   python scripts/generate_sync.py
   ```

2. **Verify Transformation**:
   - Check that `src/pyplanhat/_sync/` was generated
   - Verify `tests/_sync/` was generated
   - Ensure no `async` keywords remain in sync code
   - Confirm `httpx.AsyncClient` → `httpx.Client` transformation

3. **Validate Token Replacements**:
   - `AsyncClient` → `Client`
   - `AsyncPyPlanhat` → `PyPlanhat`
   - `async def` → `def`
   - `await` removed
   - `@pytest.mark.asyncio` removed from tests

## Code Quality Fixes

1. **Apply Ruff Formatting**:
   ```bash
   uv run ruff format src/pyplanhat/_sync/ tests/_sync/
   ```

2. **Fix Linting Issues**:
   ```bash
   uv run ruff check src/pyplanhat/_sync/ tests/_sync/ --fix
   ```

3. **Type Checking**:
   ```bash
   uv run mypy src/pyplanhat/_sync/
   ```

## Test Parity Validation

1. **Run Async Tests**:
   ```bash
   uv run pytest tests/_async/ -v --tb=short
   ```

2. **Run Sync Tests**:
   ```bash
   uv run pytest tests/_sync/ -v --tb=short
   ```

3. **Compare Results**:
   - Verify both test suites pass
   - Check that test counts are identical
   - Ensure coverage percentages match
   - Validate identical test patterns

## Generated Code Verification

### Manual Inspection Points
Check these critical transformations:

#### Client Code
```python
# Async source (src/pyplanhat/_async/client.py)
class AsyncPyPlanhat:
    def __init__(self, api_key: str = None):
        self._client = httpx.AsyncClient(...)

    async def close(self):
        await self._client.aclose()

# Generated sync (src/pyplanhat/_sync/client.py)
class PyPlanhat:
    def __init__(self, api_key: str = None):
        self._client = httpx.Client(...)

    def close(self):
        self._client.close()
```

#### Resource Code
```python
# Async source
async def list(self) -> List[Company]:
    response = await self._client.get("/companies")
    return [Company(**item) for item in response.json()]

# Generated sync
def list(self) -> List[Company]:
    response = self._client.get("/companies")
    return [Company(**item) for item in response.json()]
```

#### Test Code
```python
# Async test
@pytest.mark.asyncio
async def test_list_companies(async_client):
    result = await async_client.companies.list()

# Generated sync test
def test_list_companies(sync_client):
    result = sync_client.companies.list()
```

## Version Control Integration

1. **Check Git Status**:
   ```bash
   git status
   ```

2. **Review Changes**:
   ```bash
   git diff src/pyplanhat/_sync/
   git diff tests/_sync/
   ```

3. **Commit Generated Code**:
   ```bash
   git add src/pyplanhat/_sync/ tests/_sync/
   git commit -m "build: regenerate sync code from async source"
   ```

## Error Handling

### Common Issues and Solutions

#### Token Replacement Failures
```bash
# If async keywords remain:
grep -r "async def" src/pyplanhat/_sync/
grep -r "await " src/pyplanhat/_sync/

# Manual fix if needed
sed -i 's/async def /def /g' src/pyplanhat/_sync/*.py
```

#### Import Issues
```bash
# Check for incorrect imports
grep -r "from.*_async" src/pyplanhat/_sync/

# Should be:
# from pyplanhat._sync.client import Client
```

#### Test Decorators
```bash
# Remove remaining pytest.mark.asyncio
grep -r "@pytest.mark.asyncio" tests/_sync/
```

## Validation Checklist

### Generation Success
- [ ] Script completed without errors
- [ ] All async files have sync counterparts
- [ ] No `async` keywords in sync code
- [ ] No `await` keywords in sync code

### Code Quality
- [ ] Ruff formatting applied
- [ ] Linting issues fixed
- [ ] Type checking passes
- [ ] Import statements correct

### Test Parity
- [ ] Async tests pass
- [ ] Sync tests pass
- [ ] Test counts identical
- [ ] Coverage percentages match

### Version Control
- [ ] Generated code committed
- [ ] No manual edits detected
- [ ] Git history clean

## Output Format

```
## Sync Code Generation Report

### Generation Status
- **Script Execution**: ✅ Success / ❌ Failed
- **Files Generated**: X sync files, Y test files
- **Transformations Applied**: All successful / Issues found

### Quality Validation
- **Ruff Formatting**: ✅ Applied / ❌ Issues
- **Linting**: ✅ No issues / ❌ X issues found
- **Type Checking**: ✅ Pass / ❌ Errors found

### Test Parity
- **Async Tests**: ✅ X/Y passing
- **Sync Tests**: ✅ X/Y passing  
- **Coverage Match**: ✅ Identical / ❌ Differs

### Git Status
- **Changes Committed**: ✅ Ready / ❌ Needs attention
- **Manual Edits**: ❌ Detected / ✅ None found
```

## Usage Examples

```bash
/generate-code
# Full generation and validation cycle

/generate-code
# After implementing new async feature
```

## Agent Workflow

Recommended to run this in **builder** agent after implementing async features, but can be used in any agent.

## Notes

- Always run after changes to async source code
- Never manually edit generated sync files
- Commit generated code to version control
- Use reviewer agent to validate parity if issues arise