import asyncio
import json
import logging
import os
from pathlib import Path
from typing import Any

import openai
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)
from tqdm import tqdm

from .constants import (
    DEFAULT_CONCURRENT_SUMMARIES,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_SUMMARY_PROMPT,
)
from .schema import Document, PageSummary

logger = logging.getLogger(__name__)


# Note: No fallback summary - we want failures to be properly reported


class Summarizer:
    def __init__(
        self,
        llm_name: str = DEFAULT_OPENAI_MODEL,
        summary_prompt: str | None = None,
        max_concurrent: int = DEFAULT_CONCURRENT_SUMMARIES,
    ) -> None:
        self.llm_name = llm_name
        self.max_concurrent = max_concurrent
        self.summary_prompt = summary_prompt or DEFAULT_SUMMARY_PROMPT
        self.client = self._init_client()
        self.semaphore = asyncio.Semaphore(max_concurrent)
        # Cache JSON schema to avoid regenerating on every request
        self._schema_cache = PageSummary.model_json_schema()
        self._schema_cache["additionalProperties"] = False
        # Track token usage for cost reporting (protected by lock for thread safety)
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self._usage_lock = asyncio.Lock()

    def _init_client(self) -> AsyncOpenAI:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required. Please set your OpenAI API key in your environment variables."
            )
        base_url = os.getenv("OPENAI_BASE_URL")
        if base_url:
            return AsyncOpenAI(api_key=api_key, base_url=base_url)
        return AsyncOpenAI(api_key=api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=4, max=60),
        retry=retry_if_exception_type(
            (
                openai.RateLimitError,
                openai.APITimeoutError,
                openai.APIConnectionError,
            )
        ),
        reraise=True,
    )
    async def _summarize_with_retry(
        self,
        doc: Any,
        loop: Any,
        messages: list[dict[str, str]],
        schema: dict[str, Any],
    ) -> Any:
        """Make LLM API call with retry logic for transient failures."""
        return await self.client.chat.completions.create(  # type: ignore[call-overload]
            model=self.llm_name,
            messages=messages,  # type: ignore[arg-type]
            response_format={  # type: ignore[typeddict-item]
                "type": "json_schema",
                "json_schema": {
                    "name": "page_summary",
                    "schema": schema,
                    "strict": True,
                },
            },
        )

    async def _summarize(self, doc: Any, loop: Any) -> PageSummary | None:
        """Summarize document using OpenAI API. Returns None on failure."""
        url = doc.metadata.get("source", "unknown")
        try:
            # Truncate content if it's too long (keep first 10000 chars for now)
            content = doc.page_content[:10000]

            # Build messages with combined system prompt
            messages = [
                {"role": "system", "content": self.summary_prompt},
                {
                    "role": "user",
                    "content": f"Analyze and summarize the following webpage content:\n\n{content}",
                },
            ]

            # Use cached schema
            schema = self._schema_cache

            response = await self._summarize_with_retry(doc, loop, messages, schema)

            # Track token usage (protected by lock to prevent race conditions)
            if response and hasattr(response, "usage") and response.usage:
                async with self._usage_lock:
                    self.total_input_tokens += response.usage.prompt_tokens
                    self.total_output_tokens += response.usage.completion_tokens

            # Validate response
            if not response:
                raise ValueError("No response object from API")

            if not response.choices:
                raise ValueError(f"No choices in response: {response}")

            if not response.choices[0].message:
                raise ValueError(
                    f"No message in response choice: {response.choices[0]}"
                )

            if not response.choices[0].message.content:
                # Check if there's a finish reason that explains why
                finish_reason = (
                    response.choices[0].finish_reason
                    if hasattr(response.choices[0], "finish_reason")
                    else "unknown"
                )
                raise ValueError(
                    f"Empty content in response. Finish reason: {finish_reason}"
                )

            content = response.choices[0].message.content.strip()
            if not content:
                raise ValueError("Empty response content after stripping")

            # Parse JSON response
            try:
                parsed_response = PageSummary(**json.loads(content))
            except json.JSONDecodeError as je:
                raise ValueError(
                    f"Invalid JSON response: {je}. Content: {content[:200]}..."
                ) from je

            # Return structured response for formatting
            return parsed_response

        except Exception as e:
            # Log with full traceback for debugging
            logger.error(
                f"Failed to summarize {url}: {str(e)}",
                exc_info=e,
                extra={
                    "url": url,
                    "model": self.llm_name,
                },
            )
            # Return None to indicate failure (no fallback)
            return None

    async def summarize_document(
        self, doc: Any, cache_file: Path | None = None
    ) -> str | None:
        async with self.semaphore:
            url = doc.metadata.get("source", "")
            try:
                loop = asyncio.get_event_loop()
                page_summary = await self._summarize(doc, loop)

                # Check if summarization failed
                if page_summary is None:
                    logger.warning(f"Summarization failed for {url}")
                    return None

                # Format the summary with new structure
                title = doc.metadata.get("title", url.split("/")[-1])
                formatted_summary = f"Title: [{title}]({url})\nKeywords: {page_summary.keywords}\nSummary: {page_summary.concise_summary}\n\n"

                # Update cache if provided
                if cache_file:
                    self._update_cache(cache_file, url, formatted_summary)

                return formatted_summary
            except Exception as e:
                logger.error(
                    f"Error summarizing {url}: {str(e)}",
                    exc_info=e,
                    extra={"url": url},
                )
                return None

    def _update_cache(self, cache_file: Path, url: str, summary: str) -> None:
        """Update the cache file with a new summary (simple version for single-user CLI)."""
        try:
            # Read existing cache
            cache_data = {}
            if cache_file.exists():
                cache_data = json.loads(cache_file.read_text())

            # Update and write
            cache_data[url] = summary
            cache_file.write_text(json.dumps(cache_data, indent=2))
        except Exception as e:
            logger.exception(
                f"Could not update cache: {str(e)}",
                exc_info=e,
                extra={"cache_file": str(cache_file), "url": url},
            )

    async def summarize_all(
        self,
        docs: list[Document],
        existing_summaries: dict[str, str] | None = None,
        cache_file: Path | None = None,
    ) -> tuple[list[str], dict[str, int]]:
        # Reset token counters at start of each run
        self.total_input_tokens = 0
        self.total_output_tokens = 0

        existing_summaries = existing_summaries or {}
        summaries: list[str] = []
        docs_to_process: list[Document] = []

        # Separate cached from new documents
        for doc in docs:
            url = doc.metadata.get("source", "")
            if url in existing_summaries:
                summaries.append(existing_summaries[url])
            else:
                docs_to_process.append(doc)

        if len(existing_summaries) > 0:
            print(f"Using {len(existing_summaries)} cached summaries")

        if not docs_to_process:
            usage_stats = {
                "input_tokens": self.total_input_tokens,
                "output_tokens": self.total_output_tokens,
            }
            return summaries, usage_stats

        # Process new documents with progress bar
        print(
            f"Summarizing {len(docs_to_process)} documents (max {self.max_concurrent} concurrent)..."
        )

        tasks = [self.summarize_document(doc, cache_file) for doc in docs_to_process]

        # Use tqdm to track completion
        failed_count = 0
        with tqdm(
            total=len(docs_to_process), desc="Generating summaries", unit="doc"
        ) as pbar:
            results: list[str | None | Exception] = []
            for coro in asyncio.as_completed(tasks):
                result = await coro
                results.append(result)
                if result is None or isinstance(result, Exception):
                    failed_count += 1
                    pbar.set_postfix({"failed": failed_count})  # type: ignore[reportUnknownMemberType]
                pbar.update(1)

        # Collect successful summaries
        for result in results:
            if isinstance(result, str):
                summaries.append(result)

        # Log any failures with full context
        for result, doc in zip(results, docs_to_process, strict=False):
            if isinstance(result, Exception):
                url = doc.metadata.get("source", "unknown")
                logger.exception(
                    f"Failed to summarize document {url}: {str(result)}",
                    exc_info=result,
                    extra={"url": url},
                )

        success_count = len(results) - failed_count
        print(
            f"Summarization complete: {success_count} successful, {failed_count} failed"
        )

        # Return summaries and usage statistics
        usage_stats = {
            "input_tokens": self.total_input_tokens,
            "output_tokens": self.total_output_tokens,
        }
        return summaries, usage_stats
