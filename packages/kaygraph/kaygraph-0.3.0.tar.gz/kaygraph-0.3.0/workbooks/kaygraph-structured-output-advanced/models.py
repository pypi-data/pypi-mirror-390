"""
Advanced data models for structured output workflows.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
from datetime import datetime
import re
from typing_extensions import Annotated


# ============== Enums ==============

class TicketCategory(str, Enum):
    """Support ticket categories."""
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"
    BUG_REPORT = "bug_report"
    GENERAL = "general"

class Priority(str, Enum):
    """Priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class Sentiment(str, Enum):
    """Customer sentiment."""
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"

class ResponseTone(str, Enum):
    """Response tone options."""
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    EMPATHETIC = "empathetic"
    FORMAL = "formal"

# ============== Base Models ==============

class ValidationResult(BaseModel):
    """Result of content validation."""
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class SafetyCheck(BaseModel):
    """Safety check results."""
    has_pii: bool = False
    has_harmful_content: bool = False
    has_prompt_injection: bool = False
    pii_entities: List[str] = Field(default_factory=list)
    harmful_categories: List[str] = Field(default_factory=list)
    confidence: float = Field(ge=0.0, le=1.0)

# ============== Customer Support Models ==============

class CustomerInfo(BaseModel):
    """Customer information with validation."""
    customer_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    account_type: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if v and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('name')
    @classmethod
    def sanitize_name(cls, v):
        if v:
            # Remove potential PII markers
            v = re.sub(r'\b\d{3,}\b', '[REDACTED]', v)
        return v

class TicketStep(BaseModel):
    """Single step in ticket resolution."""
    step_number: int = Field(ge=1)
    description: str = Field(min_length=10, max_length=500)
    action: str = Field(min_length=5)
    requires_customer_input: bool = False
    estimated_time_minutes: Optional[int] = Field(None, ge=0, le=120)

class TicketResolution(BaseModel):
    """Complete ticket resolution with validation."""
    ticket_id: str
    category: TicketCategory
    priority: Priority
    sentiment: Sentiment
    customer_info: CustomerInfo
    issue_summary: str = Field(min_length=20, max_length=200)
    steps: List[TicketStep] = Field(min_items=1, max_items=10)
    final_resolution: str = Field(min_length=50, max_length=1000)
    response_tone: ResponseTone = ResponseTone.PROFESSIONAL
    confidence: float = Field(ge=0.0, le=1.0)
    requires_follow_up: bool = False
    safety_check: Optional[SafetyCheck] = None
    
    @model_validator(mode='after')
    def validate_resolution(self):
        # Ensure urgent tickets have high confidence
        if self.priority == Priority.URGENT and self.confidence < 0.8:
            self.requires_follow_up = True
        
        # Check for escalation needs
        if self.sentiment == Sentiment.ANGRY and self.response_tone != ResponseTone.EMPATHETIC:
            self.response_tone = ResponseTone.EMPATHETIC
        
        return self

# ============== Report Generation Models ==============

class ReportSection(BaseModel):
    """Section of a structured report."""
    title: str
    content: str = Field(min_length=50)
    subsections: Optional[List['ReportSection']] = None
    data_points: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(ge=0.0, le=1.0, default=1.0)

# Enable self-reference
ReportSection.model_rebuild()

class ReportMetadata(BaseModel):
    """Report metadata with validation."""
    report_id: str
    title: str
    author: str
    created_at: datetime = Field(default_factory=datetime.now)
    version: str = "1.0"
    tags: List[str] = Field(default_factory=list)
    confidentiality_level: Literal["public", "internal", "confidential", "secret"] = "internal"

class StructuredReport(BaseModel):
    """Complete structured report."""
    metadata: ReportMetadata
    executive_summary: str = Field(min_length=100, max_length=500)
    sections: List[ReportSection] = Field(min_items=1)
    conclusions: List[str] = Field(min_items=1)
    recommendations: List[str] = Field(default_factory=list)
    appendices: Optional[Dict[str, Any]] = None
    quality_score: float = Field(ge=0.0, le=1.0)
    
    @field_validator('sections')
    @classmethod
    def validate_sections(cls, v):
        # Ensure no empty sections
        for section in v:
            if not section.content.strip():
                raise ValueError(f"Section '{section.title}' has empty content")
        return v

# ============== Form Processing Models ==============

class FormFieldType(str, Enum):
    """Types of form fields."""
    TEXT = "text"
    NUMBER = "number"
    EMAIL = "email"
    DATE = "date"
    SELECT = "select"
    MULTISELECT = "multiselect"
    BOOLEAN = "boolean"
    FILE = "file"

class FormFieldValidation(BaseModel):
    """Field validation rules."""
    required: bool = False
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    allowed_values: Optional[List[str]] = None

class FormField(BaseModel):
    """Dynamic form field definition."""
    field_id: str
    label: str
    field_type: FormFieldType
    validation: FormFieldValidation
    default_value: Optional[Any] = None
    help_text: Optional[str] = None
    depends_on: Optional[Dict[str, Any]] = None  # Conditional fields

class ProcessedFormData(BaseModel):
    """Processed form submission."""
    form_id: str
    submission_id: str
    fields: Dict[str, Any]
    validation_result: ValidationResult
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    processing_notes: List[str] = Field(default_factory=list)
    compliance_checks: Dict[str, bool] = Field(default_factory=dict)

# ============== API Response Models ==============

class APIErrorDetail(BaseModel):
    """Detailed API error information."""
    code: str
    message: str
    field: Optional[str] = None
    suggestion: Optional[str] = None

class APIResponse(BaseModel):
    """Structured API response."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    errors: List[APIErrorDetail] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

# ============== Schema Evolution Models ==============

class SchemaVersion(BaseModel):
    """Schema version tracking."""
    version: str
    created_at: datetime
    changes: List[str]
    backwards_compatible: bool = True

class EvolvableSchema(BaseModel):
    """Base for schemas that support evolution."""
    model_config = ConfigDict(extra='allow')  # Allow extra fields
    
    schema_version: str = "1.0"
    captured_extra_fields: Dict[str, Any] = Field(default_factory=dict, exclude=True)
    
    @model_validator(mode='before')
    @classmethod
    def capture_extra_fields(cls, values):
        # Capture any extra fields for migration
        if isinstance(values, dict):
            known_fields = {'schema_version', 'captured_extra_fields'}
            # Get actual model fields from the class
            if hasattr(cls, 'model_fields'):
                known_fields.update(cls.model_fields.keys())
            extra = {k: v for k, v in values.items() if k not in known_fields}
            if extra:
                values['captured_extra_fields'] = extra
        return values

# ============== Complex Nested Models ==============

class WorkflowStep(BaseModel):
    """Step in a complex workflow."""
    step_id: str
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    validation_rules: List[str] = Field(default_factory=list)
    timeout_seconds: int = Field(default=300, ge=1, le=3600)

class WorkflowDefinition(BaseModel):
    """Complex workflow with dynamic schemas."""
    workflow_id: str
    name: str
    description: str
    steps: List[WorkflowStep]
    transitions: Dict[str, List[str]]  # step_id -> [next_step_ids]
    error_handlers: Dict[str, str] = Field(default_factory=dict)
    
    @model_validator(mode='after')
    def validate_workflow(self):
        # Validate all transitions reference valid steps
        step_ids = {step.step_id for step in self.steps}
        for from_step, to_steps in self.transitions.items():
            if from_step not in step_ids:
                raise ValueError(f"Invalid transition from unknown step: {from_step}")
            for to_step in to_steps:
                if to_step not in step_ids:
                    raise ValueError(f"Invalid transition to unknown step: {to_step}")
        return self

# ============== Batch Processing Models ==============

class BatchItem(BaseModel):
    """Item in a batch processing job."""
    item_id: str
    data: Dict[str, Any]
    schema_type: str
    validation_status: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

class BatchResult(BaseModel):
    """Result of batch structured generation."""
    batch_id: str
    total_items: int
    successful_items: int
    failed_items: int
    items: List[BatchItem]
    processing_time_seconds: float
    aggregate_metrics: Dict[str, Any] = Field(default_factory=dict)