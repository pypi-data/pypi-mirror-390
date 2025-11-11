from typing import Any

from pydantic import BaseModel, Field


class Document(BaseModel):
    """Simple document class to replace langchain.schema.Document."""

    page_content: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class PageSummary(BaseModel):
    content_analysis: str = Field(
        description="Comprehensive analysis of the page content (2-3 sentences, ~50-80 words). "
        "Include main topics, key concepts, important features, and unique value propositions. "
        "Be specific about what makes this content valuable and distinctive."
    )
    primary_use_cases: str = Field(
        description="3-5 specific, actionable scenarios when an LLM should reference this page (2-3 sentences total, ~40-60 words). "
        'Format as concrete use cases like: "When implementing X feature", "To understand Y concept", '
        '"For troubleshooting Z issue". Focus on practical applications.'
    )
    key_takeaways: str = Field(
        description="2-3 most valuable insights, capabilities, or pieces of information (2-3 sentences, ~40-60 words). "
        "Highlight unique knowledge, practical tips, or critical information that makes this page worth consulting. "
        "Format as distinct points separated by semicolons."
    )
    related_topics: str = Field(
        description="Relevant domains, technologies, and concepts this page relates to (1-2 sentences, ~20-30 words). "
        'List connected topics that provide context, like: "API design, REST principles, microservices architecture". '
        "Help establish the knowledge domain."
    )
    keywords: str = Field(
        description="5-10 specific, searchable terms for discovery and indexing (comma-separated list, ~15-25 words). "
        "Include technical terms, product names, methodologies, and key concepts. "
        'Example: "GraphQL, API Gateway, schema stitching, federation, Apollo Server, type safety".'
    )
    concise_summary: str = Field(
        description="Single comprehensive sentence capturing the essence of the page (15-25 words). "
        "Summarize what the page offers and its primary value in one clear, informative statement."
    )
