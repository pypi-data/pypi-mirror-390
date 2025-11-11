# GitHub Copilot Instructions for llmsbrieftxt

## Project Overview

This is `llmsbrieftxt`, a Python package that generates llms-brief.txt files by crawling documentation websites and using OpenAI to create structured descriptions. The CLI command is `llmtxt` (not `llmsbrieftxt`).

## Architecture and Code Patterns

### Async-First Design
All main functions use async/await patterns. Use `asyncio.gather()` for concurrent operations and semaphore control for rate limiting. The processing pipeline flows: URL Discovery → Content Extraction → LLM Summarization → File Generation.

### Module Organization
- **cli.py**: Simple CLI with positional URL argument (no subcommands)
- **main.py**: Orchestrates the async generation pipeline
- **crawler.py**: RobustDocCrawler for breadth-first URL discovery
- **doc_loader.py**: DocLoader wraps crawler with document loading
- **extractor.py**: HTML to markdown via trafilatura
- **summarizer.py**: OpenAI integration with retry logic (tenacity)
- **url_utils.py**: URLNormalizer for deduplication
- **url_filters.py**: Filter non-documentation URLs
- **schema.py**: Pydantic models (PageSummary)
- **constants.py**: Configuration constants

### Type Safety
Use Pydantic models for all structured data. The OpenAI integration uses structured output with the PageSummary model.

### Error Handling
Failed URL loads should be logged but not stop processing. LLM failures use exponential backoff retries via tenacity. Never let one failure break the entire pipeline.

## Development Practices

### Testing Requirements
Write tests before implementing features. Use pytest with these markers:
- `@pytest.mark.unit` for fast, isolated tests
- `@pytest.mark.requires_openai` for tests needing OPENAI_API_KEY
- `@pytest.mark.slow` for tests making external API calls

Tests go in:
- `tests/unit/` for fast tests with no external dependencies
- `tests/integration/` for tests requiring OPENAI_API_KEY

### Code Quality Tools
Before committing, always run:
1. Format: `uv run ruff format llmsbrieftxt/ tests/`
2. Lint: `uv run ruff check llmsbrieftxt/ tests/`
3. Type check: `uv run pyright llmsbrieftxt/`
4. Tests: `uv run pytest tests/unit/`

### Package Management
Use `uv` for all package operations:
- Install: `uv sync --group dev`
- Add dependency: `uv add package-name`
- Build: `uv build`

## Design Philosophy

### Unix Philosophy
This project follows "do one thing and do it well":
- Generate llms-brief.txt files only (no built-in search/list features)
- Compose with standard Unix tools (rg, grep, ls)
- Simple CLI: URL is a positional argument, no subcommands
- Plain text output for scriptability

### Simplicity Over Features
Avoid adding functionality that duplicates mature Unix tools. Every line of code must serve the core mission of generating llms-brief.txt files.

## Configuration Defaults

- **Crawl Depth**: 3 levels (hardcoded in crawler.py)
- **Output**: `~/.claude/docs/<domain>.txt` (override with `--output`)
- **Cache**: `.llmsbrieftxt_cache/` for intermediate results
- **OpenAI Model**: `gpt-5-mini` (override with `--model`)
- **Concurrency**: 10 concurrent LLM requests (prevents rate limiting)

## Commit Convention

Use conventional commits for automated versioning:
- `fix:` → patch bump (1.0.0 → 1.0.1)
- `feat:` → minor bump (1.0.0 → 1.1.0)
- `BREAKING CHANGE` or `feat!:`/`fix!:` → major bump (1.0.0 → 2.0.0)

Examples:
```bash
git commit -m "fix: handle empty sitemap gracefully"
git commit -m "feat: add --depth option for custom crawl depth"
git commit -m "feat!: change default output location"
```

## Non-Obvious Behaviors

1. URL Discovery discovers ALL pages up to depth 3, not just direct links
2. URLs like `/page`, `/page/`, and `/page#section` are deduplicated as the same URL
3. Summaries are automatically cached in `.llmsbrieftxt_cache/summaries.json`
4. Content extraction uses trafilatura to preserve HTML structure in markdown
5. File I/O is synchronous (uses standard `Path.write_text()` for simplicity)

## Known Limitations

1. Only supports OpenAI API (no other LLM providers)
2. Crawl depth is hardcoded to 3 in crawler.py
3. No CLI flag to force resume from cache (though cache exists)
4. No progress persistence if interrupted
5. Prompts and parsing assume English documentation

## Code Review Checklist

When reviewing code changes:
- Ensure async patterns are used correctly (no blocking I/O in async functions)
- Verify all functions have type hints
- Check that tests are included for new functionality
- Confirm error handling doesn't break the pipeline
- Validate that conventional commit format is used
- Ensure code follows Unix philosophy (simplicity, composability)
- Check that ruff and pyright pass without errors
- **IMPORTANT**: Always include specific file names and line numbers when providing review feedback (e.g., "main.py:165" or "line 182 in cli.py")
