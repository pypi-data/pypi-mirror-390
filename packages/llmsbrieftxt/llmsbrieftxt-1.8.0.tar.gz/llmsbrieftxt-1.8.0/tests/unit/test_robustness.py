"""Minimal robustness tests - testing our fallback logic, not third-party retry libraries."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from llmsbrieftxt.summarizer import FALLBACK_SUMMARY, Summarizer


class TestFallbackBehavior:
    """Test that errors result in fallback responses."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_returns_fallback(self, openai_api_key):
        """Verify fallback response when API calls fail."""
        summarizer = Summarizer()

        doc = MagicMock()
        doc.page_content = "Test content"
        doc.metadata = {"source": "https://example.com"}

        # Force an error
        def mock_create(*args, **kwargs):
            raise RuntimeError("API error")

        with patch.object(
            summarizer.client.chat.completions, "create", side_effect=mock_create
        ):
            loop = asyncio.get_event_loop()
            result = await summarizer._summarize(doc, loop)

            # Should get fallback response
            assert result == FALLBACK_SUMMARY
            assert result.keywords == "web, content, information"

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_json_returns_fallback(self, openai_api_key):
        """Verify fallback when LLM returns invalid JSON."""
        summarizer = Summarizer()

        doc = MagicMock()
        doc.page_content = "Test content"
        doc.metadata = {"source": "https://example.com/test"}

        # Mock response with invalid JSON
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "This is not JSON {broken"

        with patch.object(
            summarizer.client.chat.completions, "create", return_value=mock_response
        ):
            loop = asyncio.get_event_loop()
            result = await summarizer._summarize(doc, loop)

            # Should get fallback
            assert result == FALLBACK_SUMMARY

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_empty_response_returns_fallback(self, openai_api_key):
        """Verify fallback when LLM returns empty response."""
        summarizer = Summarizer()

        doc = MagicMock()
        doc.page_content = "Test content"
        doc.metadata = {"source": "https://example.com/empty"}

        # Mock empty response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = ""

        with patch.object(
            summarizer.client.chat.completions, "create", return_value=mock_response
        ):
            loop = asyncio.get_event_loop()
            result = await summarizer._summarize(doc, loop)

            # Should get fallback
            assert result == FALLBACK_SUMMARY
