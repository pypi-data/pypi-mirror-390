"""
Document Analysis Node implementations.

This module contains all the node implementations for the document analysis
system, following KayGraph patterns and production best practices.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum

from kaygraph import ValidatedNode, AsyncNode, MetricsNode, BatchNode
from ..utils.claude_api import ClaudeAPIClient, ClaudeConfig, structured_claude_call
from ..utils.embeddings import EmbeddingService, create_embedding_service
from ..utils.vector_store import VectorStore, Document, SimpleVectorStore


class DocumentType(Enum):
    """Supported document types."""
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    HTML = "html"
    JSON = "json"
    CSV = "csv"
    EMAIL = "email"
    CONTRACT = "contract"
    REPORT = "report"
    FINANCIAL = "financial"
    LEGAL = "legal"


class DocumentStatus(Enum):
    """Document processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REVIEW_REQUIRED = "review_required"


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""
    id: str
    filename: str
    file_type: DocumentType
    file_size: int
    created_at: str
    processed_at: Optional[str] = None
    author: Optional[str] = None
    department: Optional[str] = None
    classification: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    checksum: Optional[str] = None
    language: Optional[str] = None
    page_count: Optional[int] = None


@dataclass
class DocumentContent:
    """Extracted content from documents."""
    text: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    tables: List[Dict[str, Any]] = field(default_factory=list)
    images: List[Dict[str, Any]] = field(default_factory=list)
    links: List[str] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class AnalysisResult:
    """Results from document analysis."""
    document_id: str
    summary: str
    key_insights: List[str]
    entities: List[Dict[str, Any]]
    topics: List[str]
    sentiment: Optional[str] = None
    complexity_score: float = 0.0
    reading_time: int = 0
    action_items: List[str] = field(default_factory=list)


class DocumentIngestionNode(ValidatedNode):
    """
    Ingests and validates documents for processing.

    This node handles the initial document intake, validation,
    and preparation for the analysis pipeline.
    """

    def __init__(self, supported_formats: List[str] = None):
        super().__init__(
            max_retries=3,
            wait=1,
            node_id="document_ingestion"
        )
        self.supported_formats = supported_formats or ["pdf", "docx", "txt", "html", "json"]
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def validate_input(self, document_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate incoming document data."""
        required_fields = ["id", "filename", "content", "file_type"]
        for field in required_fields:
            if not document_data.get(field):
                raise ValueError(f"Missing required field: {field}")

        # Validate file type
        if document_data["file_type"] not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {document_data['file_type']}")

        # Validate content size
        content_length = len(document_data["content"])
        if content_length == 0:
            raise ValueError("Document content cannot be empty")
        if content_length > 10_000_000:  # 10MB limit
            raise ValueError("Document content too large")

        # Generate checksum
        content_hash = hashlib.md5(document_data["content"].encode()).hexdigest()
        document_data["checksum"] = content_hash

        # Add processing timestamp
        document_data["ingested_at"] = time.time()

        return document_data

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Extract document data from shared context."""
        return shared.get("incoming_document", {})

    def exec(self, validated_document: Dict[str, Any]) -> Tuple[DocumentMetadata, DocumentContent]:
        """Create structured objects from validated data."""
        # Create metadata
        metadata = DocumentMetadata(
            id=validated_document["id"],
            filename=validated_document["filename"],
            file_type=DocumentType(validated_document["file_type"]),
            file_size=len(validated_document["content"]),
            created_at=validated_document.get("created_at", time.time()),
            author=validated_document.get("author"),
            department=validated_document.get("department"),
            classification=validated_document.get("classification"),
            tags=validated_document.get("tags", []),
            checksum=validated_document["checksum"],
            language=validated_document.get("language"),
            page_count=validated_document.get("page_count")
        )

        # Create content object
        content = DocumentContent(
            text=validated_document["content"],
            structured_data=validated_document.get("structured_data", {}),
            tables=validated_document.get("tables", []),
            images=validated_document.get("images", []),
            links=validated_document.get("links", [])
        )

        return metadata, content

    def validate_output(self, result: Tuple[DocumentMetadata, DocumentContent]) -> Tuple[DocumentMetadata, DocumentContent]:
        """Validate created objects."""
        metadata, content = result
        if not metadata.id or not content.text:
            raise ValueError("Invalid document objects created")
        return result

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Tuple[DocumentMetadata, DocumentContent]) -> str:
        """Store validated document objects."""
        metadata, content = exec_res
        shared["document_metadata"] = metadata
        shared["document_content"] = content
        shared["processing_stage"] = "ingestion_complete"
        self.logger.info(f"Document {metadata.id} ingested successfully ({len(content.text)} characters)")
        return "preprocessing"


class DocumentPreprocessingNode(AsyncNode):
    """
    Preprocesses document content for analysis.

    This node cleans and normalizes text content, extracts structured
    information, and prepares the document for AI analysis.
    """

    def __init__(self):
        super().__init__(node_id="document_preprocessing")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Tuple[DocumentMetadata, DocumentContent]:
        """Extract document objects for preprocessing."""
        metadata = shared.get("document_metadata")
        content = shared.get("document_content")
        if not metadata or not content:
            raise ValueError("Document metadata and content required")
        return metadata, content

    async def exec(self, document_objects: Tuple[DocumentMetadata, DocumentContent]) -> Dict[str, Any]:
        """Preprocess document content."""
        metadata, content = document_objects

        # Clean and normalize text
        cleaned_text = self._clean_text(content.text)

        # Extract basic entities
        entities = await self._extract_entities(cleaned_text)

        # Detect language
        language = self._detect_language(cleaned_text)

        # Calculate reading time
        reading_time = self._calculate_reading_time(cleaned_text)

        # Extract sections (if document structure allows)
        sections = self._extract_sections(cleaned_text, metadata.file_type)

        return {
            "cleaned_text": cleaned_text,
            "entities": entities,
            "language": language,
            "reading_time": reading_time,
            "sections": sections,
            "word_count": len(cleaned_text.split()),
            "character_count": len(cleaned_text)
        }

    async def post(self, shared: Dict[str, Any], prep_res: Tuple[DocumentMetadata, DocumentContent], exec_res: Dict[str, Any]) -> str:
        """Store preprocessing results."""
        shared["preprocessing_results"] = exec_res

        # Update content with cleaned text
        content = shared["document_content"]
        content.text = exec_res["cleaned_text"]
        content.entities = exec_res["entities"]

        # Update metadata
        metadata = shared["document_metadata"]
        metadata.language = exec_res["language"]
        metadata.processed_at = time.time()

        self.logger.info(f"Document {metadata.id} preprocessed ({exec_res['word_count']} words)")
        return "content_analysis"

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        import re

        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)

        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\"\'\/\\]', '', text)

        # Normalize line breaks
        text = re.sub(r'\n+', '\n', text)

        return text.strip()

    async def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract basic entities from text."""
        # Simple entity extraction (in production, use NER models)
        import re

        entities = []

        # Extract emails
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)
        for email in emails:
            entities.append({"type": "email", "value": email, "confidence": 0.9})

        # Extract phone numbers
        phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)
        for phone in phones:
            entities.append({"type": "phone", "value": phone, "confidence": 0.8})

        # Extract dates
        dates = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b', text)
        for date in dates:
            entities.append({"type": "date", "value": date, "confidence": 0.7})

        # Extract monetary values
        money = re.findall(r'\$\d+(?:,\d{3})*(?:\.\d{2})?', text)
        for amount in money:
            entities.append({"type": "money", "value": amount, "confidence": 0.9})

        return entities

    def _detect_language(self, text: str) -> str:
        """Detect document language."""
        # Simple language detection based on common words
        # In production, use proper language detection libraries

        common_words = {
            "en": ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"],
            "es": ["el", "la", "y", "o", "pero", "en", "de", "para", "con", "por"],
            "fr": ["le", "la", "et", "ou", "mais", "dans", "de", "pour", "avec", "par"],
            "de": ["der", "die", "das", "und", "oder", "aber", "in", "zu", "für", "mit", "von"]
        }

        text_lower = text.lower()[:1000]  # Sample first 1000 chars
        language_scores = {}

        for lang, words in common_words.items():
            score = sum(1 for word in words if word in text_lower)
            language_scores[lang] = score

        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            return detected_lang if language_scores[detected_lang] > 2 else "unknown"

        return "unknown"

    def _calculate_reading_time(self, text: str) -> int:
        """Calculate estimated reading time in minutes."""
        word_count = len(text.split())
        # Average reading speed: 200-250 words per minute
        reading_time = max(1, round(word_count / 220))
        return reading_time

    def _extract_sections(self, text: str, file_type: DocumentType) -> List[Dict[str, Any]]:
        """Extract document sections."""
        sections = []

        if file_type in [DocumentType.PDF, DocumentType.DOCX, DocumentType.REPORT]:
            # Simple section extraction based on headings
            import re

            # Look for markdown-style headings
            heading_pattern = r'^(#{1,6})\s+(.+)$'
            headings = re.findall(heading_pattern, text, re.MULTILINE)

            for level, title in headings:
                sections.append({
                    "level": len(level),
                    "title": title.strip(),
                    "type": "heading"
                })

        return sections


class ContentAnalysisNode(AsyncNode):
    """
    Analyzes document content using Claude AI.

    This node uses Claude to perform deep content analysis,
    including topic identification, sentiment analysis, and
    complexity assessment.
    """

    def __init__(self):
        super().__init__(node_id="content_analysis")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for Claude analysis."""
        metadata = shared.get("document_metadata")
        content = shared.get("document_content")
        preprocessing = shared.get("preprocessing_results", {})

        if not metadata or not content:
            raise ValueError("Document metadata and content required")

        # Prepare text for analysis (limit to avoid token limits)
        text_to_analyze = content.text[:8000]  # Limit to ~2000 tokens

        return {
            "document_id": metadata.id,
            "filename": metadata.filename,
            "file_type": metadata.file_type.value,
            "content": text_to_analyze,
            "language": preprocessing.get("language", "unknown"),
            "word_count": preprocessing.get("word_count", 0)
        }

    async def exec(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Claude to analyze document content."""
        prompt = f"""
Analyze this document content comprehensively:

Document Info:
- ID: {analysis_data['document_id']}
- Filename: {analysis_data['filename']}
- Type: {analysis_data['file_type']}
- Language: {analysis_data['language']}
- Word Count: {analysis_data['word_count']}

Content:
{analysis_data['content']}

Please provide:
1. Overall summary (2-3 sentences)
2. Key topics/themes (max 5)
3. Main entities mentioned (people, organizations, locations)
4. Document purpose/type (report, contract, analysis, etc.)
5. Sentiment/tone (positive, negative, neutral, formal, informal)
6. Complexity level (simple, moderate, complex, very complex)
7. Target audience
8. Key insights or important information
9. Action items or next steps mentioned
10. Confidence level in analysis (0-1)

Respond in JSON format:
{{
    "summary": "brief_summary",
    "topics": ["topic1", "topic2", "topic3"],
    "entities": [
        {{"type": "person", "name": "John Doe", "role": "CEO"}},
        {{"type": "organization", "name": "Acme Corp"}}
    ],
    "document_type": "report/contract/analysis/etc",
    "sentiment": "positive/negative/neutral",
    "tone": "formal/informal/technical",
    "complexity": "simple/moderate/complex/very_complex",
    "target_audience": "executives/technical_staff/general_public",
    "key_insights": ["insight1", "insight2", "insight3"],
    "action_items": ["action1", "action2"],
    "confidence_score": 0.0
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "topics": {"type": "array", "items": {"type": "string"}},
                "entities": {"type": "array", "items": {"type": "object"}},
                "document_type": {"type": "string"},
                "sentiment": {"type": "string"},
                "tone": {"type": "string"},
                "complexity": {"type": "string"},
                "target_audience": {"type": "string"},
                "key_insights": {"type": "array", "items": {"type": "string"}},
                "action_items": {"type": "array", "items": {"type": "string"}},
                "confidence_score": {"type": "number"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store analysis results."""
        shared["content_analysis"] = exec_res

        # Update metadata with analysis results
        metadata = shared["document_metadata"]
        metadata.classification = exec_res.get("document_type")
        metadata.tags.extend(exec_res.get("topics", []))

        # Remove duplicates from tags
        metadata.tags = list(set(metadata.tags))

        self.logger.info(f"Content analysis completed for {metadata.id}")
        self.logger.info(f"Document type: {exec_res.get('document_type')}, Topics: {exec_res.get('topics', [])}")

        return "summarization"


class DocumentSummarizationNode(AsyncNode):
    """
    Generates comprehensive document summaries.

    This node creates different types of summaries for different
    use cases (executive, technical, detailed).
    """

    def __init__(self):
        super().__init__(node_id="document_summarization")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for summarization."""
        metadata = shared.get("document_metadata")
        content = shared.get("document_content")
        analysis = shared.get("content_analysis", {})

        return {
            "document_id": metadata.id,
            "content": content.text,
            "document_type": analysis.get("document_type", "unknown"),
            "complexity": analysis.get("complexity", "moderate"),
            "target_audience": analysis.get("target_audience", "general")
        }

    async def exec(self, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate multiple summary types using Claude."""
        prompt = f"""
Generate comprehensive summaries for this document:

Document ID: {summary_data['document_id']}
Type: {summary_data['document_type']}
Complexity: {summary_data['complexity']}
Target Audience: {summary_data['target_audience']}

Content:
{summary_data['content']}

Please create four different summaries:

1. Executive Summary (1-2 paragraphs, high-level overview for leadership)
2. Technical Summary (detailed technical information for specialists)
3. Action Summary (focus on decisions, action items, and next steps)
4. Abstract Summary (concise academic-style summary)

For each summary, include:
- Main purpose and scope
- Key findings or conclusions
- Important recommendations or actions
- Target audience appropriateness

Respond in JSON format:
{{
    "executive_summary": {{
        "content": "executive_summary_text",
        "word_count": 150,
        "target_audience": "leadership"
    }},
    "technical_summary": {{
        "content": "technical_summary_text",
        "word_count": 300,
        "target_audience": "technical_staff"
    }},
    "action_summary": {{
        "content": "action_summary_text",
        "word_count": 200,
        "target_audience": "project_managers",
        "action_items": ["item1", "item2", "item3"]
    }},
    "abstract_summary": {{
        "content": "abstract_summary_text",
        "word_count": 250,
        "target_audience": "researchers"
    }}
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "executive_summary": {"type": "object"},
                "technical_summary": {"type": "object"},
                "action_summary": {"type": "object"},
                "abstract_summary": {"type": "object"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store summarization results."""
        shared["document_summaries"] = exec_res
        self.logger.info(f"Generated 4 summary types for document {prep_res['document_id']}")
        return "insight_extraction"


class InsightExtractionNode(AsyncNode):
    """
    Extracts deep insights and patterns from documents.

    This node identifies non-obvious insights, trends, and
    relationships within the document content.
    """

    def __init__(self):
        super().__init__(node_id="insight_extraction")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for insight extraction."""
        metadata = shared.get("document_metadata")
        content = shared.get("document_content")
        analysis = shared.get("content_analysis", {})

        return {
            "document_id": metadata.id,
            "content": content.text,
            "document_type": analysis.get("document_type"),
            "topics": analysis.get("topics", []),
            "entities": analysis.get("entities", [])
        }

    async def exec(self, insight_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract insights using Claude."""
        prompt = f"""
Extract deep insights and patterns from this document:

Document ID: {insight_data['document_id']}
Type: {insight_data['document_type']}
Topics: {insight_data['topics']}
Entities: {insight_data['entities']}

Content:
{insight_data['content']}

Please identify and extract:

1. **Key Insights** - Non-obvious conclusions or patterns
2. **Risk Factors** - Potential risks, issues, or concerns identified
3. **Opportunities** - Business opportunities, improvements, or advantages
4. **Trends** - Emerging trends or patterns mentioned
5. **Relationships** - Connections between different entities or concepts
6. **Contradictions** - Inconsistencies or conflicting information
7. **Assumptions** - Underlying assumptions made in the document
8. **Data Gaps** - Missing information or areas needing more data
9. **Recommendations** - Strategic recommendations based on content
10. **Confidence Level** - How confident you are in these insights (0-1)

For each insight, provide:
- The insight statement
- Supporting evidence from the text
- Potential impact or importance
- Confidence level

Respond in JSON format:
{{
    "key_insights": [
        {{
            "insight": "insight_statement",
            "evidence": "supporting_text_quote",
            "importance": "high/medium/low",
            "confidence": 0.0
        }}
    ],
    "risk_factors": [
        {{
            "risk": "risk_description",
            "mitigation": "mitigation_strategy",
            "probability": "high/medium/low",
            "impact": "high/medium/low"
        }}
    ],
    "opportunities": [
        {{
            "opportunity": "opportunity_description",
            "potential_value": "high/medium/low",
            "requirements": ["requirement1", "requirement2"]
        }}
    ],
    "trends": ["trend1", "trend2", "trend3"],
    "relationships": [
        {{
            "entity1": "entity1",
            "entity2": "entity2",
            "relationship": "relationship_description",
            "strength": "strong/moderate/weak"
        }}
    ],
    "contradictions": [
        {{
            "contradiction": "description",
            "conflicting_statements": ["statement1", "statement2"]
        }}
    ],
    "assumptions": ["assumption1", "assumption2"],
    "data_gaps": ["gap1", "gap2"],
    "recommendations": [
        {{
            "recommendation": "recommendation_text",
            "priority": "high/medium/low",
            "timeline": "immediate/short_term/long_term"
        }}
    ],
    "overall_confidence": 0.0
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "key_insights": {"type": "array", "items": {"type": "object"}},
                "risk_factors": {"type": "array", "items": {"type": "object"}},
                "opportunities": {"type": "array", "items": {"type": "object"}},
                "trends": {"type": "array", "items": {"type": "string"}},
                "relationships": {"type": "array", "items": {"type": "object"}},
                "contradictions": {"type": "array", "items": {"type": "object"}},
                "assumptions": {"type": "array", "items": {"type": "string"}},
                "data_gaps": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "object"}},
                "overall_confidence": {"type": "number"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store insight extraction results."""
        shared["extracted_insights"] = exec_res

        insight_count = (
            len(exec_res.get("key_insights", [])) +
            len(exec_res.get("risk_factors", [])) +
            len(exec_res.get("opportunities", [])) +
            len(exec_res.get("recommendations", []))
        )

        self.logger.info(f"Extracted {insight_count} insights from document {prep_res['document_id']}")
        return "cross_document_analysis"


class ComplianceCheckNode(AsyncNode):
    """
    Performs compliance and regulatory checks on documents.

    This node analyzes documents for compliance requirements,
    regulatory issues, and policy adherence.
    """

    def __init__(self):
        super().__init__(node_id="compliance_check")
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare content for compliance checking."""
        metadata = shared.get("document_metadata")
        content = shared.get("document_content")
        analysis = shared.get("content_analysis", {})

        return {
            "document_id": metadata.id,
            "document_type": metadata.file_type.value,
            "department": metadata.department,
            "classification": metadata.classification,
            "content": content.text,
            "entities": content.entities,
            "topics": analysis.get("topics", [])
        }

    async def exec(self, compliance_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform compliance analysis using Claude."""
        prompt = f"""
Perform comprehensive compliance analysis on this document:

Document Info:
- ID: {compliance_data['document_id']}
- Type: {compliance_data['document_type']}
- Department: {compliance_data['department']}
- Classification: {compliance_data['classification']}

Content:
{compliance_data['content']}

Please check for:

1. **Data Privacy Compliance** - GDPR, CCPA, HIPAA, etc.
2. **Financial Regulations** - SOX, PCI DSS, etc.
3. **Industry Standards** - ISO, NIST, etc.
4. **Internal Policies** - Company policies and procedures
5. **Legal Requirements** - Contracts, liabilities, obligations
6. **Security Standards** - Information security requirements
7. **Accessibility Compliance** - WCAG, ADA, etc.
8. **Retention Requirements** - Document retention policies
9. **Classification Compliance** - Proper classification handling
10. **Risk Assessment** - Compliance risk level

For each compliance area, identify:
- Compliance status (compliant/partial/non-compliant)
- Specific issues or concerns
- Required actions or remediation
- Risk level (low/medium/high/critical)

Respond in JSON format:
{{
    "overall_compliance_score": 0.0,
    "compliance_areas": [
        {{
            "area": "data_privacy",
            "status": "compliant/partial/non_compliant",
            "issues": ["issue1", "issue2"],
            "required_actions": ["action1", "action2"],
            "risk_level": "low/medium/high/critical"
        }}
    ],
    "violations": [
        {{
            "type": "violation_type",
            "description": "violation_description",
            "severity": "low/medium/high/critical",
            "remediation": "remediation_steps"
        }}
    ],
    "recommendations": [
        {{
            "recommendation": "recommendation_text",
            "priority": "high/medium/low",
            "deadline": "immediate/30_days/90_days"
        }}
    ],
    "approval_required": true/false,
    "reviewer_type": "legal_compliance/security/management"
}}
"""

        schema = {
            "type": "object",
            "properties": {
                "overall_compliance_score": {"type": "number"},
                "compliance_areas": {"type": "array", "items": {"type": "object"}},
                "violations": {"type": "array", "items": {"type": "object"}},
                "recommendations": {"type": "array", "items": {"type": "object"}},
                "approval_required": {"type": "boolean"},
                "reviewer_type": {"type": "string"}
            }
        }

        return await structured_claude_call(prompt, schema)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store compliance check results."""
        shared["compliance_results"] = exec_res

        compliance_score = exec_res.get("overall_compliance_score", 0.0)
        violations_count = len(exec_res.get("violations", []))

        self.logger.info(f"Compliance check completed: score={compliance_score:.2f}, violations={violations_count}")

        # Route based on compliance results
        if exec_res.get("approval_required", False):
            return "manual_review"
        elif compliance_score < 0.7:
            return "risk_assessment"
        else:
            return "knowledge_graph"


class ReportGenerationNode(MetricsNode):
    """
    Generates comprehensive analysis reports.

    This node creates detailed reports combining all analysis results
    into a cohesive format for stakeholders.
    """

    def __init__(self):
        super().__init__(
            node_id="report_generation",
            metrics_collector_name="document_analysis_metrics"
        )
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Collect all analysis results for report generation."""
        return {
            "document_metadata": shared.get("document_metadata"),
            "preprocessing": shared.get("preprocessing_results", {}),
            "content_analysis": shared.get("content_analysis", {}),
            "summaries": shared.get("document_summaries", {}),
            "insights": shared.get("extracted_insights", {}),
            "compliance": shared.get("compliance_results", {}),
            "processing_time": time.time() - shared.get("start_time", time.time())
        }

    def exec(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive report."""
        metadata = report_data["document_metadata"]

        # Create report structure
        report = {
            "report_id": f"report_{metadata.id}_{int(time.time())}",
            "document_info": {
                "id": metadata.id,
                "filename": metadata.filename,
                "type": metadata.file_type.value,
                "size": metadata.file_size,
                "created_at": metadata.created_at,
                "processed_at": metadata.processed_at
            },
            "executive_summary": report_data["summaries"].get("executive_summary", {}).get("content", ""),
            "content_analysis": {
                "summary": report_data["content_analysis"].get("summary", ""),
                "topics": report_data["content_analysis"].get("topics", []),
                "entities": report_data["content_analysis"].get("entities", []),
                "sentiment": report_data["content_analysis"].get("sentiment", ""),
                "complexity": report_data["content_analysis"].get("complexity", "")
            },
            "key_insights": report_data["insights"].get("key_insights", []),
            "risk_factors": report_data["insights"].get("risk_factors", []),
            "opportunities": report_data["insights"].get("opportunities", []),
            "recommendations": report_data["insights"].get("recommendations", []),
            "compliance_summary": {
                "score": report_data["compliance"].get("overall_compliance_score", 0.0),
                "violations": len(report_data["compliance"].get("violations", [])),
                "approval_required": report_data["compliance"].get("approval_required", False)
            },
            "processing_metrics": {
                "processing_time": report_data["processing_time"],
                "word_count": report_data["preprocessing"].get("word_count", 0),
                "reading_time": report_data["preprocessing"].get("reading_time", 0)
            },
            "generated_at": time.time()
        }

        return report

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]) -> str:
        """Store generated report."""
        shared["analysis_report"] = exec_res

        # Calculate metrics
        processing_time = prep_res["processing_time"]
        word_count = prep_res["preprocessing"].get("word_count", 0)

        metrics = {
            "document_id": exec_res["document_info"]["id"],
            "processing_time": processing_time,
            "words_per_second": word_count / max(processing_time, 1),
            "insights_count": len(exec_res["key_insights"]),
            "compliance_score": exec_res["compliance_summary"]["score"],
            "report_quality": self._assess_report_quality(exec_res)
        }

        shared["final_metrics"] = metrics

        self.logger.info(f"Report generated for document {exec_res['document_info']['id']}")
        self.logger.info(f"Processing time: {processing_time:.2f}s, Quality score: {metrics['report_quality']:.2f}")

        return "complete"

    def _assess_report_quality(self, report: Dict[str, Any]) -> float:
        """Assess the quality of the generated report."""
        quality_score = 0.0

        # Check for required sections
        required_sections = [
            "executive_summary", "content_analysis", "key_insights",
            "recommendations", "compliance_summary"
        ]

        for section in required_sections:
            if report.get(section):
                if isinstance(report[section], str) and len(report[section]) > 50:
                    quality_score += 0.15
                elif isinstance(report[section], (list, dict)) and report[section]:
                    quality_score += 0.15

        # Check insight quality
        insights = report.get("key_insights", [])
        if insights:
            avg_confidence = sum(insight.get("confidence", 0) for insight in insights) / len(insights)
            quality_score += avg_confidence * 0.1

        # Check compliance
        compliance_score = report.get("compliance_summary", {}).get("score", 0)
        quality_score += compliance_score * 0.1

        return min(1.0, quality_score)