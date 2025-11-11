import os
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def sample_urls():
    return ["https://example.com", "https://example.org", "https://example.net"]


@pytest.fixture(autouse=True)
def clean_environment():
    original_env = {"OPENAI_API_KEY": os.getenv("OPENAI_API_KEY")}
    yield
    for key, value in original_env.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


@pytest.fixture
def openai_api_key():
    os.environ["OPENAI_API_KEY"] = "test-key"
    return


@pytest.fixture
def no_api_keys():
    os.environ.pop("OPENAI_API_KEY", None)
    return


def skip_if_no_openai():
    return pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"), reason="OpenAI API key not available"
    )
