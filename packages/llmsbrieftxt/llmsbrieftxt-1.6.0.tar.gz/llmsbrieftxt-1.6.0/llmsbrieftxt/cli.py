"""Command-line interface for llmsbrieftxt."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

from llmsbrieftxt.constants import (
    DEFAULT_CACHE_DIR,
    DEFAULT_CONCURRENT_SUMMARIES,
    DEFAULT_CRAWL_DEPTH,
    DEFAULT_OPENAI_MODEL,
    DOCS_DIR,
    ESTIMATED_TOKENS_PER_PAGE_INPUT,
    ESTIMATED_TOKENS_PER_PAGE_OUTPUT,
    OPENAI_PRICING,
)
from llmsbrieftxt.main import generate_llms_txt


def parse_args(test_args: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate llms-brief.txt files from documentation websites",
        epilog="Example: llmsbrieftxt https://docs.python.org/3/",
    )

    # Positional argument for URL
    parser.add_argument("url", help="URL of the documentation site to process")

    parser.add_argument(
        "--model",
        default=DEFAULT_OPENAI_MODEL,
        help=f"OpenAI model to use (default: {DEFAULT_OPENAI_MODEL})",
    )

    parser.add_argument(
        "--max-concurrent-summaries",
        type=int,
        default=DEFAULT_CONCURRENT_SUMMARIES,
        help=f"Maximum number of concurrent LLM requests (default: {DEFAULT_CONCURRENT_SUMMARIES})",
    )

    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help=f"Output file path (default: {DOCS_DIR}/<domain>.txt)",
    )

    parser.add_argument(
        "--show-urls",
        action="store_true",
        help="Preview discovered URLs with cost estimate (no processing or API calls)",
    )

    parser.add_argument(
        "--max-urls", type=int, help="Maximum number of URLs to discover and process"
    )

    parser.add_argument(
        "--depth",
        type=int,
        default=DEFAULT_CRAWL_DEPTH,
        help=f"Maximum crawl depth (default: {DEFAULT_CRAWL_DEPTH})",
    )

    parser.add_argument(
        "--cache-dir",
        type=str,
        default=DEFAULT_CACHE_DIR,
        help=f"Cache directory path (default: {DEFAULT_CACHE_DIR})",
    )

    parser.add_argument(
        "--use-cache-only",
        action="store_true",
        help="Use only cached summaries, skip API calls for new pages",
    )

    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Ignore cache and regenerate all summaries",
    )

    parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        help="Skip confirmation prompts (useful for automation)",
    )

    return parser.parse_args(test_args)


def validate_url(url: str) -> bool:
    """Validate that the URL is well-formed and uses http/https scheme."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False


def check_openai_api_key() -> bool:
    """Check if OPENAI_API_KEY is set in environment."""
    return bool(os.environ.get("OPENAI_API_KEY"))


def estimate_cost(num_pages: int, model: str) -> str:
    """
    Estimate the API cost for processing a given number of pages.

    Args:
        num_pages: Number of pages to process
        model: OpenAI model name

    Returns:
        Formatted cost estimate string
    """
    if model not in OPENAI_PRICING:
        return "Cost estimation not available for this model"

    input_price, output_price = OPENAI_PRICING[model]

    # Calculate total tokens
    total_input_tokens = num_pages * ESTIMATED_TOKENS_PER_PAGE_INPUT
    total_output_tokens = num_pages * ESTIMATED_TOKENS_PER_PAGE_OUTPUT

    # Calculate cost (prices are per 1M tokens)
    input_cost = (total_input_tokens / 1_000_000) * input_price
    output_cost = (total_output_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost

    if total_cost < 0.01:
        return f"~${total_cost:.4f}"
    elif total_cost < 1.00:
        return f"~${total_cost:.3f}"
    else:
        return f"~${total_cost:.2f}"


def get_output_path(url: str, custom_output: str | None = None) -> Path:
    """
    Get the output file path for a given URL.

    Args:
        url: The URL being processed
        custom_output: Optional custom output path

    Returns:
        Path object for the output file
    """
    if custom_output:
        # Expand environment variables and user home directory
        expanded = os.path.expandvars(custom_output)
        return Path(expanded).expanduser()

    # Extract domain from URL
    parsed = urlparse(url)
    domain = parsed.netloc or parsed.path.split("/")[0]

    # Remove www. prefix if present
    if domain.startswith("www."):
        domain = domain[4:]

    # Ensure ~/.claude/docs/ exists
    docs_dir = Path(DOCS_DIR).expanduser()
    docs_dir.mkdir(parents=True, exist_ok=True)

    return docs_dir / f"{domain}.txt"


def main() -> None:
    """Main entry point for the CLI."""
    args = parse_args()

    try:
        # Validate URL
        if not validate_url(args.url):
            print("Error: Invalid URL", file=sys.stderr)
            print(
                f"Please provide a valid HTTP or HTTPS URL. Got: {args.url}",
                file=sys.stderr,
            )
            print("Example: https://docs.python.org/3/", file=sys.stderr)
            sys.exit(1)

        # Validate depth parameter
        if args.depth < 1:
            print("Error: --depth must be at least 1", file=sys.stderr)
            sys.exit(1)

        # Check for conflicting cache flags
        if args.use_cache_only and args.force_refresh:
            print(
                "Error: Cannot use --use-cache-only and --force-refresh together",
                file=sys.stderr,
            )
            sys.exit(1)

        # Check for API key (unless just showing URLs or using cache only)
        if (
            not args.show_urls
            and not args.use_cache_only
            and not check_openai_api_key()
        ):
            print("Error: OPENAI_API_KEY not found", file=sys.stderr)
            print("Please set your OpenAI API key:", file=sys.stderr)
            print("  export OPENAI_API_KEY='sk-your-api-key-here'", file=sys.stderr)
            print("", file=sys.stderr)
            print(
                "Get your API key from: https://platform.openai.com/api-keys",
                file=sys.stderr,
            )
            sys.exit(1)

        # Determine output path
        output_path = get_output_path(args.url, args.output)

        # Expand cache directory path
        cache_dir = Path(os.path.expandvars(args.cache_dir)).expanduser()

        # Print configuration
        print(f"Processing URL: {args.url}")
        if not args.show_urls:
            print(f"Using model: {args.model}")
        print(f"Crawl depth: {args.depth}")
        print(f"Output: {output_path}")
        if args.max_urls:
            print(f"Max URLs: {args.max_urls}")
        if args.use_cache_only:
            print("Mode: Cache-only (no API calls)")
        elif args.force_refresh:
            print("Mode: Force refresh (ignoring cache)")

        # Run generation
        result = asyncio.run(
            generate_llms_txt(
                url=args.url,
                llm_name=args.model,
                max_concurrent_summaries=args.max_concurrent_summaries,
                output_path=str(output_path),
                show_urls=args.show_urls,
                max_urls=args.max_urls,
                max_depth=args.depth,
                cache_dir=str(cache_dir),
                use_cache_only=args.use_cache_only,
                force_refresh=args.force_refresh,
                skip_confirmation=args.yes,
            )
        )

        # Show cost estimate and failed URLs if available
        if args.show_urls and result:
            num_urls_value = result.get("num_urls", 0)
            # Type guard to ensure we have an int
            if isinstance(num_urls_value, int):
                print(
                    f"\nEstimated cost for {num_urls_value} pages: {estimate_cost(num_urls_value, args.model)}"
                )
            print("Note: Actual cost may vary based on page content size and caching")

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
