"""Configuration constants for llmsbrieftxt package."""

# Concurrency
DEFAULT_CONCURRENT_SUMMARIES = 10

# Default Models
DEFAULT_OPENAI_MODEL = "gpt-5-mini"

# Docs Directory
DOCS_DIR = "~/.claude/docs"  # Will be expanded to full path at runtime


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
