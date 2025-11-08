"""
Prompt chaining nodes implementing sequential processing patterns.
Each node represents a stage in a multi-step chain.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import ValidationError
from kaygraph import Node
from utils import call_llm
from models import (
    # Event models
    EventExtraction, EventDetails, EventConfirmation,
    # Document models
    DocumentExtraction, DocumentSummary, DocumentOutput,
    # Analysis models
    InitialAnalysis, CategoryAnalysis, AnalysisScore, AnalysisReport,
    # Translation models
    LanguageDetection, Translation, TranslationVerification, PolishedTranslation,
    # Research models
    ResearchQuery, ResearchFindings, ResearchSynthesis, ResearchCitation
)


# ============== Event Extraction Chain ==============

class EventExtractionNode(Node):
    """
    First stage: Determine if input is a calendar event.
    Implements gate check pattern.
    """
    
    def __init__(self, confidence_threshold: float = 0.7, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user input."""
        user_input = shared.get("user_input", "")
        if not user_input:
            raise ValueError("No user input provided")
        return user_input
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Extract event information with confidence scoring."""
        today = datetime.now()
        date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."
        
        prompt = f"""Analyze if this text describes a calendar event:
"{prep_res}"

Return JSON with:
- description: the raw text
- is_calendar_event: true/false
- confidence_score: 0.0 to 1.0
- event_type: meeting/appointment/reminder/other (if applicable)

{date_context}"""
        
        response = call_llm(
            prompt,
            system="You are an event detection assistant. Analyze text for calendar events."
        )
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            extraction = EventExtraction(**data)
            
            return {
                "extraction": extraction,
                "gate_passed": extraction.is_calendar_event and extraction.confidence_score >= self.confidence_threshold
            }
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Extraction failed: {e}")
            return {
                "extraction": None,
                "gate_passed": False,
                "error": str(e)
            }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store extraction and route based on gate check."""
        shared["event_extraction"] = exec_res.get("extraction")
        shared["gate_passed"] = exec_res.get("gate_passed", False)
        
        if exec_res.get("gate_passed"):
            self.logger.info("Gate check passed - proceeding to parse details")
            return "parse_details"
        else:
            self.logger.info("Gate check failed - not a calendar event")
            return "not_calendar"


class EventDetailsNode(Node):
    """
    Second stage: Parse specific event details.
    Only runs if gate check passes.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get event description."""
        extraction = shared.get("event_extraction")
        if not extraction:
            raise ValueError("No event extraction found")
        return extraction.description
    
    def exec(self, prep_res: str) -> EventDetails:
        """Parse detailed event information."""
        today = datetime.now()
        date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."
        
        prompt = f"""Extract event details from this text:
"{prep_res}"

{date_context}
When dates reference 'tomorrow', 'next Tuesday', etc., calculate the actual date.

Return JSON with:
- name: event name/title
- date: ISO 8601 format (YYYY-MM-DDTHH:MM:SS)
- duration_minutes: estimated duration (15-480)
- participants: list of participant names
- location: location if mentioned (optional)"""
        
        response = call_llm(
            prompt,
            system="You are an event parser. Extract structured event details."
        )
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return EventDetails(**data)
        except (json.JSONDecodeError, ValidationError) as e:
            self.logger.error(f"Details parsing failed: {e}")
            # Return minimal valid details
            return EventDetails(
                name="Event",
                date=datetime.now().isoformat(),
                duration_minutes=60,
                participants=["Unknown"]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: EventDetails) -> Optional[str]:
        """Store parsed details."""
        shared["event_details"] = exec_res
        self.logger.info(f"Parsed event: {exec_res.name} on {exec_res.date}")
        return None  # Continue to next node


class EventConfirmationNode(Node):
    """
    Third stage: Generate confirmation message.
    Final stage of event chain.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> EventDetails:
        """Get event details."""
        details = shared.get("event_details")
        if not details:
            raise ValueError("No event details found")
        return details
    
    def exec(self, prep_res: EventDetails) -> EventConfirmation:
        """Generate natural confirmation message."""
        prompt = f"""Generate a friendly confirmation for this event:
- Name: {prep_res.name}
- Date/Time: {prep_res.date}
- Duration: {prep_res.duration_minutes} minutes
- Participants: {', '.join(prep_res.participants)}
- Location: {prep_res.location or 'Not specified'}

Create:
1. A natural confirmation message (2-3 sentences)
2. A brief summary (1 sentence)
3. Optional calendar link placeholder

Sign off as "Susie"."""
        
        response = call_llm(
            prompt,
            system="You are a friendly assistant generating event confirmations."
        )
        
        # Parse response into structured format
        lines = response.strip().split('\n')
        confirmation_msg = lines[0] if lines else "Event confirmed."
        summary = lines[1] if len(lines) > 1 else "Event scheduled."
        
        return EventConfirmation(
            confirmation_message=confirmation_msg,
            summary=summary,
            calendar_link=None  # Could generate actual link here
        )
    
    def post(self, shared: Dict[str, Any], prep_res: EventDetails, exec_res: EventConfirmation) -> Optional[str]:
        """Store confirmation."""
        shared["event_confirmation"] = exec_res
        shared["chain_complete"] = True
        self.logger.info("Event chain completed successfully")
        return None


# ============== Document Processing Chain ==============

class DocumentExtractionNode(Node):
    """Extract key information from document."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get document text."""
        return shared.get("document_text", "")
    
    def exec(self, prep_res: str) -> DocumentExtraction:
        """Extract document metadata and topics."""
        prompt = f"""Analyze this document and extract:
- title (if present)
- author (if identifiable) 
- content_type (article/report/email/memo/other)
- main_topics (list of 3-5 topics)
- word_count (approximate)

Document:
{prep_res[:1000]}...

Return as JSON."""
        
        response = call_llm(prompt)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return DocumentExtraction(**data)
        except:
            # Fallback
            return DocumentExtraction(
                content_type="document",
                main_topics=["general"],
                word_count=len(prep_res.split())
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: DocumentExtraction) -> Optional[str]:
        """Store extraction."""
        shared["document_extraction"] = exec_res
        return None


class DocumentSummaryNode(Node):
    """Summarize document based on extraction."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get document text and extraction."""
        return {
            "text": shared.get("document_text", ""),
            "extraction": shared.get("document_extraction")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> DocumentSummary:
        """Generate document summary."""
        extraction = prep_res["extraction"]
        text = prep_res["text"]
        
        prompt = f"""Summarize this {extraction.content_type} about {', '.join(extraction.main_topics)}:

{text[:2000]}...

Provide:
- executive_summary (2-3 sentences)
- key_points (list of 3-5 points)
- recommendations (if applicable)
- sentiment (positive/negative/neutral)

Return as JSON."""
        
        response = call_llm(prompt)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return DocumentSummary(**data)
        except:
            return DocumentSummary(
                executive_summary="Document summarized.",
                key_points=["Key information extracted"],
                sentiment="neutral"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: DocumentSummary) -> Optional[str]:
        """Store summary."""
        shared["document_summary"] = exec_res
        return None


# ============== Analysis Chain ==============

class InitialAnalysisNode(Node):
    """Perform initial data analysis."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get data to analyze."""
        return shared.get("analysis_data", "")
    
    def exec(self, prep_res: str) -> InitialAnalysis:
        """Initial quality and completeness check."""
        prompt = f"""Analyze this data:
{prep_res[:1000]}...

Assess:
- data_quality (high/medium/low)
- completeness (0.0-1.0)
- key_metrics (dict of metric:value)
- issues_found (list of any issues)

Return as JSON."""
        
        response = call_llm(prompt)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return InitialAnalysis(**data)
        except:
            return InitialAnalysis(
                data_quality="medium",
                completeness=0.5,
                key_metrics={},
                issues_found=[]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: InitialAnalysis) -> Optional[str]:
        """Store initial analysis."""
        shared["initial_analysis"] = exec_res
        
        # Gate check - only continue if data quality is sufficient
        if exec_res.completeness < 0.3:
            self.logger.warning("Data too incomplete for analysis")
            return "incomplete_data"
        
        return None  # Continue chain


class CategoryAnalysisNode(Node):
    """Categorize and classify analyzed data."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get data and initial analysis."""
        return {
            "data": shared.get("analysis_data", ""),
            "initial": shared.get("initial_analysis")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> CategoryAnalysis:
        """Categorize the data."""
        initial = prep_res["initial"]
        
        prompt = f"""Based on initial analysis showing {initial.data_quality} quality and {initial.completeness:.1%} completeness:

Categorize this data:
{prep_res['data'][:500]}...

Provide:
- primary_category
- secondary_categories (list)
- confidence_scores (dict of category:score)
- reasoning (brief explanation)

Return as JSON."""
        
        response = call_llm(prompt)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return CategoryAnalysis(**data)
        except:
            return CategoryAnalysis(
                primary_category="general",
                secondary_categories=[],
                confidence_scores={"general": 0.5},
                reasoning="Default categorization"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: CategoryAnalysis) -> Optional[str]:
        """Store categorization."""
        shared["category_analysis"] = exec_res
        return None


# ============== Exit Nodes ==============

class NotCalendarEventNode(Node):
    """Handle non-calendar event inputs."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get original input."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> str:
        """Generate appropriate response."""
        return "This doesn't appear to be a calendar event request. Please provide event details like date, time, and participants."
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        """Store response."""
        shared["response"] = exec_res
        shared["chain_complete"] = False
        return None


class IncompleteDataNode(Node):
    """Handle incomplete data in analysis chain."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> InitialAnalysis:
        """Get initial analysis."""
        return shared.get("initial_analysis")
    
    def exec(self, prep_res: InitialAnalysis) -> str:
        """Generate incomplete data message."""
        return f"Data is {prep_res.completeness:.0%} complete. Issues found: {', '.join(prep_res.issues_found)}"
    
    def post(self, shared: Dict[str, Any], prep_res: InitialAnalysis, exec_res: str) -> Optional[str]:
        """Store message."""
        shared["error_message"] = exec_res
        shared["chain_complete"] = False
        return None