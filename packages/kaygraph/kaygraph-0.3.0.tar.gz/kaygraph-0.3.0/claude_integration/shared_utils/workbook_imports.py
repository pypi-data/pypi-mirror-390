"""
Example import patterns for workbooks using shared utilities.

This file demonstrates how workbooks should import from shared_utils
to avoid duplication while maintaining workbook-specific utilities.
"""

# Example 1: Customer Support Workbook
# In customer_support/nodes.py or customer_support/utils.py

def example_customer_support_imports():
    """Example imports for customer support workbook."""
    # Import shared utilities
    from workbooks.shared_utils import ClaudeAPIClient, EmbeddingGenerator

    # Import workbook-specific utilities
    from .utils import CRMIntegration, TicketRouter, KnowledgeBase

    # Use in node
    class SentimentAnalysisNode:
        def __init__(self):
            self.claude = ClaudeAPIClient()  # Shared
            self.crm = CRMIntegration()      # Workbook-specific


# Example 2: Document Analysis Workbook
# In document_analysis/nodes.py or document_analysis/utils.py

def example_document_analysis_imports():
    """Example imports for document analysis workbook."""
    # Import shared utilities
    from workbooks.shared_utils import ClaudeAPIClient, VectorStore

    # Import workbook-specific utilities
    from .utils import TextExtractor, ComplianceChecker, RiskAssessment

    # Use in node
    class ContentAnalysisNode:
        def __init__(self):
            self.claude = ClaudeAPIClient()        # Shared
            self.extractor = TextExtractor()       # Workbook-specific
            self.vector_store = VectorStore()      # Shared


# Example 3: Financial Analysis Workbook (future)
# In financial_analysis/nodes.py

def example_financial_imports():
    """Example imports for financial analysis workbook."""
    # Import shared utilities
    from workbooks.shared_utils import (
        ClaudeAPIClient,
        EmbeddingGenerator,
        VectorStore
    )

    # Import workbook-specific utilities
    from .utils import (
        MarketDataFetcher,
        RiskCalculator,
        PortfolioOptimizer
    )


# Import pattern for main.py files
def example_main_imports():
    """Example imports for workbook main.py demos."""
    import asyncio
    import logging
    from typing import Dict, Any

    # Import KayGraph
    from kaygraph import Graph

    # Import workbook components
    from .nodes import *  # All node classes
    from .graphs import *  # All graph creation functions
    from .utils import *   # Workbook-specific utilities

    # Import shared utilities if needed directly
    from workbooks.shared_utils import ClaudeAPIClient


# Best Practices for imports

def import_best_practices():
    """
    Best practices for managing imports in workbooks:

    1. Always import shared utilities from workbooks.shared_utils
    2. Keep workbook-specific utilities in the workbook's own utils.py
    3. Use relative imports within a workbook (.utils, .nodes)
    4. Use absolute imports for shared utilities (workbooks.shared_utils)
    5. Import only what you need, not entire modules
    6. Group imports: standard library, third-party, kaygraph, shared, local
    """

    # Good - specific imports
    from workbooks.shared_utils import ClaudeAPIClient, ClaudeAPIError

    # Bad - importing everything
    # from workbooks.shared_utils import *

    # Good - organized imports
    # Standard library
    import asyncio
    import logging
    from typing import Dict, Any, Optional

    # Third-party
    import pandas as pd
    from tenacity import retry

    # KayGraph
    from kaygraph import Graph, ValidatedNode

    # Shared utilities
    from workbooks.shared_utils import ClaudeAPIClient

    # Local workbook imports
    from .utils import WorkbookSpecificHelper
    from .nodes import CustomNode


if __name__ == "__main__":
    print("This file demonstrates import patterns for workbooks.")
    print("See the function definitions for examples.")