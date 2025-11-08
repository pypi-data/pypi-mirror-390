"""
Routing nodes implementing intelligent request routing patterns.
These nodes demonstrate dynamic routing based on content classification.
"""

import json
import time
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from kaygraph import Node
from utils import call_llm
from models import (
    CalendarRequestType, NewEventDetails, ModifyEventDetails, CalendarResponse,
    TicketPriority, TicketCategory, SupportTicketClassification,
    TechnicalIssueDetails, BillingIssueDetails, SupportTicketResponse,
    DocumentType, DocumentClassification, ProcessingRequest, ProcessingResponse,
    PrimaryRoute, SecondaryRoute, MultiLevelRoutingDecision,
    RouteDecision, RoutingMetrics
)


# ============== Calendar Routing Nodes ==============

class CalendarRouterNode(Node):
    """
    Routes calendar requests to appropriate handlers.
    Classifies the request type with confidence scoring.
    """
    
    def __init__(self, confidence_threshold: float = 0.7, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.confidence_threshold = confidence_threshold
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get user input for routing."""
        return shared.get("user_input", "")
    
    def exec(self, prep_res: str) -> CalendarRequestType:
        """Classify the calendar request."""
        system = """You are a calendar request classifier. Analyze the user input and determine:
1. The type of calendar request (new_event, modify_event, query_event, delete_event, or other)
2. Your confidence in this classification (0-1)
3. A cleaned description of the request

Return as JSON with fields: request_type, confidence_score, description"""
        
        prompt = f"Classify this calendar request: {prep_res}"
        
        response = call_llm(prompt, system=system)
        
        try:
            # Parse LLM response
            data = json.loads(response.strip().strip("```json").strip("```"))
            
            return CalendarRequestType(
                request_type=data.get("request_type", "other"),
                confidence_score=float(data.get("confidence_score", 0.5)),
                description=data.get("description", prep_res),
                original_input=prep_res
            )
        except Exception as e:
            self.logger.error(f"Failed to parse classification: {e}")
            return CalendarRequestType(
                request_type="other",
                confidence_score=0.0,
                description=prep_res,
                original_input=prep_res
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: CalendarRequestType) -> Optional[str]:
        """Route based on classification and confidence."""
        shared["calendar_classification"] = exec_res
        
        self.logger.info(
            f"Classified as {exec_res.request_type} "
            f"with confidence {exec_res.confidence_score:.2f}"
        )
        
        # Check confidence threshold
        if exec_res.confidence_score < self.confidence_threshold:
            self.logger.warning(f"Low confidence: {exec_res.confidence_score}")
            return "low_confidence"
        
        # Route to appropriate handler
        return exec_res.request_type


class NewEventHandlerNode(Node):
    """Handles new calendar event creation."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get event description."""
        classification = shared.get("calendar_classification", {})
        return classification.description
    
    def exec(self, prep_res: str) -> NewEventDetails:
        """Extract new event details."""
        system = """Extract calendar event details from the description.
Return as JSON with fields:
- name: Event name
- date: Date and time (human readable)
- duration_minutes: Duration in minutes (default 60)
- participants: List of participant names
- location: Location (optional)
- description: Event description (optional)"""
        
        prompt = f"Extract event details from: {prep_res}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return NewEventDetails(**data)
        except Exception as e:
            self.logger.error(f"Failed to extract event details: {e}")
            # Return minimal valid event
            return NewEventDetails(
                name="New Event",
                date="TBD",
                duration_minutes=60,
                participants=[]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: NewEventDetails) -> Optional[str]:
        """Create calendar response."""
        response = CalendarResponse(
            success=True,
            message=f"Created new event '{exec_res.name}' on {exec_res.date}",
            action_taken="new_event_created",
            calendar_link=f"calendar://new?event={exec_res.name}",
            event_id=f"evt_{int(time.time())}",
            details=exec_res.dict()
        )
        
        shared["calendar_response"] = response
        self.logger.info(f"Created new event: {exec_res.name}")
        
        return None


class ModifyEventHandlerNode(Node):
    """Handles calendar event modifications."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get modification description."""
        classification = shared.get("calendar_classification", {})
        return classification.description
    
    def exec(self, prep_res: str) -> ModifyEventDetails:
        """Extract modification details."""
        system = """Extract event modification details.
Return as JSON with fields:
- event_identifier: Description to identify the event
- changes: List of changes, each with {field, old_value, new_value}
- participants_to_add: List of new participants
- participants_to_remove: List of participants to remove"""
        
        prompt = f"Extract modification details from: {prep_res}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return ModifyEventDetails(**data)
        except Exception as e:
            self.logger.error(f"Failed to extract modification details: {e}")
            # Return minimal modification
            from models import EventChange
            return ModifyEventDetails(
                event_identifier="Unknown Event",
                changes=[EventChange(field="unknown", new_value="unknown")]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: ModifyEventDetails) -> Optional[str]:
        """Create modification response."""
        changes_summary = ", ".join([c.field for c in exec_res.changes])
        
        response = CalendarResponse(
            success=True,
            message=f"Modified '{exec_res.event_identifier}' - changed: {changes_summary}",
            action_taken="event_modified",
            calendar_link=f"calendar://modify?event={exec_res.event_identifier}",
            details=exec_res.dict()
        )
        
        shared["calendar_response"] = response
        self.logger.info(f"Modified event: {exec_res.event_identifier}")
        
        return None


# ============== Support Ticket Routing Nodes ==============

class SupportTicketRouterNode(Node):
    """
    Routes support tickets to appropriate departments.
    Classifies by category and priority.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get support ticket text."""
        return shared.get("ticket_text", "")
    
    def exec(self, prep_res: str) -> SupportTicketClassification:
        """Classify support ticket."""
        system = """Classify this support ticket.
Categories: technical, billing, feature_request, general, complaint
Priorities: critical, high, medium, low

Return JSON with:
- category: The ticket category
- priority: Priority level
- confidence_score: 0-1
- summary: Brief summary
- keywords: List of relevant keywords
- requires_escalation: true/false"""
        
        prompt = f"Classify this support ticket: {prep_res}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return SupportTicketClassification(**data)
        except Exception as e:
            self.logger.error(f"Failed to classify ticket: {e}")
            return SupportTicketClassification(
                category=TicketCategory.GENERAL,
                priority=TicketPriority.MEDIUM,
                confidence_score=0.5,
                summary="Unable to classify",
                keywords=[]
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: SupportTicketClassification) -> Optional[str]:
        """Route to appropriate handler."""
        shared["ticket_classification"] = exec_res
        
        self.logger.info(
            f"Classified as {exec_res.category} "
            f"with priority {exec_res.priority}"
        )
        
        # Route based on category
        return exec_res.category.value


class TechnicalSupportNode(Node):
    """Handles technical support tickets."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Tuple[str, SupportTicketClassification]:
        """Get ticket details."""
        return (
            shared.get("ticket_text", ""),
            shared.get("ticket_classification")
        )
    
    def exec(self, prep_res: Tuple[str, SupportTicketClassification]) -> TechnicalIssueDetails:
        """Extract technical issue details."""
        ticket_text, classification = prep_res
        
        system = """Extract technical issue details.
Return JSON with:
- error_message: Any error message mentioned
- affected_service: Service or component affected
- steps_to_reproduce: List of steps if mentioned
- environment: System/environment details
- urgency_reason: Why it's urgent (if applicable)"""
        
        prompt = f"Extract technical details from: {ticket_text}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return TechnicalIssueDetails(**data)
        except Exception as e:
            self.logger.error(f"Failed to extract technical details: {e}")
            return TechnicalIssueDetails()
    
    def post(self, shared: Dict[str, Any], prep_res: Tuple, exec_res: TechnicalIssueDetails) -> Optional[str]:
        """Create technical support response."""
        _, classification = prep_res
        
        # Determine response time based on priority
        response_times = {
            TicketPriority.CRITICAL: "1 hour",
            TicketPriority.HIGH: "4 hours",
            TicketPriority.MEDIUM: "24 hours",
            TicketPriority.LOW: "48 hours"
        }
        
        response = SupportTicketResponse(
            ticket_id=f"TECH-{int(time.time())}",
            routed_to="Technical Support Team",
            estimated_response_time=response_times.get(classification.priority, "24 hours"),
            priority=classification.priority,
            initial_response="Your technical issue has been received and assigned to our team.",
            escalated=classification.requires_escalation,
            assigned_agent="TechAgent-01" if classification.priority in [TicketPriority.CRITICAL, TicketPriority.HIGH] else None
        )
        
        shared["ticket_response"] = response
        self.logger.info(f"Routed to technical support: {response.ticket_id}")
        
        return None


class BillingSupportNode(Node):
    """Handles billing support tickets."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Tuple[str, SupportTicketClassification]:
        """Get ticket details."""
        return (
            shared.get("ticket_text", ""),
            shared.get("ticket_classification")
        )
    
    def exec(self, prep_res: Tuple[str, SupportTicketClassification]) -> BillingIssueDetails:
        """Extract billing issue details."""
        ticket_text, classification = prep_res
        
        system = """Extract billing issue details.
Return JSON with:
- account_id: Account ID if mentioned
- amount_disputed: Amount in dispute if mentioned
- billing_period: Billing period affected
- issue_type: overcharge, missing_payment, refund, subscription, or other"""
        
        prompt = f"Extract billing details from: {ticket_text}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            return BillingIssueDetails(**data)
        except Exception as e:
            self.logger.error(f"Failed to extract billing details: {e}")
            return BillingIssueDetails(issue_type="other")
    
    def post(self, shared: Dict[str, Any], prep_res: Tuple, exec_res: BillingIssueDetails) -> Optional[str]:
        """Create billing support response."""
        _, classification = prep_res
        
        response = SupportTicketResponse(
            ticket_id=f"BILL-{int(time.time())}",
            routed_to="Billing Department",
            estimated_response_time="12 hours",
            priority=classification.priority,
            initial_response="Your billing inquiry has been received. Our billing team will review your account.",
            escalated=exec_res.amount_disputed and exec_res.amount_disputed > 500,
            assigned_agent="BillingAgent-01"
        )
        
        shared["ticket_response"] = response
        self.logger.info(f"Routed to billing support: {response.ticket_id}")
        
        return None


# ============== Document Processing Nodes ==============

class DocumentRouterNode(Node):
    """
    Routes documents to appropriate processors.
    Classifies document type and requirements.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get document information."""
        return {
            "file_path": shared.get("file_path", ""),
            "file_name": shared.get("file_name", ""),
            "requested_operations": shared.get("requested_operations", [])
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> DocumentClassification:
        """Classify document for routing."""
        file_name = prep_res["file_name"]
        
        # Extract file extension
        file_extension = ""
        if "." in file_name:
            file_extension = file_name.split(".")[-1].lower()
        
        # Determine document type
        type_mapping = {
            "pdf": DocumentType.PDF,
            "jpg": DocumentType.IMAGE,
            "jpeg": DocumentType.IMAGE,
            "png": DocumentType.IMAGE,
            "txt": DocumentType.TEXT,
            "md": DocumentType.TEXT,
            "xls": DocumentType.SPREADSHEET,
            "xlsx": DocumentType.SPREADSHEET,
            "csv": DocumentType.SPREADSHEET,
            "ppt": DocumentType.PRESENTATION,
            "pptx": DocumentType.PRESENTATION,
            "py": DocumentType.CODE,
            "js": DocumentType.CODE,
            "java": DocumentType.CODE
        }
        
        document_type = type_mapping.get(file_extension, DocumentType.UNKNOWN)
        confidence = 0.9 if document_type != DocumentType.UNKNOWN else 0.3
        
        # Determine processing requirements
        processing_requirements = []
        if document_type == DocumentType.PDF:
            processing_requirements = ["text_extraction", "layout_analysis"]
        elif document_type == DocumentType.IMAGE:
            processing_requirements = ["ocr", "image_analysis"]
        elif document_type == DocumentType.SPREADSHEET:
            processing_requirements = ["data_extraction", "formula_evaluation"]
        
        return DocumentClassification(
            document_type=document_type,
            confidence_score=confidence,
            file_extension=file_extension,
            processing_requirements=processing_requirements
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: DocumentClassification) -> Optional[str]:
        """Route to appropriate processor."""
        shared["document_classification"] = exec_res
        
        self.logger.info(
            f"Classified as {exec_res.document_type} "
            f"with confidence {exec_res.confidence_score:.2f}"
        )
        
        # Route based on document type
        return exec_res.document_type.value


class PDFProcessorNode(Node):
    """Processes PDF documents."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> ProcessingRequest:
        """Prepare processing request."""
        import uuid
        
        return ProcessingRequest(
            document_id=str(uuid.uuid4()),
            document_path=shared.get("file_path", ""),
            requested_operations=shared.get("requested_operations", ["text_extraction"]),
            output_format="json"
        )
    
    def exec(self, prep_res: ProcessingRequest) -> ProcessingResponse:
        """Simulate PDF processing."""
        start_time = time.time()
        
        # Simulate processing
        time.sleep(0.5)  # Simulate work
        
        # Mock extracted data
        extracted_data = {
            "page_count": 10,
            "text_length": 5000,
            "tables_found": 2,
            "images_found": 5,
            "metadata": {
                "author": "Unknown",
                "created": "2024-01-01",
                "title": "Sample Document"
            }
        }
        
        return ProcessingResponse(
            document_id=prep_res.document_id,
            processor_used="PDFProcessor",
            success=True,
            processing_time_seconds=time.time() - start_time,
            output_path=f"/processed/{prep_res.document_id}.json",
            extracted_data=extracted_data
        )
    
    def post(self, shared: Dict[str, Any], prep_res: ProcessingRequest, exec_res: ProcessingResponse) -> Optional[str]:
        """Store processing result."""
        shared["processing_response"] = exec_res
        
        self.logger.info(
            f"PDF processed in {exec_res.processing_time_seconds:.2f}s"
        )
        
        return None


# ============== Multi-Level Routing Nodes ==============

class MultiLevelRouterNode(Node):
    """
    Implements hierarchical routing with multiple levels.
    Routes through primary → secondary → tertiary handlers.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Get input for routing."""
        return shared.get("query", "")
    
    def exec(self, prep_res: str) -> MultiLevelRoutingDecision:
        """Perform multi-level routing."""
        # Primary routing
        primary_route = self._determine_primary_route(prep_res)
        
        # Secondary routing based on primary
        secondary_route = self._determine_secondary_route(prep_res, primary_route)
        
        # Build routing path
        routing_path = [primary_route.value, secondary_route]
        
        # Determine final handler
        handler_map = {
            ("sales", "new_customer"): "NewCustomerHandler",
            ("sales", "existing_customer"): "AccountManagerHandler",
            ("sales", "enterprise"): "EnterpriseSalesHandler",
            ("support", "technical"): "TechnicalSupportHandler",
            ("support", "account"): "AccountSupportHandler",
            ("product", "feedback"): "ProductFeedbackHandler",
            ("product", "feature_request"): "FeatureRequestHandler",
            ("hr", "recruitment"): "RecruitmentHandler",
            ("hr", "employee"): "EmployeeRelationsHandler",
        }
        
        final_handler = handler_map.get(
            (primary_route.value, secondary_route),
            "GeneralHandler"
        )
        
        return MultiLevelRoutingDecision(
            input_text=prep_res,
            primary_route=primary_route,
            secondary_route=secondary_route,
            confidence_scores={
                "primary": 0.85,
                "secondary": 0.75
            },
            final_handler=final_handler,
            routing_path=routing_path
        )
    
    def _determine_primary_route(self, query: str) -> PrimaryRoute:
        """Determine primary routing category."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["buy", "purchase", "pricing", "quote"]):
            return PrimaryRoute.SALES
        elif any(word in query_lower for word in ["help", "issue", "problem", "broken"]):
            return PrimaryRoute.SUPPORT
        elif any(word in query_lower for word in ["feature", "improve", "suggestion"]):
            return PrimaryRoute.PRODUCT
        elif any(word in query_lower for word in ["job", "career", "benefits", "payroll"]):
            return PrimaryRoute.HR
        else:
            return PrimaryRoute.GENERAL
    
    def _determine_secondary_route(self, query: str, primary: PrimaryRoute) -> str:
        """Determine secondary routing within primary category."""
        query_lower = query.lower()
        
        if primary == PrimaryRoute.SALES:
            if "enterprise" in query_lower or "bulk" in query_lower:
                return "enterprise"
            elif "existing" in query_lower or "account" in query_lower:
                return "existing_customer"
            else:
                return "new_customer"
        
        elif primary == PrimaryRoute.SUPPORT:
            if any(word in query_lower for word in ["technical", "bug", "error"]):
                return "technical"
            else:
                return "account"
        
        elif primary == PrimaryRoute.PRODUCT:
            if "feature" in query_lower or "request" in query_lower:
                return "feature_request"
            else:
                return "feedback"
        
        elif primary == PrimaryRoute.HR:
            if any(word in query_lower for word in ["job", "apply", "career"]):
                return "recruitment"
            else:
                return "employee"
        
        else:
            return "general"
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: MultiLevelRoutingDecision) -> Optional[str]:
        """Store routing decision."""
        shared["routing_decision"] = exec_res
        
        self.logger.info(
            f"Routed through: {' → '.join(exec_res.routing_path)} "
            f"to {exec_res.final_handler}"
        )
        
        # Route to primary category for further processing
        return exec_res.primary_route.value


# ============== Fallback and Metrics Nodes ==============

class FallbackHandlerNode(Node):
    """Handles requests that couldn't be routed."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Get original request and classification."""
        return {
            "original_input": shared.get("user_input", shared.get("query", "")),
            "classification": shared.get("calendar_classification", shared.get("ticket_classification"))
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Generate fallback response."""
        original_input = prep_res["original_input"]
        
        return (
            f"I couldn't confidently determine how to handle your request: "
            f"'{original_input}'. Please provide more details or try "
            f"rephrasing your request."
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        """Store fallback response."""
        shared["fallback_response"] = exec_res
        
        # Update routing metrics
        if "routing_metrics" not in shared:
            shared["routing_metrics"] = RoutingMetrics()
        
        metrics = shared["routing_metrics"]
        metrics.total_requests += 1
        metrics.fallback_routes += 1
        
        self.logger.warning("Request routed to fallback handler")
        
        return None


class MetricsCollectorNode(Node):
    """Collects and reports routing metrics."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> RoutingMetrics:
        """Get current metrics."""
        if "routing_metrics" not in shared:
            shared["routing_metrics"] = RoutingMetrics()
        return shared["routing_metrics"]
    
    def exec(self, prep_res: RoutingMetrics) -> Dict[str, Any]:
        """Calculate metrics summary."""
        return {
            "total_requests": prep_res.total_requests,
            "success_rate": f"{prep_res.success_rate * 100:.1f}%",
            "fallback_rate": f"{prep_res.fallback_rate * 100:.1f}%",
            "average_confidence": prep_res.average_confidence,
            "routes_by_type": prep_res.routes_by_type,
            "performance": {
                "avg_processing_time_ms": prep_res.average_processing_time_ms,
                "requests_per_minute": prep_res.total_requests / max(1, prep_res.average_processing_time_ms / 60000)
            }
        }
    
    def post(self, shared: Dict[str, Any], prep_res: RoutingMetrics, exec_res: Dict) -> Optional[str]:
        """Store metrics summary."""
        shared["metrics_summary"] = exec_res
        
        self.logger.info(f"Metrics: {exec_res}")
        
        return None