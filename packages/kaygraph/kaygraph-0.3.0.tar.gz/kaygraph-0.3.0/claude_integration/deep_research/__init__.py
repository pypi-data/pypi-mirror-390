"""
Deep Research Workbook - Multi-agent research system with Claude.

This workbook implements the advanced multi-agent research patterns described
in Anthropic's blog post, showing how to build a production-grade research
system with KayGraph and Claude.
"""

from .nodes import (
    IntentClarificationNode,
    LeadResearcherNode,
    SubAgentNode,
    MemoryManagerNode,
    SearchStrategyNode,
    ResultSynthesisNode,
    CitationNode,
    QualityAssessmentNode
)

from .graphs import (
    create_research_workflow,
    create_deep_dive_workflow,
    create_breadth_first_workflow,
    create_fact_checking_workflow,
    ResearchOrchestrator
)

from .models import (
    ResearchTask,
    SubAgentTask,
    ResearchMemory,
    Citation,
    ResearchResult
)

__version__ = "0.1.0"

__all__ = [
    # Nodes
    "IntentClarificationNode",
    "LeadResearcherNode",
    "SubAgentNode",
    "MemoryManagerNode",
    "SearchStrategyNode",
    "ResultSynthesisNode",
    "CitationNode",
    "QualityAssessmentNode",

    # Graphs
    "create_research_workflow",
    "create_deep_dive_workflow",
    "create_breadth_first_workflow",
    "create_fact_checking_workflow",
    "ResearchOrchestrator",

    # Models
    "ResearchTask",
    "SubAgentTask",
    "ResearchMemory",
    "Citation",
    "ResearchResult"
]