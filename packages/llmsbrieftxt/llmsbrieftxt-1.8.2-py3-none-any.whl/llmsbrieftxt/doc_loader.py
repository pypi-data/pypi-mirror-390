"""Documentation-aware loader for intelligently discovering and crawling documentation sites."""

import asyncio
import logging
from collections.abc import Callable

import httpx
from tqdm import tqdm

from llmsbrieftxt.crawler import RobustDocCrawler
from llmsbrieftxt.extractor import default_extractor
from llmsbrieftxt.schema import Document

logger = logging.getLogger(__name__)


class DocLoader:
    """Main documentation loader using robust crawling strategies."""

    def __init__(
        self,
        max_urls: int | None = None,
        max_concurrent: int = 10,
        max_depth: int = 3,
    ):
        """Initialize the documentation loader.

        Args:
            max_urls: Optional maximum number of URLs to discover
            max_concurrent: Maximum concurrent requests (default 10)
            max_depth: Maximum crawl depth (default 3)
        """
        self.max_urls = max_urls
        self.max_concurrent = max_concurrent
        self.max_depth = max_depth
        self.crawler = RobustDocCrawler(
            max_urls=max_urls,
            max_depth=max_depth,
            max_concurrent=max_concurrent,
        )

    async def load_docs(
        self,
        url: str,
        extractor: Callable[[str], str] | None = None,
        show_urls: bool = False,
    ) -> tuple[list[Document], list[str]]:
        """Load documentation pages using robust discovery strategies.

        Args:
            url: The base URL to start from
            extractor: Optional content extractor function
            show_urls: Whether to return discovered URLs without loading

        Returns:
            Tuple of (documents, discovered_urls)
        """
        if extractor is None:
            extractor = default_extractor

        logger.info(f"Starting documentation discovery for {url}")
        print(f"Discovering documentation from {url}...")

        # Use RobustDocCrawler to discover URLs
        discovered_urls = await self.crawler.discover_urls(url)

        print(f"\nFound {len(discovered_urls)} pages")

        if show_urls:
            # Return empty documents but include URLs for preview
            return [], sorted(discovered_urls)

        # Load content from discovered URLs
        documents = await self._load_documents(list(discovered_urls), extractor)

        return documents, sorted(discovered_urls)

    async def _load_documents(
        self, urls: list[str], extractor: Callable[[str], str]
    ) -> list[Document]:
        """Load content from URLs and create documents.

        Args:
            urls: List of URLs to load
            extractor: Function to extract content from HTML

        Returns:
            List of Document objects
        """
        documents: list[Document] = []
        url_list: list[str] = urls

        async with httpx.AsyncClient(
            follow_redirects=True, timeout=httpx.Timeout(30.0)
        ) as client:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent)

            async def load_with_limit(url: str) -> Document | None:
                """Load document with semaphore-controlled concurrency."""
                async with semaphore:
                    return await self._load_single_document(url, client, extractor)

            # Process all URLs concurrently with semaphore limiting parallelism
            with tqdm(
                total=len(url_list), desc="Loading documents", unit="doc"
            ) as pbar:
                tasks = [load_with_limit(url) for url in url_list]

                # Use as_completed to update progress bar as tasks finish
                for coro in asyncio.as_completed(tasks):
                    result = await coro
                    if isinstance(result, Exception):
                        logger.warning(f"Failed to load: {result}")
                    elif result is not None:
                        documents.append(result)
                    pbar.update(1)

        return documents

    async def _load_single_document(
        self, url: str, client: httpx.AsyncClient, extractor: Callable[[str], str]
    ) -> Document | None:
        """Load a single document from a URL.

        Args:
            url: The URL to load
            client: HTTP client
            extractor: Content extraction function

        Returns:
            Document object or None if failed
        """
        try:
            response = await client.get(url, timeout=30.0, follow_redirects=True)
            if response.status_code == 200:
                content = extractor(response.text)
                if content and len(content.strip()) > 100:
                    return Document(
                        page_content=content, metadata={"source": url, "url": url}
                    )
                else:
                    logger.debug(f"No meaningful content extracted from {url}")
                    return None
            else:
                logger.debug(f"HTTP {response.status_code} for {url}")
                return None
        except Exception as e:
            logger.debug(f"Failed to load {url}: {e}")
            return None
