"""Simple URL filtering for documentation crawling."""

import logging
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class URLFilter:
    """Simple URL filtering based on file extensions."""

    # File extensions to skip (assets, downloads, media)
    FILE_EXTENSION_PATTERNS: list[str] = [
        r"\.(pdf|zip|tar|gz|exe|dmg|iso)$",  # Downloads
        r"\.(css|js|map)$",  # Web assets
        r"\.(woff2?|ttf|eot)$",  # Fonts
        r"\.(png|jpe?g|gif|svg|webp|ico|bmp)$",  # Images
        r"\.(mp4|webm|avi|mov|mp3|wav|ogg)$",  # Media
    ]

    def __init__(self) -> None:
        """Initialize URL filter with compiled patterns."""
        self.file_extension_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.FILE_EXTENSION_PATTERNS
        ]
        logger.debug(
            f"URLFilter initialized with {len(self.file_extension_patterns)} patterns"
        )

    def should_include(self, url: str) -> bool:
        """
        Determine if URL should be included in crawl.

        Logic:
        - Skip URLs with file extensions (downloads, assets, media)
        - Include everything else (documentation pages)

        Args:
            url: URL to check

        Returns:
            True if URL should be crawled, False otherwise
        """
        parsed = urlparse(url)
        path = parsed.path.lower()

        # Check file extensions
        for pattern in self.file_extension_patterns:
            if pattern.search(path):
                logger.debug(f"URL skipped by file extension: {url}")
                return False

        # Include by default
        return True

    def filter_urls(self, urls: list[str]) -> list[str]:
        """
        Filter a list of URLs.

        Args:
            urls: List of URLs to filter

        Returns:
            Filtered list of URLs
        """
        filtered = [url for url in urls if self.should_include(url)]
        skipped_count = len(urls) - len(filtered)

        if skipped_count > 0:
            logger.info(
                f"Filtered {skipped_count} URLs ({len(filtered)}/{len(urls)} remaining)"
            )

        return filtered
