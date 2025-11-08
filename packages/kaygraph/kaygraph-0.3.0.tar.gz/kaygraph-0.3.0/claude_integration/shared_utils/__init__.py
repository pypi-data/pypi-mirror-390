"""
Shared utilities for KayGraph workbooks.

This module contains utilities that are used across multiple workbooks,
such as the Claude API client and common helper functions.
"""

from .claude_api import ClaudeAPIClient, ClaudeAPIError
from .embeddings import EmbeddingGenerator, SimilarityCalculator
from .vector_store import VectorStore, VectorSearchResult

__all__ = [
    "ClaudeAPIClient",
    "ClaudeAPIError",
    "EmbeddingGenerator",
    "SimilarityCalculator",
    "VectorStore",
    "VectorSearchResult"
]

__version__ = "0.1.0"