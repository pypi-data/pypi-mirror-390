"""Command-line interface for llmsbrieftxt."""

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

from llmsbrieftxt.constants import (
    DEFAULT_CONCURRENT_SUMMARIES,
    DEFAULT_OPENAI_MODEL,
    DOCS_DIR,
)
from llmsbrieftxt.main import generate_llms_txt


def parse_args(test_args: Optional[List[str]] = None) -> argparse.Namespace:
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
        help="Preview discovered URLs without processing them",
    )

    parser.add_argument(
        "--max-urls", type=int, help="Maximum number of URLs to discover and process"
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


def get_output_path(url: str, custom_output: Optional[str] = None) -> Path:
    """
    Get the output file path for a given URL.

    Args:
        url: The URL being processed
        custom_output: Optional custom output path

    Returns:
        Path object for the output file
    """
    if custom_output:
        return Path(custom_output)

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

        # Check for API key (unless just showing URLs)
        if not args.show_urls and not check_openai_api_key():
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

        # Print configuration
        print(f"Processing URL: {args.url}")
        print(f"Using model: {args.model}")
        print(f"Output: {output_path}")
        if args.max_urls:
            print(f"Max URLs: {args.max_urls}")

        # Warn about API costs for large jobs
        if not args.show_urls and not args.max_urls:
            print("")
            print(
                "Note: This will discover and process all documentation pages (depth=3)"
            )
            print("Tip: Use --show-urls first to preview scope, or --max-urls to limit")
            print("")

        # Run generation
        asyncio.run(
            generate_llms_txt(
                url=args.url,
                llm_name=args.model,
                max_concurrent_summaries=args.max_concurrent_summaries,
                output_path=str(output_path),
                show_urls=args.show_urls,
                max_urls=args.max_urls,
            )
        )

    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
