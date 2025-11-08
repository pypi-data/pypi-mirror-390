"""Competitive Orchestration - Multiple Approaches Racing.

Factory AI Pattern: Run multiple solution approaches in parallel and pick the best one.
This is useful for complex problems where there might be multiple valid solutions.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import json

from kaygraph import AsyncGraph, AsyncNode

from nodes import ImplementationStepNode
from droids.code_reviewer import CodeReviewerDroid
from utils.claude_headless import ClaudeHeadless, OutputFormat, PermissionMode
from utils.monitoring import ProgressMonitor, AlertLevel


logger = logging.getLogger(__name__)


class CompetitiveImplementationNode(AsyncNode):
    """Implements solution using a specific approach.

    Factory AI Pattern: Specialist that tries one approach to solve the problem.
    """

    def __init__(self, approach_name: str, approach_strategy: str):
        super().__init__(node_id=f"competitive_impl_{approach_name}")
        self.approach_name = approach_name
        self.approach_strategy = approach_strategy

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare implementation with specific approach."""
        return {
            "task_description": shared.get("task_description"),
            "research_findings": shared.get("research_findings"),
            "approach_name": self.approach_name,
            "approach_strategy": self.approach_strategy,
            "target_repo": shared.get("target_repo", "."),
            "task_id": shared.get("task_id")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute implementation using this approach."""
        logger.info(f"🏁 Competitive Implementation: {self.approach_name}")

        implementation_prompt = f"""# Competitive Implementation: {self.approach_name}

## Task
{prep_res['task_description']}

## Research Context
{prep_res['research_findings']}

## Your Approach Strategy
{self.approach_strategy}

## Instructions
Implement a complete solution following the {self.approach_name} approach.

Focus on:
1. **Code Quality**: Clean, maintainable, follows conventions
2. **Performance**: Efficient implementation
3. **Testability**: Easy to test
4. **Documentation**: Clear comments and docs
5. **Error Handling**: Robust error handling

Return:
- Implementation details
- Files created/modified
- Approach rationale
- Pros/cons of this approach
- Estimated performance characteristics
"""

        claude = ClaudeHeadless(
            working_dir=Path(prep_res["target_repo"]),
            default_timeout=1800  # 30 minutes per approach
        )

        start_time = datetime.now()

        result = claude.execute(
            prompt=implementation_prompt,
            allowed_tools=["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.YOLO,
            timeout=1800
        )

        duration = (datetime.now() - start_time).total_seconds()

        if not result.success:
            return {
                "success": False,
                "approach_name": self.approach_name,
                "error": result.error,
                "duration": duration
            }

        return {
            "success": True,
            "approach_name": self.approach_name,
            "implementation": result.output,
            "cost_usd": result.cost_usd or 0.0,
            "duration": duration
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save approach implementation."""
        task_id = prep_res["task_id"]
        approach_name = exec_res["approach_name"]

        # Save implementation artifact
        impl_file = Path(f"tasks/{task_id}/competitive_approaches/{approach_name}_implementation.md")
        impl_file.parent.mkdir(parents=True, exist_ok=True)

        implementation_report = f"""# Implementation: {approach_name}

**Generated**: {datetime.now().isoformat()}
**Duration**: {exec_res['duration']:.1f}s
**Cost**: ${exec_res.get('cost_usd', 0):.4f}
**Success**: {exec_res['success']}

---

{exec_res.get('implementation', 'N/A')}

---

**Approach**: {approach_name}
"""

        impl_file.write_text(implementation_report)

        # Store in shared context
        if "competitive_implementations" not in shared:
            shared["competitive_implementations"] = {}

        shared["competitive_implementations"][approach_name] = {
            "success": exec_res["success"],
            "implementation_path": str(impl_file),
            "cost_usd": exec_res.get("cost_usd", 0),
            "duration": exec_res["duration"]
        }

        logger.info(f"✅ {approach_name} implementation complete")

        return "implemented"


class CompetitiveSolutionComparatorNode(AsyncNode):
    """Compares multiple competitive implementations and picks the best.

    Factory AI Pattern: Judge that evaluates all approaches objectively.
    """

    def __init__(self):
        super().__init__(node_id="competitive_comparator")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all competitive implementations."""
        return {
            "implementations": shared.get("competitive_implementations", {}),
            "task_description": shared.get("task_description"),
            "target_repo": shared.get("target_repo", "."),
            "task_id": shared.get("task_id")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Compare implementations and pick the best."""
        logger.info("🏆 Comparing competitive implementations...")

        implementations = prep_res["implementations"]

        if not implementations:
            return {
                "success": False,
                "error": "No implementations to compare"
            }

        # Read all implementation files
        impl_contents = {}
        for approach_name, impl_data in implementations.items():
            impl_path = Path(impl_data["implementation_path"])
            if impl_path.exists():
                impl_contents[approach_name] = impl_path.read_text()

        # Build comparison prompt
        comparison_prompt = f"""# Competitive Solution Comparison

## Task
{prep_res['task_description']}

## Implementations to Compare

{self._format_implementations(implementations, impl_contents)}

## Evaluation Criteria

Score each implementation (0-100) on:

### 1. Code Quality (25 points)
- Clean, readable code
- Follows conventions
- Well-structured
- Maintainable

### 2. Performance (20 points)
- Efficient algorithms
- Resource usage
- Scalability
- Response time

### 3. Correctness (25 points)
- Solves the problem completely
- Handles edge cases
- Proper error handling
- Robust implementation

### 4. Testability (15 points)
- Easy to test
- Good separation of concerns
- Mockable dependencies

### 5. Documentation (10 points)
- Clear comments
- API documentation
- Usage examples

### 6. Innovation (5 points)
- Creative solutions
- Best practices
- Modern patterns

## Your Task

1. **Evaluate each implementation** using the criteria above
2. **Score each implementation** (0-100 per criterion)
3. **Calculate total scores**
4. **Identify the winner**
5. **Provide detailed rationale**

## Output Format

Return JSON:
{{
  "evaluations": {{
    "approach_name": {{
      "scores": {{
        "code_quality": 85,
        "performance": 90,
        "correctness": 95,
        "testability": 80,
        "documentation": 75,
        "innovation": 70
      }},
      "total_score": 495,
      "strengths": ["...", "..."],
      "weaknesses": ["...", "..."],
      "recommendation": "pros and cons summary"
    }}
  }},
  "winner": "approach_name",
  "rationale": "Why this approach won...",
  "runner_up": "approach_name",
  "comparison_summary": "Overall comparison insights"
}}
"""

        claude = ClaudeHeadless(
            working_dir=Path(prep_res["target_repo"]),
            default_timeout=900  # 15 minutes for comparison
        )

        result = claude.execute(
            prompt=comparison_prompt,
            allowed_tools=["Read"],  # Read-only for comparison
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=900
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error
            }

        # Parse comparison results
        comparison = result.output if isinstance(result.output, dict) else {"result": result.output}

        return {
            "success": True,
            "comparison": comparison,
            "cost_usd": result.cost_usd or 0.0
        }

    def _format_implementations(
        self,
        implementations: Dict[str, Any],
        impl_contents: Dict[str, str]
    ) -> str:
        """Format implementations for comparison prompt."""
        formatted = []
        for approach_name, impl_data in implementations.items():
            content = impl_contents.get(approach_name, "N/A")
            formatted.append(f"""
### Implementation: {approach_name}
**Duration**: {impl_data['duration']:.1f}s
**Cost**: ${impl_data['cost_usd']:.4f}

```
{content[:2000]}...  # Truncated for brevity
```
""")
        return "\n".join(formatted)

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save comparison results and select winner."""
        if not exec_res["success"]:
            logger.error(f"Comparison failed: {exec_res['error']}")
            return "comparison_failed"

        task_id = prep_res["task_id"]

        # Save comparison report
        comparison_file = Path(f"tasks/{task_id}/competitive_comparison_report.md")
        comparison_file.parent.mkdir(parents=True, exist_ok=True)

        comparison_data = exec_res["comparison"]

        comparison_report = f"""# Competitive Solutions Comparison Report

**Generated**: {datetime.now().isoformat()}
**Cost**: ${exec_res['cost_usd']:.4f}

## Winner: {comparison_data.get('winner', 'N/A')}

### Rationale
{comparison_data.get('rationale', 'N/A')}

## Detailed Evaluations

{self._format_evaluations(comparison_data.get('evaluations', {}))}

## Runner-Up: {comparison_data.get('runner_up', 'N/A')}

## Comparison Summary
{comparison_data.get('comparison_summary', 'N/A')}

---

**Generated by**: Competitive Solution Comparator
"""

        comparison_file.write_text(comparison_report)

        # Store winner in shared context
        shared["competitive_winner"] = {
            "approach": comparison_data.get("winner"),
            "rationale": comparison_data.get("rationale"),
            "comparison_path": str(comparison_file),
            "evaluations": comparison_data.get("evaluations", {})
        }

        logger.info(f"🏆 Winner: {comparison_data.get('winner')}")
        logger.info(f"   Report: {comparison_file}")

        return "winner_selected"

    def _format_evaluations(self, evaluations: Dict[str, Any]) -> str:
        """Format evaluation details."""
        formatted = []
        for approach, eval_data in evaluations.items():
            scores = eval_data.get("scores", {})
            total = eval_data.get("total_score", 0)

            formatted.append(f"""
### {approach}
**Total Score**: {total}/600

**Scores**:
- Code Quality: {scores.get('code_quality', 0)}/25
- Performance: {scores.get('performance', 0)}/20
- Correctness: {scores.get('correctness', 0)}/25
- Testability: {scores.get('testability', 0)}/15
- Documentation: {scores.get('documentation', 0)}/10
- Innovation: {scores.get('innovation', 0)}/5

**Strengths**: {', '.join(eval_data.get('strengths', []))}
**Weaknesses**: {', '.join(eval_data.get('weaknesses', []))}

**Recommendation**: {eval_data.get('recommendation', 'N/A')}
""")
        return "\n".join(formatted)


def create_competitive_workflow(
    approaches: List[Tuple[str, str]],
    workspace_root: str = "./tasks"
) -> AsyncGraph:
    """Create competitive workflow where multiple approaches race.

    Args:
        approaches: List of (approach_name, strategy_description) tuples
        workspace_root: Root directory for tasks

    Returns:
        AsyncGraph with competitive orchestration

    Example:
        approaches = [
            ("minimalist", "Use minimal dependencies, keep it simple"),
            ("robust", "Full error handling, comprehensive validation"),
            ("performant", "Optimize for speed and efficiency")
        ]
    """
    logger.info(f"Creating competitive workflow with {len(approaches)} approaches")

    from nodes import TaskInitNode, ResearchNode, PlanningNode

    # Standard setup
    task_init = TaskInitNode(workspace_root=workspace_root)
    research = ResearchNode()
    planning = PlanningNode()

    # Create competitive implementation nodes
    impl_nodes = []
    for approach_name, strategy in approaches:
        node = CompetitiveImplementationNode(approach_name, strategy)
        impl_nodes.append(node)

    # Comparator
    comparator = CompetitiveSolutionComparatorNode()

    # Code reviewer for winner
    reviewer = CodeReviewerDroid()

    # Build graph
    task_init >> research >> planning

    # Fan out to all approaches (conceptually parallel)
    for node in impl_nodes:
        planning >> node >> comparator

    # Review winner
    comparator >> ("winner_selected", reviewer)
    comparator >> ("comparison_failed", None)

    # Finalize
    reviewer >> ("approve", None)
    reviewer >> ("request_changes", None)  # Could loop back to implementations

    graph = AsyncGraph(start_node=task_init)
    return graph


# Predefined competitive strategies
COMPETITIVE_STRATEGIES = {
    "minimalist": """
**Minimalist Approach**
- Use minimal dependencies
- Keep code simple and straightforward
- Favor readability over cleverness
- Easy to understand and maintain
- Quick to implement
""",

    "robust": """
**Robust Approach**
- Comprehensive error handling
- Extensive input validation
- Defensive programming
- Detailed logging
- Graceful degradation
- Production-ready from start
""",

    "performant": """
**Performance-Optimized Approach**
- Optimize for speed
- Efficient algorithms
- Minimal memory usage
- Caching where beneficial
- Async/parallel where possible
- Benchmarked and profiled
""",

    "modular": """
**Modular Approach**
- High separation of concerns
- Pluggable components
- Easy to test in isolation
- Flexible and extensible
- Clear interfaces
- SOLID principles
""",

    "monolithic": """
**Monolithic Approach**
- All logic in one place
- No external dependencies
- Self-contained
- Simple deployment
- Easy to reason about
- No microservice complexity
"""
}


def create_common_competitive_workflow(
    workspace_root: str = "./tasks",
    include_approaches: List[str] = None
) -> AsyncGraph:
    """Create competitive workflow with common strategies.

    Args:
        workspace_root: Root directory for tasks
        include_approaches: List of approach names to include.
                          Options: minimalist, robust, performant, modular, monolithic
                          Default: ['minimalist', 'robust', 'performant']

    Returns:
        AsyncGraph with predefined competitive approaches
    """
    if include_approaches is None:
        include_approaches = ['minimalist', 'robust', 'performant']

    approaches = [
        (name, COMPETITIVE_STRATEGIES[name])
        for name in include_approaches
        if name in COMPETITIVE_STRATEGIES
    ]

    return create_competitive_workflow(approaches, workspace_root)


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_competitive_workflow():
        """Test competitive workflow creation."""
        print("Testing Competitive Orchestration...")

        # Test custom approaches
        custom_approaches = [
            ("fast", "Prioritize speed over features"),
            ("feature_rich", "Maximum features, accept complexity")
        ]
        workflow1 = create_competitive_workflow(custom_approaches)
        print("✓ Created custom competitive workflow")

        # Test common strategies
        workflow2 = create_common_competitive_workflow(
            include_approaches=['minimalist', 'robust', 'performant']
        )
        print("✓ Created common competitive workflow")

        # Test all strategies
        workflow3 = create_common_competitive_workflow(
            include_approaches=list(COMPETITIVE_STRATEGIES.keys())
        )
        print(f"✓ Created workflow with all {len(COMPETITIVE_STRATEGIES)} strategies")

        print("\n✅ All competitive workflows created successfully!")
        print(f"\nAvailable strategies: {', '.join(COMPETITIVE_STRATEGIES.keys())}")

    asyncio.run(test_competitive_workflow())
