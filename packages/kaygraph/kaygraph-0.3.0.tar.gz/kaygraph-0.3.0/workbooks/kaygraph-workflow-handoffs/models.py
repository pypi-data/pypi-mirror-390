"""
Data models for handoff workflows.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime

# ============== Enums ==============

class AgentType(str, Enum):
    """Types of agents in the system."""
    TRIAGE = "triage"
    TECH_SUPPORT = "tech_support"
    BILLING = "billing"
    SALES = "sales"
    MANAGER = "manager"
    ESCALATION = "escalation"
    DOCUMENT_ANALYZER = "document_analyzer"
    DATA_EXTRACTOR = "data_extractor"
    VALIDATOR = "validator"
    GENERAL = "general"

class RequestType(str, Enum):
    """Types of customer requests."""
    TECHNICAL = "technical"
    BILLING = "billing"
    SALES = "sales"
    COMPLAINT = "complaint"
    GENERAL = "general"
    UNKNOWN = "unknown"

class Priority(str, Enum):
    """Request priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class HandoffReason(str, Enum):
    """Reasons for handoffs."""
    EXPERTISE = "expertise"
    ESCALATION = "escalation"
    WORKLOAD = "workload"
    SCHEDULED = "scheduled"
    ERROR = "error"

# ============== Request Models ==============

class CustomerRequest(BaseModel):
    """Customer request model."""
    id: str = Field(description="Unique request ID")
    customer_id: str = Field(description="Customer identifier")
    content: str = Field(description="Request content")
    type: RequestType = Field(default=RequestType.UNKNOWN)
    priority: Priority = Field(default=Priority.MEDIUM)
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class TriageAnalysis(BaseModel):
    """Triage analysis result."""
    request_type: RequestType
    priority: Priority
    recommended_agent: AgentType
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    keywords: List[str] = Field(default_factory=list)
    requires_escalation: bool = False

# ============== Agent Models ==============

class AgentProfile(BaseModel):
    """Agent profile and capabilities."""
    agent_type: AgentType
    name: str
    capabilities: List[str]
    max_workload: int = 10
    current_workload: int = 0
    available: bool = True
    expertise_areas: List[str] = Field(default_factory=list)
    escalation_threshold: float = 0.3

class AgentResponse(BaseModel):
    """Agent response to a request."""
    agent_type: AgentType
    response: str
    confidence: float = Field(ge=0.0, le=1.0)
    needs_handoff: bool = False
    suggested_handoff: Optional[AgentType] = None
    handoff_reason: Optional[HandoffReason] = None
    resolution_complete: bool = False

# ============== Handoff Models ==============

class HandoffContext(BaseModel):
    """Context preserved during handoffs."""
    request: CustomerRequest
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list)
    previous_agents: List[AgentType] = Field(default_factory=list)
    handoff_count: int = 0
    total_time: float = 0.0
    notes: List[str] = Field(default_factory=list)

class HandoffDecision(BaseModel):
    """Handoff decision details."""
    from_agent: AgentType
    to_agent: AgentType
    reason: HandoffReason
    context: HandoffContext
    timestamp: datetime = Field(default_factory=datetime.now)
    priority_override: Optional[Priority] = None

# ============== Task Models ==============

class Task(BaseModel):
    """Task for delegation."""
    id: str
    description: str
    required_skills: List[str]
    estimated_duration: float
    priority: Priority = Priority.MEDIUM
    dependencies: List[str] = Field(default_factory=list)
    assigned_to: Optional[AgentType] = None
    status: str = "pending"

class TaskBreakdown(BaseModel):
    """Manager's task breakdown."""
    original_task: str
    subtasks: List[Task]
    suggested_assignments: Dict[str, AgentType]
    estimated_total_time: float
    parallel_execution: bool = True

# ============== Document Processing Models ==============

class Document(BaseModel):
    """Document for processing."""
    id: str
    content: str
    type: str
    source: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class DocumentAnalysis(BaseModel):
    """Document analysis result."""
    document_id: str
    document_type: str
    key_entities: List[str]
    summary: str
    requires_extraction: bool
    confidence: float

class ExtractedData(BaseModel):
    """Extracted data from document."""
    document_id: str
    fields: Dict[str, Any]
    extraction_method: str
    confidence_scores: Dict[str, float]

class ValidationResult(BaseModel):
    """Validation result."""
    document_id: str
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validated_data: Optional[Dict[str, Any]] = None

# ============== Metrics Models ==============

class HandoffMetrics(BaseModel):
    """Metrics for handoff performance."""
    total_requests: int = 0
    total_handoffs: int = 0
    average_handoffs_per_request: float = 0.0
    successful_resolutions: int = 0
    escalations: int = 0
    average_resolution_time: float = 0.0
    agent_utilization: Dict[str, float] = Field(default_factory=dict)