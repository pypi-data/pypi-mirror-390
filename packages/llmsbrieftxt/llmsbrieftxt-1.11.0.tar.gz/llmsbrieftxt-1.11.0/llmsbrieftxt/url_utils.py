"""Simple URL deduplication utilities."""

from urllib.parse import urlparse, urlunparse


class URLCanonicalizer:
    """Simple URL canonicalization for documentation sites."""

    def __init__(self, keep_fragments: bool = False):
        """
        Initialize URL canonicalizer.

        Args:
            keep_fragments: Keep URL fragments (for sites using hash routing).
                           Default is False to treat #section1 and #section2 as same URL.
        """
        self.keep_fragments = keep_fragments

    def canonicalize(self, url: str) -> str:
        """
        Normalize URL for deduplication.

        Simple normalization:
        - Lowercase scheme and domain
        - Remove fragments (unless keep_fragments=True)
        - Normalize trailing slashes for directory paths

        Args:
            url: URL to canonicalize

        Returns:
            Canonicalized URL string
        """
        parsed = urlparse(url)

        # Normalize scheme and domain to lowercase
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        path = parsed.path

        # Normalize trailing slashes: add to directory-like paths
        if path and not path.endswith("/"):
            # If no file extension, treat as directory
            last_segment = path.split("/")[-1]
            if "." not in last_segment:
                path = path + "/"

        # Remove fragment unless keeping them
        fragment = parsed.fragment if self.keep_fragments else ""

        # Reconstruct URL
        return urlunparse((scheme, netloc, path, parsed.params, parsed.query, fragment))

    def deduplicate(self, urls: list[str]) -> list[str]:
        """
        Remove duplicate URLs from list while preserving order.

        Args:
            urls: List of URLs (may contain duplicates)

        Returns:
            List of unique URLs (first occurrence preserved)
        """
        seen: set[str] = set()
        unique: list[str] = []

        for url in urls:
            canonical = self.canonicalize(url)
            if canonical not in seen:
                seen.add(canonical)
                unique.append(url)  # Keep original URL

        return unique
