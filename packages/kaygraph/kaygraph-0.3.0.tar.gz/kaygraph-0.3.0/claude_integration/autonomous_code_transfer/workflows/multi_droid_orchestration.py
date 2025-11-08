"""Multi-Droid Orchestration - All Specialized Droids Working Together.

This module demonstrates Factory AI's orchestration patterns with multiple
specialized droids coordinating to complete complex tasks.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from kaygraph import AsyncGraph, AsyncNode

from nodes import (
    TaskInitNode,
    ResearchNode,
    PlanningNode,
    ImplementationStepNode,
    ValidationNode
)
from droids.code_reviewer import CodeReviewerDroid
from droids.security_checker import SecurityCheckerDroid
from droids.test_generator import TestGeneratorDroid
from utils.monitoring import ProgressMonitor, AlertLevel


logger = logging.getLogger(__name__)


class ParallelReviewAggregatorNode(AsyncNode):
    """Aggregates results from multiple parallel droid reviews.

    Factory AI Pattern: Coordinator that collects specialist outputs.
    """

    def __init__(self):
        super().__init__(node_id="parallel_review_aggregator")

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Gather all droid results."""
        return {
            "code_review": shared.get("code_review", {}),
            "security_scan": shared.get("security_scan", {}),
            "test_generation": shared.get("test_generation", {}),
            "task_id": shared.get("task_id")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate and analyze all droid results."""
        code_review = prep_res["code_review"]
        security = prep_res["security_scan"]
        tests = prep_res["test_generation"]

        # Determine overall status
        has_critical_security = security.get("risk_level") == "CRITICAL"
        needs_code_changes = code_review.get("assessment") == "REQUEST_CHANGES"
        has_test_gaps = tests.get("coverage_improvement", 0) < 80

        # Calculate aggregate score
        scores = {
            "code_quality": 100 if code_review.get("assessment") == "APPROVE" else 50,
            "security": {
                "LOW": 100,
                "MEDIUM": 75,
                "HIGH": 50,
                "CRITICAL": 0
            }.get(security.get("risk_level", "MEDIUM"), 50),
            "test_coverage": tests.get("coverage_improvement", 0)
        }

        overall_score = (
            scores["code_quality"] * 0.4 +
            scores["security"] * 0.4 +
            scores["test_coverage"] * 0.2
        )

        # Determine recommendation
        if has_critical_security:
            recommendation = "BLOCK_DEPLOYMENT"
            status = "critical_failure"
        elif overall_score >= 80:
            recommendation = "APPROVE"
            status = "approved"
        elif overall_score >= 60:
            recommendation = "APPROVE_WITH_MONITORING"
            status = "approved_with_warnings"
        else:
            recommendation = "REQUEST_CHANGES"
            status = "request_changes"

        return {
            "overall_score": overall_score,
            "scores_breakdown": scores,
            "recommendation": recommendation,
            "status": status,
            "summary": self._generate_summary(code_review, security, tests, overall_score)
        }

    def _generate_summary(
        self,
        code_review: Dict[str, Any],
        security: Dict[str, Any],
        tests: Dict[str, Any],
        overall_score: float
    ) -> str:
        """Generate human-readable summary."""
        return f"""# Multi-Droid Review Summary

## Overall Score: {overall_score:.1f}/100

### Code Review
- Assessment: {code_review.get('assessment', 'N/A')}
- Files Reviewed: {code_review.get('files_reviewed', 0)}
- Report: {code_review.get('report_path', 'N/A')}

### Security Scan
- Risk Level: {security.get('risk_level', 'N/A')}
- Action: {security.get('action', 'N/A')}
- Files Scanned: {security.get('files_scanned', 0)}
- Report: {security.get('report_path', 'N/A')}

### Test Generation
- Tests Created: {tests.get('tests_created', 0)}
- Coverage Improvement: {tests.get('coverage_improvement', 0)}%
- Report: {tests.get('report_path', 'N/A')}

## Recommendation
**{self._get_recommendation_text(overall_score)}**
"""

    def _get_recommendation_text(self, score: float) -> str:
        """Get recommendation text based on score."""
        if score >= 80:
            return "✅ APPROVED - High quality, deploy with confidence"
        elif score >= 60:
            return "⚠️ APPROVED WITH MONITORING - Good quality, watch for issues"
        else:
            return "❌ REQUEST CHANGES - Issues need to be addressed"

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save aggregate report and update monitoring."""
        task_id = prep_res["task_id"]
        monitor: Optional[ProgressMonitor] = shared.get("monitor")

        # Save aggregate report
        aggregate_file = Path(f"tasks/{task_id}/aggregate_review_report.md")
        aggregate_file.parent.mkdir(parents=True, exist_ok=True)

        aggregate_report = f"""# Aggregate Multi-Droid Review Report

**Generated**: {datetime.now().isoformat()}
**Overall Score**: {exec_res['overall_score']:.1f}/100
**Recommendation**: {exec_res['recommendation']}

---

{exec_res['summary']}

---

## Detailed Reports

1. **Code Review**: {prep_res['code_review'].get('report_path', 'N/A')}
2. **Security Scan**: {prep_res['security_scan'].get('report_path', 'N/A')}
3. **Test Generation**: {prep_res['test_generation'].get('report_path', 'N/A')}

**Generated by**: Multi-Droid Orchestration System
"""

        aggregate_file.write_text(aggregate_report)

        # Store results
        shared["aggregate_review"] = {
            "overall_score": exec_res["overall_score"],
            "recommendation": exec_res["recommendation"],
            "report_path": str(aggregate_file),
            "status": exec_res["status"]
        }

        # Update monitoring
        if monitor:
            level = AlertLevel.ERROR if exec_res["status"] == "critical_failure" else AlertLevel.INFO
            monitor.update(
                "aggregate_review",
                f"Multi-droid review complete: {exec_res['recommendation']} (score: {exec_res['overall_score']:.1f})",
                level
            )

        logger.info(f"✅ Aggregate review complete: {exec_res['recommendation']}")
        logger.info(f"   Score: {exec_res['overall_score']:.1f}/100")
        logger.info(f"   Report: {aggregate_file}")

        return exec_res["status"]  # For conditional routing


def create_multi_droid_transfer_workflow(
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None,
    supervised: bool = False
) -> AsyncGraph:
    """Create transfer workflow with all specialized droids.

    Workflow:
    1. Task Init
    2. Research
    3. Planning
    4. Implementation (iterative)
    5. PARALLEL Multi-Droid Review:
       - Code Reviewer Droid
       - Security Checker Droid
       - Test Generator Droid
    6. Aggregate Results
    7. Final Validation

    Args:
        workspace_root: Root directory for tasks
        safety_guidelines_path: Safety guidelines file
        supervised: Enable human checkpoints

    Returns:
        AsyncGraph with multi-droid orchestration
    """
    logger.info("Creating multi-droid transfer workflow")

    # Phase 0-4: Standard workflow
    task_init = TaskInitNode(workspace_root=workspace_root)
    research = ResearchNode(safety_guidelines_path=safety_guidelines_path)
    planning = PlanningNode(safety_guidelines_path=safety_guidelines_path)
    implementation = ImplementationStepNode(safety_guidelines_path=safety_guidelines_path)

    # Phase 5: Parallel Multi-Droid Review
    code_reviewer = CodeReviewerDroid()
    security_checker = SecurityCheckerDroid()
    test_generator = TestGeneratorDroid()

    # Phase 6: Aggregate Results
    aggregator = ParallelReviewAggregatorNode()

    # Phase 7: Final Validation
    validation = ValidationNode(safety_guidelines_path=safety_guidelines_path)

    # Build graph
    task_init >> research >> planning

    # Supervised mode checkpoint
    if supervised:
        planning >> ("needs_approval", None)
        planning >> (None, implementation)
    else:
        planning >> implementation

    # Implementation loop
    implementation >> ("continue", implementation)
    implementation >> ("complete", code_reviewer)  # Move to review phase

    # PARALLEL REVIEW - All droids run simultaneously
    # Note: In actual implementation, these would be launched in parallel
    # For this demonstration, we show the conceptual flow
    code_reviewer >> security_checker >> test_generator >> aggregator

    # Conditional routing based on aggregate results
    aggregator >> ("approved", validation)
    aggregator >> ("approved_with_warnings", validation)
    aggregator >> ("request_changes", implementation)  # Loop back to fix issues
    aggregator >> ("critical_failure", None)  # Pause for human intervention

    # Final validation
    validation >> ("success", None)
    validation >> ("issues_found", aggregator)  # Re-review if validation finds issues

    # Create graph
    graph = AsyncGraph(start_node=task_init)

    return graph


def create_fast_track_workflow(
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None
) -> AsyncGraph:
    """Create fast-track workflow for simple transfers.

    Skips some droid reviews for faster execution on low-risk changes.

    Workflow:
    Research → Planning → Implementation → Code Review → Validation

    Args:
        workspace_root: Root directory for tasks
        safety_guidelines_path: Safety guidelines file

    Returns:
        AsyncGraph with minimal but essential checks
    """
    logger.info("Creating fast-track workflow")

    task_init = TaskInitNode(workspace_root=workspace_root)
    research = ResearchNode(safety_guidelines_path=safety_guidelines_path)
    planning = PlanningNode(safety_guidelines_path=safety_guidelines_path)
    implementation = ImplementationStepNode(safety_guidelines_path=safety_guidelines_path)
    code_reviewer = CodeReviewerDroid()  # Only code review, skip security & tests
    validation = ValidationNode(safety_guidelines_path=safety_guidelines_path)

    # Build simplified graph
    task_init >> research >> planning >> implementation
    implementation >> ("continue", implementation)
    implementation >> ("complete", code_reviewer)
    code_reviewer >> ("approve", validation)
    code_reviewer >> ("request_changes", implementation)
    validation >> ("success", None)

    graph = AsyncGraph(start_node=task_init)
    return graph


def create_security_focused_workflow(
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None
) -> AsyncGraph:
    """Create security-focused workflow for sensitive codebases.

    Extra emphasis on security scanning with multiple iterations.

    Workflow:
    Research → Planning → Implementation → Security Scan →
    If Critical: Block
    If Issues: Fix & Re-scan
    If Clean: Code Review → Test Gen → Validation

    Args:
        workspace_root: Root directory for tasks
        safety_guidelines_path: Safety guidelines file

    Returns:
        AsyncGraph with enhanced security checks
    """
    logger.info("Creating security-focused workflow")

    task_init = TaskInitNode(workspace_root=workspace_root)
    research = ResearchNode(safety_guidelines_path=safety_guidelines_path)
    planning = PlanningNode(safety_guidelines_path=safety_guidelines_path)
    implementation = ImplementationStepNode(safety_guidelines_path=safety_guidelines_path)

    # Security-first review
    security_checker = SecurityCheckerDroid()
    code_reviewer = CodeReviewerDroid()
    test_generator = TestGeneratorDroid()
    aggregator = ParallelReviewAggregatorNode()
    validation = ValidationNode(safety_guidelines_path=safety_guidelines_path)

    # Build security-focused graph
    task_init >> research >> planning >> implementation
    implementation >> ("continue", implementation)
    implementation >> ("complete", security_checker)  # Security FIRST

    # Security conditional routing
    security_checker >> ("block_deployment", None)  # Critical issues = stop
    security_checker >> ("fix_before_prod", implementation)  # Fix and re-implement
    security_checker >> ("monitor", code_reviewer)  # Continue to other reviews
    security_checker >> ("approved", code_reviewer)

    # Continue with other droids
    code_reviewer >> test_generator >> aggregator >> validation
    validation >> ("success", None)

    graph = AsyncGraph(start_node=task_init)
    return graph


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_multi_droid_workflow():
        """Test multi-droid workflow creation."""
        print("Testing Multi-Droid Orchestration...")

        # Test standard multi-droid workflow
        workflow1 = create_multi_droid_transfer_workflow()
        print("✓ Created multi-droid transfer workflow")

        # Test fast-track workflow
        workflow2 = create_fast_track_workflow()
        print("✓ Created fast-track workflow")

        # Test security-focused workflow
        workflow3 = create_security_focused_workflow()
        print("✓ Created security-focused workflow")

        print("\n✅ All multi-droid workflows created successfully!")

    asyncio.run(test_multi_droid_workflow())
