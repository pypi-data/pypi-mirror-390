## Description
<!-- Describe your changes in detail -->

## Type of Change
<!-- Check the one that applies -->
- [ ] `feat`: New feature (minor version bump)
- [ ] `fix`: Bug fix (patch version bump)
- [ ] `docs`: Documentation only changes
- [ ] `style`: Code style changes (formatting, etc.)
- [ ] `refactor`: Code refactoring (no functional changes)
- [ ] `perf`: Performance improvements
- [ ] `test`: Adding or updating tests
- [ ] `build`: Changes to build system or dependencies
- [ ] `ci`: Changes to CI/CD configuration
- [ ] `chore`: Other changes that don't modify src or test files

## Breaking Changes
<!-- If this introduces breaking changes, check the box and describe them -->
- [ ] This is a breaking change (major version bump)

## Checklist
- [ ] PR title follows [Conventional Commits](https://www.conventionalcommits.org/) format (e.g., `feat: add new feature` or `fix: resolve bug`)
- [ ] Tests pass locally (`uv run pytest`)
- [ ] Code is formatted (`uv run black . && uv run isort .`)
- [ ] Type checking passes (`uv run mypy llmsbrieftxt/`)

---

### PR Title Format
Your PR title **must** follow this format:
```
<type>: <description>
```

**Examples:**
- `feat: add support for custom output formats`
- `fix: resolve crash when crawling large sites`
- `docs: update installation instructions`
- `feat!: redesign API (breaking change)`

**Note:** The PR title determines the version bump:
- `feat:` → minor version bump (1.0.0 → 1.1.0)
- `fix:` → patch version bump (1.0.0 → 1.0.1)
- `feat!:` or `BREAKING CHANGE:` → major version bump (1.0.0 → 2.0.0)
