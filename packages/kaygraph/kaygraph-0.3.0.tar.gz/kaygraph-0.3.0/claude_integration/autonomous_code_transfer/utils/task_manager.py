"""Task Manager for Context Engineering.

Manages task directories and markdown files for persistent context storage.
Implements the multi-step approach:
  0. Tasks - Store context in tasks/<task-id>/ folders
  1. Research - Findings in research.md
  2. Planning - Implementation plan in plan.md
  3. Implementation - Execution log in implementation.md
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
import re


def create_task_id(task_description: str) -> str:
    """Create semantic task ID slug from description.

    Args:
        task_description: Human-readable task description

    Returns:
        Semantic slug like 'doppler-integration-transfer'
    """
    # Convert to lowercase, replace spaces with hyphens
    slug = task_description.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars
    slug = re.sub(r'[-\s]+', '-', slug)   # Normalize spaces/hyphens
    slug = slug.strip('-')[:50]            # Limit length

    # Add timestamp suffix to ensure uniqueness
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    return f"{slug}-{timestamp}"


class TaskManager:
    """Manages task workspace and context files."""

    def __init__(self, workspace_root: str = "./tasks"):
        """Initialize task manager.

        Args:
            workspace_root: Root directory for all tasks
        """
        self.workspace_root = Path(workspace_root)
        self.workspace_root.mkdir(parents=True, exist_ok=True)

    def create_task(self, task_description: str, config: Dict[str, Any]) -> str:
        """Create new task workspace.

        Args:
            task_description: Description of the task
            config: Task configuration (source_repo, target_repo, etc.)

        Returns:
            task_id: Created task ID
        """
        task_id = create_task_id(task_description)
        task_dir = self.workspace_root / task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (task_dir / "checkpoints").mkdir(exist_ok=True)
        (task_dir / "logs").mkdir(exist_ok=True)

        # Write initial task.md
        task_md = self._generate_task_md(task_description, config)
        self.write_file(task_id, "task.md", task_md)

        # Write config.json for programmatic access
        config_with_meta = {
            "task_id": task_id,
            "created_at": datetime.now().isoformat(),
            "description": task_description,
            **config
        }
        self.write_file(task_id, "config.json", json.dumps(config_with_meta, indent=2))

        return task_id

    def _generate_task_md(self, description: str, config: Dict[str, Any]) -> str:
        """Generate initial task.md content.

        This is the ANCHOR that prevents context loss - agent can always
        return to this file to remember the original goal.
        """
        return f"""# Task: {description}

## Goal
Transfer the feature/pattern from source codebase to target codebase with full functionality and tests.

## Configuration
- **Source Repository**: `{config.get('source_repo', 'N/A')}`
- **Target Repository**: `{config.get('target_repo', 'N/A')}`
- **Feature Documentation**: `{config.get('documentation', 'N/A')}`
- **Mode**: {config.get('mode', 'autonomous')}

## Success Criteria
1. Feature fully implemented in target codebase
2. All tests passing (existing + new)
3. No regressions in existing functionality
4. Documentation updated
5. Code follows target codebase conventions

## Context Engineering Phases
This task follows a structured approach:

1. **Research Phase** → `research.md`
   - Analyze source codebase patterns
   - Analyze target codebase structure
   - Identify integration points
   - Document findings

2. **Planning Phase** → `plan.md`
   - Read research.md
   - Create step-by-step implementation plan
   - Identify files to create/modify
   - Plan testing strategy

3. **Implementation Phase** → `implementation.md`
   - Execute plan step-by-step
   - Create checkpoints before each change
   - Validate after each step
   - Log all actions

## Safety Guidelines
- Create git checkpoint before EVERY file modification
- Run tests after each step
- Never modify more than 5 files per iteration
- Always validate syntax before committing
- Never commit secrets or API keys

## Human Checkpoints
- After research: Review findings
- After planning: Approve implementation plan
- During implementation: Intervention on validation failures
- After completion: Final review

---
**Created**: {datetime.now().isoformat()}
**Task ID**: {config.get('task_id', 'pending')}
"""

    def get_task_dir(self, task_id: str) -> Path:
        """Get task directory path."""
        return self.workspace_root / task_id

    def write_file(self, task_id: str, filename: str, content: str) -> None:
        """Write content to task file.

        Args:
            task_id: Task identifier
            filename: File name (e.g., 'research.md')
            content: File content
        """
        task_dir = self.get_task_dir(task_id)
        file_path = task_dir / filename
        file_path.write_text(content, encoding='utf-8')

    def read_file(self, task_id: str, filename: str) -> Optional[str]:
        """Read content from task file.

        Args:
            task_id: Task identifier
            filename: File name (e.g., 'research.md')

        Returns:
            File content or None if not exists
        """
        task_dir = self.get_task_dir(task_id)
        file_path = task_dir / filename

        if not file_path.exists():
            return None

        return file_path.read_text(encoding='utf-8')

    def append_to_file(self, task_id: str, filename: str, content: str) -> None:
        """Append content to task file.

        Useful for implementation.md logging.
        """
        existing = self.read_file(task_id, filename) or ""
        updated = existing + "\n" + content
        self.write_file(task_id, filename, updated)

    def create_checkpoint(self, task_id: str, step_number: int, description: str,
                         git_commit: Optional[str] = None) -> str:
        """Create checkpoint for rollback capability.

        Args:
            task_id: Task identifier
            step_number: Current step number
            description: What was done in this step
            git_commit: Optional git commit hash

        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"checkpoint-{step_number:03d}"
        checkpoint_dir = self.get_task_dir(task_id) / "checkpoints" / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        # Write checkpoint metadata
        metadata = {
            "checkpoint_id": checkpoint_id,
            "step_number": step_number,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "git_commit": git_commit
        }

        checkpoint_file = checkpoint_dir / "metadata.json"
        checkpoint_file.write_text(json.dumps(metadata, indent=2))

        return checkpoint_id

    def list_checkpoints(self, task_id: str) -> List[Dict[str, Any]]:
        """List all checkpoints for a task.

        Returns:
            List of checkpoint metadata dictionaries
        """
        checkpoints_dir = self.get_task_dir(task_id) / "checkpoints"
        if not checkpoints_dir.exists():
            return []

        checkpoints = []
        for checkpoint_dir in sorted(checkpoints_dir.iterdir()):
            if not checkpoint_dir.is_dir():
                continue

            metadata_file = checkpoint_dir / "metadata.json"
            if metadata_file.exists():
                metadata = json.loads(metadata_file.read_text())
                checkpoints.append(metadata)

        return checkpoints

    def log_event(self, task_id: str, event: str, level: str = "INFO") -> None:
        """Log event to task log file.

        Args:
            task_id: Task identifier
            event: Event description
            level: Log level (INFO, WARNING, ERROR)
        """
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {event}\n"

        log_file = self.get_task_dir(task_id) / "logs" / "events.log"
        log_file.parent.mkdir(exist_ok=True)

        with open(log_file, 'a') as f:
            f.write(log_entry)

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get current task status.

        Returns:
            Dictionary with task status information
        """
        task_dir = self.get_task_dir(task_id)

        # Check which files exist to determine phase
        has_research = (task_dir / "research.md").exists()
        has_plan = (task_dir / "plan.md").exists()
        has_implementation = (task_dir / "implementation.md").exists()

        # Determine current phase
        if not has_research:
            phase = "initialized"
        elif not has_plan:
            phase = "research_complete"
        elif not has_implementation:
            phase = "planning_complete"
        else:
            phase = "implementation_in_progress"

        # Count checkpoints
        checkpoints = self.list_checkpoints(task_id)

        return {
            "task_id": task_id,
            "phase": phase,
            "checkpoints_count": len(checkpoints),
            "latest_checkpoint": checkpoints[-1] if checkpoints else None,
            "files": {
                "task_md": (task_dir / "task.md").exists(),
                "research_md": has_research,
                "plan_md": has_plan,
                "implementation_md": has_implementation,
            }
        }

    def generate_research_template(self, task_id: str) -> str:
        """Generate template for research.md.

        This template guides the agent on what to research.
        """
        config = self.read_file(task_id, "config.json")
        config_data = json.loads(config) if config else {}

        return f"""# Research Phase

**Task**: {config_data.get('description', 'N/A')}
**Phase**: 1 - Research
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Source Codebase Analysis

### Feature Files
List all files related to the feature in source codebase:
- [ ] Identify main implementation files
- [ ] Identify configuration files
- [ ] Identify test files
- [ ] Identify documentation files

### Dependencies
List all dependencies required by the feature:
- [ ] NPM/pip packages
- [ ] System dependencies
- [ ] External services

### Patterns & Conventions
Document code patterns used:
- [ ] File structure conventions
- [ ] Naming conventions
- [ ] Configuration patterns
- [ ] Error handling patterns

## Target Codebase Analysis

### Current Structure
Document target codebase structure:
- [ ] Existing file organization
- [ ] Current dependencies
- [ ] Existing patterns
- [ ] Test setup

### Integration Points
Identify where feature should integrate:
- [ ] Configuration location
- [ ] Service initialization
- [ ] Environment variables
- [ ] Build/deploy scripts

## Similar Patterns in Target
Search for similar patterns already in target:
- [ ] Similar integrations
- [ ] Configuration patterns
- [ ] Testing patterns

## Questions for User
List any questions that need clarification:
1. ...
2. ...

## Summary
Provide concise summary of findings that will be used in planning phase.

---
**Next Step**: Planning Phase - Create implementation plan based on these findings.
"""

    def generate_plan_template(self, task_id: str) -> str:
        """Generate template for plan.md.

        This template guides the agent on creating the implementation plan.
        """
        return f"""# Planning Phase

**Task ID**: {task_id}
**Phase**: 2 - Planning
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Context from Research
> Read and summarize key findings from research.md here

## Implementation Strategy
Describe the high-level approach:
1. ...
2. ...

## Detailed Step-by-Step Plan

### Step 1: [Description]
- **Objective**: What this step achieves
- **Files to modify/create**:
  - `path/to/file.ts` - What changes
- **Commands to run**: npm install xyz
- **Tests**: What to test
- **Checkpoint**: Create checkpoint-001
- **Expected duration**: X minutes
- **Rollback plan**: If this fails, do...

### Step 2: [Description]
...

### Step N: Final Validation
- **Objective**: Verify complete integration
- **Tests to run**: Full test suite
- **Validation checks**:
  - [ ] All tests pass
  - [ ] No regressions
  - [ ] Feature works as expected
  - [ ] Documentation updated

## Risk Assessment
- **Risk 1**: ...
  - Mitigation: ...
- **Risk 2**: ...
  - Mitigation: ...

## Estimated Total Duration
X hours (based on N steps * Y minutes each)

## Human Approval Points
- [ ] After Step X - Reason
- [ ] Before Step Y - Reason
- [ ] After final validation

## Success Criteria Checklist
- [ ] All files created/modified as planned
- [ ] All dependencies installed
- [ ] All tests passing
- [ ] No existing functionality broken
- [ ] Documentation complete
- [ ] Code follows conventions

---
**Next Step**: Implementation Phase - Execute this plan step-by-step with validation.
"""

    def generate_implementation_template(self, task_id: str) -> str:
        """Generate template for implementation.md.

        This is a LOG file that gets appended to during execution.
        """
        return f"""# Implementation Phase

**Task ID**: {task_id}
**Phase**: 3 - Implementation
**Started**: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Execution Log

This file logs all actions taken during implementation.
Each step includes: timestamp, action, result, checkpoint.

---

"""


# Utility functions for testing
if __name__ == "__main__":
    import tempfile
    import shutil

    # Create temporary workspace
    temp_dir = tempfile.mkdtemp()
    print(f"Testing TaskManager in: {temp_dir}")

    try:
        # Initialize manager
        manager = TaskManager(workspace_root=temp_dir)

        # Create task
        task_id = manager.create_task(
            "Transfer Doppler Integration to Target Codebase",
            {
                "source_repo": "/path/to/template",
                "target_repo": "/path/to/target",
                "documentation": "/path/to/doppler-docs.md",
                "mode": "autonomous"
            }
        )

        print(f"✓ Created task: {task_id}")

        # Write research template
        research_template = manager.generate_research_template(task_id)
        manager.write_file(task_id, "research.md", research_template)
        print("✓ Generated research.md template")

        # Create checkpoint
        checkpoint_id = manager.create_checkpoint(
            task_id,
            step_number=1,
            description="Initial setup complete",
            git_commit="abc123"
        )
        print(f"✓ Created checkpoint: {checkpoint_id}")

        # Log event
        manager.log_event(task_id, "Test event logged successfully")
        print("✓ Logged test event")

        # Get status
        status = manager.get_task_status(task_id)
        print(f"✓ Task status: {status['phase']}")

        # List files created
        task_dir = manager.get_task_dir(task_id)
        print(f"\n📁 Task directory structure:")
        for path in sorted(task_dir.rglob("*")):
            if path.is_file():
                rel_path = path.relative_to(task_dir)
                print(f"   {rel_path}")

        print("\n✅ All tests passed!")

    finally:
        # Cleanup
        shutil.rmtree(temp_dir)
        print(f"\n🧹 Cleaned up temp directory")
