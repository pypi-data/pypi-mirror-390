"""Main generation pipeline for llmsbrieftxt."""

import json
import logging
import re
from pathlib import Path

from llmsbrieftxt.constants import (
    ESTIMATED_TOKENS_PER_PAGE_INPUT,
    ESTIMATED_TOKENS_PER_PAGE_OUTPUT,
    OPENAI_PRICING,
)
from llmsbrieftxt.doc_loader import DocLoader
from llmsbrieftxt.extractor import default_extractor
from llmsbrieftxt.summarizer import Summarizer

logger = logging.getLogger(__name__)


def calculate_actual_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Calculate actual API cost from token usage.

    Args:
        input_tokens: Number of input tokens used
        output_tokens: Number of output tokens generated
        model: OpenAI model name

    Returns:
        Total cost in dollars
    """
    if model not in OPENAI_PRICING:
        return 0.0

    input_price, output_price = OPENAI_PRICING[model]
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    return input_cost + output_cost


def format_cost(cost: float) -> str:
    """Format cost as a dollar string."""
    if cost < 0.01:
        return f"${cost:.4f}"
    elif cost < 1.00:
        return f"${cost:.3f}"
    else:
        return f"${cost:.2f}"


def get_cache_stats(cache_file: Path, model: str) -> dict[str, int | float | str]:
    """
    Get cache statistics including size and estimated savings.

    Args:
        cache_file: Path to cache file
        model: OpenAI model name for cost calculation

    Returns:
        Dictionary with cache statistics
    """
    if not cache_file.exists():
        return {
            "num_entries": 0,
            "size_mb": 0.0,
            "estimated_savings": "$0.00",
        }

    try:
        # Get file size
        size_bytes = cache_file.stat().st_size
        size_mb = size_bytes / (1024 * 1024)

        # Count entries
        with open(cache_file) as f:
            cache_data = json.load(f)
            num_entries = len(cache_data)

        # Estimate savings (num_entries * avg cost per page)
        avg_input_tokens = ESTIMATED_TOKENS_PER_PAGE_INPUT
        avg_output_tokens = ESTIMATED_TOKENS_PER_PAGE_OUTPUT
        savings_per_page = calculate_actual_cost(
            avg_input_tokens, avg_output_tokens, model
        )
        total_savings = num_entries * savings_per_page

        return {
            "num_entries": num_entries,
            "size_mb": size_mb,
            "estimated_savings": format_cost(total_savings),
        }
    except Exception as e:
        logger.warning(f"Could not read cache stats from {cache_file}: {str(e)}")
        return {
            "num_entries": 0,
            "size_mb": 0.0,
            "estimated_savings": "$0.00",
        }


def extract_url_from_summary(summary: str) -> str | None:
    """
    Extract URL from a summary in the format: Title: [title](URL).

    Args:
        summary: Formatted summary string

    Returns:
        Extracted URL or None if not found
    """
    # Match markdown link format: [text](url)
    match = re.search(r"\[([^\]]+)\]\(([^)]+)\)", summary)
    if match:
        return match.group(2)
    return None


def ensure_directory_exists(file_path: str) -> None:
    """Ensure the parent directory of the given file path exists.

    Args:
        file_path: Path to the file whose parent directory should be created

    Raises:
        RuntimeError: If directory creation fails due to permissions or other issues
    """
    dir_path = Path(file_path).parent
    if dir_path == Path("."):
        return  # Current directory, no need to create

    try:
        dir_path.mkdir(parents=True, exist_ok=True)
        if not dir_path.exists():
            print(f"Created directory: {dir_path}")
    except OSError as e:
        raise RuntimeError(f"Failed to create directory {dir_path}: {e}") from e


async def generate_llms_txt(
    url: str,
    llm_name: str = "o4-mini",
    max_concurrent_summaries: int = 10,
    output_path: str = "llms.txt",
    show_urls: bool = False,
    max_urls: int | None = None,
    max_depth: int = 3,
    cache_dir: str = ".llmsbrieftxt_cache",
    use_cache_only: bool = False,
    force_refresh: bool = False,
    skip_confirmation: bool = False,
) -> dict[str, int | list[str] | bool] | None:
    """
    Generate llms-brief.txt file from a documentation website.

    Args:
        url: URL of the documentation site to crawl
        llm_name: OpenAI model to use for summarization
        max_concurrent_summaries: Maximum concurrent LLM requests
        output_path: Path to write the output file
        show_urls: If True, only show discovered URLs without processing
        max_urls: Maximum number of URLs to discover/process
        max_depth: Maximum crawl depth for URL discovery
        cache_dir: Directory to store cached summaries
        use_cache_only: If True, only use cached summaries (no API calls)
        force_refresh: If True, ignore cache and regenerate all summaries
        skip_confirmation: If True, skip confirmation prompt for high costs

    Returns:
        Dictionary with metadata including 'success' boolean (for show_urls mode returns dict, otherwise None on success)
    """
    urls_processed = 0
    summaries_generated = 0
    new_summaries_generated = 0  # Track new (non-cached) summaries
    failed_urls: set[str] = set()  # Use set to avoid duplicates

    # Set up cache directory
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_file = cache_path / "summaries.json"

    # Load existing summaries from cache if available (unless force refresh)
    existing_summaries: dict[str, str] = {}
    if not force_refresh and cache_file.exists():
        try:
            with open(cache_file) as f:
                existing_summaries = json.load(f)
                # Show cache stats
                cache_stats = get_cache_stats(cache_file, llm_name)
                print(
                    f"\nCache: {cache_stats['num_entries']} entries ({cache_stats['size_mb']:.1f}MB on disk)"
                )
                print(
                    f"Approximate value from cache: ~{cache_stats['estimated_savings']} in saved API calls"
                )
        except Exception as e:
            print(f"Warning: Could not load cache: {str(e)}")
    elif force_refresh and cache_file.exists():
        print("\nForce refresh enabled - ignoring existing cache")

    extractor = default_extractor
    output_file = output_path

    # If show_urls is True, just show discovered URLs and exit
    if show_urls:
        print("Discovering documentation URLs...")
        doc_loader = DocLoader(max_urls=max_urls, max_depth=max_depth)
        _, discovered_urls = await doc_loader.load_docs(
            url, extractor=extractor, show_urls=True
        )
        print("\nDiscovered URLs:")
        for discovered_url in discovered_urls:
            print(f"  - {discovered_url}")
        print(f"\nTotal: {len(discovered_urls)} unique URLs")

        # Calculate how many would be cached vs new
        num_cached = sum(1 for u in discovered_urls if u in existing_summaries)
        num_new = len(discovered_urls) - num_cached
        if existing_summaries:
            print(f"Cached: {num_cached} | New: {num_new}")

        return {"num_urls": len(discovered_urls), "failed_urls": [], "success": True}

    # Load and process documents
    doc_loader = DocLoader(max_urls=max_urls, max_depth=max_depth)
    docs, discovered_urls = await doc_loader.load_docs(url, extractor=extractor)
    urls_processed = len(docs)

    # Track which URLs failed to load
    loaded_urls = {doc.metadata.get("source") for doc in docs}
    failed_urls.update(u for u in discovered_urls if u not in loaded_urls)

    # Show cost estimate and get confirmation (unless using cache-only or skip_confirmation)
    if not use_cache_only and not skip_confirmation:
        num_cached = sum(1 for u in discovered_urls if u in existing_summaries)
        num_new = len(discovered_urls) - num_cached
        estimated_cost_new = calculate_actual_cost(
            num_new * ESTIMATED_TOKENS_PER_PAGE_INPUT,
            num_new * ESTIMATED_TOKENS_PER_PAGE_OUTPUT,
            llm_name,
        )

        print(f"\nThis run: {num_new} new pages, {num_cached} cached")
        if num_cached > 0:
            saved_cost = calculate_actual_cost(
                num_cached * ESTIMATED_TOKENS_PER_PAGE_INPUT,
                num_cached * ESTIMATED_TOKENS_PER_PAGE_OUTPUT,
                llm_name,
            )
            print(
                f"Estimated cost: {format_cost(estimated_cost_new)} (saving {format_cost(saved_cost)} via cache)"
            )
        else:
            print(f"Estimated cost: {format_cost(estimated_cost_new)}")

        # Prompt for confirmation if cost is significant (> $1.00)
        if estimated_cost_new > 1.00:
            print(
                f"\nWARNING: This will cost approximately {format_cost(estimated_cost_new)}"
            )
            response = input("Continue? [y/N]: ").strip().lower()
            if response not in ["y", "yes"]:
                print("Cancelled by user")
                return None

    # Handle cache-only mode
    usage_stats: dict[str, int] = {"input_tokens": 0, "output_tokens": 0}
    num_docs_to_process = len(docs)
    num_cached_used = sum(
        1 for doc in docs if doc.metadata.get("source", "") in existing_summaries
    )
    num_new_needed = num_docs_to_process - num_cached_used

    if use_cache_only:
        print("\nCache-only mode: Using only cached summaries")
        summaries: list[str] = []
        for doc in docs:
            doc_url = doc.metadata.get("source", "")
            if doc_url in existing_summaries:
                summaries.append(existing_summaries[doc_url])
            else:
                print(f"  Warning: No cache for {doc_url}")
                failed_urls.add(doc_url)
        summaries_generated = len(summaries)
        new_summaries_generated = 0  # No new summaries in cache-only mode
    else:
        # Initialize summarizer
        print(f"\nGenerating summaries with {llm_name}...")
        summarizer = Summarizer(
            llm_name=llm_name,
            max_concurrent=max_concurrent_summaries,
        )

        summaries: list[str] = []
        try:
            summaries, usage_stats = await summarizer.summarize_all(
                docs, existing_summaries=existing_summaries, cache_file=cache_file
            )
            summaries_generated = len(summaries)
            # Calculate new summaries (total - cached)
            new_summaries_generated = summaries_generated - num_cached_used

            # Track URLs that failed summarization by extracting URLs from summaries
            summarized_urls: set[str] = set()
            for summary in summaries:
                if summary:
                    extracted_url: str | None = extract_url_from_summary(summary)
                    if extracted_url:
                        summarized_urls.add(extracted_url)

            # Add docs that weren't successfully summarized to failed_urls
            for doc in docs:
                doc_url = doc.metadata.get("source", "")
                if doc_url and doc_url not in summarized_urls:
                    failed_urls.add(doc_url)
        except KeyboardInterrupt:
            print("Process interrupted by user. Saving partial results...")
            new_summaries_generated = 0  # Initialize in case recovery fails
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        partial_summaries = json.load(f)
                        summaries = list(partial_summaries.values())
                        summaries_generated = len(summaries)
                        new_summaries_generated = max(
                            0, summaries_generated - num_cached_used
                        )
                        print(f"Recovered {len(summaries)} summaries from cache")
                except Exception:
                    # Silently ignore cache read errors during interrupt recovery
                    # If we can't recover from cache, we'll continue with empty results
                    pass
        except Exception as e:
            print(f"Summarization process error: {str(e)}")
            new_summaries_generated = 0  # Initialize in case recovery fails
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        partial_summaries = json.load(f)
                        summaries = list(partial_summaries.values())
                        summaries_generated = len(summaries)
                        new_summaries_generated = max(
                            0, summaries_generated - num_cached_used
                        )
                        print(
                            f"Recovered {len(summaries)} partial summaries from cache"
                        )
                except Exception:
                    # If cache recovery fails during error handling, continue with empty results
                    summaries = []
        finally:
            # Write results to file
            if summaries:
                ensure_directory_exists(output_file)
                output_content = "".join(summaries)
                Path(output_file).write_text(output_content, encoding="utf-8")
            else:
                ensure_directory_exists(output_file)
                Path(output_file).write_text("", encoding="utf-8")

            # Print summary
            print(f"\n{'=' * 50}")
            print(f"Processed: {summaries_generated}/{urls_processed} pages")
            if urls_processed > 0:
                success_rate = summaries_generated / urls_processed * 100
                print(f"Success rate: {success_rate:.1f}%")

            # Show actual API cost if tokens were used
            if usage_stats["input_tokens"] > 0 or usage_stats["output_tokens"] > 0:
                actual_cost = calculate_actual_cost(
                    usage_stats["input_tokens"], usage_stats["output_tokens"], llm_name
                )
                num_cached = len(existing_summaries)
                if num_cached > 0:
                    # Calculate how much we saved via cache
                    saved_cost = calculate_actual_cost(
                        num_cached * ESTIMATED_TOKENS_PER_PAGE_INPUT,
                        num_cached * ESTIMATED_TOKENS_PER_PAGE_OUTPUT,
                        llm_name,
                    )
                    print(
                        f"Actual cost: {format_cost(actual_cost)} (saved {format_cost(saved_cost)} via cache)"
                    )
                else:
                    print(f"Actual cost: {format_cost(actual_cost)}")

            print(f"Output: {output_file}")

            # Report failed URLs
            if failed_urls:
                print(f"Failed URLs: {len(failed_urls)}")
                failed_file = Path(output_file).parent / "failed_urls.txt"
                # Sort URLs for consistent output
                failed_file.write_text("\n".join(sorted(failed_urls)), encoding="utf-8")
                print(f"Failed URLs written to: {failed_file}")
            print(f"{'=' * 50}")

        # Determine success based on whether we generated new summaries when needed
        success = True
        if not use_cache_only:
            # If there were new pages that needed API calls
            if num_new_needed > 0:
                # Success only if we generated at least one new summary
                if new_summaries_generated == 0:
                    print("\nERROR: All API calls failed - no new summaries generated")
                    success = False
                elif new_summaries_generated < num_new_needed:
                    print(
                        f"\nWARNING: Some API calls failed ({new_summaries_generated}/{num_new_needed} successful)"
                    )
            # If all pages were cached, that's fine
        else:
            # Cache-only mode: success if we have any summaries
            success = summaries_generated > 0
            if not success:
                print("\nERROR: No cached summaries found")

        # Return success indicator (for CLI exit code)
        return {
            "success": success,
            "summaries_generated": summaries_generated,
            "new_summaries": new_summaries_generated,
        }

    return None
