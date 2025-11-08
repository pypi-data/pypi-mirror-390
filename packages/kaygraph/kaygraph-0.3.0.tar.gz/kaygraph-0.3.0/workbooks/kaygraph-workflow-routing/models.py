"""
Pydantic models for routing workflows.
These define structured data for routing decisions and specialized handling.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============== Calendar Routing Models ==============

class CalendarRequestType(BaseModel):
    """Classification of calendar request."""
    request_type: Literal["new_event", "modify_event", "query_event", "delete_event", "other"]
    confidence_score: float = Field(ge=0, le=1)
    description: str = Field(description="Cleaned description of the request")
    original_input: str = Field(description="Original user input")


class NewEventDetails(BaseModel):
    """Details for creating a new calendar event."""
    name: str = Field(description="Name of the event")
    date: str = Field(description="Date and time of the event")
    duration_minutes: int = Field(default=60, ge=15)
    participants: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    description: Optional[str] = None
    
    @validator('duration_minutes')
    def validate_duration(cls, v):
        """Ensure reasonable duration."""
        if v > 480:  # 8 hours
            raise ValueError("Event duration too long (max 8 hours)")
        return v


class EventChange(BaseModel):
    """Details for a single change to an event."""
    field: str = Field(description="Field to change")
    old_value: Optional[str] = None
    new_value: str = Field(description="New value for the field")


class ModifyEventDetails(BaseModel):
    """Details for modifying an existing event."""
    event_identifier: str = Field(description="Description to identify the event")
    changes: List[EventChange] = Field(min_items=1)
    participants_to_add: List[str] = Field(default_factory=list)
    participants_to_remove: List[str] = Field(default_factory=list)


class CalendarResponse(BaseModel):
    """Response for calendar operations."""
    success: bool
    message: str
    action_taken: str
    calendar_link: Optional[str] = None
    event_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


# ============== Support Ticket Routing Models ==============

class TicketPriority(str, Enum):
    """Support ticket priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TicketCategory(str, Enum):
    """Support ticket categories."""
    TECHNICAL = "technical"
    BILLING = "billing"
    FEATURE_REQUEST = "feature_request"
    GENERAL = "general"
    COMPLAINT = "complaint"


class SupportTicketClassification(BaseModel):
    """Classification of support ticket."""
    category: TicketCategory
    priority: TicketPriority
    confidence_score: float = Field(ge=0, le=1)
    summary: str = Field(description="Brief summary of the issue")
    keywords: List[str] = Field(default_factory=list)
    requires_escalation: bool = False


class TechnicalIssueDetails(BaseModel):
    """Details for technical support issues."""
    error_message: Optional[str] = None
    affected_service: Optional[str] = None
    steps_to_reproduce: List[str] = Field(default_factory=list)
    environment: Optional[str] = None
    urgency_reason: Optional[str] = None


class BillingIssueDetails(BaseModel):
    """Details for billing issues."""
    account_id: Optional[str] = None
    amount_disputed: Optional[float] = None
    billing_period: Optional[str] = None
    issue_type: Literal["overcharge", "missing_payment", "refund", "subscription", "other"]


class SupportTicketResponse(BaseModel):
    """Response for support ticket routing."""
    ticket_id: str
    routed_to: str
    estimated_response_time: str
    priority: TicketPriority
    initial_response: str
    escalated: bool = False
    assigned_agent: Optional[str] = None


# ============== Document Processing Models ==============

class DocumentType(str, Enum):
    """Types of documents for processing."""
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    CODE = "code"
    UNKNOWN = "unknown"


class DocumentClassification(BaseModel):
    """Classification of document for routing."""
    document_type: DocumentType
    confidence_score: float = Field(ge=0, le=1)
    file_extension: Optional[str] = None
    detected_language: Optional[str] = None
    contains_tables: bool = False
    contains_images: bool = False
    page_count: Optional[int] = None
    processing_requirements: List[str] = Field(default_factory=list)


class ProcessingRequest(BaseModel):
    """Request for document processing."""
    document_id: str
    document_path: str
    requested_operations: List[str]
    output_format: Optional[str] = None
    priority: Literal["normal", "high"] = "normal"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessingResponse(BaseModel):
    """Response from document processing."""
    document_id: str
    processor_used: str
    success: bool
    processing_time_seconds: float
    output_path: Optional[str] = None
    extracted_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


# ============== Multi-Level Routing Models ==============

class PrimaryRoute(str, Enum):
    """Primary routing categories."""
    SALES = "sales"
    SUPPORT = "support"
    PRODUCT = "product"
    HR = "hr"
    GENERAL = "general"


class SecondaryRoute(BaseModel):
    """Secondary routing within primary category."""
    primary: PrimaryRoute
    secondary: str
    confidence_score: float = Field(ge=0, le=1)
    reasoning: str


class MultiLevelRoutingDecision(BaseModel):
    """Complete multi-level routing decision."""
    input_text: str
    primary_route: PrimaryRoute
    secondary_route: str
    tertiary_route: Optional[str] = None
    confidence_scores: Dict[str, float]
    final_handler: str
    routing_path: List[str]
    metadata: Dict[str, Any] = Field(default_factory=dict)


# ============== Generic Routing Models ==============

class RouteDecision(BaseModel):
    """Generic routing decision."""
    route_name: str
    confidence_score: float = Field(ge=0, le=1)
    reasoning: Optional[str] = None
    fallback_route: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RoutingMetrics(BaseModel):
    """Metrics for routing performance."""
    total_requests: int = 0
    successful_routes: int = 0
    fallback_routes: int = 0
    failed_routes: int = 0
    average_confidence: float = 0.0
    routes_by_type: Dict[str, int] = Field(default_factory=dict)
    average_processing_time_ms: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Calculate routing success rate."""
        if self.total_requests == 0:
            return 0.0
        return self.successful_routes / self.total_requests
    
    @property
    def fallback_rate(self) -> float:
        """Calculate fallback usage rate."""
        if self.total_requests == 0:
            return 0.0
        return self.fallback_routes / self.total_requests