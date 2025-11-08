"""
Pydantic models for human-in-the-loop patterns.
These define structured data for approval workflows and feedback collection.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============== Approval Models ==============

class ApprovalStatus(str, Enum):
    """Status of approval request."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MODIFIED = "modified"


class ApprovalRequest(BaseModel):
    """Request for human approval."""
    request_id: str = Field(description="Unique request identifier")
    content: str = Field(description="Content to be approved")
    context: Optional[str] = Field(default=None, description="Additional context")
    risk_level: Literal["low", "medium", "high"] = Field(default="medium")
    requested_at: datetime = Field(default_factory=datetime.now)
    requested_by: str = Field(default="ai_agent")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ApprovalResponse(BaseModel):
    """Human response to approval request."""
    request_id: str
    status: ApprovalStatus
    approved_by: str = Field(default="human_reviewer")
    approved_at: datetime = Field(default_factory=datetime.now)
    comments: Optional[str] = None
    modified_content: Optional[str] = None
    
    @validator('modified_content')
    def validate_modified_content(cls, v, values):
        """Ensure modified content is provided when status is MODIFIED."""
        if values.get('status') == ApprovalStatus.MODIFIED and not v:
            raise ValueError("Modified content required when status is MODIFIED")
        return v


# ============== Feedback Models ==============

class FeedbackType(str, Enum):
    """Types of feedback."""
    RATING = "rating"
    CORRECTION = "correction"
    SUGGESTION = "suggestion"
    QUALITY = "quality"


class FeedbackRequest(BaseModel):
    """Request for human feedback."""
    feedback_id: str = Field(description="Unique feedback identifier")
    ai_response: str = Field(description="AI-generated response")
    original_prompt: str = Field(description="Original user prompt")
    feedback_type: FeedbackType = Field(default=FeedbackType.QUALITY)
    options: Optional[List[str]] = Field(default=None, description="Multiple choice options")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class FeedbackResponse(BaseModel):
    """Human feedback on AI response."""
    feedback_id: str
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    feedback_text: Optional[str] = None
    corrections: Optional[str] = None
    suggestions: Optional[List[str]] = Field(default_factory=list)
    provided_at: datetime = Field(default_factory=datetime.now)
    provided_by: str = Field(default="human_reviewer")
    
    @validator('rating')
    def validate_feedback(cls, v, values):
        """Ensure at least one form of feedback is provided."""
        if not v and not values.get('feedback_text') and not values.get('corrections'):
            raise ValueError("Must provide rating, feedback text, or corrections")
        return v


# ============== Review Models ==============

class ReviewItem(BaseModel):
    """Item for quality review."""
    item_id: str
    content: str
    generated_at: datetime
    confidence_score: float = Field(ge=0, le=1)
    category: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ReviewDecision(str, Enum):
    """Review decisions."""
    ACCEPT = "accept"
    REJECT = "reject"
    MODIFY = "modify"
    ESCALATE = "escalate"


class ReviewResult(BaseModel):
    """Result of quality review."""
    item_id: str
    decision: ReviewDecision
    reviewer: str = Field(default="human_reviewer")
    reviewed_at: datetime = Field(default_factory=datetime.now)
    quality_score: Optional[int] = Field(default=None, ge=1, le=10)
    issues: List[str] = Field(default_factory=list)
    modifications: Optional[str] = None
    escalation_reason: Optional[str] = None


# ============== Escalation Models ==============

class EscalationReason(str, Enum):
    """Reasons for escalation."""
    LOW_CONFIDENCE = "low_confidence"
    HIGH_RISK = "high_risk"
    COMPLEX_QUERY = "complex_query"
    USER_REQUEST = "user_request"
    POLICY_VIOLATION = "policy_violation"
    UNKNOWN_INTENT = "unknown_intent"


class EscalationRequest(BaseModel):
    """Request for human escalation."""
    escalation_id: str
    query: str
    ai_response: Optional[str] = None
    reason: EscalationReason
    confidence_score: Optional[float] = Field(default=None, ge=0, le=1)
    risk_score: Optional[float] = Field(default=None, ge=0, le=1)
    context: Dict[str, Any] = Field(default_factory=dict)
    escalated_at: datetime = Field(default_factory=datetime.now)


class EscalationResponse(BaseModel):
    """Human response to escalation."""
    escalation_id: str
    human_response: str
    action_taken: Literal["resolved", "delegated", "deferred"]
    handled_by: str = Field(default="human_agent")
    handled_at: datetime = Field(default_factory=datetime.now)
    follow_up_required: bool = False
    notes: Optional[str] = None


# ============== Refinement Models ==============

class RefinementRequest(BaseModel):
    """Request for iterative refinement."""
    refinement_id: str
    iteration: int = Field(ge=1)
    current_output: str
    original_prompt: str
    previous_feedback: List[str] = Field(default_factory=list)
    max_iterations: int = Field(default=3, ge=1, le=10)


class RefinementGuidance(BaseModel):
    """Human guidance for refinement."""
    refinement_id: str
    iteration: int
    satisfied: bool
    guidance: Optional[str] = None
    specific_changes: List[str] = Field(default_factory=list)
    examples: List[str] = Field(default_factory=list)
    
    @validator('guidance')
    def validate_guidance(cls, v, values):
        """Ensure guidance is provided if not satisfied."""
        if not values.get('satisfied') and not v and not values.get('specific_changes'):
            raise ValueError("Must provide guidance or specific changes if not satisfied")
        return v


# ============== Aggregate Models ==============

class HumanFeedbackSession(BaseModel):
    """Complete feedback session."""
    session_id: str
    started_at: datetime = Field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    total_reviews: int = Field(ge=0, default=0)
    approvals: int = Field(ge=0, default=0)
    rejections: int = Field(ge=0, default=0)
    modifications: int = Field(ge=0, default=0)
    average_quality: Optional[float] = None
    reviewer_id: str
    notes: Optional[str] = None
    
    @property
    def approval_rate(self) -> float:
        """Calculate approval rate."""
        if self.total_reviews == 0:
            return 0.0
        return self.approvals / self.total_reviews
    
    @property
    def duration_minutes(self) -> Optional[float]:
        """Calculate session duration in minutes."""
        if self.ended_at:
            return (self.ended_at - self.started_at).total_seconds() / 60
        return None