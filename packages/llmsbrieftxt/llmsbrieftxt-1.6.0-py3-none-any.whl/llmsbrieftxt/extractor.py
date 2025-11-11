import logging
from typing import Any

from trafilatura import extract
from trafilatura.settings import use_config

logger = logging.getLogger(__name__)


# Cache Trafilatura config to avoid recreating on every extraction
_trafilatura_config: Any = None


def _get_trafilatura_config() -> Any:
    """Get or create cached Trafilatura config."""
    global _trafilatura_config
    if _trafilatura_config is None:
        _trafilatura_config = use_config()
        _trafilatura_config.set("DEFAULT", "MIN_EXTRACTED_SIZE", "200")
        _trafilatura_config.set("DEFAULT", "MIN_FILE_SIZE", "100")
    return _trafilatura_config


def default_extractor(html: str) -> str:
    """
    Extract main content from HTML using Trafilatura.

    Trafilatura intelligently extracts the main content while filtering out:
    - Navigation menus
    - Sidebars
    - Footers
    - Cookie banners
    - Advertisements

    Args:
        html: Raw HTML content

    Returns:
        Extracted content as markdown string (empty string if extraction fails)
    """
    # Get cached Trafilatura config
    config = _get_trafilatura_config()

    # Extract with Trafilatura
    try:
        result = extract(
            html,
            config=config,
            output_format="markdown",
            include_links=True,
            include_images=False,  # Images not needed for text summaries
            include_tables=True,
            include_comments=False,
            favor_recall=True,  # Prefer extracting more rather than less
        )

        if result:
            logger.debug(
                f"Trafilatura extracted {len(result)} chars "
                f"(reduced from {len(html)} chars HTML)"
            )
            return str(result)
        else:
            logger.debug("Trafilatura extraction returned no content")
            return ""

    except Exception as e:
        logger.warning(f"Trafilatura extraction failed: {e}")
        return ""
