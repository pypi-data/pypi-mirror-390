"""Unit tests for the doc_loader module."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llmsbrieftxt.doc_loader import DocLoader


class TestDocLoader:
    """Test the main DocLoader class."""

    @pytest.mark.asyncio
    async def test_load_docs_basic(self):
        """Test basic document loading."""
        # Mock the crawler's discover_urls method
        with patch("llmsbrieftxt.doc_loader.RobustDocCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler

            # Mock discovery to return some URLs
            mock_crawler.discover_urls.return_value = {"https://example.com/"}

            # Mock httpx client for content loading
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                html = "<html><body>Test content here</body></html>"
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.text = html

                mock_client.get.return_value = mock_response

                loader = DocLoader()
                docs, urls = await loader.load_docs("https://example.com")

                # Should discover at least the base URL
                assert len(urls) >= 1
                assert any("example.com" in url for url in urls)

    @pytest.mark.asyncio
    async def test_load_docs_show_urls_only(self):
        """Test showing URLs without loading content."""
        with patch("llmsbrieftxt.doc_loader.RobustDocCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler

            # Mock discovery to return multiple URLs
            mock_crawler.discover_urls.return_value = {
                "https://example.com/",
                "https://example.com/docs",
                "https://example.com/api",
            }

            loader = DocLoader()
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            assert len(docs) == 0  # No documents loaded
            assert len(urls) == 3  # URLs discovered
            assert "https://example.com/" in urls

    @pytest.mark.asyncio
    async def test_load_docs_with_max_urls(self):
        """Test that max_urls limit is respected."""
        with patch("llmsbrieftxt.doc_loader.RobustDocCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler

            # Mock discovery to return limited URLs
            mock_crawler.discover_urls.return_value = {
                f"https://example.com/page{i}" for i in range(5)
            }

            loader = DocLoader(max_urls=5)
            docs, urls = await loader.load_docs("https://example.com", show_urls=True)

            assert len(urls) <= 5

    @pytest.mark.asyncio
    async def test_load_docs_content_validation(self):
        """Test that empty content is filtered out."""
        with patch("llmsbrieftxt.doc_loader.RobustDocCrawler") as mock_crawler_class:
            mock_crawler = AsyncMock()
            mock_crawler_class.return_value = mock_crawler

            mock_crawler.discover_urls.return_value = {
                "https://example.com/page1",
                "https://example.com/page2",
            }

            with patch("httpx.AsyncClient") as mock_client_class:
                mock_client = AsyncMock()
                mock_client_class.return_value.__aenter__.return_value = mock_client

                # First page has content, second is empty
                responses = []

                # Good content
                response1 = MagicMock()
                response1.status_code = 200
                response1.text = (
                    "<html><body>" + ("Test content " * 50) + "</body></html>"
                )
                responses.append(response1)

                # Empty content (too short)
                response2 = MagicMock()
                response2.status_code = 200
                response2.text = "<html><body>x</body></html>"
                responses.append(response2)

                mock_client.get.side_effect = responses

                loader = DocLoader(max_urls=2)
                docs, urls = await loader.load_docs("https://example.com")

                # Should only have one document (empty one filtered)
                assert len(docs) == 1
