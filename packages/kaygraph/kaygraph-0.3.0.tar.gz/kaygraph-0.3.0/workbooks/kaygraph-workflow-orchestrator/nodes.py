"""
Orchestrator nodes implementing complex task coordination patterns.
These nodes demonstrate orchestrator-worker patterns for managing multi-step workflows.
"""

import time
import json
import logging
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from kaygraph import Node
from utils import call_llm
from models import (
    TaskType, TaskPriority, TaskStatus,
    SubTask, TaskResult, OrchestratorPlan,
    BlogSection, BlogStructure, SectionContent, BlogReview,
    ReportSection, ReportStructure, DataAnalysisResult, ReportResult,
    ProjectTask, ProjectPhase, ProjectPlan,
    WorkerCapability, WorkAssignment, WorkerPool,
    OrchestrationState, OrchestrationResult
)


# ============== Orchestrator Nodes ==============

class BlogOrchestratorNode(Node):
    """
    Orchestrates blog writing workflow.
    Plans structure and coordinates section writing.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare blog requirements."""
        return {
            "topic": shared.get("topic", ""),
            "target_length": shared.get("target_length", 1000),
            "style": shared.get("style", "informative"),
            "target_audience": shared.get("target_audience", "general")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> BlogStructure:
        """Plan blog structure."""
        topic = prep_res["topic"]
        target_length = prep_res["target_length"]
        style = prep_res["style"]
        
        system = """You are a blog content strategist. Analyze the topic and create a detailed blog structure.
Return JSON with:
- topic: The blog topic
- target_audience: Who this is for
- tone: Writing tone
- sections: Array of sections, each with:
  - section_type: intro/body/conclusion/etc
  - title: Section title
  - description: What to cover
  - style_guide: Writing style
  - target_length_words: Word count
  - key_points: Array of key points to cover
- total_target_words: Total word count
- seo_keywords: Array of SEO keywords"""
        
        prompt = f"""Create a blog structure for:
Topic: {topic}
Target Length: {target_length} words
Style: {style}
Target Audience: {prep_res['target_audience']}"""
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            
            # Create sections
            sections = []
            for section_data in data.get("sections", []):
                sections.append(BlogSection(**section_data))
            
            return BlogStructure(
                topic=data.get("topic", topic),
                target_audience=data.get("target_audience", "general"),
                tone=data.get("tone", style),
                sections=sections,
                total_target_words=data.get("total_target_words", target_length),
                seo_keywords=data.get("seo_keywords", [])
            )
        except Exception as e:
            self.logger.error(f"Failed to parse blog structure: {e}")
            # Return default structure
            return BlogStructure(
                topic=topic,
                target_audience="general",
                tone=style,
                sections=[
                    BlogSection(
                        section_type="intro",
                        title="Introduction",
                        description="Introduce the topic",
                        style_guide=style,
                        target_length_words=200
                    ),
                    BlogSection(
                        section_type="body",
                        title="Main Content",
                        description="Cover main points",
                        style_guide=style,
                        target_length_words=600
                    ),
                    BlogSection(
                        section_type="conclusion",
                        title="Conclusion",
                        description="Summarize key points",
                        style_guide=style,
                        target_length_words=200
                    )
                ],
                total_target_words=target_length
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: BlogStructure) -> Optional[str]:
        """Store blog structure for workers."""
        shared["blog_structure"] = exec_res
        shared["sections_to_write"] = exec_res.sections
        shared["written_sections"] = {}
        
        self.logger.info(f"Blog structure planned: {len(exec_res.sections)} sections")
        
        return None


class BlogWriterNode(Node):
    """
    Worker node that writes individual blog sections.
    Context-aware writing based on previous sections.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Tuple[BlogSection, Dict[str, SectionContent]]:
        """Get next section to write and context."""
        sections_to_write = shared.get("sections_to_write", [])
        written_sections = shared.get("written_sections", {})
        
        if not sections_to_write:
            return None, written_sections
        
        # Get next section
        next_section = sections_to_write[0]
        
        return next_section, written_sections
    
    def exec(self, prep_res: Tuple[BlogSection, Dict[str, SectionContent]]) -> Optional[SectionContent]:
        """Write a blog section with context."""
        if not prep_res or prep_res[0] is None:
            return None
        
        section, previous_sections = prep_res
        
        # Build context from previous sections
        context = ""
        if previous_sections:
            context = "Previous sections:\n"
            for sec_type, content in previous_sections.items():
                context += f"\n{content.title}:\n{content.content[:200]}...\n"
        
        system = f"""You are a blog writer. Write the {section.section_type} section following these guidelines:
- Style: {section.style_guide}
- Target length: {section.target_length_words} words
- Key points to cover: {', '.join(section.key_points) if section.key_points else 'Use your judgment'}

{context}

Write naturally with good flow and transitions."""
        
        prompt = f"""Write the "{section.title}" section:
{section.description}"""
        
        content = call_llm(prompt, system=system)
        
        # Count words
        word_count = len(content.split())
        
        # Extract key points covered (simplified)
        key_points = section.key_points if section.key_points else ["Main topic covered"]
        
        return SectionContent(
            section_type=section.section_type,
            title=section.title,
            content=content,
            word_count=word_count,
            key_points_covered=key_points
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Tuple, exec_res: Optional[SectionContent]) -> Optional[str]:
        """Store written section and update queue."""
        if not exec_res:
            return "no_more_sections"
        
        # Store written section
        shared["written_sections"][exec_res.section_type] = exec_res
        
        # Remove from queue
        sections_to_write = shared.get("sections_to_write", [])
        if sections_to_write:
            sections_to_write.pop(0)
        
        self.logger.info(f"Wrote {exec_res.section_type}: {exec_res.word_count} words")
        
        # Check if more sections to write
        if sections_to_write:
            return "write_next"
        else:
            return "all_sections_complete"


class BlogReviewerNode(Node):
    """
    Reviews and improves blog cohesion.
    Provides final polished version.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather blog content for review."""
        return {
            "structure": shared.get("blog_structure"),
            "sections": shared.get("written_sections", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> BlogReview:
        """Review and improve blog cohesion."""
        structure = prep_res["structure"]
        sections = prep_res["sections"]
        
        # Build full blog text
        full_text = ""
        for section in structure.sections:
            if section.section_type in sections:
                content = sections[section.section_type]
                full_text += f"\n\n## {content.title}\n\n{content.content}"
        
        system = """You are a blog editor. Review this blog for:
1. Cohesion between sections
2. Smooth transitions
3. Consistent tone
4. Overall readability

Provide:
- cohesion_score: 0-1
- readability_score: 0-1
- suggested_edits: List of specific improvements
- final_version: The complete, polished blog"""
        
        prompt = f"""Review this blog about "{structure.topic}":

Target Audience: {structure.target_audience}
Tone: {structure.tone}

{full_text}

Provide your review and a polished final version."""
        
        response = call_llm(prompt, system=system)
        
        # Parse response (simplified)
        cohesion_score = 0.85  # Would parse from response
        readability_score = 0.9
        
        # Extract suggested edits
        suggested_edits = [
            {"section": "intro", "suggestion": "Add hook to grab reader attention"},
            {"section": "conclusion", "suggestion": "Strengthen call-to-action"}
        ]
        
        # For now, use the assembled text as final version
        final_version = f"# {structure.topic}\n{full_text}"
        
        return BlogReview(
            cohesion_score=cohesion_score,
            readability_score=readability_score,
            suggested_edits=suggested_edits,
            final_version=final_version,
            seo_optimization_notes="Consider adding more keyword variations"
        )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: BlogReview) -> Optional[str]:
        """Store final blog review."""
        shared["blog_review"] = exec_res
        
        self.logger.info(
            f"Blog review complete. Cohesion: {exec_res.cohesion_score:.2f}, "
            f"Readability: {exec_res.readability_score:.2f}"
        )
        
        return None


# ============== General Orchestrator ==============

class TaskOrchestratorNode(Node):
    """
    General task orchestrator for complex workflows.
    Plans and allocates tasks dynamically.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare orchestration requirements."""
        return {
            "objective": shared.get("objective", ""),
            "constraints": shared.get("constraints", {}),
            "available_resources": shared.get("resources", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> OrchestratorPlan:
        """Create orchestration plan."""
        objective = prep_res["objective"]
        
        system = """You are a task orchestrator. Break down the objective into subtasks.
Return JSON with:
- plan_id: Unique ID
- objective: The main objective
- analysis: Your analysis
- strategy: Execution strategy
- tasks: Array of tasks with:
  - task_id: Unique ID
  - task_type: analysis/generation/transformation/validation/aggregation/review
  - description: What to do
  - requirements: Object with requirements
  - dependencies: Array of task IDs this depends on
  - priority: critical/high/medium/low
  - estimated_duration_minutes: Time estimate
- expected_duration_minutes: Total time
- resource_requirements: Resources needed"""
        
        prompt = f"Create an execution plan for: {objective}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            
            # Create tasks
            tasks = []
            for task_data in data.get("tasks", []):
                tasks.append(SubTask(
                    task_id=task_data.get("task_id", f"task_{len(tasks)}"),
                    task_type=TaskType(task_data.get("task_type", "analysis")),
                    description=task_data.get("description", ""),
                    requirements=task_data.get("requirements", {}),
                    dependencies=task_data.get("dependencies", []),
                    priority=TaskPriority(task_data.get("priority", "medium")),
                    estimated_duration_minutes=task_data.get("estimated_duration_minutes", 10)
                ))
            
            return OrchestratorPlan(
                plan_id=f"plan_{int(time.time())}",
                objective=objective,
                analysis=data.get("analysis", ""),
                strategy=data.get("strategy", ""),
                tasks=tasks,
                expected_duration_minutes=data.get("expected_duration_minutes", 60),
                resource_requirements=data.get("resource_requirements", {})
            )
        except Exception as e:
            self.logger.error(f"Failed to parse orchestration plan: {e}")
            # Return simple plan
            return OrchestratorPlan(
                plan_id=f"plan_{int(time.time())}",
                objective=objective,
                analysis="Failed to analyze properly",
                strategy="Sequential execution",
                tasks=[
                    SubTask(
                        task_id="task_0",
                        task_type=TaskType.ANALYSIS,
                        description="Analyze the objective",
                        priority=TaskPriority.HIGH
                    ),
                    SubTask(
                        task_id="task_1",
                        task_type=TaskType.GENERATION,
                        description="Generate solution",
                        dependencies=["task_0"],
                        priority=TaskPriority.MEDIUM
                    )
                ],
                expected_duration_minutes=30
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: OrchestratorPlan) -> Optional[str]:
        """Initialize orchestration state."""
        # Create worker pool
        worker_pool = WorkerPool(
            workers=[
                WorkerCapability(
                    worker_id=f"worker_{i}",
                    capabilities=list(TaskType),
                    max_concurrent_tasks=2,
                    specializations=[TaskType.ANALYSIS.value, TaskType.GENERATION.value] if i % 2 == 0 else [TaskType.TRANSFORMATION.value, TaskType.VALIDATION.value]
                )
                for i in range(4)  # 4 workers
            ],
            total_capacity=8,
            current_utilization=0.0
        )
        
        # Initialize orchestration state
        state = OrchestrationState(
            plan=exec_res,
            task_queue=exec_res.tasks.copy(),
            worker_pool=worker_pool
        )
        
        shared["orchestration_state"] = state
        
        self.logger.info(
            f"Orchestration plan created: {len(exec_res.tasks)} tasks, "
            f"expected duration: {exec_res.expected_duration_minutes} minutes"
        )
        
        return None


class WorkerNode(Node):
    """
    Generic worker node that executes assigned tasks.
    """
    
    def __init__(self, worker_id: str = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.worker_id = worker_id or f"worker_{id(self)}"
        self.logger = logging.getLogger(f"{self.__class__.__name__}[{self.worker_id}]")
    
    def prep(self, shared: Dict[str, Any]) -> Optional[SubTask]:
        """Get next available task."""
        state = shared.get("orchestration_state")
        if not state:
            return None
        
        # Find task that:
        # 1. Is in queue
        # 2. Has all dependencies completed
        # 3. Matches worker capabilities
        
        completed_ids = {t.task_id for t in state.completed_tasks}
        
        for task in state.task_queue:
            # Check dependencies
            if all(dep in completed_ids for dep in task.dependencies):
                return task
        
        return None
    
    def exec(self, prep_res: Optional[SubTask]) -> Optional[TaskResult]:
        """Execute assigned task."""
        if not prep_res:
            return None
        
        task = prep_res
        start_time = time.time()
        
        try:
            # Simulate task execution based on type
            if task.task_type == TaskType.ANALYSIS:
                result = self._execute_analysis(task)
            elif task.task_type == TaskType.GENERATION:
                result = self._execute_generation(task)
            elif task.task_type == TaskType.TRANSFORMATION:
                result = self._execute_transformation(task)
            elif task.task_type == TaskType.VALIDATION:
                result = self._execute_validation(task)
            else:
                result = {"status": "completed", "data": "Generic task completed"}
            
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.COMPLETED,
                result=result,
                execution_time_seconds=time.time() - start_time,
                worker_id=self.worker_id
            )
        except Exception as e:
            self.logger.error(f"Task {task.task_id} failed: {e}")
            return TaskResult(
                task_id=task.task_id,
                status=TaskStatus.FAILED,
                error=str(e),
                execution_time_seconds=time.time() - start_time,
                worker_id=self.worker_id
            )
    
    def _execute_analysis(self, task: SubTask) -> Dict[str, Any]:
        """Execute analysis task."""
        time.sleep(random.uniform(1, 3))  # Simulate work
        return {
            "analysis_complete": True,
            "findings": ["Finding 1", "Finding 2", "Finding 3"],
            "confidence": 0.85
        }
    
    def _execute_generation(self, task: SubTask) -> Dict[str, Any]:
        """Execute generation task."""
        time.sleep(random.uniform(2, 4))  # Simulate work
        return {
            "generated_content": f"Generated content for {task.description}",
            "word_count": random.randint(100, 500)
        }
    
    def _execute_transformation(self, task: SubTask) -> Dict[str, Any]:
        """Execute transformation task."""
        time.sleep(random.uniform(1, 2))  # Simulate work
        return {
            "transformed": True,
            "output_format": "json",
            "records_processed": random.randint(10, 100)
        }
    
    def _execute_validation(self, task: SubTask) -> Dict[str, Any]:
        """Execute validation task."""
        time.sleep(random.uniform(0.5, 1.5))  # Simulate work
        return {
            "valid": random.random() > 0.2,
            "errors": [] if random.random() > 0.3 else ["Error 1", "Error 2"],
            "warnings": ["Warning 1"] if random.random() > 0.5 else []
        }
    
    def post(self, shared: Dict[str, Any], prep_res: Optional[SubTask], exec_res: Optional[TaskResult]) -> Optional[str]:
        """Update orchestration state."""
        if not exec_res:
            return "no_task"
        
        state = shared.get("orchestration_state")
        if state:
            # Remove from queue
            state.task_queue = [t for t in state.task_queue if t.task_id != exec_res.task_id]
            
            # Add to completed or failed
            if exec_res.status == TaskStatus.COMPLETED:
                state.completed_tasks.append(exec_res)
            else:
                state.failed_tasks.append(exec_res)
            
            self.logger.info(f"Task {exec_res.task_id} {exec_res.status}")
        
        # Check if more tasks available
        if state and state.task_queue:
            return "more_tasks"
        else:
            return "no_more_tasks"


# ============== Specialized Orchestrators ==============

class ReportOrchestratorNode(Node):
    """
    Orchestrates report generation workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare report requirements."""
        return {
            "topic": shared.get("report_topic", ""),
            "data_sources": shared.get("data_sources", []),
            "report_type": shared.get("report_type", "analysis")
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> ReportStructure:
        """Plan report structure."""
        topic = prep_res["topic"]
        
        system = """Plan a comprehensive report structure.
Return JSON with:
- title: Report title
- purpose: Report purpose
- sections: Array of sections with:
  - section_name: Name
  - data_sources: Required data sources
  - analysis_type: Type of analysis
  - visualization_requirements: Visualizations needed
  - dependencies: Other sections this depends on
- executive_summary_requirements: What to include
- appendices: List of appendices"""
        
        prompt = f"Create a report structure for: {topic}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            
            sections = []
            for section_data in data.get("sections", []):
                sections.append(ReportSection(**section_data))
            
            return ReportStructure(
                title=data.get("title", f"Report on {topic}"),
                purpose=data.get("purpose", "Comprehensive analysis"),
                sections=sections,
                executive_summary_requirements=data.get("executive_summary_requirements", ""),
                appendices=data.get("appendices", [])
            )
        except Exception as e:
            self.logger.error(f"Failed to parse report structure: {e}")
            # Return default structure
            return ReportStructure(
                title=f"Report on {topic}",
                purpose="Analysis and recommendations",
                sections=[
                    ReportSection(
                        section_name="Data Analysis",
                        data_sources=["primary_data"],
                        analysis_type="statistical",
                        visualization_requirements=["charts", "tables"]
                    ),
                    ReportSection(
                        section_name="Findings",
                        data_sources=["analysis_results"],
                        analysis_type="interpretation",
                        dependencies=["Data Analysis"]
                    )
                ],
                executive_summary_requirements="Key findings and recommendations"
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: ReportStructure) -> Optional[str]:
        """Store report structure."""
        shared["report_structure"] = exec_res
        shared["report_sections"] = {}
        
        self.logger.info(f"Report structure planned: {len(exec_res.sections)} sections")
        
        return None


class ProjectPlannerNode(Node):
    """
    Orchestrates project planning workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare project requirements."""
        return {
            "project_description": shared.get("project_description", ""),
            "constraints": shared.get("constraints", {}),
            "resources": shared.get("available_resources", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> ProjectPlan:
        """Create project plan."""
        description = prep_res["project_description"]
        
        system = """Create a detailed project plan.
Return JSON with:
- project_name: Name
- objectives: List of objectives
- phases: Array of phases with:
  - phase_name: Name
  - objectives: Phase objectives
  - tasks: Array of tasks with:
    - task_name: Name
    - description: Description
    - estimated_hours: Hours
    - required_skills: Skills needed
    - dependencies: Other tasks
    - deliverables: What will be delivered
    - risk_level: low/medium/high
  - duration_weeks: Phase duration
  - milestones: Key milestones
- total_duration_weeks: Total duration
- required_resources: Resources needed
- risk_assessment: Risk analysis
- success_criteria: How to measure success"""
        
        prompt = f"Create a project plan for: {description}"
        
        response = call_llm(prompt, system=system)
        
        try:
            data = json.loads(response.strip().strip("```json").strip("```"))
            
            phases = []
            for phase_data in data.get("phases", []):
                tasks = []
                for task_data in phase_data.get("tasks", []):
                    tasks.append(ProjectTask(**task_data))
                
                phases.append(ProjectPhase(
                    phase_name=phase_data.get("phase_name"),
                    objectives=phase_data.get("objectives", []),
                    tasks=tasks,
                    duration_weeks=phase_data.get("duration_weeks", 1),
                    milestones=phase_data.get("milestones", [])
                ))
            
            return ProjectPlan(
                project_name=data.get("project_name", "New Project"),
                objectives=data.get("objectives", []),
                phases=phases,
                total_duration_weeks=data.get("total_duration_weeks", 12),
                required_resources=data.get("required_resources", {}),
                risk_assessment=data.get("risk_assessment", {}),
                success_criteria=data.get("success_criteria", [])
            )
        except Exception as e:
            self.logger.error(f"Failed to parse project plan: {e}")
            # Return simple plan
            return ProjectPlan(
                project_name="Project",
                objectives=["Complete project successfully"],
                phases=[
                    ProjectPhase(
                        phase_name="Planning",
                        objectives=["Define requirements"],
                        tasks=[
                            ProjectTask(
                                task_name="Requirements gathering",
                                description="Gather all requirements",
                                estimated_hours=40,
                                risk_level="low"
                            )
                        ],
                        duration_weeks=2
                    )
                ],
                total_duration_weeks=8
            )
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: ProjectPlan) -> Optional[str]:
        """Store project plan."""
        shared["project_plan"] = exec_res
        
        total_tasks = sum(len(phase.tasks) for phase in exec_res.phases)
        self.logger.info(
            f"Project plan created: {len(exec_res.phases)} phases, "
            f"{total_tasks} tasks, {exec_res.total_duration_weeks} weeks"
        )
        
        return None


# ============== Result Aggregation ==============

class OrchestrationAggregatorNode(Node):
    """
    Aggregates results from orchestrated workflow.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def prep(self, shared: Dict[str, Any]) -> OrchestrationState:
        """Get orchestration state."""
        return shared.get("orchestration_state")
    
    def exec(self, prep_res: OrchestrationState) -> OrchestrationResult:
        """Aggregate orchestration results."""
        if not prep_res:
            return None
        
        state = prep_res
        
        # Determine status
        if len(state.failed_tasks) == 0:
            status = "success"
        elif len(state.completed_tasks) > 0:
            status = "partial_success"
        else:
            status = "failed"
        
        # Calculate duration
        duration = (datetime.now() - state.start_time).total_seconds()
        
        # Aggregate results
        final_output = {
            "completed_tasks": [t.task_id for t in state.completed_tasks],
            "failed_tasks": [t.task_id for t in state.failed_tasks],
            "results": {t.task_id: t.result for t in state.completed_tasks}
        }
        
        # Performance metrics
        avg_execution_time = sum(t.execution_time_seconds for t in state.completed_tasks) / len(state.completed_tasks) if state.completed_tasks else 0
        
        performance_metrics = {
            "average_task_time": avg_execution_time,
            "total_duration": duration,
            "efficiency": len(state.completed_tasks) / len(state.plan.tasks) if state.plan.tasks else 0,
            "worker_utilization": state.worker_pool.current_utilization
        }
        
        return OrchestrationResult(
            plan_id=state.plan.plan_id,
            status=status,
            completed_tasks=len(state.completed_tasks),
            failed_tasks=len(state.failed_tasks),
            total_duration_seconds=duration,
            final_output=final_output,
            task_results=state.completed_tasks + state.failed_tasks,
            performance_metrics=performance_metrics
        )
    
    def post(self, shared: Dict[str, Any], prep_res: OrchestrationState, exec_res: OrchestrationResult) -> Optional[str]:
        """Store final orchestration result."""
        shared["orchestration_result"] = exec_res
        
        self.logger.info(
            f"Orchestration complete: {exec_res.status}, "
            f"{exec_res.completed_tasks}/{exec_res.completed_tasks + exec_res.failed_tasks} tasks completed"
        )
        
        return None