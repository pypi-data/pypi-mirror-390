"""
Recovery nodes implementing resilient patterns.
These nodes demonstrate error handling, retries, and fallback strategies.
"""

import time
import json
import logging
import random
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta
from pydantic import ValidationError
from kaygraph import Node
from utils import call_llm
from models import (
    ErrorType, ErrorInfo, RetryStatus, RetryStrategy,
    FallbackResult, CircuitState, CircuitBreakerStatus,
    RecoveryResult, ServiceHealth, SystemHealth
)


# ============== Retry Pattern Nodes ==============

class RetryNode(Node):
    """
    Node with automatic retry on failure.
    Implements exponential backoff and configurable retry logic.
    """
    
    def __init__(
        self, 
        max_retries: int = 3,
        initial_backoff: float = 1.0,
        backoff_multiplier: float = 2.0,
        max_backoff: float = 30.0,
        *args, **kwargs
    ):
        # Don't pass max_retries to parent
        super().__init__(*args, **kwargs)
        self.retry_strategy = RetryStrategy(
            max_attempts=max_retries,
            initial_backoff=initial_backoff,
            backoff_multiplier=backoff_multiplier,
            max_backoff=max_backoff
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare input for processing."""
        return shared.get("input", "")
    
    def exec(self, prep_res: str) -> RecoveryResult:
        """Execute with retry logic."""
        retry_status = RetryStatus(
            attempts=0,
            max_attempts=self.retry_strategy.max_attempts,
            backoff_seconds=self.retry_strategy.initial_backoff
        )
        
        start_time = time.time()
        last_error = None
        
        while retry_status.attempts < retry_status.max_attempts:
            retry_status.attempts += 1
            
            try:
                # Simulate potential failure (30% chance)
                if random.random() < 0.3:
                    raise Exception("Simulated transient error")
                
                # Actual processing
                result = self._process_with_llm(prep_res)
                
                # Success!
                return RecoveryResult(
                    success=True,
                    result=result,
                    strategy_used="retry",
                    attempts_made=retry_status.attempts,
                    total_duration_seconds=time.time() - start_time
                )
                
            except Exception as e:
                last_error = ErrorInfo(
                    error_type=ErrorType.TRANSIENT,
                    message=str(e),
                    attempt_number=retry_status.attempts,
                    recoverable=True
                )
                retry_status.last_error = last_error
                
                self.logger.warning(
                    f"Attempt {retry_status.attempts} failed: {e}"
                )
                
                # Check if we should retry
                if retry_status.attempts < retry_status.max_attempts:
                    # Calculate backoff
                    backoff = min(
                        retry_status.backoff_seconds,
                        self.retry_strategy.max_backoff
                    )
                    self.logger.info(f"Retrying in {backoff:.1f} seconds...")
                    time.sleep(backoff)
                    
                    # Increase backoff for next attempt
                    retry_status.backoff_seconds *= self.retry_strategy.backoff_multiplier
        
        # All retries exhausted
        return RecoveryResult(
            success=False,
            error=last_error,
            strategy_used="retry",
            attempts_made=retry_status.attempts,
            total_duration_seconds=time.time() - start_time
        )
    
    def _process_with_llm(self, text: str) -> str:
        """Process text with LLM (may fail)."""
        prompt = f"Summarize this text in one sentence: {text}"
        return call_llm(prompt)
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: RecoveryResult) -> Optional[str]:
        """Store recovery result."""
        shared["recovery_result"] = exec_res
        
        if exec_res.success:
            shared["output"] = exec_res.result
            self.logger.info(f"Success after {exec_res.attempts_made} attempts")
        else:
            shared["error"] = exec_res.error
            self.logger.error("All retry attempts exhausted")
        
        return "success" if exec_res.success else "failure"


# ============== Fallback Pattern Nodes ==============

class FallbackNode(Node):
    """
    Node with fallback strategies.
    Tries multiple approaches in order of preference.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for processing."""
        return {
            "text": shared.get("input", ""),
            "user_info": shared.get("user_info", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> FallbackResult:
        """Execute with fallback chain."""
        text = prep_res["text"]
        
        # Try primary method: Full extraction
        try:
            result = self._extract_full_info(text)
            return FallbackResult(
                primary_failed=False,
                fallback_level=0,
                method_used="full_extraction",
                result=result,
                is_partial=False
            )
        except Exception as e:
            self.logger.warning(f"Primary method failed: {e}")
        
        # Fallback 1: Partial extraction
        try:
            result = self._extract_partial_info(text)
            return FallbackResult(
                primary_failed=True,
                fallback_level=1,
                method_used="partial_extraction",
                result=result,
                is_partial=True,
                missing_features=["age", "phone"]
            )
        except Exception as e:
            self.logger.warning(f"Fallback 1 failed: {e}")
        
        # Fallback 2: Basic extraction
        try:
            result = self._extract_basic_info(text)
            return FallbackResult(
                primary_failed=True,
                fallback_level=2,
                method_used="basic_extraction",
                result=result,
                is_partial=True,
                missing_features=["age", "phone", "email"]
            )
        except Exception as e:
            self.logger.warning(f"Fallback 2 failed: {e}")
        
        # Final fallback: Return raw text
        return FallbackResult(
            primary_failed=True,
            fallback_level=3,
            method_used="raw_text",
            result={"raw_text": text},
            is_partial=True,
            missing_features=["all_structured_data"]
        )
    
    def _extract_full_info(self, text: str) -> Dict[str, Any]:
        """Try to extract complete user information."""
        prompt = f"""Extract user information from this text:
{text}

Return JSON with: name, email, age, phone
All fields are required."""
        
        response = call_llm(prompt)
        data = json.loads(response.strip().strip("```json").strip("```"))
        
        # Validate all fields present
        required = ["name", "email", "age", "phone"]
        if not all(field in data for field in required):
            raise ValueError("Missing required fields")
        
        return data
    
    def _extract_partial_info(self, text: str) -> Dict[str, Any]:
        """Extract partial information."""
        prompt = f"""Extract any user information you can find:
{text}

Return JSON with available fields: name, email
Missing fields can be null."""
        
        response = call_llm(prompt)
        return json.loads(response.strip().strip("```json").strip("```"))
    
    def _extract_basic_info(self, text: str) -> Dict[str, Any]:
        """Extract just the name."""
        prompt = f"Extract any person's name from: {text}"
        name = call_llm(prompt).strip()
        return {"name": name}
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: FallbackResult) -> Optional[str]:
        """Store fallback result."""
        shared["fallback_result"] = exec_res
        shared["output"] = exec_res.result
        
        if exec_res.is_partial:
            self.logger.info(
                f"Used fallback level {exec_res.fallback_level}: {exec_res.method_used}"
            )
            if exec_res.missing_features:
                self.logger.warning(f"Missing features: {exec_res.missing_features}")
        
        return None


# ============== Circuit Breaker Pattern ==============

class CircuitBreakerNode(Node):
    """
    Node with circuit breaker pattern.
    Prevents cascading failures by blocking calls after threshold.
    """
    
    def __init__(
        self,
        failure_threshold: int = 3,
        success_threshold: int = 2,
        timeout_seconds: float = 30.0,
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout_seconds = timeout_seconds
        self.circuit_status = CircuitBreakerStatus(
            state=CircuitState.CLOSED,
            failure_count=0,
            success_count=0
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Check circuit state and prepare input."""
        if not self.circuit_status.can_attempt():
            raise RuntimeError(f"Circuit breaker is {self.circuit_status.state}")
        
        return shared.get("input", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Execute with circuit breaker protection."""
        try:
            # Simulate service that may fail
            if random.random() < 0.4:  # 40% failure rate
                raise Exception("Service unavailable")
            
            # Successful call
            result = f"Processed: {prep_res}"
            self._record_success()
            
            return {
                "success": True,
                "result": result,
                "circuit_state": self.circuit_status.state
            }
            
        except Exception as e:
            self._record_failure()
            
            return {
                "success": False,
                "error": str(e),
                "circuit_state": self.circuit_status.state
            }
    
    def _record_success(self):
        """Record successful call."""
        self.circuit_status.success_count += 1
        self.circuit_status.last_success_time = datetime.now()
        
        if self.circuit_status.state == CircuitState.HALF_OPEN:
            if self.circuit_status.success_count >= self.success_threshold:
                # Close circuit after enough successes
                self.logger.info("Circuit breaker closing (recovered)")
                self.circuit_status.state = CircuitState.CLOSED
                self.circuit_status.failure_count = 0
                self.circuit_status.success_count = 0
    
    def _record_failure(self):
        """Record failed call."""
        self.circuit_status.failure_count += 1
        self.circuit_status.last_failure_time = datetime.now()
        
        if self.circuit_status.state == CircuitState.CLOSED:
            if self.circuit_status.failure_count >= self.failure_threshold:
                # Open circuit after too many failures
                self.logger.warning("Circuit breaker opening (too many failures)")
                self.circuit_status.state = CircuitState.OPEN
                self.circuit_status.next_attempt_time = (
                    datetime.now() + timedelta(seconds=self.timeout_seconds)
                )
        elif self.circuit_status.state == CircuitState.HALF_OPEN:
            # Single failure in half-open state reopens circuit
            self.logger.warning("Circuit breaker reopening (failed in half-open)")
            self.circuit_status.state = CircuitState.OPEN
            self.circuit_status.next_attempt_time = (
                datetime.now() + timedelta(seconds=self.timeout_seconds)
            )
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store result and update circuit state."""
        shared["circuit_result"] = exec_res
        shared["circuit_state"] = self.circuit_status.state.value
        
        # Check if we should transition to half-open
        if (self.circuit_status.state == CircuitState.OPEN and
            self.circuit_status.next_attempt_time and
            datetime.now() >= self.circuit_status.next_attempt_time):
            self.logger.info("Circuit breaker moving to half-open")
            self.circuit_status.state = CircuitState.HALF_OPEN
            self.circuit_status.success_count = 0
            self.circuit_status.failure_count = 0
        
        return "success" if exec_res["success"] else "failure"


# ============== Graceful Degradation ==============

class GracefulDegradationNode(Node):
    """
    Node that degrades functionality gracefully.
    Provides partial results instead of complete failure.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> str:
        """Prepare request."""
        return shared.get("query", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        """Execute with graceful degradation."""
        results = {
            "full_analysis": None,
            "summary": None,
            "keywords": None,
            "basic_response": None,
            "features_available": []
        }
        
        # Try full analysis
        try:
            results["full_analysis"] = self._full_analysis(prep_res)
            results["features_available"].append("full_analysis")
        except Exception as e:
            self.logger.warning(f"Full analysis failed: {e}")
        
        # Try summary (less resource intensive)
        try:
            results["summary"] = self._generate_summary(prep_res)
            results["features_available"].append("summary")
        except Exception as e:
            self.logger.warning(f"Summary failed: {e}")
        
        # Try keyword extraction (even simpler)
        try:
            results["keywords"] = self._extract_keywords(prep_res)
            results["features_available"].append("keywords")
        except Exception as e:
            self.logger.warning(f"Keyword extraction failed: {e}")
        
        # Basic response (always works)
        results["basic_response"] = f"Received query about: {prep_res[:50]}..."
        results["features_available"].append("basic_response")
        
        # Determine degradation level
        feature_count = len(results["features_available"])
        if feature_count == 4:
            results["degradation_level"] = "none"
        elif feature_count == 3:
            results["degradation_level"] = "minimal"
        elif feature_count == 2:
            results["degradation_level"] = "moderate"
        else:
            results["degradation_level"] = "severe"
        
        return results
    
    def _full_analysis(self, query: str) -> str:
        """Perform full analysis (may fail)."""
        if random.random() < 0.3:
            raise Exception("Full analysis unavailable")
        
        prompt = f"""Provide a comprehensive analysis of: {query}
Include context, implications, and recommendations."""
        
        return call_llm(prompt)
    
    def _generate_summary(self, query: str) -> str:
        """Generate summary (more resilient)."""
        if random.random() < 0.2:
            raise Exception("Summary service down")
        
        return f"Summary: This query is about {query[:30]}..."
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords (very resilient)."""
        if random.random() < 0.1:
            raise Exception("Keyword service error")
        
        # Simple keyword extraction
        words = query.lower().split()
        keywords = [w for w in words if len(w) > 4][:5]
        return keywords
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        """Store degraded results."""
        shared["degradation_result"] = exec_res
        shared["degradation_level"] = exec_res["degradation_level"]
        
        self.logger.info(
            f"Completed with {exec_res['degradation_level']} degradation. "
            f"Features available: {exec_res['features_available']}"
        )
        
        return None


# ============== Error Aggregation ==============

class ErrorAggregationNode(Node):
    """
    Node that aggregates errors for analysis.
    Helps identify patterns and systemic issues.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.error_history = []
    
    def prep(self, shared: Dict[str, Any]) -> List[str]:
        """Get batch of items to process."""
        return shared.get("batch_items", [])
    
    def exec(self, prep_res: List[str]) -> Dict[str, Any]:
        """Process batch and aggregate errors."""
        results = []
        errors = []
        
        for i, item in enumerate(prep_res):
            try:
                # Process item (20% failure rate)
                if random.random() < 0.2:
                    error_type = random.choice(list(ErrorType))
                    raise Exception(f"{error_type} error for item {i}")
                
                result = f"Processed: {item}"
                results.append({"index": i, "success": True, "result": result})
                
            except Exception as e:
                error_info = ErrorInfo(
                    error_type=ErrorType.TRANSIENT,
                    message=str(e),
                    attempt_number=1,
                    recoverable=True,
                    details={"item_index": i, "item": item}
                )
                errors.append(error_info)
                self.error_history.append(error_info)
                results.append({"index": i, "success": False, "error": str(e)})
        
        # Analyze error patterns
        error_analysis = self._analyze_errors(errors)
        
        return {
            "total_items": len(prep_res),
            "successful": len([r for r in results if r["success"]]),
            "failed": len(errors),
            "results": results,
            "error_analysis": error_analysis
        }
    
    def _analyze_errors(self, errors: List[ErrorInfo]) -> Dict[str, Any]:
        """Analyze error patterns."""
        if not errors:
            return {"patterns": "No errors to analyze"}
        
        # Count by type
        type_counts = {}
        for error in errors:
            type_counts[error.error_type] = type_counts.get(error.error_type, 0) + 1
        
        # Find most common
        most_common = max(type_counts.items(), key=lambda x: x[1])
        
        return {
            "error_types": type_counts,
            "most_common_type": most_common[0],
            "error_rate": len(errors) / len(self.error_history) if self.error_history else 0,
            "recent_trend": "increasing" if len(errors) > 2 else "stable"
        }
    
    def post(self, shared: Dict[str, Any], prep_res: List, exec_res: Dict) -> Optional[str]:
        """Store aggregated results."""
        shared["batch_result"] = exec_res
        
        self.logger.info(
            f"Batch complete: {exec_res['successful']}/{exec_res['total_items']} successful"
        )
        
        if exec_res["failed"] > 0:
            self.logger.warning(
                f"Error analysis: {exec_res['error_analysis']}"
            )
        
        return None


# ============== Health Check Node ==============

class HealthCheckNode(Node):
    """
    Node that performs health checks on services.
    Used for monitoring and proactive recovery.
    """
    
    def __init__(self, services: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.services = services
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> List[str]:
        """Prepare services to check."""
        return self.services
    
    def exec(self, prep_res: List[str]) -> SystemHealth:
        """Check health of all services."""
        service_healths = {}
        
        for service in prep_res:
            health = self._check_service_health(service)
            service_healths[service] = health
        
        return SystemHealth(
            services=service_healths,
            overall_health=all(h.healthy for h in service_healths.values())
        )
    
    def _check_service_health(self, service_name: str) -> ServiceHealth:
        """Check individual service health."""
        start_time = time.time()
        
        try:
            # Simulate service check (80% healthy)
            if random.random() < 0.8:
                response_time = random.uniform(10, 100)
                return ServiceHealth(
                    service_name=service_name,
                    healthy=True,
                    response_time_ms=response_time
                )
            else:
                raise Exception(f"{service_name} is not responding")
                
        except Exception as e:
            return ServiceHealth(
                service_name=service_name,
                healthy=False,
                error_message=str(e),
                response_time_ms=(time.time() - start_time) * 1000
            )
    
    def post(self, shared: Dict[str, Any], prep_res: List, exec_res: SystemHealth) -> Optional[str]:
        """Store health check results."""
        shared["system_health"] = exec_res
        
        if exec_res.overall_health:
            self.logger.info("All services healthy")
        else:
            self.logger.warning(
                f"Degraded services: {exec_res.degraded_services}"
            )
        
        return "healthy" if exec_res.overall_health else "degraded"