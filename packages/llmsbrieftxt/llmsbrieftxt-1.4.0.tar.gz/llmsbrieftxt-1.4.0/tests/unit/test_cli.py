"""Tests for CLI argument parsing."""

import os

import pytest

from llmsbrieftxt.cli import estimate_cost, get_output_path, parse_args, validate_url


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
        ("model_arg", "expected"),
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
    def test_depth_flag_default(self):
        """Test default depth value."""
        args = parse_args(["https://example.com"])
        assert args.depth == 3

    @pytest.mark.unit
    def test_depth_flag_custom(self):
        """Test custom depth value."""
        args = parse_args(["https://example.com", "--depth", "5"])
        assert args.depth == 5

    @pytest.mark.unit
    def test_cache_dir_flag_default(self):
        """Test default cache directory."""
        args = parse_args(["https://example.com"])
        assert args.cache_dir == ".llmsbrieftxt_cache"

    @pytest.mark.unit
    def test_cache_dir_flag_custom(self):
        """Test custom cache directory."""
        args = parse_args(["https://example.com", "--cache-dir", "/tmp/mycache"])
        assert args.cache_dir == "/tmp/mycache"

    @pytest.mark.unit
    def test_use_cache_only_flag(self):
        """Test --use-cache-only flag."""
        args = parse_args(["https://example.com", "--use-cache-only"])
        assert args.use_cache_only is True

    @pytest.mark.unit
    def test_force_refresh_flag(self):
        """Test --force-refresh flag."""
        args = parse_args(["https://example.com", "--force-refresh"])
        assert args.force_refresh is True

    @pytest.mark.unit
    def test_all_new_arguments_together(self):
        """Test all new arguments combined."""
        args = parse_args(
            [
                "https://example.com",
                "--depth",
                "2",
                "--cache-dir",
                "custom_cache",
                "--max-urls",
                "100",
            ]
        )
        assert args.url == "https://example.com"
        assert args.depth == 2
        assert args.cache_dir == "custom_cache"
        assert args.max_urls == 100

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


class TestCostEstimation:
    """Tests for cost estimation."""

    @pytest.mark.unit
    def test_cost_estimate_small_job(self):
        """Test cost estimation for small number of pages."""
        cost = estimate_cost(10, "gpt-5-mini")
        assert cost.startswith("~$")
        assert "$0." in cost

    @pytest.mark.unit
    def test_cost_estimate_medium_job(self):
        """Test cost estimation for medium number of pages."""
        cost = estimate_cost(100, "gpt-4o-mini")
        assert cost.startswith("~$")
        assert "$" in cost

    @pytest.mark.unit
    def test_cost_estimate_large_job(self):
        """Test cost estimation for large number of pages."""
        cost = estimate_cost(500, "gpt-4o")
        assert cost.startswith("~$")
        assert float(cost.replace("~$", "")) > 1.0

    @pytest.mark.unit
    def test_cost_estimate_unknown_model(self):
        """Test cost estimation for unknown model."""
        cost = estimate_cost(100, "unknown-model")
        assert "not available" in cost

    @pytest.mark.unit
    def test_cost_estimate_zero_pages(self):
        """Test cost estimation for zero pages."""
        cost = estimate_cost(0, "gpt-5-mini")
        assert cost == "~$0.0000"


class TestOutputPathExpansion:
    """Tests for output path with environment variable expansion."""

    @pytest.mark.unit
    def test_output_path_with_tilde_expansion(self):
        """Test output path with ~ expands to home directory."""
        path = get_output_path("https://example.com", "~/docs/output.txt")
        assert "~" not in str(path)
        assert str(path).startswith(os.path.expanduser("~"))

    @pytest.mark.unit
    def test_output_path_with_env_var(self, monkeypatch):
        """Test output path with $VAR environment variable."""
        monkeypatch.setenv("MYDIR", "/tmp/testdir")
        path = get_output_path("https://example.com", "$MYDIR/output.txt")
        assert str(path) == "/tmp/testdir/output.txt"

    @pytest.mark.unit
    def test_output_path_with_env_var_braces(self, monkeypatch):
        """Test output path with ${VAR} environment variable."""
        monkeypatch.setenv("TESTDIR", "/tmp/test")
        path = get_output_path("https://example.com", "${TESTDIR}/docs/output.txt")
        assert str(path) == "/tmp/test/docs/output.txt"

    @pytest.mark.unit
    def test_output_path_default_no_expansion(self):
        """Test default output path (no custom path) works correctly."""
        path = get_output_path("https://docs.example.com")
        # Should contain .claude/docs in path
        assert ".claude/docs" in str(path)
        assert str(path).endswith("docs.example.com.txt")
