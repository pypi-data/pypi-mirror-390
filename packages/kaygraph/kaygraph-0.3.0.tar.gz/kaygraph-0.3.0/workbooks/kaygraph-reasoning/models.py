"""
Data models for reasoning workflows.
"""

from enum import Enum
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from datetime import datetime


# ============== Enums ==============

class ReasoningType(str, Enum):
    """Types of reasoning approaches."""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STEP_BY_STEP = "step_by_step"
    TREE_OF_THOUGHT = "tree_of_thought"
    SELF_REFLECTION = "self_reflection"
    MULTI_PATH = "multi_path"

class ProblemType(str, Enum):
    """Types of problems to solve."""
    MATH = "math"
    LOGIC = "logic"
    CODE = "code"
    DECISION = "decision"
    ANALYSIS = "analysis"
    CREATIVE = "creative"

class ThoughtStatus(str, Enum):
    """Status of a thought or reasoning step."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    FAILED = "failed"
    REVISED = "revised"

# ============== Reasoning Models ==============

class ThoughtStep(BaseModel):
    """A single step in the reasoning process."""
    id: str
    content: str
    reasoning_type: str = "analysis"
    confidence: float = Field(ge=0.0, le=1.0)
    dependencies: List[str] = Field(default_factory=list)
    status: ThoughtStatus = ThoughtStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class ReasoningPlan(BaseModel):
    """Plan for solving a problem."""
    problem: str
    problem_type: ProblemType
    approach: ReasoningType
    steps: List[ThoughtStep]
    current_step: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    iterations: int = 0
    max_iterations: int = 10

class ReasoningState(BaseModel):
    """Current state of the reasoning process."""
    plan: ReasoningPlan
    completed_steps: List[str] = Field(default_factory=list)
    thought_history: List[ThoughtStep] = Field(default_factory=list)
    insights: List[str] = Field(default_factory=list)
    final_answer: Optional[str] = None
    total_confidence: float = Field(ge=0.0, le=1.0, default=0.0)

# ============== Math Reasoning Models ==============

class MathProblem(BaseModel):
    """Mathematical problem representation."""
    description: str
    known_values: Dict[str, float]
    unknown_variable: str
    constraints: List[str] = Field(default_factory=list)
    problem_type: str = "algebra"  # algebra, geometry, probability, etc.

class MathStep(BaseModel):
    """A step in mathematical reasoning."""
    step_number: int
    description: str
    operation: str
    expression: str
    result: Optional[float] = None
    units: Optional[str] = None
    verified: bool = False

class MathSolution(BaseModel):
    """Complete mathematical solution."""
    problem: MathProblem
    steps: List[MathStep]
    final_answer: str
    verification_method: Optional[str] = None
    alternative_solutions: List[str] = Field(default_factory=list)

# ============== Logic Reasoning Models ==============

class LogicConstraint(BaseModel):
    """A constraint in a logic problem."""
    id: str
    description: str
    entities: List[str]
    relationship: str
    satisfied: Optional[bool] = None

class LogicState(BaseModel):
    """Current state of logic problem solving."""
    entities: Dict[str, Any]
    constraints: List[LogicConstraint]
    deductions: List[str] = Field(default_factory=list)
    contradictions: List[str] = Field(default_factory=list)
    solution_valid: Optional[bool] = None

# ============== Code Analysis Models ==============

class CodeIssue(BaseModel):
    """An issue found in code analysis."""
    severity: str  # error, warning, suggestion
    line_number: Optional[int] = None
    description: str
    fix_suggestion: Optional[str] = None

class CodeAnalysis(BaseModel):
    """Result of code analysis."""
    code_snippet: str
    language: str
    purpose: str
    issues: List[CodeIssue] = Field(default_factory=list)
    complexity_score: Optional[float] = None
    improvements: List[str] = Field(default_factory=list)
    test_cases: List[Dict[str, Any]] = Field(default_factory=list)

# ============== Decision Making Models ==============

class DecisionFactor(BaseModel):
    """A factor in decision making."""
    name: str
    description: str
    weight: float = Field(ge=0.0, le=1.0)
    score: Optional[float] = Field(ge=0.0, le=10.0, default=None)
    reasoning: Optional[str] = None

class DecisionOption(BaseModel):
    """An option in decision making."""
    id: str
    name: str
    description: str
    pros: List[str] = Field(default_factory=list)
    cons: List[str] = Field(default_factory=list)
    factors: List[DecisionFactor] = Field(default_factory=list)
    total_score: Optional[float] = None

class DecisionAnalysis(BaseModel):
    """Complete decision analysis."""
    question: str
    context: str
    options: List[DecisionOption]
    recommendation: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning_summary: str

# ============== Multi-Path Models ==============

class ReasoningPath(BaseModel):
    """A single reasoning path."""
    id: str
    description: str
    steps: List[ThoughtStep]
    confidence: float = Field(ge=0.0, le=1.0)
    result: Optional[str] = None
    abandoned: bool = False
    abandon_reason: Optional[str] = None

class MultiPathAnalysis(BaseModel):
    """Analysis using multiple reasoning paths."""
    problem: str
    paths: List[ReasoningPath]
    best_path_id: Optional[str] = None
    consensus_answer: Optional[str] = None
    disagreements: List[str] = Field(default_factory=list)

# ============== Self-Reflection Models ==============

class ReflectionPoint(BaseModel):
    """A point of self-reflection."""
    thought_id: str
    reflection: str
    issues_found: List[str] = Field(default_factory=list)
    corrections_made: List[str] = Field(default_factory=list)
    confidence_before: float
    confidence_after: float

class ReasoningReview(BaseModel):
    """Review of the reasoning process."""
    total_steps: int
    successful_steps: int
    failed_steps: int
    revisions_made: int
    reflection_points: List[ReflectionPoint]
    overall_quality: float = Field(ge=0.0, le=1.0)
    lessons_learned: List[str] = Field(default_factory=list)