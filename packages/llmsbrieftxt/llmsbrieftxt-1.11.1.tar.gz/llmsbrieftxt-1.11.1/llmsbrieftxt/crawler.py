"""Simple web crawler with sitemap support and BFS fallback."""

import asyncio
import contextlib
import io
import logging
import sys
from collections.abc import Generator
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup, Tag
from tenacity import retry, stop_after_attempt, wait_exponential
from usp.tree import sitemap_tree_for_homepage  # type: ignore[import-untyped]

from llmsbrieftxt.url_filters import URLFilter
from llmsbrieftxt.url_utils import URLCanonicalizer

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def suppress_output() -> Generator[None, None, None]:
    """Suppress stdout and stderr temporarily.

    USP library prints noisy errors to console.
    Suppress them when sitemap parsing fails (expected for SPA sites).
    """
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    try:
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        yield
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


class RobustDocCrawler:
    """Production-ready documentation crawler with sitemap and BFS fallback."""

    def __init__(
        self,
        max_urls: int | None = None,
        max_depth: int = 3,
        max_concurrent: int = 10,
    ):
        """Initialize the crawler.

        Args:
            max_urls: Maximum number of URLs to crawl (None = unlimited)
            max_depth: Maximum crawl depth
            max_concurrent: Maximum concurrent requests
        """
        self.max_urls = max_urls or 500
        self.max_depth = max_depth
        self.max_concurrent = max_concurrent
        self.discovered_urls: set[str] = set()
        self.user_agent = (
            "llmsbrieftxt-bot/1.0 (+https://github.com/stevennevins/llmsbrief)"
        )
        self.url_canonicalizer = URLCanonicalizer(keep_fragments=False)
        self.url_filter = URLFilter()
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def discover_urls(self, base_url: str) -> set[str]:
        """Discover URLs using sitemap or BFS crawling.

        Priority:
        1. Sitemap (fastest, most complete)
        2. BFS crawling (fallback)

        Args:
            base_url: The starting URL

        Returns:
            Set of discovered URLs
        """
        self.discovered_urls = set()

        # Strategy 1: Try sitemap first
        logger.info("Strategy 1: Checking for sitemap...")
        sitemap_urls = await self._discover_from_sitemap(base_url)
        if sitemap_urls:
            logger.info(f"Sitemap discovery successful: {len(sitemap_urls)} URLs")
            self.discovered_urls = sitemap_urls
            return self._apply_limits(sitemap_urls)

        # Strategy 2: Fall back to BFS crawling
        logger.info("Strategy 2: Using BFS crawler...")
        crawled_urls = await self._crawl_bfs(base_url)
        logger.info(f"BFS discovery complete: {len(crawled_urls)} URLs")
        self.discovered_urls = crawled_urls
        return self._apply_limits(crawled_urls)

    async def _discover_from_sitemap(self, base_url: str) -> set[str]:
        """Discover URLs from sitemap.xml files.

        Args:
            base_url: The base URL to discover sitemap for

        Returns:
            Set of URLs found in sitemaps
        """
        urls: set[str] = set()

        try:
            # Try standard sitemap location
            parsed = urlparse(base_url)
            base_domain = f"{parsed.scheme}://{parsed.netloc}"
            sitemap_url = f"{base_domain}/sitemap.xml"
            logger.info("Trying standard sitemap location")

            # Parse sitemap (with timeout)
            # Suppress noisy errors from USP library (expected for SPA sites)
            try:
                logger.info(f"Parsing sitemap: {sitemap_url}")
                with suppress_output():
                    tree = await asyncio.wait_for(
                        asyncio.to_thread(sitemap_tree_for_homepage, sitemap_url),  # type: ignore[reportUnknownArgumentType]
                        timeout=30.0,
                    )
                sitemap_pages = [page.url for page in tree.all_pages()]

                if sitemap_pages:
                    logger.info(
                        f"Found {len(sitemap_pages)} URLs in sitemap {sitemap_url}"
                    )

                    # Filter URLs to only those under base path
                    base_path = self._get_base_path(base_url)
                    for url in sitemap_pages:
                        if self._is_under_base_path(url, base_path):
                            urls.add(url)
            except asyncio.TimeoutError:
                logger.debug(f"Timeout parsing sitemap {sitemap_url}")

        except Exception as e:
            logger.debug(f"Sitemap discovery failed: {e}")

        return urls

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    async def _fetch_with_retry(self, url: str, client: httpx.AsyncClient) -> str:
        """Fetch URL with retry logic and concurrency limiting."""
        async with self.semaphore:
            response = await client.get(url, timeout=30.0, follow_redirects=True)
            response.raise_for_status()
            return response.text

    async def _crawl_bfs(self, base_url: str) -> set[str]:
        """Crawl using breadth-first search.

        Args:
            base_url: The starting URL

        Returns:
            Set of discovered URLs
        """
        discovered: set[str] = set()
        to_visit: set[str] = {base_url}
        visited: set[str] = set()
        base_path = self._get_base_path(base_url)

        # Print initial discovery status
        print("Discovering URLs: 0 found", end="", flush=True)

        async with httpx.AsyncClient(
            follow_redirects=True, timeout=httpx.Timeout(30.0)
        ) as client:
            for depth in range(self.max_depth):
                if not to_visit or len(discovered) >= self.max_urls:
                    break

                logger.info(f"Depth {depth}: {len(to_visit)} URLs to visit")
                current_level = list(to_visit)
                to_visit: set[str] = set()

                # Process in batches
                for i in range(0, len(current_level), self.max_concurrent):
                    # Check if we've reached max_urls before processing next batch
                    if len(discovered) >= self.max_urls:
                        break

                    batch = current_level[i : i + self.max_concurrent]
                    tasks = [
                        self._extract_links(url, client, base_path) for url in batch
                    ]
                    results = await asyncio.gather(*tasks, return_exceptions=True)

                    for url, result in zip(batch, results, strict=False):
                        # Check max_urls before adding each URL
                        if len(discovered) >= self.max_urls:
                            break

                        visited.add(url)
                        discovered.add(url)

                        # Update live counter
                        print(
                            f"\rDiscovering URLs: {len(discovered)} found",
                            end="",
                            flush=True,
                        )

                        if not isinstance(result, Exception) and isinstance(
                            result, set
                        ):
                            # Add new URLs to visit
                            for link in result:
                                if (
                                    link not in visited
                                    and link not in discovered
                                    and link not in to_visit
                                    and len(discovered) < self.max_urls
                                ):
                                    to_visit.add(link)

                logger.info(
                    f"Depth {depth} complete: {len(discovered)} URLs discovered"
                )

        # Final newline after live counter
        print()  # Move to next line
        return discovered

    async def _extract_links(
        self, url: str, client: httpx.AsyncClient, base_path: str
    ) -> set[str]:
        """Extract links from a page."""
        links: set[str] = set()

        try:
            html = await self._fetch_with_retry(url, client)
            soup = BeautifulSoup(html, "html.parser")

            for anchor in soup.find_all("a", href=True):
                if not isinstance(anchor, Tag):
                    continue
                href_value = anchor.get("href")
                if (
                    href_value
                    and isinstance(href_value, str)
                    and self._is_valid_doc_link(href_value)
                ):
                    href = href_value
                    absolute_url = urljoin(url, href)
                    if self._is_under_base_path(absolute_url, base_path):
                        links.add(absolute_url)

        except Exception as e:
            logger.debug(f"Failed to extract links from {url}: {e}")

        return links

    def _get_base_path(self, url: str) -> str:
        """Extract the base path from a URL for scope filtering.

        Args:
            url: The URL to extract base path from

        Returns:
            Base path string
        """
        parsed = urlparse(url)

        # For GitHub repos, extract user/repo
        if "github.com" in parsed.netloc:
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 2:
                # Handle special GitHub paths
                if parts[2:3] == ["wiki"]:
                    return f"/{parts[0]}/{parts[1]}/wiki/"
                elif parts[2:4] == ["tree"]:
                    # Include branch in path
                    if len(parts) >= 4:
                        return f"/{parts[0]}/{parts[1]}/tree/{parts[3]}/"
                    return f"/{parts[0]}/{parts[1]}/"
                elif parts[2:3] == ["blob"]:
                    # Single file path
                    return f"/{parts[0]}/{parts[1]}/"
                else:
                    # Standard repo root
                    return f"/{parts[0]}/{parts[1]}/"

        # For regular docs, use the full path up to the last segment
        path = parsed.path
        if not path or path == "/":
            return "/"

        # If path looks like a file, remove the filename
        if "." in path.split("/")[-1]:
            path = "/".join(path.split("/")[:-1]) + "/"
        elif not path.endswith("/"):
            path = path + "/"

        return path

    def _is_under_base_path(self, url: str, base_path: str) -> bool:
        """Check if URL is under the base path.

        Args:
            url: The URL to check
            base_path: The base path to compare against

        Returns:
            True if URL is under base path
        """
        parsed = urlparse(url)
        url_path = parsed.path if parsed.path else "/"

        # Ensure consistent trailing slashes
        if not url_path.endswith("/") and "." not in url_path.split("/")[-1]:
            url_path = url_path + "/"

        return url_path.startswith(base_path)

    def _is_valid_doc_link(self, link: str) -> bool:
        """Check if a link is likely to be documentation using filtering.

        Args:
            link: The link to check

        Returns:
            True if link appears to be documentation
        """
        # Skip invalid links
        if not link or link.startswith("#") or link.startswith("javascript:"):
            return False

        # Use URLFilter for extension-based filtering
        return self.url_filter.should_include(link)

    def _apply_limits(self, urls: set[str]) -> set[str]:
        """Apply canonicalization, deduplication, and max_urls limit.

        Args:
            urls: Set of URLs to process

        Returns:
            Canonicalized, deduplicated, and limited set of URLs
        """
        # Convert set to list for deduplication (preserves order)
        url_list = list(urls)

        # Deduplicate using URL canonicalizer
        unique_urls = self.url_canonicalizer.deduplicate(url_list)

        duplicates_removed = len(url_list) - len(unique_urls)
        if duplicates_removed > 0:
            logger.info(
                f"Removed {duplicates_removed} duplicate URLs "
                f"({len(url_list)} -> {len(unique_urls)})"
            )

        # Apply max_urls limit
        if self.max_urls and len(unique_urls) > self.max_urls:
            logger.info(f"Limiting {len(unique_urls)} URLs to {self.max_urls}")
            unique_urls = unique_urls[: self.max_urls]

        return set(unique_urls)
