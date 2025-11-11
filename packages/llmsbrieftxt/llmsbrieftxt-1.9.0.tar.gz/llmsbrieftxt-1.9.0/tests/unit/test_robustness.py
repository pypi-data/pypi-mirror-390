"""Minimal robustness tests - testing error handling and failure reporting."""

import asyncio
from unittest.mock import MagicMock, patch

import pytest

from llmsbrieftxt.summarizer import Summarizer


class TestFailureBehavior:
    """Test that errors are properly detected and reported."""

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_returns_none(self, openai_api_key):
        """Verify None response when API calls fail."""
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

            # Should return None on failure
            assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_invalid_json_returns_none(self, openai_api_key):
        """Verify None when LLM returns invalid JSON."""
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

            # Should return None
            assert result is None

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_empty_response_returns_none(self, openai_api_key):
        """Verify None when LLM returns empty response."""
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

            # Should return None
            assert result is None
