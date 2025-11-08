"""
Pydantic models for control flow patterns.
These define the structured data used in routing decisions.
"""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, validator


# ============== Intent Classification Models ==============

class IntentClassification(BaseModel):
    """Basic intent classification result."""
    intent: Literal["question", "request", "complaint", "statement", "unknown"]
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    sub_category: Optional[str] = None
    
    @validator('confidence')
    def round_confidence(cls, v):
        """Round to 2 decimal places."""
        return round(v, 2)


class DetailedIntent(BaseModel):
    """More detailed intent analysis."""
    primary_intent: str
    secondary_intents: List[str] = Field(default_factory=list)
    entities: Dict[str, Any] = Field(default_factory=dict)
    sentiment: Literal["positive", "negative", "neutral"]
    urgency: Literal["low", "medium", "high", "critical"]
    complexity: Literal["simple", "moderate", "complex"]


# ============== Routing Decision Models ==============

class RoutingDecision(BaseModel):
    """Routing decision based on control logic."""
    route: str = Field(description="The chosen route/handler")
    reason: str = Field(description="Why this route was chosen")
    confidence: float = Field(ge=0, le=1)
    alternatives: List[Dict[str, float]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PriorityRouting(BaseModel):
    """Priority-based routing decision."""
    priority_level: Literal["p0", "p1", "p2", "p3", "p4"]
    handler: str
    estimated_time: int = Field(description="Estimated handling time in minutes")
    escalation_required: bool = False
    reason: str


# ============== Decision Tree Models ==============

class DecisionCriteria(BaseModel):
    """Criteria for decision tree evaluation."""
    criterion: str
    value: Any
    met: bool
    weight: float = Field(ge=0, le=1, default=1.0)


class DecisionNode(BaseModel):
    """Node in a decision tree."""
    node_id: str
    question: str
    criteria: List[DecisionCriteria]
    yes_path: Optional[str] = None
    no_path: Optional[str] = None
    action: Optional[str] = None
    is_leaf: bool = False


class DecisionResult(BaseModel):
    """Result of decision tree traversal."""
    path_taken: List[str]
    final_action: str
    criteria_evaluated: List[DecisionCriteria]
    confidence: float = Field(ge=0, le=1)


# ============== Multi-Criteria Control Models ==============

class ControlFactor(BaseModel):
    """Individual control factor for multi-criteria decisions."""
    factor_name: str
    value: Any
    normalized_score: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    
    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution."""
        return self.normalized_score * self.weight


class MultiCriteriaDecision(BaseModel):
    """Decision based on multiple weighted factors."""
    factors: List[ControlFactor]
    total_score: float = Field(ge=0, le=1)
    decision: str
    reasoning: str
    threshold_met: bool
    
    @validator('total_score', pre=False, always=True)
    def calculate_total(cls, v, values):
        """Calculate total from factors if not provided."""
        if 'factors' in values and values['factors']:
            total = sum(f.weighted_score for f in values['factors'])
            # Normalize if weights don't sum to 1
            weight_sum = sum(f.weight for f in values['factors'])
            if weight_sum > 0:
                return total / weight_sum
        return v


# ============== Threshold Control Models ==============

class ThresholdCheck(BaseModel):
    """Threshold-based control check."""
    metric_name: str
    current_value: float
    threshold: float
    comparison: Literal["greater", "less", "equal"]
    passed: bool
    action_if_passed: str
    action_if_failed: str
    
    @validator('passed', pre=False, always=True)
    def check_threshold(cls, v, values):
        """Automatically check if threshold is met."""
        if all(k in values for k in ['current_value', 'threshold', 'comparison']):
            current = values['current_value']
            threshold = values['threshold']
            comparison = values['comparison']
            
            if comparison == "greater":
                return current > threshold
            elif comparison == "less":
                return current < threshold
            else:  # equal
                return abs(current - threshold) < 0.001
        return v


class ThresholdDecision(BaseModel):
    """Decision based on multiple threshold checks."""
    checks: List[ThresholdCheck]
    all_must_pass: bool = False
    final_action: str
    passed_count: int
    total_count: int
    
    @validator('passed_count', pre=False, always=True)
    def count_passed(cls, v, values):
        """Count how many checks passed."""
        if 'checks' in values:
            return sum(1 for check in values['checks'] if check.passed)
        return 0
    
    @validator('total_count', pre=False, always=True)
    def count_total(cls, v, values):
        """Count total checks."""
        if 'checks' in values:
            return len(values['checks'])
        return 0


# ============== Conditional Routing Models ==============

class Condition(BaseModel):
    """Single condition for evaluation."""
    field: str
    operator: Literal["eq", "ne", "gt", "lt", "gte", "lte", "contains", "in"]
    value: Any
    result: Optional[bool] = None


class ConditionalRoute(BaseModel):
    """Route with conditions."""
    route_name: str
    conditions: List[Condition]
    require_all: bool = True
    priority: int = Field(ge=0, default=0)
    handler: str
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate if conditions are met given context."""
        results = []
        for condition in self.conditions:
            field_value = context.get(condition.field)
            
            if condition.operator == "eq":
                result = field_value == condition.value
            elif condition.operator == "ne":
                result = field_value != condition.value
            elif condition.operator == "gt":
                result = field_value > condition.value
            elif condition.operator == "lt":
                result = field_value < condition.value
            elif condition.operator == "gte":
                result = field_value >= condition.value
            elif condition.operator == "lte":
                result = field_value <= condition.value
            elif condition.operator == "contains":
                result = condition.value in str(field_value)
            elif condition.operator == "in":
                result = field_value in condition.value
            else:
                result = False
                
            condition.result = result
            results.append(result)
        
        if self.require_all:
            return all(results)
        else:
            return any(results)


# ============== State Machine Models ==============

class StateTransition(BaseModel):
    """State machine transition."""
    from_state: str
    to_state: str
    trigger: str
    conditions: List[Condition] = Field(default_factory=list)
    actions: List[str] = Field(default_factory=list)


class StateMachine(BaseModel):
    """Simple state machine for control flow."""
    current_state: str
    states: List[str]
    transitions: List[StateTransition]
    history: List[str] = Field(default_factory=list)
    
    def can_transition(self, trigger: str, context: Dict[str, Any]) -> Optional[str]:
        """Check if transition is possible."""
        for transition in self.transitions:
            if (transition.from_state == self.current_state and 
                transition.trigger == trigger):
                # Check conditions if any
                if transition.conditions:
                    route = ConditionalRoute(
                        route_name="temp",
                        conditions=transition.conditions,
                        require_all=True,
                        handler=""
                    )
                    if route.evaluate(context):
                        return transition.to_state
                else:
                    return transition.to_state
        return None