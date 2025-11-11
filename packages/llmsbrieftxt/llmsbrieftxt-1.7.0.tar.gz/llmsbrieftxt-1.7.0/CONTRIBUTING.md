# Contributing to llmsbrieftxt

Thank you for your interest in contributing to llmsbrieftxt! This document provides guidelines and instructions for contributing.

## Code of Conduct

Be respectful, constructive, and professional in all interactions.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) for package management
- OpenAI API key (for integration tests)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/stevennevins/llmsbrief.git
cd llmsbrief

# Install dependencies
uv sync --group dev

# Set up your OpenAI API key for integration tests
export OPENAI_API_KEY="sk-your-api-key-here"
```

## Development Workflow

### 1. Create a Branch

```bash
# Create a feature branch
git checkout -b feat/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### 2. Make Your Changes

Follow the project's architecture and design philosophy:

- **Unix Philosophy**: Do one thing well
- **Simplicity**: Keep code focused and maintainable
- **Async-first**: Use async/await for I/O operations
- **Type Safety**: Include type hints for all functions

### 3. Write Tests

All new features and bug fixes should include tests:

```bash
# Write unit tests in tests/unit/
# Write integration tests in tests/integration/ (if needed)

# Run unit tests (fast, no API calls)
uv run pytest tests/unit/

# Run all tests
uv run pytest
```

Test markers:
- `@pytest.mark.unit` - Pure unit tests (no external dependencies)
- `@pytest.mark.requires_openai` - Requires OPENAI_API_KEY
- `@pytest.mark.slow` - Makes external API calls

### 4. Ensure Code Quality

Before committing, run all quality checks:

```bash
# Lint code
uv run ruff check llmsbrieftxt/ tests/

# Format code
uv run ruff format llmsbrieftxt/ tests/

# Type checking
uv run mypy llmsbrieftxt/

# Run tests
uv run pytest
```

### 5. Commit Your Changes

We use [Conventional Commits](https://www.conventionalcommits.org/) for automated versioning:

**Commit Types:**
- `feat:` - New feature (minor version bump)
- `fix:` - Bug fix (patch version bump)
- `docs:` - Documentation only changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks
- `ci:` - CI/CD changes

**Breaking Changes:**
- Add `!` after type for breaking changes: `feat!:`, `fix!:`
- Or include `BREAKING CHANGE:` in commit body

**Examples:**
```bash
git commit -m "feat: add --depth option for custom crawl depth"
git commit -m "fix: handle empty sitemap gracefully"
git commit -m "docs: update README installation instructions"
git commit -m "feat!: change default output location to ~/.claude/docs"
```

### 6. Push and Create Pull Request

```bash
# Push your branch
git push origin feat/your-feature-name

# Create a pull request on GitHub
# Use the PR template and fill in all sections
```

## Pull Request Guidelines

### PR Title Format

Follow conventional commit format:
```
<type>: <description>

Examples:
feat: add support for custom user agents
fix: resolve URL normalization edge case
docs: improve installation instructions
```

### PR Description

Use the PR template to include:
- **Summary**: What changes does this PR introduce?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Checklist**: Confirm all quality checks passed

### Review Process

1. Automated checks must pass (CI, linting, type checking, tests)
2. At least one maintainer approval required
3. PR title must follow conventional commit format
4. All conversations must be resolved

## Project Structure

```
llmsbrieftxt/
├── llmsbrieftxt/          # Main package
│   ├── cli.py             # CLI entry point
│   ├── main.py            # Orchestration
│   ├── crawler.py         # URL discovery
│   ├── doc_loader.py      # Document loading
│   ├── extractor.py       # HTML to markdown
│   ├── summarizer.py      # OpenAI integration
│   ├── url_utils.py       # URL normalization
│   ├── url_filters.py     # URL filtering
│   ├── schema.py          # Pydantic models
│   └── constants.py       # Configuration
├── tests/
│   ├── unit/              # Fast unit tests
│   ├── integration/       # Tests requiring API
│   └── fixtures/          # Test data
└── scripts/               # Automation scripts
```

## Key Design Principles

### 1. Async Processing Pipeline
```
URL Discovery → Content Extraction → LLM Summarization → File Generation
```

All I/O operations use async/await.

### 2. URL Normalization
Sophisticated deduplication prevents processing the same page twice:
- Removes trailing slashes, fragments, default ports
- Normalizes scheme and domain case
- Handles subdomain relationships

### 3. Error Recovery
- Failed URL loads are logged but don't stop processing
- LLM failures trigger exponential backoff retries
- Automatic caching prevents redundant API calls

### 4. Testing Strategy
- Unit tests mock all external dependencies
- Integration tests use real OpenAI API (marked accordingly)
- Fast unit tests encourage TDD

## Common Tasks

### Running Specific Tests

```bash
# Run a specific test file
uv run pytest tests/unit/test_cli.py

# Run a specific test function
uv run pytest tests/unit/test_cli.py::test_function_name

# Run with verbose output
uv run pytest -vv -s
```

### Debugging

```bash
# Use --show-urls to preview URL discovery
uv run llmtxt https://example.com --show-urls

# Check cache contents
cat .llmsbrieftxt_cache/summaries.json

# Run pytest with verbose output
uv run pytest -vv -s
```

### Modifying Core Components

**URL Discovery Logic:**
- Edit `crawler.py` for crawling behavior
- Edit `url_filters.py` for filtering logic
- Edit `url_utils.py` for normalization
- Test: `uv run pytest tests/unit/test_doc_loader.py`

**Summarization:**
- Edit `summarizer.py` for OpenAI integration
- Edit `constants.py` for DEFAULT_SUMMARY_PROMPT
- Edit `schema.py` for response structure
- Test: `uv run pytest tests/unit/test_summarizer.py`

## Release Process

Releases are fully automated via GitHub Actions:

1. **Push to main**: Commit with conventional commit message
2. **Auto-bump**: CI analyzes commits and creates version tag
3. **Auto-build**: Package built with static version
4. **Auto-publish**: Published to PyPI and GitHub releases

**No manual version bumping required!** The CI/CD handles everything.

## Questions or Issues?

- **Bug reports**: [Open an issue](https://github.com/stevennevins/llmsbrief/issues)
- **Feature requests**: [Open an issue](https://github.com/stevennevins/llmsbrief/issues) with detailed use case
- **Questions**: [Open a discussion](https://github.com/stevennevins/llmsbrief/discussions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
