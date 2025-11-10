import logging
from typing import Any

from markdownify import markdownify  # type: ignore[import-untyped]
from trafilatura import extract
from trafilatura.settings import use_config

logger = logging.getLogger(__name__)


# Cache Trafilatura config to avoid recreating on every extraction
_TRAFILATURA_CONFIG = None


def _get_trafilatura_config() -> Any:
    """Get or create cached Trafilatura config."""
    global _TRAFILATURA_CONFIG
    if _TRAFILATURA_CONFIG is None:
        _TRAFILATURA_CONFIG = use_config()
        _TRAFILATURA_CONFIG.set("DEFAULT", "MIN_EXTRACTED_SIZE", "200")
        _TRAFILATURA_CONFIG.set("DEFAULT", "MIN_FILE_SIZE", "100")
    return _TRAFILATURA_CONFIG


def default_extractor(html: str) -> str:
    """
    Extract main content from HTML using Trafilatura.

    Trafilatura intelligently extracts the main content while filtering out:
    - Navigation menus
    - Sidebars
    - Footers
    - Cookie banners
    - Advertisements

    Falls back to markdownify if Trafilatura fails or returns insufficient content.

    Args:
        html: Raw HTML content

    Returns:
        Extracted content as markdown string
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

        # Validate extraction quality
        if result and len(result) >= 100:
            logger.debug(
                f"Trafilatura extracted {len(result)} chars "
                f"(reduced from {len(html)} chars HTML)"
            )
            return str(result)
        else:
            logger.debug(
                f"Trafilatura extraction insufficient "
                f"({len(result) if result else 0} chars), using fallback"
            )

    except Exception as e:
        logger.debug(f"Trafilatura failed: {e}, using fallback")

    # Fallback to markdownify
    logger.debug("Using markdownify fallback")
    result = markdownify(html)
    return str(result)
