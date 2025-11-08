"""
Pydantic models for recovery patterns.
These define structured data for error handling and recovery flows.
"""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============== Error and Status Models ==============

class ErrorType(str, Enum):
    """Types of errors that can occur."""
    TRANSIENT = "transient"
    PERMANENT = "permanent"
    TIMEOUT = "timeout"
    VALIDATION = "validation"
    UNKNOWN = "unknown"


class ErrorInfo(BaseModel):
    """Information about an error."""
    error_type: ErrorType
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    attempt_number: int = Field(ge=1)
    recoverable: bool = True
    details: Optional[Dict[str, Any]] = None


class RetryStatus(BaseModel):
    """Status of retry attempts."""
    attempts: int = Field(ge=0)
    max_attempts: int = Field(ge=1)
    last_error: Optional[ErrorInfo] = None
    backoff_seconds: float = Field(ge=0)
    should_retry: bool = True
    
    @property
    def attempts_remaining(self) -> int:
        """Calculate remaining attempts."""
        return max(0, self.max_attempts - self.attempts)


# ============== Recovery Strategy Models ==============

class RecoveryStrategy(BaseModel):
    """Base recovery strategy configuration."""
    strategy_type: str
    enabled: bool = True
    priority: int = Field(ge=0, default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class RetryStrategy(RecoveryStrategy):
    """Retry strategy with backoff."""
    strategy_type: str = Field(default="retry")
    max_attempts: int = Field(ge=1, default=3)
    initial_backoff: float = Field(ge=0, default=1.0)
    backoff_multiplier: float = Field(ge=1.0, default=2.0)
    max_backoff: float = Field(ge=0, default=60.0)
    retry_on: List[ErrorType] = Field(default_factory=lambda: [ErrorType.TRANSIENT, ErrorType.TIMEOUT])


class FallbackStrategy(RecoveryStrategy):
    """Fallback strategy configuration."""
    strategy_type: str = Field(default="fallback")
    fallback_methods: List[str] = Field(default_factory=list)
    degrade_gracefully: bool = True
    minimum_functionality: Dict[str, Any] = Field(default_factory=dict)


class CircuitBreakerStrategy(RecoveryStrategy):
    """Circuit breaker configuration."""
    strategy_type: str = Field(default="circuit_breaker")
    failure_threshold: int = Field(ge=1, default=5)
    success_threshold: int = Field(ge=1, default=2)
    timeout_seconds: float = Field(ge=0, default=60.0)
    half_open_max_calls: int = Field(ge=1, default=3)


# ============== Circuit Breaker State ==============

class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Blocking calls
    HALF_OPEN = "half_open"  # Testing recovery


class CircuitBreakerStatus(BaseModel):
    """Current status of a circuit breaker."""
    state: CircuitState
    failure_count: int = Field(ge=0)
    success_count: int = Field(ge=0)
    last_failure_time: Optional[datetime] = None
    last_success_time: Optional[datetime] = None
    next_attempt_time: Optional[datetime] = None
    
    def can_attempt(self) -> bool:
        """Check if we can attempt a call."""
        if self.state == CircuitState.CLOSED:
            return True
        elif self.state == CircuitState.OPEN:
            if self.next_attempt_time and datetime.now() >= self.next_attempt_time:
                return True
            return False
        else:  # HALF_OPEN
            return True


# ============== Recovery Result Models ==============

class RecoveryResult(BaseModel):
    """Result of a recovery attempt."""
    success: bool
    result: Optional[Any] = None
    error: Optional[ErrorInfo] = None
    strategy_used: str
    attempts_made: int = Field(ge=0)
    total_duration_seconds: float = Field(ge=0)
    degraded: bool = False
    
    @property
    def has_result(self) -> bool:
        """Check if we have any result (even degraded)."""
        return self.result is not None


class FallbackResult(BaseModel):
    """Result from fallback processing."""
    primary_failed: bool = True
    fallback_level: int = Field(ge=0)
    method_used: str
    result: Any
    is_partial: bool = False
    missing_features: List[str] = Field(default_factory=list)


# ============== Aggregated Error Models ==============

class ErrorAggregation(BaseModel):
    """Aggregated error information."""
    total_errors: int = Field(ge=0)
    errors_by_type: Dict[ErrorType, int] = Field(default_factory=dict)
    recent_errors: List[ErrorInfo] = Field(default_factory=list)
    error_rate: float = Field(ge=0, le=1)
    time_window_seconds: float = Field(ge=0, default=300.0)
    
    def add_error(self, error: ErrorInfo):
        """Add an error to aggregation."""
        self.total_errors += 1
        error_type = error.error_type
        self.errors_by_type[error_type] = self.errors_by_type.get(error_type, 0) + 1
        self.recent_errors.append(error)
        # Keep only recent errors within time window
        cutoff = datetime.now().timestamp() - self.time_window_seconds
        self.recent_errors = [
            e for e in self.recent_errors 
            if e.timestamp.timestamp() > cutoff
        ]


# ============== Health Check Models ==============

class ServiceHealth(BaseModel):
    """Health status of a service."""
    service_name: str
    healthy: bool
    last_check: datetime = Field(default_factory=datetime.now)
    consecutive_failures: int = Field(ge=0, default=0)
    response_time_ms: Optional[float] = None
    error_message: Optional[str] = None
    
    @validator('response_time_ms')
    def validate_response_time(cls, v):
        """Ensure positive response time."""
        if v is not None and v < 0:
            raise ValueError("Response time must be positive")
        return v


class SystemHealth(BaseModel):
    """Overall system health."""
    services: Dict[str, ServiceHealth]
    overall_health: bool
    degraded_services: List[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('overall_health', pre=False, always=True)
    def calculate_overall_health(cls, v, values):
        """Calculate overall health from services."""
        if 'services' in values:
            all_healthy = all(s.healthy for s in values['services'].values())
            return all_healthy
        return v
    
    @validator('degraded_services', pre=False, always=True)
    def find_degraded_services(cls, v, values):
        """Find degraded services."""
        if 'services' in values:
            degraded = [
                name for name, health in values['services'].items() 
                if not health.healthy
            ]
            return degraded
        return v


# ============== Recovery Policy Models ==============

class RecoveryPolicy(BaseModel):
    """Complete recovery policy configuration."""
    name: str
    description: Optional[str] = None
    strategies: List[Union[RetryStrategy, FallbackStrategy, CircuitBreakerStrategy]]
    error_aggregation_enabled: bool = True
    health_check_interval_seconds: float = Field(ge=0, default=30.0)
    max_total_duration_seconds: float = Field(ge=0, default=300.0)
    
    def get_strategies_by_priority(self) -> List[RecoveryStrategy]:
        """Get strategies sorted by priority."""
        return sorted(self.strategies, key=lambda s: s.priority, reverse=True)