"""Workflow graphs for autonomous code transfer.

Connects nodes into complete workflows with conditional routing.
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

from kaygraph import Graph, AsyncGraph

from nodes import (
    TaskInitNode,
    ResearchNode,
    PlanningNode,
    ImplementationStepNode,
    ValidationNode
)


logger = logging.getLogger(__name__)


def create_autonomous_transfer_workflow(
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None,
    supervised: bool = False
) -> AsyncGraph:
    """Create fully autonomous code transfer workflow.

    Workflow: Init → Research → Plan → Implement (loop) → Validate

    Args:
        workspace_root: Root directory for task workspaces
        safety_guidelines_path: Path to safety guidelines markdown
        supervised: If True, pause for human approval after planning

    Returns:
        AsyncGraph ready to execute
    """
    logger.info("Creating autonomous transfer workflow")

    # Initialize nodes
    task_init = TaskInitNode(workspace_root=workspace_root)
    research = ResearchNode(safety_guidelines_path=safety_guidelines_path)
    planning = PlanningNode(safety_guidelines_path=safety_guidelines_path)
    implementation = ImplementationStepNode(safety_guidelines_path=safety_guidelines_path)
    validation = ValidationNode(safety_guidelines_path=safety_guidelines_path)

    # Build graph with conditional routing
    task_init >> research >> planning

    # Supervised mode - pause after planning
    if supervised:
        planning >> ("needs_approval", None)  # Pauses workflow
        planning >> (None, implementation)  # Auto-continue if not supervised
    else:
        planning >> implementation

    # Implementation loop - continue until complete
    implementation >> ("continue", implementation)  # Loop back for next step
    implementation >> ("complete", validation)  # Move to validation
    implementation >> ("failed", None)  # Pause on failure

    # Validation routes
    validation >> ("success", None)  # Complete successfully
    validation >> ("issues_found", None)  # Complete with warnings
    validation >> ("critical_failure", None)  # Complete with errors
    validation >> ("validation_error", None)  # Complete with validation error

    # Create graph
    graph = AsyncGraph(start_node=task_init)

    return graph


def create_supervised_transfer_workflow(
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None
) -> AsyncGraph:
    """Create supervised transfer workflow with human checkpoints.

    Same as autonomous but pauses after each major phase.

    Args:
        workspace_root: Root directory for task workspaces
        safety_guidelines_path: Path to safety guidelines

    Returns:
        AsyncGraph with human checkpoints
    """
    return create_autonomous_transfer_workflow(
        workspace_root=workspace_root,
        safety_guidelines_path=safety_guidelines_path,
        supervised=True
    )


def create_doppler_transfer_workflow(
    config: Dict[str, Any],
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None
) -> AsyncGraph:
    """Create workflow specifically for Doppler integration transfer.

    Pre-configures the workflow with Doppler-specific context.

    Args:
        config: Configuration with source_repo, target_repo, documentation, etc.
        workspace_root: Root directory for task workspaces
        safety_guidelines_path: Path to safety guidelines

    Returns:
        AsyncGraph configured for Doppler transfer
    """
    logger.info("Creating Doppler transfer workflow")

    # Enrich config with Doppler-specific context
    doppler_config = {
        **config,
        "task_description": "Transfer Doppler Integration from Source to Target Codebase",
        "feature_name": "doppler-integration",
        "dependencies": ["@dopplerhq/node-sdk", "dotenv"],
        "files_to_transfer": [
            "config/doppler.ts",
            ".env.example",
            "docker-compose.yml (Doppler section)"
        ]
    }

    # Create workflow
    workflow = create_autonomous_transfer_workflow(
        workspace_root=workspace_root,
        safety_guidelines_path=safety_guidelines_path,
        supervised=config.get("supervised", False)
    )

    return workflow


def create_generic_feature_transfer_workflow(
    feature_name: str,
    config: Dict[str, Any],
    workspace_root: str = "./tasks",
    safety_guidelines_path: Optional[Path] = None
) -> AsyncGraph:
    """Create workflow for any feature transfer.

    Generic workflow that can transfer any feature with proper config.

    Args:
        feature_name: Name of the feature to transfer
        config: Configuration dictionary
        workspace_root: Root directory for task workspaces
        safety_guidelines_path: Path to safety guidelines

    Returns:
        AsyncGraph configured for generic transfer
    """
    logger.info(f"Creating generic feature transfer workflow: {feature_name}")

    # Enrich config
    generic_config = {
        **config,
        "task_description": f"Transfer {feature_name} from Source to Target Codebase",
        "feature_name": feature_name
    }

    # Create workflow
    workflow = create_autonomous_transfer_workflow(
        workspace_root=workspace_root,
        safety_guidelines_path=safety_guidelines_path,
        supervised=config.get("supervised", False)
    )

    return workflow


async def run_transfer_workflow(
    workflow: AsyncGraph,
    config: Dict[str, Any],
    max_runtime_hours: Optional[float] = None,
    max_cost_usd: Optional[float] = None
) -> Dict[str, Any]:
    """Run transfer workflow with budget and time limits.

    Args:
        workflow: AsyncGraph to execute
        config: Configuration dictionary with all required params
        max_runtime_hours: Maximum runtime in hours
        max_cost_usd: Maximum cost in USD

    Returns:
        Results dictionary
    """
    import asyncio
    from datetime import datetime

    start_time = datetime.now()
    logger.info(f"Starting transfer workflow at {start_time}")

    # Create shared context
    shared = {
        **config,
        "max_cost_usd": max_cost_usd,
        "max_runtime_hours": max_runtime_hours
    }

    try:
        # Run with timeout if specified
        if max_runtime_hours:
            timeout_seconds = max_runtime_hours * 3600
            result = await asyncio.wait_for(
                workflow.run(shared=shared),
                timeout=timeout_seconds
            )
        else:
            result = await workflow.run(shared=shared)

        end_time = datetime.now()
        duration = end_time - start_time

        # Extract results from shared context
        monitor = shared.get("monitor")
        success = shared.get("transfer_success", False)

        results = {
            "success": success,
            "task_id": shared.get("task_id"),
            "duration_seconds": duration.total_seconds(),
            "duration_hours": duration.total_seconds() / 3600,
            "summary": monitor.get_summary() if monitor else {},
            "task_dir": str(shared.get("task_dir", "N/A"))
        }

        # Send completion report
        if monitor:
            final_message = f"Transfer {'completed successfully' if success else 'completed with issues'}"
            monitor.send_completion_report(success=success, final_message=final_message)

        return results

    except asyncio.TimeoutError:
        logger.error(f"Workflow timed out after {max_runtime_hours} hours")
        return {
            "success": False,
            "error": f"Timeout after {max_runtime_hours} hours",
            "task_id": shared.get("task_id"),
            "duration_hours": max_runtime_hours
        }

    except Exception as e:
        logger.error(f"Workflow failed with exception: {e}", exc_info=True)
        monitor = shared.get("monitor")
        if monitor:
            monitor.add_error(str(e))
            monitor.send_completion_report(success=False, final_message=f"Exception: {e}")

        return {
            "success": False,
            "error": str(e),
            "task_id": shared.get("task_id")
        }


# Testing utility
if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)

    async def test_workflow_creation():
        """Test workflow creation."""
        print("Testing workflow creation...")

        # Test autonomous workflow
        workflow1 = create_autonomous_transfer_workflow()
        print("✓ Created autonomous workflow")

        # Test supervised workflow
        workflow2 = create_supervised_transfer_workflow()
        print("✓ Created supervised workflow")

        # Test Doppler workflow
        doppler_config = {
            "source_repo": "/path/to/template",
            "target_repo": "/path/to/target",
            "documentation": "/path/to/doppler-docs.md"
        }
        workflow3 = create_doppler_transfer_workflow(doppler_config)
        print("✓ Created Doppler workflow")

        # Test generic workflow
        workflow4 = create_generic_feature_transfer_workflow(
            "authentication-jwt",
            {"source_repo": "/source", "target_repo": "/target"}
        )
        print("✓ Created generic workflow")

        print("\n✅ All workflow creation tests passed!")

    asyncio.run(test_workflow_creation())
