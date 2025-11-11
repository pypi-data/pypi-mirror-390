"""Main generation pipeline for llmsbrieftxt."""

import json
import re
from pathlib import Path

from llmsbrieftxt.doc_loader import DocLoader
from llmsbrieftxt.extractor import default_extractor
from llmsbrieftxt.summarizer import Summarizer


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
) -> dict[str, int | list[str]] | None:
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

    Returns:
        Dictionary with metadata (for show_urls mode) or None
    """
    urls_processed = 0
    summaries_generated = 0
    failed_urls: set[str] = set()  # Use set to avoid duplicates

    # Set up cache directory
    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    cache_file = cache_path / "summaries.json"

    # Load existing summaries from cache if available (unless force refresh)
    existing_summaries: dict[str, str] = {}
    if cache_file.exists() and not force_refresh:
        try:
            with open(cache_file) as f:
                existing_summaries = json.load(f)
                print(f"Found {len(existing_summaries)} cached summaries")
        except Exception as e:
            print(f"Warning: Could not load cache: {str(e)}")
    elif force_refresh and cache_file.exists():
        print("Force refresh enabled - ignoring existing cache")

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

        return {"num_urls": len(discovered_urls), "failed_urls": []}

    # Load and process documents
    doc_loader = DocLoader(max_urls=max_urls, max_depth=max_depth)
    docs, discovered_urls = await doc_loader.load_docs(url, extractor=extractor)
    urls_processed = len(docs)

    # Track which URLs failed to load
    loaded_urls = {doc.metadata.get("source") for doc in docs}
    failed_urls.update(u for u in discovered_urls if u not in loaded_urls)

    # Handle cache-only mode
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
    else:
        # Initialize summarizer
        print(f"\nGenerating summaries with {llm_name}...")
        summarizer = Summarizer(
            llm_name=llm_name,
            max_concurrent=max_concurrent_summaries,
        )

        summaries: list[str] = []
        try:
            summaries = await summarizer.summarize_all(
                docs, existing_summaries=existing_summaries, cache_file=cache_file
            )
            summaries_generated = len(summaries)

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
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        partial_summaries = json.load(f)
                        summaries = list(partial_summaries.values())
                        summaries_generated = len(summaries)
                        print(f"Recovered {len(summaries)} summaries from cache")
                except Exception:
                    # Silently ignore cache read errors during interrupt recovery
                    # If we can't recover from cache, we'll continue with empty results
                    pass
        except Exception as e:
            print(f"Summarization process error: {str(e)}")
            if cache_file.exists():
                try:
                    with open(cache_file) as f:
                        partial_summaries = json.load(f)
                        summaries = list(partial_summaries.values())
                        summaries_generated = len(summaries)
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
            print(f"Output: {output_file}")

            # Report failed URLs
            if failed_urls:
                print(f"Failed URLs: {len(failed_urls)}")
                failed_file = Path(output_file).parent / "failed_urls.txt"
                # Sort URLs for consistent output
                failed_file.write_text("\n".join(sorted(failed_urls)), encoding="utf-8")
                print(f"Failed URLs written to: {failed_file}")
            print(f"{'=' * 50}")

    return None
