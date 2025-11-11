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
- **OpenAI Integration**: `Summarizer` class uses OpenAI API with structured output (supports any OpenAI-compatible endpoint via `OPENAI_BASE_URL` env var)
- **Structured Output**: All LLM responses use Pydantic models (`PageSummary`)

### URL Normalization Strategy
The `URLNormalizer` class (url_utils.py) implements deduplication:
- Removes trailing slashes, fragments, and default ports
- Normalizes scheme and domain to lowercase
- Handles subdomain relationships
- Preserves query parameters (may affect documentation content)

### Error Recovery and Success Determination
- Failed URL loads are logged but don't stop processing
- LLM failures trigger exponential backoff retries (via tenacity)
- Summaries are cached to `.llmsbrieftxt_cache/` directory automatically
- Success is determined by:
  - **Normal mode**: At least one new summary generated if new pages exist; exit 0 if any summaries generated (new or cached), exit 1 only if no summaries generated
  - **Cache-only mode**: At least one cached summary found; exit 0 if summaries exist, exit 1 if cache empty
  - **Partial failures**: Exit 0 if some summaries generated (shows WARNING), exit 1 only if all API calls failed
- Failed retries return `None` instead of fallback placeholders

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

### E2E Testing with Ollama
For testing without OpenAI API costs, use Ollama as a local LLM provider:

```bash
# Install Ollama (one-time setup)
curl -fsSL https://ollama.com/install.sh | sh
# Or download from: https://ollama.com/download

# Start Ollama service
ollama serve &

# Pull a lightweight model (tinyllama: 637MB, phi3:mini: 2.3GB)
ollama pull tinyllama

# Run E2E tests with Ollama
export OPENAI_BASE_URL="http://localhost:11434/v1"
export OPENAI_API_KEY="ollama-dummy-key"
uv run pytest tests/integration/test_ollama_e2e.py -v

# Or test the CLI directly with Ollama
llmtxt https://example.com --model tinyllama --max-urls 5 --depth 1
```

**Why Ollama for Testing:**
- ✅ Zero API costs - runs completely local
- ✅ OpenAI-compatible endpoint at `http://localhost:11434/v1`
- ✅ Fast lightweight models (tinyllama, phi3:mini, gemma2:2b)
- ✅ Cached in GitHub Actions (~/.ollama directory)
- ✅ Same code path as production OpenAI usage

**Model Recommendations:**
- `tinyllama` (637MB) - Fastest, good for CI/CD
- `phi3:mini` (2.3GB) - Better quality, still fast
- `gemma2:2b` (1.6GB) - Balanced option

### Code Quality
```bash
# Lint code (run before committing)
uv run ruff check llmsbrieftxt/ tests/

# Format code (in-place)
uv run ruff format llmsbrieftxt/ tests/

# Check formatting without modifying
uv run ruff format --check llmsbrieftxt/ tests/

# Type checking
uv run pyright llmsbrieftxt/
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
llmtxt https://example.com --show-urls  # Preview URLs with cost estimate
llmtxt https://example.com --max-urls 50
llmtxt https://example.com --depth 2  # Control crawl depth (default: 3)
llmtxt https://example.com --use-cache-only  # No API calls, cache only
llmtxt https://example.com --force-refresh  # Ignore cache, regenerate all
llmtxt https://example.com --cache-dir /tmp/cache  # Custom cache location
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
- **Crawl Depth**: 3 levels from starting URL (configurable with `--depth`)
- **Output Location**: `~/.claude/docs/<domain>.txt` (can override with `--output`)
- **Cache Directory**: `.llmsbrieftxt_cache/` for intermediate results (can override with `--cache-dir`)

### New Features (as of latest update)
- **Cost Estimation**: `--show-urls` now displays estimated API cost before processing
- **Cache Control**: `--use-cache-only` and `--force-refresh` flags for cache management
- **Failed URL Tracking**: Failed URLs are written to `failed_urls.txt` next to output file
- **Depth Configuration**: Crawl depth is now configurable via `--depth` flag

### Default Model
- **OpenAI Model**: `gpt-5-mini` (defined in constants.py, can override with `--model`)

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
- **cli.py** - Simple CLI with positional URL argument
- **main.py** - Orchestrates the generation pipeline
- **crawler.py** - RobustDocCrawler handles URL discovery
- **doc_loader.py** - DocLoader wraps crawler with document loading
- **extractor.py** - HTML to markdown conversion via trafilatura
- **summarizer.py** - OpenAI integration with retry logic

### Utility Modules
- **url_utils.py** - URLNormalizer for deduplication
- **url_filters.py** - Filter non-documentation URLs
- **schema.py** - Pydantic models (PageSummary)
- **constants.py** - Configuration constants

### Removed in v1.0.0
- **search.py** - Removed (use ripgrep/grep instead)
- **docs_manager.py** - Removed (inlined into cli.py)
- **styling.py** - Removed (plain text output is more scriptable)

## Non-Obvious Behaviors

1. **URL Discovery**: Discovers ALL pages up to configured depth (default 3), not just pages linked from your starting URL
2. **Duplicate Handling**: `/page`, `/page/`, and `/page#section` are treated as the same URL
3. **Concurrency Limit**: Default 10 concurrent LLM requests prevents rate limiting
4. **Automatic Caching**: Summaries cached in `.llmsbrieftxt_cache/summaries.json` and reused automatically
5. **Content Extraction**: Uses `trafilatura` for HTML→markdown, preserving structure
6. **Sync File I/O**: Uses standard `Path.write_text()` instead of async file I/O (simpler, sufficient)
7. **Cost Estimation**: `--show-urls` shows both discovered URLs count AND estimated API cost
8. **Cache-First**: When using cache, shows "Cached: X | New: Y" breakdown before processing
9. **Failed URL Reporting**: Failed URLs saved to `failed_urls.txt` in same directory as output
10. **Environment Variables**: `--output` and `--cache-dir` support `$HOME` and other env var expansion

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
4. Format code: `uv run ruff format llmsbrieftxt/ tests/`
5. Lint code: `uv run ruff check llmsbrieftxt/ tests/`
6. Check types: `uv run pyright llmsbrieftxt/`

### Debugging Issues
1. Check logs - logger is configured in most modules
2. Use `--show-urls` to preview URL discovery and cost estimate
3. Check cache: `.llmsbrieftxt_cache/summaries.json` (or custom `--cache-dir`)
4. Check failed URLs: `failed_urls.txt` in output directory
5. Test with limited scope: `--max-urls 10 --depth 1` for quick testing
6. Use `--use-cache-only` to test output generation without API calls
7. Run with verbose pytest: `uv run pytest -vv -s`

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

## Versioning and Releases

### Conventional Commits
This project uses **conventional commits** for automated versioning:

- `fix:` → patch bump (1.0.0 → 1.0.1)
- `feat:` → minor bump (1.0.0 → 1.1.0)
- `BREAKING CHANGE` or `feat!:`/`fix!:` → major bump (1.0.0 → 2.0.0)

Examples:
```bash
git commit -m "fix: handle empty sitemap gracefully"
git commit -m "feat: add --depth option for custom crawl depth"
git commit -m "feat!: change default output location to ~/.claude/docs"
```

### Automated Release Process
Releases are **fully automated** via GitHub Actions:

1. **Push to main**: Commit to main branch with conventional commit message
2. **Auto-bump**: GitHub Actions runs `scripts/bump_version.py` to analyze commits and create a version tag
3. **Auto-build**: If version bumped, builds package with injected static version
4. **Auto-publish**: Publishes to PyPI and creates GitHub release with notes

**No manual steps required** - the CI/CD pipeline handles everything from commit analysis to PyPI publication.

### Manual Build (for testing)
```bash
# Run full test suite
uv run pytest

# Build locally
uv build
```

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
2. **No Progress Persistence**: If interrupted, must restart (though cache helps and is used automatically on restart)
3. **English-Centric**: Prompts and parsing assume English documentation
4. **No Incremental Timestamp Checking**: Force refresh or cache-only mode, but no "only update changed pages" mode

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
