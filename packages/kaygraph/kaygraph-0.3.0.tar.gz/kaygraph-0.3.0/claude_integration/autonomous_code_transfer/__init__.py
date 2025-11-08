"""Autonomous Code Transfer Agent.

A production-ready system for transferring features between codebases using
KayGraph orchestration + Claude Code headless execution.

Quick Start:
    >>> from autonomous_code_transfer import create_doppler_transfer_workflow, run_transfer_workflow
    >>>
    >>> config = {
    ...     "source_repo": "/path/to/source",
    ...     "target_repo": "/path/to/target",
    ...     "documentation": "/path/to/docs.md"
    ... }
    >>>
    >>> workflow = create_doppler_transfer_workflow(config)
    >>> results = await run_transfer_workflow(workflow, config)
"""

from graphs import (
    create_autonomous_transfer_workflow,
    create_supervised_transfer_workflow,
    create_doppler_transfer_workflow,
    create_generic_feature_transfer_workflow,
    run_transfer_workflow
)

from nodes import (
    TaskInitNode,
    ResearchNode,
    PlanningNode,
    ImplementationStepNode,
    ValidationNode
)

from utils.task_manager import TaskManager
from utils.claude_headless import ClaudeHeadless
from utils.safety import SafetyManager
from utils.monitoring import ProgressMonitor

__version__ = "1.0.0"

__all__ = [
    # Workflows
    "create_autonomous_transfer_workflow",
    "create_supervised_transfer_workflow",
    "create_doppler_transfer_workflow",
    "create_generic_feature_transfer_workflow",
    "run_transfer_workflow",

    # Nodes
    "TaskInitNode",
    "ResearchNode",
    "PlanningNode",
    "ImplementationStepNode",
    "ValidationNode",

    # Utilities
    "TaskManager",
    "ClaudeHeadless",
    "SafetyManager",
    "ProgressMonitor",
]
