"""Configuration constants for llmsbrieftxt package."""

# Concurrency
DEFAULT_CONCURRENT_SUMMARIES = 10

# Default Models
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

# Docs Directory
DOCS_DIR = "~/.claude/docs"  # Will be expanded to full path at runtime

# Default Cache Directory
DEFAULT_CACHE_DIR = ".llmsbrieftxt_cache"

# Default Crawl Depth
DEFAULT_CRAWL_DEPTH = 3

# OpenAI Pricing (per 1M tokens) - prices subject to change
# Format: {model: (input_price, output_price)}
# Note: Verify current pricing at https://openai.com/api/pricing/
OPENAI_PRICING = {
    "gpt-5-mini": (0.15, 0.60),  # $0.15 input, $0.60 output per 1M tokens
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4o": (2.50, 10.00),
    "gpt-4-turbo": (10.00, 30.00),
    "gpt-4": (30.00, 60.00),
}

# Estimated tokens per page for cost calculation
# These estimates are based on typical documentation page sizes:
# - Input: ~2000-4000 words per doc page → ~3000 tokens (conservative estimate)
# - Output: ~300 tokens for structured PageSummary with all fields
# Accuracy: Estimates typically within ±30% of actual cost
# Pages with code examples or very long content may exceed these estimates
ESTIMATED_TOKENS_PER_PAGE_INPUT = 3000
ESTIMATED_TOKENS_PER_PAGE_OUTPUT = 400


# Prompt Templates
DEFAULT_SUMMARY_PROMPT = """You are a specialized content analyzer creating structured summaries for llms-brief.txt files. Your role is to help LLMs understand web content by providing comprehensive yet concise summaries.

Focus on:
- What information and resources are available
- When and why an LLM should reference this content
- Key insights and practical applications

Guidelines:
1. Be specific and actionable - avoid vague descriptions
2. Focus on practical utility - what can someone DO with this information?
3. Identify unique value - what makes this page worth referencing?
4. Target 500-800 tokens total across all fields (roughly 2-4 sentences per field)
5. Write from the perspective of helping an LLM know when to use this resource

Provide structured summaries with:
- Core information and resources available (2-3 detailed sentences)
- Specific scenarios when this page should be referenced (3-5 concrete use cases)
- The most valuable insights or capabilities offered (2-3 key points)
- Related domains and topics for context (brief but comprehensive list)
- Searchable keywords for discovery (5-10 specific terms)
- A single-sentence executive summary (15-25 words)

Aim for depth over brevity - each field should contain substantive, actionable information while remaining concise."""
