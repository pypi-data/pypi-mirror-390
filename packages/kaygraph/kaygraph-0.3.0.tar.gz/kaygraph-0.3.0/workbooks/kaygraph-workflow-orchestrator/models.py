"""
Pydantic models for orchestrator workflows.
These define structured data for task orchestration and coordination.
"""

from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============== Task Definition Models ==============

class TaskType(str, Enum):
    """Types of tasks that can be orchestrated."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    TRANSFORMATION = "transformation"
    VALIDATION = "validation"
    AGGREGATION = "aggregation"
    REVIEW = "review"


class TaskPriority(str, Enum):
    """Task priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class SubTask(BaseModel):
    """Individual task definition."""
    task_id: str = Field(description="Unique task identifier")
    task_type: TaskType
    description: str = Field(description="What this task should accomplish")
    requirements: Dict[str, Any] = Field(default_factory=dict, description="Task requirements")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs this depends on")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    estimated_duration_minutes: Optional[int] = None
    assigned_worker: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TaskResult(BaseModel):
    """Result from task execution."""
    task_id: str
    status: TaskStatus
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_seconds: float
    worker_id: str
    artifacts: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


# ============== Orchestration Plan Models ==============

class OrchestratorPlan(BaseModel):
    """Complete orchestration plan."""
    plan_id: str
    objective: str = Field(description="Overall objective")
    analysis: str = Field(description="Analysis of the task")
    strategy: str = Field(description="Execution strategy")
    tasks: List[SubTask] = Field(description="List of tasks to execute")
    expected_duration_minutes: int
    resource_requirements: Dict[str, Any] = Field(default_factory=dict)
    
    @validator('tasks')
    def validate_dependencies(cls, tasks):
        """Ensure all dependencies exist."""
        task_ids = {t.task_id for t in tasks}
        for task in tasks:
            for dep in task.dependencies:
                if dep not in task_ids:
                    raise ValueError(f"Task {task.task_id} depends on non-existent task {dep}")
        return tasks


# ============== Blog Orchestration Models ==============

class BlogSection(BaseModel):
    """Blog section definition."""
    section_type: str = Field(description="Type of section (intro, body, conclusion, etc.)")
    title: str = Field(description="Section title")
    description: str = Field(description="What this section should cover")
    style_guide: str = Field(description="Writing style guidelines")
    target_length_words: int = Field(ge=50, le=2000)
    key_points: List[str] = Field(default_factory=list)
    
    
class BlogStructure(BaseModel):
    """Complete blog structure plan."""
    topic: str
    target_audience: str
    tone: str = Field(description="Writing tone (formal, casual, technical, etc.)")
    sections: List[BlogSection]
    total_target_words: int
    seo_keywords: List[str] = Field(default_factory=list)
    

class SectionContent(BaseModel):
    """Content for a blog section."""
    section_type: str
    title: str
    content: str
    word_count: int
    key_points_covered: List[str]
    transitions: Dict[str, str] = Field(default_factory=dict, description="Transitions to other sections")


class BlogReview(BaseModel):
    """Blog review and improvement suggestions."""
    cohesion_score: float = Field(ge=0, le=1, description="Overall cohesion score")
    readability_score: float = Field(ge=0, le=1)
    suggested_edits: List[Dict[str, str]] = Field(default_factory=list)
    final_version: str
    seo_optimization_notes: Optional[str] = None


# ============== Report Generation Models ==============

class ReportSection(BaseModel):
    """Report section definition."""
    section_name: str
    data_sources: List[str] = Field(description="Data sources to use")
    analysis_type: str = Field(description="Type of analysis needed")
    visualization_requirements: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class ReportStructure(BaseModel):
    """Complete report structure."""
    title: str
    purpose: str
    sections: List[ReportSection]
    executive_summary_requirements: str
    appendices: List[str] = Field(default_factory=list)


class DataAnalysisResult(BaseModel):
    """Result from data analysis."""
    section_name: str
    findings: List[str]
    data_summary: Dict[str, Any]
    visualizations: List[str] = Field(default_factory=list, description="Paths or descriptions of visualizations")
    confidence_level: float = Field(ge=0, le=1)


class ReportResult(BaseModel):
    """Complete report result."""
    title: str
    executive_summary: str
    sections: List[DataAnalysisResult]
    conclusions: List[str]
    recommendations: List[str]
    appendices: Dict[str, Any] = Field(default_factory=dict)
    generation_timestamp: datetime = Field(default_factory=datetime.now)


# ============== Project Planning Models ==============

class ProjectTask(BaseModel):
    """Project task definition."""
    task_name: str
    description: str
    estimated_hours: float = Field(gt=0)
    required_skills: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    deliverables: List[str] = Field(default_factory=list)
    risk_level: Literal["low", "medium", "high"]


class ProjectPhase(BaseModel):
    """Project phase definition."""
    phase_name: str
    objectives: List[str]
    tasks: List[ProjectTask]
    duration_weeks: float = Field(gt=0)
    milestones: List[str] = Field(default_factory=list)


class ProjectPlan(BaseModel):
    """Complete project plan."""
    project_name: str
    objectives: List[str]
    phases: List[ProjectPhase]
    total_duration_weeks: float
    required_resources: Dict[str, int] = Field(default_factory=dict, description="Resource type to count")
    risk_assessment: Dict[str, str] = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)


# ============== Worker Assignment Models ==============

class WorkerCapability(BaseModel):
    """Worker capability definition."""
    worker_id: str
    capabilities: List[TaskType]
    current_load: int = Field(ge=0, description="Current number of assigned tasks")
    max_concurrent_tasks: int = Field(gt=0, default=3)
    specializations: List[str] = Field(default_factory=list)
    performance_score: float = Field(ge=0, le=1, default=0.8)


class WorkAssignment(BaseModel):
    """Work assignment to a worker."""
    assignment_id: str
    task_id: str
    worker_id: str
    assigned_at: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    context: Dict[str, Any] = Field(default_factory=dict, description="Context for task execution")


class WorkerPool(BaseModel):
    """Pool of available workers."""
    workers: List[WorkerCapability]
    total_capacity: int
    current_utilization: float = Field(ge=0, le=1)
    
    @validator('total_capacity', pre=False, always=True)
    def calculate_capacity(cls, v, values):
        """Calculate total capacity from workers."""
        if 'workers' in values:
            return sum(w.max_concurrent_tasks for w in values['workers'])
        return v
    
    @validator('current_utilization', pre=False, always=True)
    def calculate_utilization(cls, v, values):
        """Calculate current utilization."""
        if 'workers' in values:
            total_capacity = sum(w.max_concurrent_tasks for w in values['workers'])
            current_load = sum(w.current_load for w in values['workers'])
            return current_load / total_capacity if total_capacity > 0 else 0
        return v


# ============== Orchestration Execution Models ==============

class OrchestrationState(BaseModel):
    """Current state of orchestration."""
    plan: OrchestratorPlan
    task_queue: List[SubTask] = Field(default_factory=list)
    in_progress: List[WorkAssignment] = Field(default_factory=list)
    completed_tasks: List[TaskResult] = Field(default_factory=list)
    failed_tasks: List[TaskResult] = Field(default_factory=list)
    worker_pool: WorkerPool
    start_time: datetime = Field(default_factory=datetime.now)
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        total = len(self.plan.tasks)
        completed = len(self.completed_tasks)
        return (completed / total * 100) if total > 0 else 0
    
    @property
    def is_complete(self) -> bool:
        """Check if orchestration is complete."""
        return len(self.completed_tasks) + len(self.failed_tasks) == len(self.plan.tasks)


class OrchestrationResult(BaseModel):
    """Final result of orchestration."""
    plan_id: str
    status: Literal["success", "partial_success", "failed"]
    completed_tasks: int
    failed_tasks: int
    total_duration_seconds: float
    final_output: Any
    task_results: List[TaskResult]
    performance_metrics: Dict[str, float] = Field(default_factory=dict)