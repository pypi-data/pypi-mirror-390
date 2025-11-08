"""
Deep Research utilities following KayGraph patterns.

This module provides search tools and utilities for the deep research system,
keeping vendor-specific code separate from workflow logic.
"""

from .search_tools import (
    BraveSearchClient,
    BraveAIGroundingClient,
    JinaSearchClient,
    SearchResult,
    SearchToolFactory
)

from .research_utils import (
    Aspect,
    Entity,
    detect_query_type,
    extract_aspects_from_query,
    extract_entities,
    allocate_agents_by_priority,
    generate_aspect_queries,
    calculate_priority_score,
    merge_aspect_findings
)

__all__ = [
    # Search tools
    "BraveSearchClient",
    "BraveAIGroundingClient",
    "JinaSearchClient",
    "SearchResult",
    "SearchToolFactory",

    # Research utilities
    "Aspect",
    "Entity",
    "detect_query_type",
    "extract_aspects_from_query",
    "extract_entities",
    "allocate_agents_by_priority",
    "generate_aspect_queries",
    "calculate_priority_score",
    "merge_aspect_findings"
]