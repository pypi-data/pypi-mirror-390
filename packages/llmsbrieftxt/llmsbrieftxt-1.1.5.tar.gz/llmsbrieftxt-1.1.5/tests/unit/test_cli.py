"""Tests for CLI argument parsing."""

import pytest

from llmsbrieftxt.cli import parse_args, validate_url


class TestCLIArgumentParsing:
    """Tests for CLI argument parsing."""

    @pytest.mark.unit
    def test_positional_url_parsing(self):
        """Test basic URL as positional argument."""
        args = parse_args(["https://example.com"])
        assert args.url == "https://example.com"
        assert args.model == "gpt-5-mini"

    @pytest.mark.unit
    def test_positional_url_with_model(self):
        """Test URL with custom model."""
        args = parse_args(["https://example.com", "--model", "gpt-4o"])
        assert args.url == "https://example.com"
        assert args.model == "gpt-4o"

    @pytest.mark.unit
    @pytest.mark.parametrize(
        "model_arg,expected",
        [
            ("gpt-5-mini", "gpt-5-mini"),
            ("gpt-4o", "gpt-4o"),
            ("gpt-4o-mini", "gpt-4o-mini"),
        ],
    )
    def test_model_argument_parsing(self, model_arg, expected):
        """Test various model arguments."""
        args = parse_args(["https://example.com", "--model", model_arg])
        assert args.url == "https://example.com"
        assert args.model == expected

    @pytest.mark.unit
    def test_max_concurrent_summaries_default(self):
        """Test default max concurrent summaries."""
        args = parse_args(["https://example.com"])
        assert args.max_concurrent_summaries == 10

    @pytest.mark.unit
    def test_max_concurrent_summaries_custom(self):
        """Test custom max concurrent summaries."""
        args = parse_args(["https://example.com", "--max-concurrent-summaries", "20"])
        assert args.max_concurrent_summaries == 20

    @pytest.mark.unit
    def test_all_arguments_together(self):
        """Test all arguments combined."""
        args = parse_args(
            [
                "https://example.com",
                "--model",
                "gpt-4o",
                "--max-concurrent-summaries",
                "15",
                "--output",
                "custom.txt",
            ]
        )
        assert args.url == "https://example.com"
        assert args.model == "gpt-4o"
        assert args.max_concurrent_summaries == 15
        assert args.output == "custom.txt"

    @pytest.mark.unit
    def test_invalid_max_concurrent_type(self):
        """Test that invalid max concurrent type is rejected."""
        with pytest.raises(SystemExit):
            parse_args(
                [
                    "https://example.com",
                    "--max-concurrent-summaries",
                    "not-a-number",
                ]
            )

    @pytest.mark.unit
    def test_output_path_default(self):
        """Test default output path (None - computed from URL)."""
        args = parse_args(["https://example.com"])
        assert args.output is None

    @pytest.mark.unit
    def test_output_path_custom(self):
        """Test custom output path."""
        args = parse_args(["https://example.com", "--output", "custom/path/output.txt"])
        assert args.output == "custom/path/output.txt"

    @pytest.mark.unit
    def test_output_path_absolute(self):
        """Test absolute output path."""
        args = parse_args(["https://example.com", "--output", "/tmp/my_llms-brief.txt"])
        assert args.output == "/tmp/my_llms-brief.txt"

    @pytest.mark.unit
    def test_show_urls_flag(self):
        """Test --show-urls flag."""
        args = parse_args(["https://example.com", "--show-urls"])
        assert args.show_urls is True

    @pytest.mark.unit
    def test_max_urls_flag(self):
        """Test --max-urls flag."""
        args = parse_args(["https://example.com", "--max-urls", "50"])
        assert args.max_urls == 50

    @pytest.mark.unit
    def test_no_url_exits(self):
        """Test that providing no URL exits with error."""
        with pytest.raises(SystemExit):
            parse_args([])


class TestURLValidation:
    """Tests for URL validation."""

    @pytest.mark.unit
    def test_valid_http_url(self):
        """Test valid HTTP URL."""
        assert validate_url("http://example.com") is True

    @pytest.mark.unit
    def test_valid_https_url(self):
        """Test valid HTTPS URL."""
        assert validate_url("https://example.com") is True

    @pytest.mark.unit
    def test_valid_url_with_path(self):
        """Test valid URL with path."""
        assert validate_url("https://docs.python.org/3/") is True

    @pytest.mark.unit
    def test_invalid_url_no_scheme(self):
        """Test invalid URL without scheme."""
        assert validate_url("example.com") is False

    @pytest.mark.unit
    def test_invalid_url_wrong_scheme(self):
        """Test invalid URL with wrong scheme."""
        assert validate_url("ftp://example.com") is False

    @pytest.mark.unit
    def test_invalid_url_empty(self):
        """Test invalid empty URL."""
        assert validate_url("") is False

    @pytest.mark.unit
    def test_invalid_url_malformed(self):
        """Test invalid malformed URL."""
        assert validate_url("not-a-url") is False
