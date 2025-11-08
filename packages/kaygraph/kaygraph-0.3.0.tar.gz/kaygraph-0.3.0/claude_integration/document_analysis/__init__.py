"""
Enterprise Document Analysis System - Claude + KayGraph Integration.

This workbook demonstrates a production-ready document analysis and insights
system that uses Claude for intelligent document processing, summarization,
and knowledge extraction within KayGraph workflows.

Features:
- Multi-format document ingestion and preprocessing
- Intelligent document summarization and key insights extraction
- Cross-document analysis and pattern detection
- Knowledge graph construction from documents
- Compliance and risk assessment
- Automated report generation
- Integration with enterprise document stores
"""

from .nodes import *
from .graphs import *
from .utils import *

__all__ = [
    # Nodes
    'DocumentIngestionNode',
    'DocumentPreprocessingNode',
    'ContentAnalysisNode',
    'DocumentSummarizationNode',
    'InsightExtractionNode',
    'CrossDocumentAnalysisNode',
    'ComplianceCheckNode',
    'RiskAssessmentNode',
    'KnowledgeGraphBuilderNode',
    'ReportGenerationNode',

    # Graphs
    'DocumentAnalysisWorkflow',
    'BatchDocumentProcessing',
    'ComplianceAssessmentWorkflow',
    'KnowledgeGraphConstruction',
    'ExecutiveReportingWorkflow',

    # Utils
    'DocumentStore',
    'TextExtractor',
    'ComplianceRules',
    'RiskAssessmentFramework',
    'ReportTemplate'
]