## Description

<!-- Provide a brief description of the changes in this PR -->

## Type of Change

Please select the type of change (check one):

- [ ] `feat`: New feature (minor version bump in semantic versioning)
- [ ] `fix`: Bug fix (patch version bump)
- [ ] `docs`: Documentation only changes (no version bump)
- [ ] `style`: Code style/formatting changes (no version bump)
- [ ] `refactor`: Code refactoring without changing functionality (no version bump)
- [ ] `test`: Adding or updating tests (no version bump)
- [ ] `chore`: Maintenance tasks, dependency updates (no version bump)
- [ ] `perf`: Performance improvements (patch version bump)

## Breaking Changes

- [ ] This PR introduces breaking changes (major version bump)

<!-- If checked, describe the breaking changes and migration path -->

## Checklist

- [ ] Code follows the project's style guidelines (`ruff check` passes)
- [ ] Code is properly formatted (`ruff format` passes)
- [ ] Type checking passes (`mypy src/` passes)
- [ ] Tests added/updated for new functionality
- [ ] All tests pass locally (`pytest -v`)
- [ ] Documentation updated (if applicable)
- [ ] Sync code regenerated (if async code changed: `python scripts/generate_sync.py`)
- [ ] Commit messages follow [Conventional Commits](https://www.conventionalcommits.org/) format

## Testing

<!-- Describe how you tested these changes -->

## Related Issues

<!-- Link related issues using #issue_number or "Closes #issue_number" -->

---

**Note on Conventional Commits**: This project uses conventional commit messages to prepare for automated releases with [Python Semantic Release](https://python-semantic-release.readthedocs.io/). Your commit messages should follow the format:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Examples:
- `feat(companies): add bulk update endpoint`
- `fix(auth): handle expired token gracefully`
- `docs(readme): update installation instructions`

This practice will enable automated version bumping and changelog generation in future releases.
