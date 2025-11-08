"""Code Reviewer Droid - Factory AI Pattern Implementation.

Specialized agent for code review following Factory AI's reviewer droid pattern.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from kaygraph import AsyncNode
from utils.claude_headless import ClaudeHeadless, OutputFormat, PermissionMode


logger = logging.getLogger(__name__)


class CodeReviewerDroid(AsyncNode):
    """Factory AI-style code review droid.

    **Purpose**: Senior code reviewer that analyzes changes for:
    - Correctness issues
    - Missing tests
    - Security vulnerabilities
    - Breaking changes
    - Migration risks

    **Tools**: Read-only (Read, Grep, Glob)
    **Model**: Inherits from parent or uses Sonnet for balance
    **Output**: Small metadata + artifact file path
    """

    REVIEW_PROMPT_TEMPLATE = """# Code Review Droid

You are a senior code reviewer performing thorough analysis of code changes.

## Operating Rules
1. Read all changed files before forming opinions
2. Use Grep to find related code and patterns
3. Focus on correctness, security, and maintainability
4. Flag breaking changes immediately
5. Be constructive - suggest improvements, don't just criticize

## Input Context
Changed Files:
{changed_files}

Diff Summary:
{diff_summary}

## Your Review Tasks

### 1. Correctness Analysis
- Logic errors or bugs
- Edge cases not handled
- Potential race conditions
- Off-by-one errors
- Null/undefined handling

### 2. Security Review
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication bypasses
- Exposed secrets or API keys
- Insecure dependencies
- OWASP Top 10 issues

### 3. Test Coverage
- Are there tests for new code?
- Do tests cover edge cases?
- Are tests meaningful (not just for coverage)?
- Integration tests needed?

### 4. Breaking Changes
- Public API modifications
- Database schema changes
- Configuration changes requiring updates
- Backwards compatibility issues

### 5. Migration Risks
- Deprecated API usage
- Data migration needed?
- Coordination with other services?
- Rollback complexity

### 6. Code Quality
- Follows project conventions
- Clear variable/function names
- Appropriate comments
- No code duplication
- Proper error handling

## Output Format

Generate a comprehensive review report with these sections:

### ✅ What Looks Good
List positive aspects of the changes.

### ⚠️ Concerns (Non-Blocking)
Issues that should be addressed but don't block merge.

### ❌ Must Fix Before Merge
Critical issues that MUST be resolved.

### 📝 Suggestions
Optional improvements for consideration.

### 🔍 Questions
Things that need clarification from the author.

### 📊 Summary
- Overall assessment: APPROVE / REQUEST_CHANGES / NEEDS_DISCUSSION
- Risk level: LOW / MEDIUM / HIGH
- Confidence level: 70-100%
- Estimated fix time (if changes needed)

## Important
- Be thorough but concise
- Use concrete examples from the code
- Reference specific file paths and line numbers
- Provide actionable feedback
- If uncertain, ask questions rather than making assumptions
"""

    def __init__(
        self,
        working_dir: Optional[Path] = None,
        model: str = "inherit"
    ):
        super().__init__(node_id="code_reviewer_droid")
        self.working_dir = working_dir
        self.model = model
        # Read-only tools following Factory pattern
        self.allowed_tools = ["Read", "Grep", "Glob"]

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare review inputs."""
        return {
            "changed_files": shared.get("changed_files", []),
            "diff_summary": shared.get("diff_summary", ""),
            "target_repo": shared.get("target_repo", "."),
            "pr_number": shared.get("pr_number"),
            "task_id": shared.get("task_id", "review")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute code review using Claude Code headless."""
        logger.info("🔍 Code Reviewer Droid starting review...")

        # Build review prompt
        review_prompt = self.REVIEW_PROMPT_TEMPLATE.format(
            changed_files="\n".join(f"- {f}" for f in prep_res["changed_files"]),
            diff_summary=prep_res["diff_summary"]
        )

        # Initialize Claude with restricted tools
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["target_repo"]),
            default_timeout=900  # 15 minutes for review
        )

        # Execute review
        result = claude.execute(
            prompt=review_prompt,
            allowed_tools=self.allowed_tools,  # Read-only!
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.ACCEPT_EDITS,
            timeout=900
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error,
                "review_report": None,
                "assessment": "ERROR"
            }

        # Parse review output
        review_content = result.output.get("result", "") if isinstance(result.output, dict) else str(result.output)

        return {
            "success": True,
            "review_content": review_content,
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save review report as artifact file."""
        if not exec_res["success"]:
            logger.error(f"Code review failed: {exec_res['error']}")
            return "review_failed"

        # Write review artifact (Factory pattern: large output goes to file)
        task_id = prep_res["task_id"]
        review_file = Path(f"tasks/{task_id}/code_review_report.md")
        review_file.parent.mkdir(parents=True, exist_ok=True)

        # Add metadata header
        review_report = f"""# Code Review Report

**Reviewed**: {datetime.now().isoformat()}
**Duration**: {exec_res['duration_ms']}ms
**Cost**: ${exec_res['cost_usd']:.4f}
**Reviewer**: Code Reviewer Droid
**Files Reviewed**: {len(prep_res['changed_files'])}

---

{exec_res['review_content']}

---

**Generated by**: Code Reviewer Droid (Factory AI Pattern)
"""

        review_file.write_text(review_report)

        # Parse assessment from review
        review_lower = exec_res["review_content"].lower()
        if "approve" in review_lower:
            assessment = "APPROVE"
        elif "request" in review_lower or "must fix" in review_lower:
            assessment = "REQUEST_CHANGES"
        else:
            assessment = "NEEDS_DISCUSSION"

        # Return small metadata (Factory pattern: not full content!)
        shared["code_review"] = {
            "assessment": assessment,
            "report_path": str(review_file),
            "cost_usd": exec_res["cost_usd"],
            "files_reviewed": len(prep_res["changed_files"])
        }

        logger.info(f"✅ Code review complete: {assessment}")
        logger.info(f"   Report: {review_file}")

        return assessment.lower()  # For conditional routing


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_code_reviewer():
        """Test code reviewer droid."""
        print("Testing Code Reviewer Droid...")

        droid = CodeReviewerDroid()

        # Mock shared context
        shared = {
            "task_id": "test-review",
            "target_repo": ".",
            "changed_files": [
                "src/auth.py",
                "src/api/users.py",
                "tests/test_auth.py"
            ],
            "diff_summary": "Added JWT authentication with refresh tokens",
            "pr_number": 123
        }

        # Prepare
        prep_res = await droid.prep(shared)
        print(f"✓ Prepared review for {len(prep_res['changed_files'])} files")

        # Note: exec() requires actual Claude Code CLI to work
        # This would execute the review in a real scenario
        # exec_res = await droid.exec(prep_res)

        print("✅ Code Reviewer Droid test structure valid")

    asyncio.run(test_code_reviewer())
