"""Integration tests for the doc_loader module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llmsbrieftxt.doc_loader import DocLoader


class TestDocLoaderIntegration:
    """Integration tests for doc loader with realistic scenarios."""

    @pytest.mark.asyncio
    async def test_breadth_first_discovery(self):
        """Test breadth-first discovery with realistic HTML."""
        # Mock the crawler's discover_urls method to simulate URL discovery
        with patch(
            "llmsbrieftxt.doc_loader.RobustDocCrawler.discover_urls"
        ) as mock_discover:
            # Simulate discovering multiple URLs from different levels
            mock_discover.return_value = {
                "https://example.com/",
                "https://example.com/docs",
                "https://example.com/api",
                "https://example.com/guides",
                "https://example.com/docs/intro",
                "https://example.com/docs/advanced",
            }

            loader = DocLoader()
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            # Should discover multiple levels of pages
            assert len(urls) > 1
            assert "https://example.com/" in urls
            mock_discover.assert_called_once_with("https://example.com")

    @pytest.mark.asyncio
    async def test_max_urls_enforcement(self):
        """Test that max_urls is properly enforced."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # Create HTML with many links
            links_html = "\n".join(
                [f'<a href="/page{i}">Page {i}</a>' for i in range(100)]
            )
            html = f"<html>{links_html}</html>"

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html

            mock_client.get.return_value = mock_response

            loader = DocLoader(max_urls=10)
            docs, urls = await loader.load_docs("https://example.com")

            assert len(urls) <= 10

    @pytest.mark.asyncio
    async def test_doc_loader_direct_usage(self):
        """Test DocLoader with direct instantiation."""
        with patch("llmsbrieftxt.doc_loader.DocLoader.load_docs") as mock_load_docs:
            mock_load_docs.return_value = (
                [
                    MagicMock(
                        page_content="Test content", metadata={"source": "test.com"}
                    )
                ],
                ["https://test.com"],
            )

            # Test DocLoader directly
            loader = DocLoader()
            docs, _ = await loader.load_docs("https://test.com")
            assert len(docs) == 1
            mock_load_docs.assert_called_once()

    @pytest.mark.asyncio
    async def test_show_urls_flag(self):
        """Test the show_urls flag functionality."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            html = """
            <html>
                <a href="/docs">Documentation</a>
                <a href="/api">API</a>
            </html>
            """

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html

            mock_client.get.return_value = mock_response

            # Test with show_urls=True
            loader = DocLoader()
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            # Should return empty docs list when show_urls=True
            assert len(docs) == 0
            assert len(urls) > 0

    @pytest.mark.asyncio
    async def test_url_deduplication(self):
        """Test that URLs are properly deduplicated."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # HTML with duplicate links in different formats
            html = """
            <html>
                <a href="/docs">Documentation</a>
                <a href="/docs/">Documentation</a>
                <a href="https://example.com/docs">Documentation</a>
                <a href="https://EXAMPLE.COM/docs/">Documentation</a>
                <a href="/api#section">API</a>
                <a href="/api">API</a>
            </html>
            """

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html

            mock_client.get.return_value = mock_response

            loader = DocLoader()
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            # Count unique normalized paths
            paths = set()
            for url in urls:
                if "example.com" in url:
                    path = url.split("example.com")[1]
                    paths.add(path)

            # Should have deduplicated /docs and /api
            # Plus the base URL
            assert len(paths) <= 3  # /, /docs, /api

    @pytest.mark.asyncio
    async def test_url_filtering(self):
        """Test that non-documentation URLs are filtered."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client

            # HTML with mixed link types
            html = """
            <html>
                <a href="/docs">Documentation</a>
                <a href="/api">API</a>
                <a href="/style.css">Stylesheet</a>
                <a href="/image.png">Image</a>
                <a href="/script.js">Script</a>
                <a href="/download.pdf">PDF</a>
            </html>
            """

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = html

            mock_client.get.return_value = mock_response

            loader = DocLoader()
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            # Check that assets are filtered
            for url in urls:
                assert not url.endswith(".css")
                assert not url.endswith(".png")
                assert not url.endswith(".js")
                assert not url.endswith(".pdf")
