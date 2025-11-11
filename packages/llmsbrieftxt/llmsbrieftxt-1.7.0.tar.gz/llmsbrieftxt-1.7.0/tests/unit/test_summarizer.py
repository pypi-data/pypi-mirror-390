import asyncio
import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llmsbrieftxt.summarizer import Summarizer


class TestSummarizerInitialization:
    @pytest.mark.unit
    def test_default_initialization(self, openai_api_key):
        summarizer = Summarizer()
        assert summarizer.llm_name == "gpt-5-mini"
        assert summarizer.max_concurrent == 10
        assert "structured summaries" in summarizer.summary_prompt

    @pytest.mark.unit
    def test_custom_parameters(self, openai_api_key):
        custom_prompt = "Custom summarization prompt"
        summarizer = Summarizer(
            llm_name="gpt-4o",
            summary_prompt=custom_prompt,
            max_concurrent=5,
        )
        assert summarizer.llm_name == "gpt-4o"
        assert summarizer.summary_prompt == custom_prompt
        assert summarizer.max_concurrent == 5

    @pytest.mark.unit
    def test_openai_client_initialization(self, openai_api_key):
        summarizer = Summarizer()
        assert summarizer.client is not None
        assert summarizer.client.api_key == "test-key"

    @pytest.mark.unit
    def test_missing_openai_api_key(self, no_api_keys):
        with pytest.raises(
            ValueError, match="OPENAI_API_KEY environment variable is required"
        ):
            Summarizer()


class TestSummarizerDocumentProcessing:
    @pytest.fixture
    def mock_document(self):
        doc = MagicMock()
        doc.metadata = {"source": "https://example.com/test-page", "title": "Test Page"}
        doc.page_content = "This is test content for summarization."
        return doc

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_openai_document_summarization(self, openai_api_key, mock_document):
        mock_response = MagicMock()
        # Mock JSON response matching PageSummary schema
        mock_response.choices[0].message.content = json.dumps(
            {
                "content_analysis": "Test content analysis",
                "primary_use_cases": "testing purposes",
                "key_takeaways": "Key point 1, Key point 2",
                "related_topics": "testing, development",
                "keywords": "test, page, content",
                "concise_summary": "This is a test page.",
            }
        )
        summarizer = Summarizer()
        # Use AsyncMock for async client calls
        with patch.object(
            summarizer.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response
            result = await summarizer.summarize_document(mock_document)
        assert result is not None
        assert "Title: [Test Page](https://example.com/test-page)" in result
        assert "Keywords: test, page, content" in result
        assert "Summary: This is a test page." in result

    @pytest.mark.unit
    def test_document_with_missing_metadata(self, openai_api_key):
        doc = MagicMock()
        doc.metadata = {"source": "https://example.com/no-title"}
        doc.page_content = "Content without title"
        summarizer = Summarizer()
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "content_analysis": "Test analysis",
                "primary_use_cases": "general reference",
                "key_takeaways": "Basic information",
                "related_topics": "general",
                "keywords": "content",
                "concise_summary": "A page with content.",
            }
        )
        with patch.object(
            summarizer.client.chat.completions, "create", return_value=mock_response
        ):
            import asyncio

            result = asyncio.run(summarizer.summarize_document(doc))
        assert "Title: [no-title](https://example.com/no-title)" in result

    @pytest.mark.unit
    @patch("asyncio.get_event_loop")
    def test_summarization_error_handling(
        self, mock_loop, openai_api_key, mock_document
    ):
        mock_loop.return_value.run_in_executor.side_effect = Exception("API Error")
        summarizer = Summarizer()
        import asyncio

        result = asyncio.run(summarizer.summarize_document(mock_document))
        # Now returns a fallback message with new format instead of None
        assert result is not None
        assert "Keywords: web, content, information" in result
        assert (
            "Summary: This page contains web content relevant to the topic." in result
        )

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_parallel_summarization(self, openai_api_key):
        docs = []
        for i in range(3):
            doc = MagicMock()
            doc.metadata = {
                "source": f"https://example.com/page-{i}",
                "title": f"Page {i}",
            }
            doc.page_content = f"Content for page {i}"
            docs.append(doc)
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "content_analysis": "Test",
                "primary_use_cases": "testing",
                "key_takeaways": "Test points",
                "related_topics": "test",
                "keywords": "test",
                "concise_summary": "Test page content",
            }
        )
        # Add usage stats to mock response
        mock_response.usage.prompt_tokens = 100
        mock_response.usage.completion_tokens = 50
        summarizer = Summarizer(max_concurrent=2)
        with (
            patch("asyncio.get_event_loop") as mock_loop,
            patch.object(
                summarizer.client.chat.completions, "create", return_value=mock_response
            ),
        ):
            future = asyncio.Future()
            future.set_result(mock_response)
            mock_loop.return_value.run_in_executor.return_value = future
            results, usage_stats = await summarizer.summarize_all(docs)
        assert len(results) == 3
        # Results may be in any order due to async completion
        for i in range(3):
            assert any(f"Title: [Page {i}]" in result for result in results)
        # Verify usage stats are returned
        assert "input_tokens" in usage_stats
        assert "output_tokens" in usage_stats

    @pytest.mark.unit
    def test_clean_summary_formatting(self, openai_api_key, mock_document):
        mock_response = MagicMock()
        mock_response.choices[0].message.content = json.dumps(
            {
                "content_analysis": "Test",
                "primary_use_cases": "testing\nwith newlines",
                "key_takeaways": "Points\nwith breaks",
                "related_topics": "test",
                "keywords": "test",
                "concise_summary": "Summary\n\nwith double newlines",
            }
        )
        summarizer = Summarizer()
        # Use AsyncMock for async client calls
        with patch.object(
            summarizer.client.chat.completions, "create", new_callable=AsyncMock
        ) as mock_create:
            mock_create.return_value = mock_response
            import asyncio

            result = asyncio.run(summarizer.summarize_document(mock_document))
        # Check that the keywords and summary lines are properly formatted
        assert "Keywords: test" in result
        assert "Summary: Summary\n\nwith double newlines" in result
        assert result.endswith("\n\n")
