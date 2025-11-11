---
description: Check completion criteria for a phase
---

Review all issues in phase $ARGUMENTS, verify completion criteria, check for blockers, and suggest next tasks.

## Phase Analysis

1. **Load Phase Tasks**:
   ```bash
   gh issue list --label "phase-$ARGUMENTS" --state all --json number,title,state,labels
   ```

2. **Check Completion Status**:
   - Review all tasks in the specified phase
   - Verify completion criteria from `docs/pyplanhat/PLAN.md`
   - Identify any incomplete or blocked tasks

3. **Quality Validation**:
   - Run test suite for phase-specific features
   - Check linting and type checking status
   - Verify documentation completeness

## Completion Criteria Check

### Phase 0: Foundation
- [ ] P0-0: Planhat API research completed and documented
- [ ] P0-1: Project configuration updated with correct dependencies
- [ ] P0-2: Directory structure created with src/ layout
- [ ] P0-3: Generated code properly configured in version control
- [ ] P0-4: unasync integration working with token replacements
- [ ] P0-5: Custom exception hierarchy implemented
- [ ] P0-6: Core client shell with authentication
- [ ] P0-7: Initial sync code generated and verified
- [ ] P0-8: Top-level package imports configured
- [ ] P0-9: CI workflow running and passing

### Phase 1: Companies
- [ ] P1-1: Company Pydantic model with exact API schema
- [ ] P1-2: AsyncCompanies resource with full CRUD
- [ ] P1-3: Comprehensive async tests with error scenarios
- [ ] P1-4: Sync code generated and verified
- [ ] P1-5: Full test suite passing with coverage

### Phase 2: Resources
- [ ] P2-1: End Users resource implemented
- [ ] P2-2: Conversations resource implemented
- [ ] P2-3: Resources wired to main client

### Phase 3: Documentation
- [ ] P3-1: mkdocs setup with Material theme
- [ ] P3-2: User-facing documentation complete
- [ ] P3-3: mkdocstrings configured for API reference
- [ ] P3-4: Release workflow implemented
- [ ] P3-5: Trusted publishing configured

### Phase 4: Release
- [ ] P4-1: Final review and merge complete
- [ ] P4-2: Release triggered and version bumped
- [ ] P4-3: Package published to PyPI successfully

## Quality Gates Validation

### Test Suite
```bash
# Run full test suite
uv run pytest -v

# Check coverage
uv run pytest --cov=src/pyplanhat --cov-report=term-missing
```

### Code Quality
```bash
# Linting
uv run ruff check .

# Formatting
uv run ruff format --check .

# Type checking
uv run mypy src/
```

### Generated Code
```bash
# Regenerate and verify
python scripts/generate_sync.py
git diff --exit-code src/pyplanhat/_sync tests/_sync
```

## Blocker Identification

Check for:
- **Incomplete Dependencies**: Previous phase tasks not finished
- **Test Failures**: Any failing tests blocking completion
- **Documentation Gaps**: Missing or outdated documentation
- **Architecture Issues**: Deviations from documented patterns
- **Tooling Problems**: CI/CD or build failures

## Output Format

### Phase Summary
```
## Phase $ARGUMENTS Validation Summary

### Completion Status
- **Tasks Complete**: X/Y (Z%)
- **Critical Blockers**: N identified
- **Quality Gates**: ✅ All Passed / ❌ Issues Found

### Task Status
| Task | Status        | Issues          |
| ---- | ------------- | --------------- |
| P0-1 | ✅ Complete    | None            |
| P0-2 | ⚠️ In Progress | Missing tests   |
| P0-3 | ❌ Blocked     | Depends on P0-2 |

### Next Steps
1. **Immediate**: Complete P0-2 test coverage
2. **Short-term**: Finish P0-3 implementation
3. **Ready for Phase 1**: After P0-2 and P0-3 complete
```

### Quality Report
```
## Quality Gates Status

### Tests
- **Async Tests**: ✅ Passing (95% coverage)
- **Sync Tests**: ✅ Passing (95% coverage)
- **Parity**: ✅ Equivalent

### Code Quality
- **Linting**: ✅ No issues
- **Formatting**: ✅ Compliant
- **Type Checking**: ✅ No errors

### Documentation
- **API Reference**: ✅ Generated
- **User Guide**: ✅ Complete
- **Examples**: ✅ Working
```

## Usage Examples

```bash
/validate-phase P0
# Checks Phase 0 foundation completion

/validate-phase P1
# Validates Phase 1 companies implementation

/validate-phase P2
# Reviews Phase 2 resources completion
```

## Agent Workflow

Recommended to run this in **reviewer** agent for objective analysis, but can be used in any agent for status checks.

## Notes

- Provides detailed status for project management decisions
- Identifies specific blockers preventing phase completion
- Suggests concrete next steps for team coordination