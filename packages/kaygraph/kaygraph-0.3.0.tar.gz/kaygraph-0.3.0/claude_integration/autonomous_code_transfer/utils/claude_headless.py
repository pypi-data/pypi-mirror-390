"""Claude Code Headless Integration.

Wrapper for executing Claude Code in headless mode with proper error handling,
output parsing, and session management.
"""

import subprocess
import json
import time
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Claude Code output formats."""
    TEXT = "text"
    JSON = "json"
    STREAM_JSON = "stream-json"


class PermissionMode(Enum):
    """Permission handling modes."""
    INTERACTIVE = "interactive"  # Default - ask for permissions
    ACCEPT_EDITS = "acceptEdits"  # Auto-accept file edits
    YOLO = "yolo"  # Skip all permissions (dangerously-skip-permissions)


@dataclass
class ClaudeResult:
    """Result from Claude Code execution."""
    success: bool
    output: Union[str, Dict[str, Any]]
    session_id: Optional[str] = None
    cost_usd: Optional[float] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    exit_code: int = 0


class ClaudeHeadless:
    """Wrapper for Claude Code headless execution."""

    def __init__(
        self,
        working_dir: Optional[Path] = None,
        default_timeout: int = 3600,  # 1 hour default
        safety_guidelines_path: Optional[Path] = None,
        max_cost_usd: Optional[float] = None
    ):
        """Initialize Claude Code headless wrapper.

        Args:
            working_dir: Working directory for Claude Code execution
            default_timeout: Default timeout in seconds
            safety_guidelines_path: Path to safety guidelines markdown
            max_cost_usd: Maximum cost limit per execution
        """
        self.working_dir = working_dir or Path.cwd()
        self.default_timeout = default_timeout
        self.safety_guidelines_path = safety_guidelines_path
        self.max_cost_usd = max_cost_usd
        self.total_cost = 0.0

        # Verify claude command is available
        self._verify_claude_installed()

    def _verify_claude_installed(self) -> None:
        """Verify Claude Code CLI is installed."""
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode != 0:
                raise RuntimeError("Claude Code CLI not found or not working")
            logger.info(f"Claude Code CLI version: {result.stdout.strip()}")
        except FileNotFoundError:
            raise RuntimeError(
                "Claude Code CLI not installed. "
                "Install from: https://code.claude.com/docs/en/installation"
            )
        except subprocess.TimeoutExpired:
            raise RuntimeError("Claude Code CLI verification timed out")

    def execute(
        self,
        prompt: str,
        allowed_tools: Optional[List[str]] = None,
        disallowed_tools: Optional[List[str]] = None,
        output_format: OutputFormat = OutputFormat.JSON,
        permission_mode: PermissionMode = PermissionMode.ACCEPT_EDITS,
        append_system_prompt: Optional[str] = None,
        timeout: Optional[int] = None,
        session_id: Optional[str] = None,
        verbose: bool = False
    ) -> ClaudeResult:
        """Execute Claude Code in headless mode.

        Args:
            prompt: Task prompt for Claude
            allowed_tools: List of allowed tools (e.g., ["Read", "Edit", "Write", "Bash"])
            disallowed_tools: List of disallowed tools
            output_format: Output format (text, json, stream-json)
            permission_mode: How to handle permissions
            append_system_prompt: Additional system prompt
            timeout: Execution timeout in seconds
            session_id: Resume from existing session
            verbose: Enable verbose logging

        Returns:
            ClaudeResult with execution outcome
        """
        # Build command
        cmd = ["claude"]

        # Non-interactive mode
        if session_id:
            cmd.extend(["--resume", session_id, "--no-interactive"])
        else:
            cmd.extend(["-p", prompt])

        # Output format
        cmd.extend(["--output-format", output_format.value])

        # Tools
        if allowed_tools:
            cmd.extend(["--allowedTools", ",".join(allowed_tools)])
        if disallowed_tools:
            cmd.extend(["--disallowedTools", ",".join(disallowed_tools)])

        # Permission mode
        if permission_mode == PermissionMode.YOLO:
            cmd.append("--dangerously-skip-permissions")
        elif permission_mode == PermissionMode.ACCEPT_EDITS:
            cmd.extend(["--permission-mode", "acceptEdits"])

        # System prompt
        system_prompt_parts = []
        if self.safety_guidelines_path and self.safety_guidelines_path.exists():
            system_prompt_parts.append(f"@{self.safety_guidelines_path}")
        if append_system_prompt:
            system_prompt_parts.append(append_system_prompt)

        if system_prompt_parts:
            cmd.extend(["--append-system-prompt", " ".join(system_prompt_parts)])

        # Verbose
        if verbose:
            cmd.append("--verbose")

        # Cost limiting (if we exceed budget, don't execute)
        if self.max_cost_usd and self.total_cost >= self.max_cost_usd:
            return ClaudeResult(
                success=False,
                output={},
                error=f"Cost limit reached: ${self.total_cost:.2f} >= ${self.max_cost_usd:.2f}"
            )

        # Execute
        logger.info(f"Executing Claude Code: {' '.join(cmd)}")
        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=timeout or self.default_timeout
            )

            duration_ms = int((time.time() - start_time) * 1000)

            # Parse output
            if output_format == OutputFormat.JSON:
                try:
                    output_data = json.loads(result.stdout)
                    session_id = output_data.get("session_id")
                    cost_usd = output_data.get("total_cost_usd", 0.0)
                    self.total_cost += cost_usd

                    return ClaudeResult(
                        success=result.returncode == 0,
                        output=output_data,
                        session_id=session_id,
                        cost_usd=cost_usd,
                        duration_ms=duration_ms,
                        error=result.stderr if result.returncode != 0 else None,
                        exit_code=result.returncode
                    )
                except json.JSONDecodeError as e:
                    return ClaudeResult(
                        success=False,
                        output=result.stdout,
                        error=f"Failed to parse JSON output: {e}",
                        duration_ms=duration_ms,
                        exit_code=result.returncode
                    )
            else:
                return ClaudeResult(
                    success=result.returncode == 0,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None,
                    duration_ms=duration_ms,
                    exit_code=result.returncode
                )

        except subprocess.TimeoutExpired:
            duration_ms = int((time.time() - start_time) * 1000)
            return ClaudeResult(
                success=False,
                output={},
                error=f"Execution timed out after {timeout or self.default_timeout}s",
                duration_ms=duration_ms,
                exit_code=-1
            )
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            return ClaudeResult(
                success=False,
                output={},
                error=f"Execution failed: {str(e)}",
                duration_ms=duration_ms,
                exit_code=-1
            )

    def execute_research(
        self,
        task: str,
        context: Dict[str, Any],
        timeout: int = 600  # 10 minutes for research
    ) -> ClaudeResult:
        """Execute research phase with appropriate permissions.

        Args:
            task: Research task description
            context: Task context (source_repo, target_repo, etc.)
            timeout: Timeout in seconds

        Returns:
            ClaudeResult with research findings
        """
        prompt = f"""
# Research Phase Task

{task}

## Context
- Source Repository: {context.get('source_repo', 'N/A')}
- Target Repository: {context.get('target_repo', 'N/A')}
- Documentation: {context.get('documentation', 'N/A')}

## Your Task
Analyze both codebases and document findings in structured format.

1. **Source Codebase Analysis**
   - Identify all files related to the feature
   - List dependencies required
   - Document code patterns and conventions

2. **Target Codebase Analysis**
   - Document current structure
   - Identify integration points
   - Find similar existing patterns

3. **Summary**
   - Provide concise findings for planning phase

Return findings in structured markdown format.
"""

        return self.execute(
            prompt=prompt,
            allowed_tools=["Read", "Grep", "Glob"],  # Read-only for research
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=timeout
        )

    def execute_planning(
        self,
        research_findings: str,
        context: Dict[str, Any],
        timeout: int = 600  # 10 minutes for planning
    ) -> ClaudeResult:
        """Execute planning phase with research context.

        Args:
            research_findings: Output from research phase
            context: Task context
            timeout: Timeout in seconds

        Returns:
            ClaudeResult with implementation plan
        """
        prompt = f"""
# Planning Phase Task

## Research Findings
{research_findings}

## Context
- Source Repository: {context.get('source_repo', 'N/A')}
- Target Repository: {context.get('target_repo', 'N/A')}

## Your Task
Create a detailed step-by-step implementation plan based on research findings.

For each step include:
1. Objective - What the step achieves
2. Files to modify/create - Specific paths
3. Commands to run - Exact commands
4. Tests - What to test
5. Checkpoint - Create checkpoint after this step
6. Rollback plan - What to do if it fails

Also include:
- Risk assessment with mitigations
- Estimated duration
- Human approval points (if needed)
- Success criteria checklist

Return plan in structured markdown format suitable for automated execution.
"""

        return self.execute(
            prompt=prompt,
            allowed_tools=["Read"],  # Read-only for planning
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=timeout
        )

    def execute_implementation_step(
        self,
        step_description: str,
        step_details: Dict[str, Any],
        context: Dict[str, Any],
        timeout: int = 3600,  # 1 hour per step
        yolo_mode: bool = False
    ) -> ClaudeResult:
        """Execute single implementation step with full permissions.

        Args:
            step_description: Step description
            step_details: Step details from plan
            context: Task context
            timeout: Timeout in seconds
            yolo_mode: Enable fully autonomous mode (skip all permissions)

        Returns:
            ClaudeResult with execution outcome
        """
        prompt = f"""
# Implementation Step

## Step Description
{step_description}

## Step Details
{json.dumps(step_details, indent=2)}

## Context
- Target Repository: {context.get('target_repo', 'N/A')}
- Current Step: {context.get('current_step_number', 'N/A')}

## Your Task
Execute this implementation step carefully:

1. **Before Changes**: Verify current state
2. **Execute**: Make the required changes
3. **Validate**: Run tests and checks
4. **Report**: Provide detailed report of what was done

## Safety Rules
- Validate syntax before saving files
- Run tests after changes
- Never commit secrets or API keys
- Follow existing code conventions
- Create meaningful commit messages

Return structured report with:
- Files modified/created
- Commands executed
- Test results
- Any issues encountered
"""

        permission_mode = PermissionMode.YOLO if yolo_mode else PermissionMode.ACCEPT_EDITS

        return self.execute(
            prompt=prompt,
            allowed_tools=["Read", "Edit", "Write", "Bash", "Grep", "Glob"],
            output_format=OutputFormat.JSON,
            permission_mode=permission_mode,
            timeout=timeout
        )

    def execute_validation(
        self,
        implementation_summary: str,
        context: Dict[str, Any],
        timeout: int = 900  # 15 minutes for validation
    ) -> ClaudeResult:
        """Execute validation phase with testing permissions.

        Args:
            implementation_summary: Summary of what was implemented
            context: Task context
            timeout: Timeout in seconds

        Returns:
            ClaudeResult with validation results
        """
        prompt = f"""
# Validation Phase

## Implementation Summary
{implementation_summary}

## Context
- Target Repository: {context.get('target_repo', 'N/A')}

## Your Task
Validate the implementation comprehensively:

1. **Syntax Checks**
   - Run linter
   - Check for compilation errors

2. **Test Execution**
   - Run all existing tests
   - Run new tests
   - Check test coverage

3. **Integration Validation**
   - Verify feature works as expected
   - Test edge cases
   - Check error handling

4. **Regression Testing**
   - Ensure existing functionality still works
   - No breaking changes introduced

Return validation report with:
- Test results (pass/fail counts)
- Issues found (if any)
- Recommendation: "success", "issues_found", or "critical_failure"
"""

        return self.execute(
            prompt=prompt,
            allowed_tools=["Read", "Bash", "Grep"],  # Can run tests
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=timeout
        )

    def get_total_cost(self) -> float:
        """Get total cost accumulated across all executions."""
        return self.total_cost


# Utility for testing
if __name__ == "__main__":
    import tempfile

    logging.basicConfig(level=logging.INFO)

    print("Testing ClaudeHeadless wrapper...")

    # Create temporary working directory
    with tempfile.TemporaryDirectory() as temp_dir:
        working_dir = Path(temp_dir)

        # Initialize wrapper
        wrapper = ClaudeHeadless(
            working_dir=working_dir,
            default_timeout=30,  # Short timeout for testing
            max_cost_usd=1.00
        )

        print("✓ ClaudeHeadless initialized")

        # Test simple execution
        result = wrapper.execute(
            prompt="Echo 'Hello from Claude Code headless!'",
            allowed_tools=["Bash"],
            output_format=OutputFormat.JSON,
            timeout=10
        )

        if result.success:
            print(f"✓ Execution successful")
            print(f"  Duration: {result.duration_ms}ms")
            if result.cost_usd:
                print(f"  Cost: ${result.cost_usd:.4f}")
        else:
            print(f"✗ Execution failed: {result.error}")

        print(f"\n✓ Total cost: ${wrapper.get_total_cost():.4f}")
        print("\n✅ All tests passed!")
