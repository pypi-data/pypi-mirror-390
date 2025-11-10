"""Main generation pipeline for llmsbrieftxt."""

import json
from pathlib import Path
from typing import Dict, Optional

from llmsbrieftxt.doc_loader import DocLoader
from llmsbrieftxt.extractor import default_extractor
from llmsbrieftxt.summarizer import Summarizer


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
    max_urls: Optional[int] = None,
) -> None:
    """
    Generate llms-brief.txt file from a documentation website.

    Args:
        url: URL of the documentation site to crawl
        llm_name: OpenAI model to use for summarization
        max_concurrent_summaries: Maximum concurrent LLM requests
        output_path: Path to write the output file
        show_urls: If True, only show discovered URLs without processing
        max_urls: Maximum number of URLs to discover/process
    """
    urls_processed = 0
    summaries_generated = 0

    # Set up cache directory
    cache_dir = Path(".llmsbrieftxt_cache")
    cache_dir.mkdir(exist_ok=True)
    cache_file = cache_dir / "summaries.json"

    # Load existing summaries from cache if available
    existing_summaries: Dict[str, str] = {}
    if cache_file.exists():
        try:
            with open(cache_file, "r") as f:
                existing_summaries = json.load(f)
                print(f"Using {len(existing_summaries)} cached summaries")
        except Exception as e:
            print(f"Warning: Could not load cache: {str(e)}")

    extractor = default_extractor
    output_file = output_path

    # If show_urls is True, just show discovered URLs and exit
    if show_urls:
        print("Discovering documentation URLs...")
        doc_loader = DocLoader(max_urls=max_urls)
        _, discovered_urls = await doc_loader.load_docs(
            url, extractor=extractor, show_urls=True
        )
        print("\nDiscovered URLs:")
        for discovered_url in discovered_urls:
            print(f"  - {discovered_url}")
        print(f"\nTotal: {len(discovered_urls)} unique URLs")
        return

    # Load and process documents
    doc_loader = DocLoader(max_urls=max_urls)
    docs, discovered_urls = await doc_loader.load_docs(url, extractor=extractor)
    urls_processed = len(docs)

    # Initialize summarizer
    print(f"\nGenerating summaries with {llm_name}...")
    summarizer = Summarizer(
        llm_name=llm_name,
        max_concurrent=max_concurrent_summaries,
    )

    summaries = []
    try:
        summaries = await summarizer.summarize_all(
            docs, existing_summaries=existing_summaries, cache_file=cache_file
        )
        summaries_generated = len(summaries)
    except KeyboardInterrupt:
        print("Process interrupted by user. Saving partial results...")
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    partial_summaries = json.load(f)
                    summaries = list(partial_summaries.values())
                    summaries_generated = len(summaries)
                    print(f"Recovered {len(summaries)} summaries from cache")
            except Exception:
                pass
    except Exception as e:
        print(f"Summarization process error: {str(e)}")
        if cache_file.exists():
            try:
                with open(cache_file, "r") as f:
                    partial_summaries = json.load(f)
                    summaries = list(partial_summaries.values())
                    summaries_generated = len(summaries)
                    print(f"Recovered {len(summaries)} partial summaries from cache")
            except Exception:
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
        print(f"{'=' * 50}")
