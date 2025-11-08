"""
Advanced declarative workflow nodes for KayGraph.

Provides sophisticated patterns for enterprise-grade workflows including:
- Advanced template engine with Jinja2 support
- Dynamic orchestration with AI-driven planning
- Circuit breaker pattern for reliability
- Tool registry for dynamic function calling
- Intelligent caching system
"""

import re
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from kaygraph import Node, ValidatedNode, AsyncNode
import logging

# Try to import advanced libraries
try:
    from jinja2 import Template, Environment, BaseLoader
    HAS_JINJA2 = True
except ImportError:
    HAS_JINJA2 = False

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logger = logging.getLogger(__name__)


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    failures: int = 0
    successes: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    consecutive_failures: int = 0


class CircuitBreakerNode(ValidatedNode):
    """
    Circuit breaker pattern implementation for fault tolerance.

    Protects downstream services from cascading failures and provides
    graceful degradation when services are unavailable.
    """

    def __init__(self,
                 failure_threshold: int = 5,
                 recovery_timeout: float = 60.0,
                 half_open_max_calls: int = 3,
                 expected_recovery_time: float = 30.0,
                 node_id: Optional[str] = None, **kwargs):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying recovery
            half_open_max_calls: Max calls allowed in half-open state
            expected_recovery_time: Expected time for service recovery
            node_id: Optional node identifier
            **kwargs: Additional arguments
        """
        super().__init__(node_id=node_id or "circuit_breaker", **kwargs)

        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        self.expected_recovery_time = expected_recovery_time

        self._state = CircuitBreakerState.CLOSED
        self._metrics = CircuitBreakerMetrics()
        self._half_open_calls = 0
        self._last_state_change = time.time()

    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state."""
        return self._state

    @property
    def metrics(self) -> CircuitBreakerMetrics:
        """Get circuit breaker metrics."""
        return self._metrics

    def _should_attempt_reset(self) -> bool:
        """Check if circuit should be reset to half-open."""
        return (
            self._state == CircuitBreakerState.OPEN and
            time.time() - self._last_state_change >= self.recovery_timeout
        )

    def _record_success(self):
        """Record a successful call."""
        self._metrics.successes += 1
        self._metrics.last_success_time = time.time()
        self._metrics.consecutive_failures = 0

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.CLOSED
            self._half_open_calls = 0
            self.logger.info("Circuit breaker closed after successful call")

    def _record_failure(self):
        """Record a failed call."""
        self._metrics.failures += 1
        self._metrics.last_failure_time = time.time()
        self._metrics.consecutive_failures += 1

        if self._state == CircuitBreakerState.HALF_OPEN:
            self._state = CircuitBreakerState.OPEN
            self._last_state_change = time.time()
            self.logger.warning("Circuit breaker opened after failure in half-open state")
        elif (self._state == CircuitBreakerState.CLOSED and
              self._metrics.consecutive_failures >= self.failure_threshold):
            self._state = CircuitBreakerState.OPEN
            self._last_state_change = time.time()
            self.logger.warning(f"Circuit breaker opened after {self.failure_threshold} consecutive failures")

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Check circuit state and prepare execution."""
        # Reset to half-open if recovery timeout passed
        if self._should_attempt_reset():
            self._state = CircuitBreakerState.HALF_OPEN
            self._half_open_calls = 0
            self.logger.info("Circuit breaker transitioning to half-open state")

        # Reject calls if circuit is open
        if self._state == CircuitBreakerState.OPEN:
            raise Exception(f"Circuit breaker is OPEN (since {time.time() - self._last_state_change:.1f}s ago)")

        # Limit calls in half-open state
        if self._state == CircuitBreakerState.HALF_OPEN:
            if self._half_open_calls >= self.half_open_max_calls:
                raise Exception(f"Circuit breaker is HALF-OPEN (max calls {self.half_open_max_calls} reached)")

        return shared

    def exec(self, shared: Dict[str, Any]) -> Any:
        """Execute the protected operation."""
        if self._state == CircuitBreakerState.HALF_OPEN:
            self._half_open_calls += 1

        # In a real implementation, this would call the protected service
        # For demo, we'll simulate success/failure based on shared state
        should_fail = shared.get("simulate_failure", False)

        if should_fail:
            raise Exception("Simulated service failure")

        # Simulate processing time
        time.sleep(0.1)

        return {
            "result": "Operation successful",
            "timestamp": time.time(),
            "circuit_state": self._state.value
        }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Record result and update circuit state."""
        if exec_res and "result" in exec_res:
            self._record_success()
            shared["circuit_breaker_result"] = exec_res
        else:
            self._record_failure()
            shared["circuit_breaker_error"] = str(exec_res) if exec_res else "Unknown error"

        # Store metrics in shared state
        shared["circuit_breaker_metrics"] = {
            "state": self._state.value,
            "successes": self._metrics.successes,
            "failures": self._metrics.failures,
            "consecutive_failures": self._metrics.consecutive_failures,
            "success_rate": (
                self._metrics.successes /
                max(1, self._metrics.successes + self._metrics.failures)
            )
        }

        return "default"


class ToolRegistryNode(ValidatedNode):
    """
    Dynamic tool registry for function calling and integration.

    Manages a registry of tools/functions that can be called dynamically
    during workflow execution, with automatic discovery and validation.
    """

    def __init__(self,
                 tools: Optional[Dict[str, Any]] = None,
                 auto_discover: bool = False,
                 node_id: Optional[str] = None, **kwargs):
        """
        Initialize tool registry.

        Args:
            tools: Dictionary of available tools
            auto_discover: Whether to auto-discover tools from shared state
            node_id: Optional node identifier
            **kwargs: Additional arguments
        """
        super().__init__(node_id=node_id or "tool_registry", **kwargs)

        self.tools = tools or {}
        self.auto_discover = auto_discover
        self._discovered_tools = {}

    def register_tool(self, name: str, tool_func: Callable, **metadata):
        """Register a tool with the registry."""
        self.tools[name] = {
            "function": tool_func,
            "metadata": metadata,
            "registered_at": time.time()
        }
        logger.info(f"Registered tool: {name}")

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare tools and execution context."""
        tool_calls = shared.get("tool_calls", [])

        # Auto-discover tools if enabled
        if self.auto_discover:
            self._discover_tools(shared)

        # Merge discovered tools
        all_tools = {**self.tools, **self._discovered_tools}

        return {
            "tool_calls": tool_calls,
            "available_tools": list(all_tools.keys()),
            "tools": all_tools,
            "context": shared
        }

    def exec(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute tool calls."""
        tool_calls = context["tool_calls"]
        tools = context["tools"]
        results = []

        for tool_call in tool_calls:
            tool_name = tool_call.get("tool")
            parameters = tool_call.get("parameters", {})

            if tool_name not in tools:
                error_result = {
                    "tool": tool_name,
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                    "available_tools": list(tools.keys())
                }
                results.append(error_result)
                continue

            try:
                tool_info = tools[tool_name]
                tool_func = tool_info["function"]

                # Execute tool
                if asyncio.iscoroutinefunction(tool_func):
                    # Async tool (not supported in sync mode)
                    result = f"Async tool '{tool_name}' not supported in sync mode"
                else:
                    result = tool_func(**parameters)

                success_result = {
                    "tool": tool_name,
                    "success": True,
                    "result": result,
                    "parameters": parameters,
                    "metadata": tool_info.get("metadata", {})
                }
                results.append(success_result)

            except Exception as e:
                error_result = {
                    "tool": tool_name,
                    "success": False,
                    "error": str(e),
                    "parameters": parameters
                }
                results.append(error_result)
                logger.error(f"Tool '{tool_name}' execution failed: {e}")

        return results

    def _discover_tools(self, shared: Dict[str, Any]):
        """Auto-discover tools from shared state."""
        # Look for functions in shared state
        for key, value in shared.items():
            if callable(value) and not key.startswith("_"):
                self._discovered_tools[key] = {
                    "function": value,
                    "metadata": {"discovered": True, "source": "shared_state"},
                    "registered_at": time.time()
                }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store tool execution results."""
        shared["tool_results"] = exec_res
        shared["tool_execution_summary"] = {
            "total_calls": len(exec_res),
            "successful_calls": sum(1 for r in exec_res if r.get("success", False)),
            "failed_calls": sum(1 for r in exec_res if not r.get("success", False)),
            "tools_used": list(set(r.get("tool") for r in exec_res if r.get("success")))
        }

        return "default"


class SimplePlannerNode(Node):
    """
    LLM-driven task planning without complex execution infrastructure.

    This simplified planner focuses on what LLMs do best: breaking down
    objectives into structured task lists. The actual execution is handled
    by KayGraph's existing parallel/batch capabilities.

    Perfect for LLM-driven workflow creation where the LLM generates
    the plan and KayGraph executes it.
    """

    def __init__(self,
                 objective_key: str = "objective",
                 node_id: Optional[str] = None, **kwargs):
        """
        Initialize simple planner.

        Args:
            objective_key: Key in shared store containing the objective
            node_id: Optional node identifier
            **kwargs: Additional arguments
        """
        super().__init__(node_id=node_id or "planner", **kwargs)
        self.objective_key = objective_key

    def prep(self, shared: Dict[str, Any]) -> str:
        """Get objective from shared store."""
        return shared.get(self.objective_key, "")

    def exec(self, objective: str) -> Dict[str, Any]:
        """Use LLM to break down objective into tasks."""
        if not objective:
            return {"tasks": [], "error": "No objective provided"}

        planning_prompt = f"""
        Break down this objective into specific, actionable tasks:
        {objective}

        Return a JSON list of tasks with this structure:
        {{
            "tasks": [
                {{
                    "id": "task_1",
                    "description": "Specific task description",
                    "type": "llm_call" | "data_transform" | "validation" | "api_call",
                    "dependencies": []
                }}
            ]
        }}

        Keep tasks:
        - Specific and actionable
        - Ordered by dependencies
        - Focused on single responsibilities
        """

        try:
            from utils.call_llm import extract_json
            plan = extract_json(planning_prompt)
            return plan
        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Return simple fallback plan
            return {
                "tasks": [
                    {
                        "id": "task_1",
                        "description": objective,
                        "type": "llm_call",
                        "dependencies": []
                    }
                ]
            }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store task plan in shared store."""
        shared["task_plan"] = exec_res.get("tasks", [])
        shared["planning_complete"] = True

        return "default"


class SimpleCacheNode(Node):
    """
    Simple in-memory caching for LLM calls and expensive operations.

    Zero dependencies, LRU eviction, perfect for reducing redundant
    LLM API calls (which cost real money!).

    LLMs can easily configure cache behavior through simple parameters:
    - max_size: Maximum number of cached items
    - cache_key_fields: Which fields to use for cache key generation
    """

    def __init__(self,
                 max_size: int = 100,
                 cache_key_fields: Optional[List[str]] = None,
                 node_id: Optional[str] = None, **kwargs):
        """
        Initialize simple cache.

        Args:
            max_size: Maximum number of cached items (LRU eviction)
            cache_key_fields: Fields to include in cache key (default: all)
            node_id: Optional node identifier
            **kwargs: Additional arguments
        """
        super().__init__(node_id=node_id or "cache", **kwargs)
        self.max_size = max_size
        self.cache_key_fields = cache_key_fields

        self._cache = {}
        self._access_order = []  # Track access order for LRU

    def _make_cache_key(self, data: Any) -> str:
        """Generate cache key from data."""
        import hashlib
        import json

        if isinstance(data, dict):
            # Use only specified fields if provided
            if self.cache_key_fields:
                filtered_data = {k: data[k] for k in self.cache_key_fields if k in data}
            else:
                filtered_data = data

            # Sort keys for consistent hashing
            key_str = json.dumps(filtered_data, sort_keys=True)
        else:
            key_str = str(data)

        return hashlib.md5(key_str.encode()).hexdigest()

    def _evict_lru(self):
        """Evict least recently used item."""
        if self._access_order:
            lru_key = self._access_order.pop(0)
            self._cache.pop(lru_key, None)

    def prep(self, shared: Dict[str, Any]) -> Any:
        """Get cache input from shared store."""
        return shared.get("cache_input")

    def exec(self, cache_input: Any) -> Dict[str, Any]:
        """Check cache, return cached value or mark as cache miss."""
        if cache_input is None:
            return {"cache_hit": False, "result": None}

        cache_key = self._make_cache_key(cache_input)

        # Check cache
        if cache_key in self._cache:
            # Update access order (move to end = most recently used)
            self._access_order.remove(cache_key)
            self._access_order.append(cache_key)

            return {
                "cache_hit": True,
                "result": self._cache[cache_key],
                "cache_key": cache_key
            }

        # Cache miss - result will be stored by post() after computation
        return {
            "cache_hit": False,
            "result": None,
            "cache_key": cache_key
        }

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: Any) -> str:
        """Store cache miss results if computation was done."""
        cache_result = exec_res

        # If cache miss and computation result is available, store it
        if not cache_result["cache_hit"] and "computed_result" in shared:
            cache_key = cache_result["cache_key"]
            computed_result = shared["computed_result"]

            # Evict if at max size
            if len(self._cache) >= self.max_size:
                self._evict_lru()

            # Store in cache
            self._cache[cache_key] = computed_result
            self._access_order.append(cache_key)

        # Store cache stats
        shared["cache_result"] = cache_result
        shared["cache_stats"] = {
            "size": len(self._cache),
            "max_size": self.max_size,
            "hit_rate": self._calculate_hit_rate()
        }

        return "default"

    def _calculate_hit_rate(self) -> float:
        """Calculate cache hit rate (simplified)."""
        # In production, track hits/misses over time
        # For simplicity, just return cache utilization
        if self.max_size == 0:
            return 0.0
        return len(self._cache) / self.max_size


# Factory function for creating advanced nodes
def create_advanced_node(node_type: str, config: Dict[str, Any], **kwargs) -> Node:
    """
    Create an advanced node from configuration.

    Args:
        node_type: Type of advanced node to create
        config: Configuration for the node
        **kwargs: Additional parameters

    Returns:
        Configured advanced node instance
    """
    if node_type == "circuit_breaker":
        return CircuitBreakerNode(**config, **kwargs)
    elif node_type == "advanced_template":
        return AdvancedTemplateNode(**config, **kwargs)
    elif node_type == "tool_registry":
        return ToolRegistryNode(**config, **kwargs)
    elif node_type == "dynamic_orchestrator":
        return DynamicOrchestratorNode(**config, **kwargs)
    elif node_type == "intelligent_cache":
        return IntelligentCacheNode(**config, **kwargs)
    else:
        raise ValueError(f"Unknown advanced node type: {node_type}")


# Built-in tools for the tool registry
def web_search_tool(query: str, max_results: int = 10) -> Dict[str, Any]:
    """Built-in web search tool (simulated)."""
    return {
        "query": query,
        "results": [
            {"title": f"Result {i+1} for '{query}'", "url": f"https://example.com/{i}"}
            for i in range(min(max_results, 3))
        ],
        "total_results": max_results
    }


def data_analysis_tool(data: List[Dict[str, Any]], analysis_type: str = "summary") -> Dict[str, Any]:
    """Built-in data analysis tool."""
    if not data:
        return {"error": "No data provided for analysis"}

    if analysis_type == "summary":
        return {
            "count": len(data),
            "keys": list(data[0].keys()) if data else [],
            "sample": data[0] if data else None
        }
    else:
        return {"error": f"Analysis type '{analysis_type}' not implemented"}


# Register built-in tools
BUILTIN_TOOLS = {
    "web_search": web_search_tool,
    "data_analysis": data_analysis_tool
}