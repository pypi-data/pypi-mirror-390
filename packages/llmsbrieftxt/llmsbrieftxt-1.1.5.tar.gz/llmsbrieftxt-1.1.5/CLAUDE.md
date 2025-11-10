# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

llmsbrieftxt is a Python package that automatically generates [llms-brief.txt](https://llmstxt.org/) files by crawling websites and using OpenAI to create structured descriptions of each page.

**Package Name**: `llmsbrieftxt`
**CLI Command**: `llmtxt`
**Main Entry**: `from llmsbrieftxt.main import generate_llms_txt`
**Version**: 1.0.0 (production-ready, focused generator)

## Architecture

### Async Processing Pipeline
The system follows a strict async pipeline pattern across multiple modules:

```
URL Discovery (doc_loader.py) → Content Extraction (extractor.py) → LLM Summarization (summarizer.py) → File Generation (main.py)
```

- **Breadth-First Discovery**: `DocLoader` uses `RobustDocCrawler` to discover URLs up to depth 3
- **URL Normalization**: `URLNormalizer` prevents duplicates through sophisticated normalization
- **Concurrent Processing**: Uses `asyncio.gather()` with semaphore control (`max_concurrent_summaries`)
- **OpenAI Integration**: `Summarizer` class uses OpenAI API with structured output
- **Structured Output**: All LLM responses use Pydantic models (`PageSummary`)

### URL Normalization Strategy
The `URLNormalizer` class (url_utils.py) implements deduplication:
- Removes trailing slashes, fragments, and default ports
- Normalizes scheme and domain to lowercase
- Handles subdomain relationships
- Preserves query parameters (may affect documentation content)

### Error Recovery
- Failed URL loads are logged but don't stop processing
- LLM failures trigger exponential backoff retries (via tenacity)
- Summaries are cached to `.llmsbrieftxt_cache/` directory automatically

## Development Commands

### Running Tests
```bash
# Run all tests
uv run pytest

# Run unit tests only (fast)
uv run pytest tests/unit/

# Run integration tests (requires OPENAI_API_KEY)
uv run pytest tests/integration/

# Run with verbose output
uv run pytest -v

# Run specific test
uv run pytest tests/unit/test_cli.py::test_function_name
```

### Code Quality
```bash
# Format and lint (run before committing)
uv run black llmsbrieftxt/ tests/
uv run isort llmsbrieftxt/ tests/
uv run ruff llmsbrieftxt/ tests/

# Type checking
uv run mypy llmsbrieftxt/
```

### Package Management
```bash
# Install package with dev dependencies
uv sync --group dev

# Add new dependency
uv add package-name

# Build distribution
uv build
```

## CLI Usage

The CLI is a focused single-purpose tool for generating llms-brief.txt files:

```bash
# Basic usage (requires OPENAI_API_KEY env var)
llmtxt https://docs.python.org/3/

# With options
llmtxt https://example.com --model gpt-4o
llmtxt https://example.com --show-urls
llmtxt https://example.com --max-urls 50
llmtxt https://example.com --output custom-path.txt
```

**Search and List**: Use standard Unix tools instead of built-in commands:
```bash
# Search (use ripgrep or grep)
rg "async functions" ~/.claude/docs/
grep -r "error handling" ~/.claude/docs/

# List (use ls)
ls -lh ~/.claude/docs/
```

## Critical Configuration

### Default Behavior
These are the production defaults:
- **Crawl Depth**: 3 levels from starting URL (hardcoded in crawler.py)
- **Output Location**: `~/.claude/docs/<domain>.txt` (can override with `--output`)
- **Cache Directory**: `.llmsbrieftxt_cache/` for intermediate results

### Default Model
- **OpenAI Model**: `o4-mini` (defined in constants.py, can override with `--model`)

### Environment Variables
- **OPENAI_API_KEY**: Required for all generation operations

## Code Patterns

### Async Context
All main functions are async. When calling from sync code:
```python
import asyncio
asyncio.run(generate_llms_txt(...))
```

### Test Organization
```
tests/
├── unit/           # Fast, isolated tests (no external deps)
├── integration/    # Tests requiring OPENAI_API_KEY
└── fixtures/       # Shared test data
```

Test markers:
- `@pytest.mark.unit` - Pure unit tests
- `@pytest.mark.requires_openai` - Needs OPENAI_API_KEY
- `@pytest.mark.slow` - Makes external API calls

## Module Reference

### Core Modules (Production v1.0.0)
- **cli.py** (~170 lines) - Simple CLI with positional URL argument
- **main.py** (~150 lines) - Orchestrates the generation pipeline
- **crawler.py** (441 lines) - RobustDocCrawler handles URL discovery
- **doc_loader.py** (154 lines) - DocLoader wraps crawler with document loading
- **extractor.py** (78 lines) - HTML to markdown conversion via trafilatura
- **summarizer.py** (296 lines) - OpenAI integration with retry logic

### Utility Modules
- **url_utils.py** (135 lines) - URLNormalizer for deduplication
- **url_filters.py** (153 lines) - Filter non-documentation URLs
- **schema.py** (42 lines) - Pydantic models (PageSummary)
- **constants.py** (36 lines) - Configuration constants

### Removed in v1.0.0
- **search.py** - Removed (use ripgrep/grep instead)
- **docs_manager.py** - Removed (inlined into cli.py)
- **styling.py** - Removed (plain text output is more scriptable)

## Non-Obvious Behaviors

1. **URL Discovery**: Discovers ALL pages up to depth 3, not just pages linked from your starting URL
2. **Duplicate Handling**: `/page`, `/page/`, and `/page#section` are treated as the same URL
3. **Concurrency Limit**: Default 10 concurrent LLM requests prevents rate limiting
4. **Automatic Caching**: Summaries cached in `.llmsbrieftxt_cache/summaries.json` and reused automatically
5. **Content Extraction**: Uses `trafilatura` for HTML→markdown, preserving structure
6. **Sync File I/O**: Uses standard `Path.write_text()` instead of async file I/O (simpler, sufficient)

## Using llms-brief.txt Files

When working with codebases that use documented libraries, llms-brief.txt files serve as structured navigation maps. Each entry contains:
```
Title: [Page Name](URL)
Keywords: searchable, terms, functions, concepts
Summary: One-line description of page content

```

### When to Reference llms-brief.txt
- **Before implementing**: Search for examples/guides for unfamiliar library functions
- **During debugging**: Find error handling docs and troubleshooting guides
- **Code review**: Verify correct API usage against official documentation
- **Refactoring**: Locate migration guides and best practices

### How to Search llms-brief.txt

Use ripgrep (recommended) or grep:
```bash
# Search all docs
rg -i "async" ~/.claude/docs/

# Search specific doc
rg "useState" ~/.claude/docs/react.dev.txt

# Show context around matches
rg -C 2 "error handling" ~/.claude/docs/

# Count matches
rg -c "api" ~/.claude/docs/
```

Or use grep:
```bash
# Search all docs
grep -r "async functions" ~/.claude/docs/

# Case-insensitive
grep -ri "error" ~/.claude/docs/

# With line numbers
grep -rn "hooks" ~/.claude/docs/
```

### Search Strategies
- **Keywords** field contains function names, concepts, and technical terms
- **Summary** field helps prioritize which docs to read first
- **Title** field shows the exact page name and URL
- Search case-insensitively when exploring broad concepts
- Search multiple related terms together for comprehensive results

## Common Development Tasks

### Adding a New Feature
1. Write tests first (tests/unit/)
2. Implement feature
3. Run tests: `uv run pytest tests/unit/`
4. Format code: `uv run black . && uv run isort .`
5. Check types: `uv run mypy llmsbrieftxt/`

### Debugging Issues
1. Check logs - logger is configured in most modules
2. Use `--show-urls` to preview URL discovery
3. Check cache: `.llmsbrieftxt_cache/summaries.json`
4. Run with verbose pytest: `uv run pytest -vv -s`

### Modifying URL Discovery Logic
- Edit `crawler.py` for crawling behavior
- Edit `url_filters.py` for filtering logic
- Edit `url_utils.py` for normalization
- Run tests: `uv run pytest tests/unit/test_doc_loader.py`

### Modifying Summarization
- Edit `summarizer.py` for OpenAI integration
- Edit `constants.py` for DEFAULT_SUMMARY_PROMPT
- Edit `schema.py` for response structure
- Run tests: `uv run pytest tests/unit/test_summarizer.py`

## Production Deployment

The package is designed for:
1. **PyPI distribution**: `uv build` creates wheel and sdist
2. **Direct installation**: `pip install llmsbrieftxt`
3. **CLI usage**: Entry point defined in pyproject.toml

### Release Process
1. Update version in pyproject.toml
2. Run full test suite: `uv run pytest`
3. Build: `uv build`
4. Publish: Upload to PyPI

## Design Philosophy (v1.0.0)

**Unix Philosophy**: Do one thing and do it well
- **Focus**: Generate llms-brief.txt files (one job only)
- **Compose**: Let users use rg/grep for search, ls for listing
- **Simplicity**: No subcommands, URL is positional argument
- **Scriptable**: Plain text output, proper exit codes

**Production-Ready**:
- 35% less code than v0.x (removed 885 lines)
- No feature duplication with standard tools
- Clear, focused value proposition
- Every line serves the core mission

## Known Limitations

1. **OpenAI Only**: Currently only supports OpenAI API (no other LLM providers)
2. **Depth Hardcoded**: Crawl depth is hardcoded to 3 in crawler.py
3. **No Resume Flag**: Cache exists but no CLI flag to force resume from cache
4. **No Progress Persistence**: If interrupted, must restart (though cache helps)
5. **English-Centric**: Prompts and parsing assume English documentation

## Migration from v0.x

Version 1.0.0 removes search and list functionality:

```bash
# Before (v0.x)
llmsbrieftxt generate https://docs.python.org/3/
llmsbrieftxt search "async"
llmsbrieftxt list

# After (v1.0.0)
llmtxt https://docs.python.org/3/
rg "async" ~/.claude/docs/
ls ~/.claude/docs/
```

**Why**: Focus on core value. Search/list are better served by mature Unix tools.
