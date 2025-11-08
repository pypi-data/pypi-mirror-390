"""
Pydantic models for parallelization workflows.
These define structured data for parallel processing patterns.
"""

from typing import List, Optional, Dict, Any, Literal, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============== Validation Models ==============

class ValidationResult(BaseModel):
    """Result from a single validation check."""
    check_name: str
    passed: bool
    confidence: float = Field(ge=0, le=1)
    details: Optional[str] = None
    execution_time_ms: float = Field(ge=0)
    error: Optional[str] = None


class SecurityValidation(BaseModel):
    """Security validation results."""
    is_safe: bool
    risk_level: Literal["none", "low", "medium", "high", "critical"]
    risk_flags: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class FormatValidation(BaseModel):
    """Format validation results."""
    is_valid: bool
    format_type: str
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class BusinessRuleValidation(BaseModel):
    """Business rule validation results."""
    rules_passed: List[str] = Field(default_factory=list)
    rules_failed: List[str] = Field(default_factory=list)
    overall_valid: bool
    compliance_score: float = Field(ge=0, le=1)


class ParallelValidationSummary(BaseModel):
    """Summary of all parallel validations."""
    total_checks: int
    passed_checks: int
    failed_checks: int
    total_execution_time_ms: float
    parallel_execution_time_ms: float
    speedup_factor: float
    all_validations: List[ValidationResult]
    
    @property
    def success_rate(self) -> float:
        """Calculate validation success rate."""
        if self.total_checks == 0:
            return 0.0
        return self.passed_checks / self.total_checks


# ============== Enrichment Models ==============

class EnrichmentSource(str, Enum):
    """Available enrichment sources."""
    USER_PROFILE = "user_profile"
    LOCATION = "location"
    SOCIAL_MEDIA = "social_media"
    COMPANY = "company"
    FINANCIAL = "financial"
    BEHAVIORAL = "behavioral"


class EnrichmentResult(BaseModel):
    """Result from a single enrichment source."""
    source: EnrichmentSource
    success: bool
    data: Dict[str, Any] = Field(default_factory=dict)
    confidence_score: float = Field(ge=0, le=1, default=0.0)
    fetch_time_ms: float = Field(ge=0)
    error: Optional[str] = None


class UserProfileEnrichment(BaseModel):
    """User profile enrichment data."""
    full_name: Optional[str] = None
    email_verified: bool = False
    phone_verified: bool = False
    account_age_days: Optional[int] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    segments: List[str] = Field(default_factory=list)


class LocationEnrichment(BaseModel):
    """Location enrichment data."""
    country: Optional[str] = None
    city: Optional[str] = None
    timezone: Optional[str] = None
    coordinates: Optional[Dict[str, float]] = None
    ip_type: Optional[str] = None


class CompanyEnrichment(BaseModel):
    """Company enrichment data."""
    company_name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    revenue_range: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)


class EnrichedData(BaseModel):
    """Complete enriched data."""
    original_data: Dict[str, Any]
    enrichments: Dict[EnrichmentSource, EnrichmentResult]
    enrichment_timestamp: datetime = Field(default_factory=datetime.now)
    total_sources: int
    successful_sources: int
    total_enrichment_time_ms: float
    
    @property
    def enrichment_rate(self) -> float:
        """Calculate enrichment success rate."""
        if self.total_sources == 0:
            return 0.0
        return self.successful_sources / self.total_sources


# ============== Batch Processing Models ==============

class BatchItem(BaseModel):
    """Individual item in a batch."""
    item_id: str
    data: Dict[str, Any]
    priority: Literal["low", "normal", "high"] = "normal"
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProcessingResult(BaseModel):
    """Result from processing a single item."""
    item_id: str
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    processing_time_ms: float
    worker_id: str
    retry_count: int = 0


class BatchConfiguration(BaseModel):
    """Configuration for batch processing."""
    batch_size: int = Field(gt=0, default=100)
    worker_count: int = Field(gt=0, default=4)
    max_retries: int = Field(ge=0, default=2)
    timeout_ms: float = Field(gt=0, default=30000)
    enable_progress_tracking: bool = True
    error_threshold_percent: float = Field(ge=0, le=100, default=10.0)


class BatchProgress(BaseModel):
    """Progress tracking for batch processing."""
    total_items: int
    processed_items: int
    successful_items: int
    failed_items: int
    retry_items: int
    elapsed_time_ms: float
    estimated_time_remaining_ms: Optional[float] = None
    current_throughput: float = Field(default=0.0, description="Items per second")
    
    @property
    def progress_percent(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.processed_items == 0:
            return 0.0
        return self.successful_items / self.processed_items


class BatchResult(BaseModel):
    """Complete batch processing result."""
    batch_id: str
    configuration: BatchConfiguration
    items_processed: List[ProcessingResult]
    progress: BatchProgress
    start_time: datetime
    end_time: Optional[datetime] = None
    status: Literal["running", "completed", "failed", "cancelled"]
    error_message: Optional[str] = None


# ============== Map-Reduce Models ==============

class MapTask(BaseModel):
    """Task for map phase."""
    task_id: str
    input_data: Any
    mapper_name: str
    partition_key: Optional[str] = None


class MapResult(BaseModel):
    """Result from map phase."""
    task_id: str
    key: str
    value: Any
    processing_time_ms: float
    worker_id: str


class ReduceTask(BaseModel):
    """Task for reduce phase."""
    key: str
    values: List[Any]
    reducer_name: str


class ReduceResult(BaseModel):
    """Result from reduce phase."""
    key: str
    result: Any
    value_count: int
    processing_time_ms: float


class MapReduceJob(BaseModel):
    """Complete map-reduce job."""
    job_id: str
    input_count: int
    mapper_count: int
    reducer_count: int
    map_results: List[MapResult]
    reduce_results: List[ReduceResult]
    total_time_ms: float
    map_time_ms: float
    shuffle_time_ms: float
    reduce_time_ms: float
    
    @property
    def efficiency(self) -> float:
        """Calculate processing efficiency."""
        if self.total_time_ms == 0:
            return 0.0
        processing_time = self.map_time_ms + self.reduce_time_ms
        return processing_time / self.total_time_ms


# ============== Pipeline Models ==============

class PipelineStage(BaseModel):
    """Definition of a pipeline stage."""
    stage_name: str
    parallelism: int = Field(gt=0, default=1)
    timeout_ms: float = Field(gt=0, default=10000)
    retry_on_failure: bool = True
    optional: bool = False


class StageResult(BaseModel):
    """Result from a pipeline stage."""
    stage_name: str
    input_data: Any
    output_data: Any
    success: bool
    execution_time_ms: float
    parallel_executions: int
    errors: List[str] = Field(default_factory=list)


class PipelineExecution(BaseModel):
    """Complete pipeline execution."""
    pipeline_id: str
    stages: List[PipelineStage]
    stage_results: List[StageResult]
    total_execution_time_ms: float
    parallel_speedup: float
    bottleneck_stage: Optional[str] = None
    overall_success: bool


# ============== Performance Metrics ==============

class ParallelizationMetrics(BaseModel):
    """Metrics for parallel execution performance."""
    sequential_time_ms: float
    parallel_time_ms: float
    speedup_factor: float
    efficiency: float = Field(ge=0, le=1)
    worker_utilization: Dict[str, float]
    overhead_ms: float
    optimal_worker_count: int
    
    @validator('speedup_factor')
    def validate_speedup(cls, v, values):
        """Calculate speedup factor."""
        if 'sequential_time_ms' in values and 'parallel_time_ms' in values:
            if values['parallel_time_ms'] > 0:
                return values['sequential_time_ms'] / values['parallel_time_ms']
        return v
    
    @property
    def speedup_percentage(self) -> float:
        """Calculate speedup as percentage."""
        return (self.speedup_factor - 1) * 100