"""
End-to-end integration tests with Ollama as the LLM provider.

These tests require:
- OPENAI_BASE_URL environment variable set to Ollama endpoint (e.g., http://localhost:11434/v1)
- OPENAI_API_KEY environment variable (can be any value for Ollama)
- Ollama service running with tinyllama model pulled
"""

import os
import tempfile
from pathlib import Path

import pytest

from llmsbrieftxt.main import generate_llms_txt


@pytest.mark.asyncio
@pytest.mark.requires_openai
async def test_ollama_basic_generation():
    """Test basic llms-brief.txt generation with Ollama."""
    # Verify Ollama endpoint is configured
    base_url = os.getenv("OPENAI_BASE_URL")
    assert base_url, "OPENAI_BASE_URL must be set for Ollama tests"
    assert "11434" in base_url or "ollama" in base_url.lower(), (
        f"Expected Ollama endpoint, got: {base_url}"
    )

    # Use a simple test URL (example.com is perfect for this)
    test_url = "https://example.com"

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "test_output.txt"
        cache_dir = Path(tmp_dir) / "cache"

        # Generate with Ollama (using tinyllama model)
        await generate_llms_txt(
            url=test_url,
            output_path=str(output_file),
            llm_name="tinyllama",  # Ollama model name
            max_urls=5,  # Limit to just a few URLs for speed
            max_depth=1,  # Only one level deep
            cache_dir=str(cache_dir),
            skip_confirmation=True,  # Skip confirmation prompt in tests
        )

        # Verify output was created
        assert output_file.exists(), "Output file should be created"
        content = output_file.read_text()

        # Verify basic structure
        assert len(content) > 0, "Output should not be empty"
        assert "Title:" in content, "Output should contain Title field"
        assert "Keywords:" in content, "Output should contain Keywords field"
        assert "Summary:" in content, "Output should contain Summary field"
        assert test_url in content, "Output should contain the test URL"

        print(f"✓ Generated {len(content)} bytes of content")
        print(f"✓ Cache directory: {cache_dir}")


@pytest.mark.asyncio
@pytest.mark.requires_openai
async def test_ollama_with_cache():
    """Test that caching works correctly with Ollama."""
    base_url = os.getenv("OPENAI_BASE_URL")
    assert base_url, "OPENAI_BASE_URL must be set for Ollama tests"

    test_url = "https://example.com"

    with tempfile.TemporaryDirectory() as tmp_dir:
        output_file = Path(tmp_dir) / "test_output.txt"
        cache_dir = Path(tmp_dir) / "cache"

        # First run - should generate and cache
        await generate_llms_txt(
            url=test_url,
            output_path=str(output_file),
            llm_name="tinyllama",
            max_urls=3,
            max_depth=1,
            cache_dir=str(cache_dir),
            skip_confirmation=True,
        )

        first_content = output_file.read_text()
        assert len(first_content) > 0

        # Verify cache was created
        cache_file = cache_dir / "summaries.json"
        assert cache_file.exists(), "Cache file should be created"

        # Second run - should use cache
        output_file.unlink()  # Delete output to ensure regeneration
        await generate_llms_txt(
            url=test_url,
            output_path=str(output_file),
            llm_name="tinyllama",
            max_urls=3,
            max_depth=1,
            cache_dir=str(cache_dir),
            skip_confirmation=True,
        )

        second_content = output_file.read_text()
        assert len(second_content) > 0

        print("✓ Cache test passed")
