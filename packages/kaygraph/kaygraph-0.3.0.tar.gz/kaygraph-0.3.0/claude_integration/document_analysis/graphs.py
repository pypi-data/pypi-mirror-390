"""
Document Analysis Workflow Graphs.

This module contains the graph definitions for the document analysis system,
implementing various document processing patterns and workflows.
"""

import logging
from typing import Dict, Any, List, Optional
from kaygraph import Graph

from .nodes import (
    DocumentIngestionNode,
    DocumentPreprocessingNode,
    ContentAnalysisNode,
    DocumentSummarizationNode,
    InsightExtractionNode,
    ComplianceCheckNode,
    ReportGenerationNode
)


def create_document_analysis_workflow():
    """
    Creates the main document analysis workflow.

    This workflow processes documents through:
    1. Ingestion and validation
    2. Preprocessing and normalization
    3. Content analysis using Claude
    4. Summarization (multiple types)
    5. Insight extraction
    6. Compliance checking
    7. Report generation

    Returns:
        Graph: The configured document analysis workflow
    """
    logger = logging.getLogger(__name__)

    # Create all nodes
    ingestion = DocumentIngestionNode()
    preprocessing = DocumentPreprocessingNode()
    content_analysis = ContentAnalysisNode()
    summarization = DocumentSummarizationNode()
    insight_extraction = InsightExtractionNode()
    compliance = ComplianceCheckNode()
    report_generation = ReportGenerationNode()

    # Define workflow connections
    ingestion >> preprocessing
    preprocessing >> content_analysis
    content_analysis >> summarization
    summarization >> insight_extraction

    # Branch based on document type for compliance
    insight_extraction - "cross_document_analysis" >> report_generation

    # Compliance routing
    insight_extraction >> compliance
    compliance - "manual_review" >> report_generation
    compliance - "risk_assessment" >> report_generation
    compliance - "knowledge_graph" >> report_generation

    logger.info("Document analysis workflow created")
    return Graph(start=ingestion)


def create_batch_document_workflow():
    """
    Creates a workflow for processing multiple documents in batch.

    This workflow efficiently processes multiple documents:
    1. Batch ingestion with validation
    2. Parallel preprocessing
    3. Concurrent analysis
    4. Aggregated insights
    5. Cross-document analysis
    6. Consolidated reporting

    Returns:
        Graph: The batch processing workflow
    """
    logger = logging.getLogger(__name__)

    from kaygraph import BatchNode, ParallelBatchNode

    class BatchDocumentIngestion(ParallelBatchNode):
        """Batch ingestion for multiple documents."""

        def __init__(self):
            super().__init__(
                max_workers=5,
                node_id="batch_document_ingestion"
            )

        def prep(self, shared):
            return shared.get("batch_documents", [])

        def exec(self, document):
            # Validate each document
            required_fields = ["id", "filename", "content", "file_type"]
            if all(field in document for field in required_fields):
                return {
                    "id": document["id"],
                    "filename": document["filename"],
                    "file_type": document["file_type"],
                    "content": document["content"],
                    "status": "valid"
                }
            return {"status": "invalid", "document": document}

        def post(self, shared, prep_res, exec_res_list):
            valid_docs = [doc for doc in exec_res_list if doc.get("status") == "valid"]
            invalid_docs = [doc for doc in exec_res_list if doc.get("status") == "invalid"]

            shared["valid_documents"] = valid_docs
            shared["invalid_documents"] = invalid_docs
            shared["batch_stats"] = {
                "total": len(exec_res_list),
                "valid": len(valid_docs),
                "invalid": len(invalid_docs)
            }

            return "batch_analysis"

    class BatchContentAnalysis(ParallelBatchNode):
        """Batch content analysis using parallel processing."""

        def __init__(self):
            super().__init__(
                max_workers=3,  # Limit for API rate limits
                node_id="batch_content_analysis"
            )

        def prep(self, shared):
            return shared.get("valid_documents", [])

        def exec(self, document):
            # Simulate content analysis
            # In production, this would call Claude API
            return {
                "document_id": document["id"],
                "summary": f"Summary of {document['filename']}",
                "topics": ["topic1", "topic2"],
                "sentiment": "neutral",
                "complexity": "moderate"
            }

        def post(self, shared, prep_res, exec_res_list):
            shared["batch_analysis_results"] = exec_res_list
            return "cross_document_synthesis"

    class CrossDocumentSynthesis(BatchNode):
        """Synthesizes insights across multiple documents."""

        def __init__(self):
            super().__init__(node_id="cross_document_synthesis")

        def prep(self, shared):
            return shared.get("batch_analysis_results", [])

        def exec(self, analysis_results):
            # Aggregate insights across documents
            all_topics = set()
            sentiment_counts = {}

            for result in analysis_results:
                all_topics.update(result.get("topics", []))
                sentiment = result.get("sentiment", "unknown")
                sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1

            return {
                "unique_topics": list(all_topics),
                "sentiment_distribution": sentiment_counts,
                "document_count": len(analysis_results),
                "cross_references": self._find_cross_references(analysis_results)
            }

        def _find_cross_references(self, results):
            # Find common themes across documents
            cross_refs = []
            for i, doc1 in enumerate(results):
                for j, doc2 in enumerate(results[i+1:], i+1):
                    common_topics = set(doc1.get("topics", [])) & set(doc2.get("topics", []))
                    if common_topics:
                        cross_refs.append({
                            "doc1": doc1["document_id"],
                            "doc2": doc2["document_id"],
                            "common_topics": list(common_topics)
                        })
            return cross_refs

        def post(self, shared, prep_res, exec_res):
            shared["cross_document_insights"] = exec_res
            return "batch_report"

    # Create batch workflow nodes
    batch_ingestion = BatchDocumentIngestion()
    batch_analysis = BatchContentAnalysis()
    cross_synthesis = CrossDocumentSynthesis()
    batch_report = ReportGenerationNode()

    # Connect batch workflow
    batch_ingestion >> batch_analysis
    batch_analysis >> cross_synthesis
    cross_synthesis >> batch_report

    logger.info("Batch document workflow created")
    return Graph(start=batch_ingestion)


def create_compliance_assessment_workflow():
    """
    Creates a specialized workflow for compliance and regulatory assessment.

    This workflow focuses on:
    1. Document classification
    2. Regulatory requirement checking
    3. Risk assessment
    4. Violation detection
    5. Remediation recommendations
    6. Compliance reporting

    Returns:
        Graph: The compliance assessment workflow
    """
    logger = logging.getLogger(__name__)

    # Import specialized compliance nodes
    from kaygraph import ValidatedNode

    class DocumentClassificationNode(ValidatedNode):
        """Classifies documents for compliance purposes."""

        def __init__(self):
            super().__init__(node_id="document_classification")

        def validate_input(self, document):
            if not document.get("content"):
                raise ValueError("Document content required for classification")
            return document

        def prep(self, shared):
            return shared.get("document_content", {})

        def exec(self, document):
            # Classify document type for compliance
            # In production, use ML classifier or Claude
            classification = {
                "type": "contract",  # contract, policy, report, etc.
                "sensitivity": "confidential",  # public, internal, confidential, restricted
                "regulatory_scope": ["GDPR", "SOX"],  # applicable regulations
                "risk_level": "medium"  # low, medium, high, critical
            }
            return classification

        def validate_output(self, classification):
            required = ["type", "sensitivity", "regulatory_scope", "risk_level"]
            if not all(key in classification for key in required):
                raise ValueError("Incomplete classification")
            return classification

        def post(self, shared, prep_res, exec_res):
            shared["document_classification"] = exec_res
            return "regulatory_check"

    class RegulatoryCheckNode(ValidatedNode):
        """Checks document against regulatory requirements."""

        def __init__(self):
            super().__init__(node_id="regulatory_check")

        def prep(self, shared):
            return {
                "content": shared.get("document_content", {}),
                "classification": shared.get("document_classification", {})
            }

        def exec(self, check_data):
            regulations = check_data["classification"].get("regulatory_scope", [])

            # Check against each regulation
            checks = []
            for regulation in regulations:
                checks.append({
                    "regulation": regulation,
                    "status": "compliant",  # compliant, partial, non_compliant
                    "violations": [],
                    "warnings": ["Consider reviewing data retention policy"],
                    "confidence": 0.85
                })

            return {
                "regulatory_checks": checks,
                "overall_compliance": "partial",
                "action_required": True
            }

        def post(self, shared, prep_res, exec_res):
            shared["regulatory_results"] = exec_res

            if exec_res.get("action_required"):
                return "risk_assessment"
            else:
                return "compliance_report"

    class RiskAssessmentNode(ValidatedNode):
        """Performs detailed risk assessment."""

        def __init__(self):
            super().__init__(node_id="risk_assessment")

        def prep(self, shared):
            return {
                "classification": shared.get("document_classification", {}),
                "regulatory": shared.get("regulatory_results", {})
            }

        def exec(self, risk_data):
            # Assess risks based on classification and regulatory results
            risk_assessment = {
                "overall_risk": "medium",
                "risk_factors": [
                    {
                        "factor": "data_privacy",
                        "level": "high",
                        "mitigation": "Implement data encryption"
                    },
                    {
                        "factor": "regulatory_compliance",
                        "level": "medium",
                        "mitigation": "Update compliance procedures"
                    }
                ],
                "recommendations": [
                    "Conduct privacy impact assessment",
                    "Review data handling procedures"
                ],
                "review_required": True
            }
            return risk_assessment

        def post(self, shared, prep_res, exec_res):
            shared["risk_assessment"] = exec_res
            return "compliance_report"

    # Create compliance workflow nodes
    ingestion = DocumentIngestionNode()
    preprocessing = DocumentPreprocessingNode()
    classification = DocumentClassificationNode()
    regulatory_check = RegulatoryCheckNode()
    risk_assessment = RiskAssessmentNode()
    compliance_report = ReportGenerationNode()

    # Connect compliance workflow
    ingestion >> preprocessing
    preprocessing >> classification
    classification >> regulatory_check
    regulatory_check - "risk_assessment" >> risk_assessment
    regulatory_check - "compliance_report" >> compliance_report
    risk_assessment >> compliance_report

    logger.info("Compliance assessment workflow created")
    return Graph(start=ingestion)


def create_executive_reporting_workflow():
    """
    Creates a workflow optimized for executive-level reporting.

    This workflow focuses on:
    1. High-level analysis
    2. Key metrics extraction
    3. Visual insights preparation
    4. Strategic recommendations
    5. Executive summary generation

    Returns:
        Graph: The executive reporting workflow
    """
    logger = logging.getLogger(__name__)

    from kaygraph import AsyncNode

    class ExecutiveSummaryNode(AsyncNode):
        """Generates executive-level summaries."""

        def __init__(self):
            super().__init__(node_id="executive_summary")

        async def prep(self, shared):
            return {
                "document": shared.get("document_content", {}),
                "analysis": shared.get("content_analysis", {}),
                "insights": shared.get("extracted_insights", {})
            }

        async def exec(self, summary_data):
            # Generate executive summary
            # In production, use Claude for sophisticated summarization
            return {
                "executive_summary": "High-level strategic overview...",
                "key_metrics": {
                    "roi_impact": "15%",
                    "risk_level": "medium",
                    "opportunity_score": 8.5
                },
                "strategic_recommendations": [
                    "Proceed with implementation",
                    "Monitor risk factors closely"
                ],
                "decision_points": [
                    "Approve budget allocation",
                    "Review in Q2"
                ]
            }

        async def post(self, shared, prep_res, exec_res):
            shared["executive_summary"] = exec_res
            return "visual_insights"

    class VisualInsightsNode(AsyncNode):
        """Prepares data for visualization."""

        def __init__(self):
            super().__init__(node_id="visual_insights")

        async def prep(self, shared):
            return shared.get("executive_summary", {})

        async def exec(self, summary_data):
            # Prepare visualization data
            return {
                "charts": [
                    {
                        "type": "pie",
                        "title": "Risk Distribution",
                        "data": {"low": 30, "medium": 50, "high": 20}
                    },
                    {
                        "type": "bar",
                        "title": "Opportunity Analysis",
                        "data": {"Q1": 85, "Q2": 92, "Q3": 78, "Q4": 88}
                    }
                ],
                "kpis": summary_data.get("key_metrics", {}),
                "trends": ["Increasing compliance", "Decreasing risk"]
            }

        async def post(self, shared, prep_res, exec_res):
            shared["visual_insights"] = exec_res
            return "executive_report"

    # Create executive reporting nodes
    ingestion = DocumentIngestionNode()
    content_analysis = ContentAnalysisNode()
    executive_summary = ExecutiveSummaryNode()
    visual_insights = VisualInsightsNode()
    report_generation = ReportGenerationNode()

    # Connect executive workflow (streamlined)
    ingestion >> content_analysis
    content_analysis >> executive_summary
    executive_summary >> visual_insights
    visual_insights >> report_generation

    logger.info("Executive reporting workflow created")
    return Graph(start=ingestion)


def get_available_workflows():
    """
    Returns a dictionary of all available workflows.

    Returns:
        Dict[str, callable]: Dictionary of workflow creation functions
    """
    return {
        "document_analysis": create_document_analysis_workflow,
        "batch_processing": create_batch_document_workflow,
        "compliance_assessment": create_compliance_assessment_workflow,
        "executive_reporting": create_executive_reporting_workflow
    }


def create_workflow(workflow_name: str):
    """
    Creates a specific workflow by name.

    Args:
        workflow_name (str): Name of the workflow to create

    Returns:
        Graph: The requested workflow graph

    Raises:
        ValueError: If workflow_name is not recognized
    """
    workflows = get_available_workflows()

    if workflow_name not in workflows:
        available = ", ".join(workflows.keys())
        raise ValueError(f"Unknown workflow: {workflow_name}. Available: {available}")

    return workflows[workflow_name]()


if __name__ == "__main__":
    """Demo the workflow creation."""
    import asyncio

    # Setup logging
    logging.basicConfig(level=logging.INFO)

    # Test all workflows
    print("Testing Document Analysis Workflows...")

    for name, creator in get_available_workflows().items():
        print(f"\nCreating {name} workflow...")
        workflow = creator()
        print(f"✅ {name} workflow created successfully")

    print("\n✅ All workflows created successfully!")