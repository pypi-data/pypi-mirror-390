"""
Pydantic models for structured data workflows.
These define type-safe schemas for data extraction, transformation, and validation.
"""

from typing import List, Optional, Dict, Any, Union, Literal
from datetime import datetime, date as DateType, time as TimeType
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


# ============== Meeting Extraction Models ==============

class MeetingParticipant(BaseModel):
    """Individual meeting participant."""
    name: str
    email: Optional[str] = None
    role: Optional[str] = None
    required: bool = True


class MeetingLocation(BaseModel):
    """Meeting location details."""
    type: Literal["in_person", "virtual", "hybrid"]
    name: Optional[str] = None
    address: Optional[str] = None
    meeting_link: Optional[str] = None
    room_number: Optional[str] = None
    
    @model_validator(mode='after')
    def validate_location_details(self):
        """Ensure appropriate details for location type."""
        if self.type == 'virtual' and not self.meeting_link:
            raise ValueError("Virtual meetings require a meeting link")
        if self.type == 'in_person' and not (self.address or self.room_number):
            raise ValueError("In-person meetings require address or room number")
        return self


class MeetingEvent(BaseModel):
    """Structured meeting event data."""
    name: str = Field(description="Meeting title")
    date: DateType = Field(description="Meeting date")
    start_time: TimeType = Field(description="Start time")
    end_time: Optional[TimeType] = Field(description="End time")
    participants: List[MeetingParticipant]
    location: Optional[MeetingLocation] = None
    agenda: Optional[List[str]] = Field(default_factory=list)
    notes: Optional[str] = None
    recurring: bool = False
    recurrence_pattern: Optional[str] = None
    
    @field_validator('end_time')
    @classmethod
    def validate_end_time(cls, v, info):
        """Ensure end time is after start time."""
        if v and 'start_time' in info.data and v <= info.data['start_time']:
            raise ValueError("End time must be after start time")
        return v
    
    @property
    def duration_minutes(self) -> Optional[int]:
        """Calculate meeting duration in minutes."""
        if self.end_time and self.start_time:
            start_minutes = self.start_time.hour * 60 + self.start_time.minute
            end_minutes = self.end_time.hour * 60 + self.end_time.minute
            return end_minutes - start_minutes
        return None


# ============== Invoice Processing Models ==============

class InvoiceLineItem(BaseModel):
    """Individual line item in an invoice."""
    description: str
    quantity: float = Field(gt=0)
    unit_price: float = Field(ge=0)
    tax_rate: float = Field(ge=0, le=1, default=0)
    discount_percent: float = Field(ge=0, le=1, default=0)
    
    @property
    def subtotal(self) -> float:
        """Calculate line item subtotal."""
        base = self.quantity * self.unit_price
        discount = base * self.discount_percent
        return base - discount
    
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount."""
        return self.subtotal * self.tax_rate
    
    @property
    def total(self) -> float:
        """Calculate total including tax."""
        return self.subtotal + self.tax_amount


class InvoiceAddress(BaseModel):
    """Address information."""
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    street: str
    city: str
    state: Optional[str] = None
    postal_code: str
    country: str = "USA"


class Invoice(BaseModel):
    """Structured invoice data."""
    invoice_number: str
    invoice_date: DateType
    due_date: DateType
    billing_address: InvoiceAddress
    shipping_address: Optional[InvoiceAddress] = None
    line_items: List[InvoiceLineItem]
    notes: Optional[str] = None
    payment_terms: str = "Net 30"
    currency: str = "USD"
    
    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v, info):
        """Ensure due date is after invoice date."""
        if 'invoice_date' in info.data and v < info.data['invoice_date']:
            raise ValueError("Due date must be after invoice date")
        return v
    
    @property
    def subtotal(self) -> float:
        """Calculate invoice subtotal."""
        return sum(item.subtotal for item in self.line_items)
    
    @property
    def total_tax(self) -> float:
        """Calculate total tax."""
        return sum(item.tax_amount for item in self.line_items)
    
    @property
    def total(self) -> float:
        """Calculate invoice total."""
        return sum(item.total for item in self.line_items)


# ============== Contact Information Models ==============

class PhoneNumber(BaseModel):
    """Structured phone number."""
    type: Literal["mobile", "work", "home", "other"]
    number: str
    country_code: str = "+1"
    primary: bool = False
    
    @field_validator('number')
    @classmethod
    def validate_phone_number(cls, v):
        """Basic phone number validation."""
        # Remove common formatting characters
        cleaned = v.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
        if not cleaned.isdigit() or len(cleaned) < 10:
            raise ValueError("Invalid phone number format")
        return v


class EmailAddress(BaseModel):
    """Structured email address."""
    type: Literal["personal", "work", "other"]
    email: str
    primary: bool = False
    verified: bool = False
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if "@" not in v or "." not in v.split("@")[1]:
            raise ValueError("Invalid email format")
        return v.lower()


class SocialMedia(BaseModel):
    """Social media profile."""
    platform: Literal["linkedin", "twitter", "github", "facebook", "other"]
    username: str
    url: Optional[str] = None


class ContactInfo(BaseModel):
    """Complete contact information."""
    first_name: str
    last_name: str
    middle_name: Optional[str] = None
    title: Optional[str] = None
    company: Optional[str] = None
    department: Optional[str] = None
    emails: List[EmailAddress] = Field(default_factory=list)
    phones: List[PhoneNumber] = Field(default_factory=list)
    addresses: List[InvoiceAddress] = Field(default_factory=list)
    social_media: List[SocialMedia] = Field(default_factory=list)
    notes: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)
    
    @property
    def primary_email(self) -> Optional[str]:
        """Get primary email address."""
        for email in self.emails:
            if email.primary:
                return email.email
        return self.emails[0].email if self.emails else None
    
    @property
    def primary_phone(self) -> Optional[str]:
        """Get primary phone number."""
        for phone in self.phones:
            if phone.primary:
                return phone.number
        return self.phones[0].number if self.phones else None


# ============== Product Catalog Models ==============

class ProductDimensions(BaseModel):
    """Product physical dimensions."""
    length: float = Field(gt=0)
    width: float = Field(gt=0)
    height: float = Field(gt=0)
    unit: Literal["inches", "cm", "mm"] = "inches"
    weight: float = Field(gt=0)
    weight_unit: Literal["lbs", "kg", "g"] = "lbs"


class ProductVariant(BaseModel):
    """Product variant (size, color, etc)."""
    sku: str
    name: str
    attributes: Dict[str, str]  # e.g., {"color": "red", "size": "large"}
    price_adjustment: float = 0
    stock_quantity: int = 0
    images: List[str] = Field(default_factory=list)


class Product(BaseModel):
    """Structured product data."""
    product_id: str
    name: str
    description: str
    category: str
    subcategory: Optional[str] = None
    brand: str
    base_price: float = Field(gt=0)
    currency: str = "USD"
    variants: List[ProductVariant] = Field(default_factory=list)
    dimensions: Optional[ProductDimensions] = None
    tags: List[str] = Field(default_factory=list)
    images: List[str] = Field(default_factory=list)
    in_stock: bool = True
    featured: bool = False
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    @property
    def price_range(self) -> tuple[float, float]:
        """Get min and max price across variants."""
        if not self.variants:
            return (self.base_price, self.base_price)
        
        prices = [self.base_price + v.price_adjustment for v in self.variants]
        return (min(prices), max(prices))


# ============== Data Transformation Models ==============

class SchemaVersion(str, Enum):
    """Schema version identifiers."""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"


class DataTransformation(BaseModel):
    """Transformation operation definition."""
    source_field: str
    target_field: str
    transform_type: Literal["rename", "cast", "calculate", "merge", "split"]
    parameters: Dict[str, Any] = Field(default_factory=dict)


class SchemaMapping(BaseModel):
    """Schema transformation mapping."""
    source_schema: str
    target_schema: str
    version: SchemaVersion
    transformations: List[DataTransformation]
    validation_rules: List[str] = Field(default_factory=list)


# ============== Pipeline Models ==============

class PipelineStage(BaseModel):
    """Individual pipeline stage configuration."""
    stage_name: str
    stage_type: Literal["extract", "transform", "validate", "load"]
    input_schema: Optional[str] = None
    output_schema: Optional[str] = None
    error_handling: Literal["fail", "skip", "default"] = "skip"
    retry_count: int = Field(ge=0, default=0)
    timeout_seconds: Optional[int] = None


class DataQualityMetrics(BaseModel):
    """Data quality metrics for pipeline monitoring."""
    total_records: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    skipped_records: int = 0
    error_records: int = 0
    completeness_score: float = Field(ge=0, le=1, default=0)
    accuracy_score: float = Field(ge=0, le=1, default=0)
    consistency_score: float = Field(ge=0, le=1, default=0)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.total_records == 0:
            return 0.0
        return self.valid_records / self.total_records
    
    @property
    def overall_quality_score(self) -> float:
        """Calculate overall quality score."""
        return (self.completeness_score + self.accuracy_score + self.consistency_score) / 3


class PipelineResult(BaseModel):
    """Pipeline execution result."""
    pipeline_id: str
    start_time: datetime
    end_time: datetime
    stages_completed: List[str]
    stages_failed: List[str]
    data_quality: DataQualityMetrics
    output_location: Optional[str] = None
    error_log: List[Dict[str, Any]] = Field(default_factory=list)
    
    @property
    def duration_seconds(self) -> float:
        """Calculate pipeline duration."""
        return (self.end_time - self.start_time).total_seconds()
    
    @property
    def success(self) -> bool:
        """Check if pipeline succeeded."""
        return len(self.stages_failed) == 0