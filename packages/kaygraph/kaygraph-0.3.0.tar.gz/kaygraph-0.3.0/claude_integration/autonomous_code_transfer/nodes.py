"""KayGraph Nodes for Autonomous Code Transfer.

Implements the multi-step context engineering approach:
  0. Tasks - Initialize task workspace
  1. Research - Analyze codebases and document findings
  2. Planning - Create detailed implementation plan
  3. Implementation - Execute plan with checkpoints
  4. Validation - Verify and test implementation
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from kaygraph import AsyncNode, ValidatedNode, Node

from utils.task_manager import TaskManager
from utils.claude_headless import ClaudeHeadless, OutputFormat, PermissionMode
from utils.safety import SafetyManager
from utils.monitoring import ProgressMonitor, AlertLevel


logger = logging.getLogger(__name__)


# ===== PHASE 0: TASK INITIALIZATION =====

class TaskInitNode(Node):
    """Initialize task workspace and context files.

    Creates the task directory structure and task.md with the goal.
    """

    def __init__(self, workspace_root: str = "./tasks"):
        super().__init__(node_id="task_init")
        self.task_manager = TaskManager(workspace_root=workspace_root)

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare task initialization."""
        return {
            "description": shared.get("task_description", "Feature Transfer"),
            "config": shared
        }

    def exec(self, prep_res: Dict[str, Any]) -> str:
        """Create task workspace."""
        task_id = self.task_manager.create_task(
            task_description=prep_res["description"],
            config=prep_res["config"]
        )

        logger.info(f"✓ Task initialized: {task_id}")
        return task_id

    def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: str):
        """Store task_id and initialize monitoring."""
        task_id = exec_res
        shared["task_id"] = task_id
        shared["task_dir"] = self.task_manager.get_task_dir(task_id)

        # Initialize monitor
        monitor = ProgressMonitor(
            task_id=task_id,
            webhook_url=shared.get("webhook_url"),
            email_config=shared.get("email_config"),
            slack_webhook=shared.get("slack_webhook"),
            log_file=shared["task_dir"] / "logs" / "progress.log"
        )
        shared["monitor"] = monitor

        monitor.update(
            "initialization",
            f"Task workspace created: {task_id}",
            AlertLevel.INFO
        )

        # Initialize safety manager if target repo provided
        if "target_repo" in shared:
            safety = SafetyManager(Path(shared["target_repo"]))
            shared["safety"] = safety

        return None  # Continue to next phase


# ===== PHASE 1: RESEARCH =====

class ResearchNode(AsyncNode):
    """Research phase: Analyze source and target codebases.

    Writes findings to research.md for planning phase.
    """

    def __init__(self, safety_guidelines_path: Optional[Path] = None):
        super().__init__(node_id="research")
        self.safety_guidelines_path = safety_guidelines_path

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare research task."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))

        # Generate research template
        research_template = task_manager.generate_research_template(shared["task_id"])
        task_manager.write_file(shared["task_id"], "research_template.md", research_template)

        # Read task.md for context
        task_md = task_manager.read_file(shared["task_id"], "task.md")

        return {
            "task_md": task_md,
            "research_template": research_template,
            "source_repo": shared.get("source_repo"),
            "target_repo": shared.get("target_repo"),
            "documentation": shared.get("documentation"),
            "working_dir": shared.get("target_repo", ".")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute research using Claude Code headless."""
        # Initialize Claude headless client
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["working_dir"]),
            safety_guidelines_path=self.safety_guidelines_path,
            default_timeout=900  # 15 minutes for research
        )

        research_prompt = f"""
# Research Phase Task

You are conducting research for an autonomous code transfer project.

## Original Task
{prep_res['task_md']}

## Your Research Objectives

1. **Analyze Source Codebase** ({prep_res['source_repo']})
   - Identify ALL files related to the feature
   - List ALL dependencies (packages, system deps, external services)
   - Document code patterns, naming conventions, configuration patterns
   - Find tests related to the feature

2. **Analyze Target Codebase** ({prep_res['target_repo']})
   - Document current file organization
   - Identify where the feature should integrate
   - Find similar existing patterns
   - Understand current testing setup

3. **Document Integration Strategy**
   - How will source patterns fit into target structure?
   - What conflicts might arise?
   - What needs to be adapted vs copied directly?

## Research Template to Fill
{prep_res['research_template']}

## Important
- Be thorough - the planning phase depends on your findings
- Use Grep to search for patterns across codebases
- Use Read to examine specific files
- Document EVERYTHING - nothing is obvious
- If you need clarification, list questions in the template

Return your completed research in the same template structure.
"""

        result = claude.execute(
            prompt=research_prompt,
            allowed_tools=["Read", "Grep", "Glob"],
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=900
        )

        return {
            "success": result.success,
            "research_findings": result.output.get("result", "")  if isinstance(result.output, dict) else result.output,
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms,
            "error": result.error
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save research findings to research.md."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))
        monitor: ProgressMonitor = shared["monitor"]

        if exec_res["success"]:
            # Write research.md
            task_manager.write_file(
                shared["task_id"],
                "research.md",
                exec_res["research_findings"]
            )

            # Update monitoring
            monitor.update(
                "research",
                "Research phase complete - findings documented in research.md",
                AlertLevel.INFO
            )
            monitor.update_metrics(
                steps_completed=1,
                cost_usd=exec_res["cost_usd"]
            )

            task_manager.log_event(
                shared["task_id"],
                f"Research complete in {exec_res['duration_ms']}ms"
            )

            return None  # Continue to planning
        else:
            error_msg = f"Research failed: {exec_res['error']}"
            monitor.add_error(error_msg)
            raise RuntimeError(error_msg)


# ===== PHASE 2: PLANNING =====

class PlanningNode(AsyncNode):
    """Planning phase: Create detailed implementation plan.

    Reads research.md and writes plan.md with step-by-step execution plan.
    """

    def __init__(self, safety_guidelines_path: Optional[Path] = None):
        super().__init__(node_id="planning")
        self.safety_guidelines_path = safety_guidelines_path

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare planning task."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))

        # Read context files
        task_md = task_manager.read_file(shared["task_id"], "task.md")
        research_md = task_manager.read_file(shared["task_id"], "research.md")
        plan_template = task_manager.generate_plan_template(shared["task_id"])

        return {
            "task_md": task_md,
            "research_md": research_md,
            "plan_template": plan_template,
            "working_dir": shared.get("target_repo", ".")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute planning using Claude Code headless."""
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["working_dir"]),
            safety_guidelines_path=self.safety_guidelines_path,
            default_timeout=900  # 15 minutes for planning
        )

        planning_prompt = f"""
# Planning Phase Task

You are creating a detailed implementation plan for autonomous code transfer.

## Original Task
{prep_res['task_md']}

## Research Findings
{prep_res['research_md']}

## Your Planning Objectives

Create a comprehensive, step-by-step implementation plan that can be executed autonomously.

For EACH step, provide:
1. **Step Number and Description** - Clear, specific objective
2. **Files to Modify/Create** - Exact file paths
3. **Commands to Run** - Exact bash commands (npm install, etc.)
4. **Testing** - What tests to run to validate this step
5. **Checkpoint** - Will create checkpoint-XXX after this step
6. **Estimated Duration** - Realistic time estimate
7. **Rollback Plan** - What to do if this step fails

Also include:
- **Risk Assessment**: List potential risks and mitigations
- **Total Duration Estimate**: Sum of all steps
- **Human Approval Points**: Steps that need human review (if any)
- **Success Criteria Checklist**: Final validation requirements

## Planning Template
{prep_res['plan_template']}

## Important Guidelines for Autonomous Execution
- Break complex steps into smaller atomic steps
- Each step should take <1 hour
- Steps should be idempotent (safe to retry)
- Include validation after each significant change
- Plan for failures with rollback strategies
- Never plan to modify >5 files in one step

Return your completed plan in the template structure, ready for automated execution.
"""

        result = claude.execute(
            prompt=planning_prompt,
            allowed_tools=["Read"],  # Read-only for planning
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=900
        )

        return {
            "success": result.success,
            "plan": result.output.get("result", "") if isinstance(result.output, dict) else result.output,
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms,
            "error": result.error
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save plan to plan.md and parse steps."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))
        monitor: ProgressMonitor = shared["monitor"]

        if exec_res["success"]:
            # Write plan.md
            task_manager.write_file(
                shared["task_id"],
                "plan.md",
                exec_res["plan"]
            )

            # Parse plan to extract step count (simple heuristic)
            plan_text = exec_res["plan"]
            step_count = plan_text.count("### Step") if "### Step" in plan_text else 5

            shared["implementation_steps_total"] = step_count
            shared["implementation_step_current"] = 0

            # Update monitoring
            monitor.update(
                "planning",
                f"Planning complete - {step_count} steps defined in plan.md",
                AlertLevel.INFO
            )
            monitor.update_metrics(
                steps_completed=2,
                steps_total=step_count + 3,  # +3 for init, research, planning, validation
                cost_usd=exec_res["cost_usd"]
            )

            task_manager.log_event(
                shared["task_id"],
                f"Planning complete: {step_count} steps, {exec_res['duration_ms']}ms"
            )

            # Check if supervised mode - pause for approval
            if shared.get("supervised", False):
                monitor.update(
                    "planning",
                    "⏸️  PAUSED - Waiting for human approval of plan.md",
                    AlertLevel.WARNING
                )
                return "needs_approval"  # Signal to pause

            return None  # Continue to implementation
        else:
            error_msg = f"Planning failed: {exec_res['error']}"
            monitor.add_error(error_msg)
            raise RuntimeError(error_msg)


# ===== PHASE 3: IMPLEMENTATION =====

class ImplementationStepNode(AsyncNode):
    """Execute single implementation step from plan.md.

    Creates checkpoint before execution, validates after.
    """

    def __init__(self, safety_guidelines_path: Optional[Path] = None):
        super().__init__(node_id="implementation_step")
        self.safety_guidelines_path = safety_guidelines_path

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare implementation step."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))

        # Read necessary context
        task_md = task_manager.read_file(shared["task_id"], "task.md")
        plan_md = task_manager.read_file(shared["task_id"], "plan.md")

        # Get current step
        current_step = shared.get("implementation_step_current", 0) + 1
        shared["implementation_step_current"] = current_step

        return {
            "task_md": task_md,
            "plan_md": plan_md,
            "step_number": current_step,
            "total_steps": shared.get("implementation_steps_total", 0),
            "working_dir": shared.get("target_repo", ".")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute implementation step using Claude Code with YOLO mode."""
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["working_dir"]),
            safety_guidelines_path=self.safety_guidelines_path,
            default_timeout=3600  # 1 hour per step
        )

        yolo_mode = prep_res.get("yolo_mode", True)  # Enable autonomous mode by default

        implementation_prompt = f"""
# Implementation Step {prep_res['step_number']}/{prep_res['total_steps']}

## Original Task
{prep_res['task_md']}

## Full Implementation Plan
{prep_res['plan_md']}

## Your Task for THIS Step
Execute ONLY Step {prep_res['step_number']} from the plan above.

### Execution Process:
1. **Read the step details carefully** - What files, what changes, what commands
2. **Create/modify files as specified** - Follow existing code conventions
3. **Run any commands specified** - Install dependencies, build, etc.
4. **Validate syntax** - Ensure no compilation/lint errors
5. **Run tests** - Execute tests specified in the step
6. **Report results** - Detailed summary of what was done

### Safety Rules (CRITICAL):
- Validate syntax before committing changes
- Run tests after changes
- Never expose secrets or API keys
- Follow target codebase conventions
- Create meaningful file changes

### Return Format:
Provide structured JSON response with:
{{
  "step_number": {prep_res['step_number']},
  "files_modified": ["path/to/file1", "path/to/file2"],
  "files_created": ["path/to/file3"],
  "commands_executed": ["npm install xyz", "npm test"],
  "test_results": {{"passed": X, "failed": Y}},
  "syntax_valid": true/false,
  "success": true/false,
  "summary": "What was accomplished",
  "issues": ["Any problems encountered"]
}}

Execute Step {prep_res['step_number']} now.
"""

        result = claude.execute(
            prompt=implementation_prompt,
            allowed_tools=["Read", "Edit", "Write", "Bash", "Grep", "Glob"],
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.YOLO if yolo_mode else PermissionMode.ACCEPT_EDITS,
            timeout=3600
        )

        return {
            "success": result.success,
            "step_result": result.output if isinstance(result.output, dict) else {"summary": result.output},
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms,
            "error": result.error
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Log step results and create checkpoint."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))
        monitor: ProgressMonitor = shared["monitor"]
        safety: Optional[SafetyManager] = shared.get("safety")

        step_number = prep_res["step_number"]

        if exec_res["success"]:
            step_result = exec_res["step_result"]

            # Create git checkpoint
            if safety:
                checkpoint = safety.create_checkpoint(
                    checkpoint_id=f"{step_number:03d}",
                    message=f"Step {step_number}: {step_result.get('summary', 'Implementation step')}"
                )

                task_manager.create_checkpoint(
                    shared["task_id"],
                    step_number=step_number,
                    description=step_result.get("summary", ""),
                    git_commit=checkpoint.commit_hash
                )

                monitor.update_metrics(checkpoints_created=1)

            # Log to implementation.md
            implementation_log = f"""
### Step {step_number} - {datetime.now().isoformat()}

**Summary**: {step_result.get('summary', 'N/A')}

**Files Modified**: {', '.join(step_result.get('files_modified', []))}
**Files Created**: {', '.join(step_result.get('files_created', []))}
**Commands**: {', '.join(step_result.get('commands_executed', []))}
**Tests**: {step_result.get('test_results', {})}

**Status**: ✓ Success
**Duration**: {exec_res['duration_ms']}ms
**Cost**: ${exec_res['cost_usd']:.4f}

---
"""
            task_manager.append_to_file(shared["task_id"], "implementation.md", implementation_log)

            # Update monitoring
            monitor.update(
                "implementation",
                f"Step {step_number}/{prep_res['total_steps']} complete: {step_result.get('summary', '')}",
                AlertLevel.INFO
            )
            monitor.update_metrics(
                steps_completed=2 + step_number,  # +2 for init, research
                files_modified=len(step_result.get('files_modified', []) + step_result.get('files_created', [])),
                tests_passed=step_result.get('test_results', {}).get('passed', 0),
                tests_failed=step_result.get('test_results', {}).get('failed', 0),
                cost_usd=exec_res['cost_usd']
            )

            # Check if more steps remaining
            if step_number < prep_res['total_steps']:
                return "continue"  # Loop back to execute next step
            else:
                return "complete"  # Move to validation
        else:
            error_msg = f"Step {step_number} failed: {exec_res['error']}"
            monitor.add_error(error_msg)
            return "failed"  # Move to error handling or pause


# ===== PHASE 4: VALIDATION =====

class ValidationNode(AsyncNode):
    """Validate complete implementation with comprehensive testing."""

    def __init__(self, safety_guidelines_path: Optional[Path] = None):
        super().__init__(node_id="validation")
        self.safety_guidelines_path = safety_guidelines_path

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare validation."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))

        # Read context
        task_md = task_manager.read_file(shared["task_id"], "task.md")
        implementation_md = task_manager.read_file(shared["task_id"], "implementation.md")

        return {
            "task_md": task_md,
            "implementation_md": implementation_md,
            "working_dir": shared.get("target_repo", ".")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation using Claude Code."""
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["working_dir"]),
            safety_guidelines_path=self.safety_guidelines_path,
            default_timeout=900  # 15 minutes for validation
        )

        validation_prompt = f"""
# Validation Phase

## Original Task
{prep_res['task_md']}

## Implementation Summary
{prep_res['implementation_md']}

## Your Validation Tasks

Perform comprehensive validation of the implementation:

### 1. Syntax and Compilation
- Run linters (eslint, tsc, pylint, etc.)
- Check for compilation errors
- Verify no syntax errors

### 2. Test Execution
- Run ALL existing tests
- Run newly created tests
- Check test coverage if available
- Report pass/fail counts

### 3. Integration Validation
- Verify feature works as expected
- Test main use cases
- Test edge cases
- Check error handling

### 4. Regression Testing
- Ensure existing functionality still works
- No breaking changes introduced
- Dependencies resolve correctly

### 5. Code Quality
- Follows conventions
- No code smells
- Proper error handling

### Return Format:
Provide structured JSON response:
{{
  "syntax_check": {{"status": "passed/failed", "errors": []}},
  "tests": {{"total": X, "passed": Y, "failed": Z, "coverage": "%"}},
  "integration": {{"status": "passed/failed", "issues": []}},
  "regression": {{"status": "passed/failed", "issues": []}},
  "overall_status": "success/issues_found/critical_failure",
  "recommendation": "approve/fix_issues/rollback",
  "summary": "Overall assessment"
}}

Execute comprehensive validation now.
"""

        result = claude.execute(
            prompt=validation_prompt,
            allowed_tools=["Read", "Bash", "Grep"],
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=900
        )

        return {
            "success": result.success,
            "validation_result": result.output if isinstance(result.output, dict) else {"summary": result.output},
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms,
            "error": result.error
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save validation results and determine final status."""
        task_manager = TaskManager(workspace_root=str(shared["task_dir"].parent))
        monitor: ProgressMonitor = shared["monitor"]

        if exec_res["success"]:
            validation_result = exec_res["validation_result"]

            # Write validation report
            validation_report = f"""
# Validation Report

**Date**: {datetime.now().isoformat()}
**Duration**: {exec_res['duration_ms']}ms

## Results

### Syntax Check
Status: {validation_result.get('syntax_check', {}).get('status', 'N/A')}
Errors: {validation_result.get('syntax_check', {}).get('errors', [])}

### Tests
Total: {validation_result.get('tests', {}).get('total', 0)}
Passed: {validation_result.get('tests', {}).get('passed', 0)}
Failed: {validation_result.get('tests', {}).get('failed', 0)}
Coverage: {validation_result.get('tests', {}).get('coverage', 'N/A')}

### Integration
Status: {validation_result.get('integration', {}).get('status', 'N/A')}
Issues: {validation_result.get('integration', {}).get('issues', [])}

### Regression
Status: {validation_result.get('regression', {}).get('status', 'N/A')}
Issues: {validation_result.get('regression', {}).get('issues', [])}

## Overall Assessment
Status: {validation_result.get('overall_status', 'N/A')}
Recommendation: {validation_result.get('recommendation', 'N/A')}

Summary:
{validation_result.get('summary', 'N/A')}
"""
            task_manager.write_file(shared["task_id"], "validation_report.md", validation_report)

            # Update monitoring
            overall_status = validation_result.get('overall_status', 'unknown')
            tests = validation_result.get('tests', {})

            monitor.update_metrics(
                steps_completed=shared.get("implementation_steps_total", 0) + 3,  # All steps + phases
                tests_passed=tests.get('passed', 0),
                tests_failed=tests.get('failed', 0),
                cost_usd=exec_res['cost_usd']
            )

            if overall_status == "success":
                monitor.update(
                    "validation",
                    "✅ Validation passed - all tests successful",
                    AlertLevel.INFO
                )
                shared["transfer_success"] = True
                return "success"
            elif overall_status == "issues_found":
                monitor.update(
                    "validation",
                    "⚠️ Validation found issues - review required",
                    AlertLevel.WARNING
                )
                shared["transfer_success"] = False
                return "issues_found"
            else:
                monitor.update(
                    "validation",
                    "❌ Validation failed - critical issues",
                    AlertLevel.ERROR
                )
                shared["transfer_success"] = False
                return "critical_failure"
        else:
            error_msg = f"Validation failed to execute: {exec_res['error']}"
            monitor.add_error(error_msg)
            shared["transfer_success"] = False
            return "validation_error"
