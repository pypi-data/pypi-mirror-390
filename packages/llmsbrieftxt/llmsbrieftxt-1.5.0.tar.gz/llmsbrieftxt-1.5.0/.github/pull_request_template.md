## Summary

<!-- Provide a brief description of the changes in this PR -->

## Motivation

<!-- Why is this change needed? What problem does it solve? -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] `feat:` New feature (minor version bump)
- [ ] `fix:` Bug fix (patch version bump)
- [ ] `docs:` Documentation only changes
- [ ] `style:` Code style changes (formatting, whitespace, etc.)
- [ ] `refactor:` Code refactoring (no functional changes)
- [ ] `perf:` Performance improvements
- [ ] `test:` Adding or updating tests
- [ ] `chore:` Maintenance tasks, dependency updates
- [ ] `ci:` CI/CD pipeline changes
- [ ] `BREAKING CHANGE` (requires `!` in PR title or `BREAKING CHANGE:` in description)

## Testing

<!-- Describe how you tested these changes -->

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated (if applicable)
- [ ] All existing tests pass (`uv run pytest`)
- [ ] Manual testing performed (describe below)

**Manual Testing:**
<!-- Describe any manual testing you performed -->

## Code Quality Checklist

<!-- Confirm all checks pass before requesting review -->

- [ ] Code linted successfully (`uv run ruff check llmsbrieftxt/ tests/`)
- [ ] Code formatted successfully (`uv run ruff format llmsbrieftxt/ tests/`)
- [ ] Type checking passes (`uv run mypy llmsbrieftxt/`)
- [ ] All tests pass (`uv run pytest`)
- [ ] PR title follows [Conventional Commits](https://www.conventionalcommits.org/) format
- [ ] Commit messages follow Conventional Commits format

## Additional Context

<!-- Add any other context, screenshots, or information about the PR here -->

## Related Issues

<!-- Link any related issues using GitHub keywords: Fixes #123, Closes #456, Relates to #789 -->

---

<!--
PR Title Format:
- feat: add support for custom user agents
- fix: resolve URL normalization edge case
- docs: improve installation instructions
- feat!: change default output location (breaking change)
-->
