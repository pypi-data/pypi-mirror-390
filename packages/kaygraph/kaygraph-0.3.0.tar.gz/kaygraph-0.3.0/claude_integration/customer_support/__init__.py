"""
Customer Support System - Real-world Claude + KayGraph integration.

This workbook demonstrates a production-ready customer support system that
uses Claude for intelligent ticket routing, response generation, and
sentiment analysis within a KayGraph workflow.

Features:
- Automatic ticket categorization and priority assignment
- Intelligent response generation based on customer sentiment
- Multi-step escalation workflows
- Performance monitoring and metrics collection
- Integration with external systems (CRM, knowledge base)
"""

from .nodes import *
from .graphs import *
from .utils import *

__all__ = [
    # Nodes
    'TicketIngestionNode',
    'SentimentAnalysisNode',
    'TicketCategorizationNode',
    'PriorityAssignmentNode',
    'ResponseGenerationNode',
    'EscalationDecisionNode',
    'KnowledgeBaseSearchNode',
    'HumanEscalationNode',
    'CustomerSatisfactionNode',

    # Graphs
    'CustomerSupportWorkflow',
    'EscalationWorkflow',
    'HighPriorityWorkflow',

    # Utils
    'CRMIntegration',
    'KnowledgeBase',
    'SupportMetrics'
]