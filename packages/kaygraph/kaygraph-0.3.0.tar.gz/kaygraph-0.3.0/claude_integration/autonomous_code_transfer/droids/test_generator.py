"""Test Generator Droid - Factory AI Pattern Implementation.

Specialized agent for test generation following Factory AI's testing droid pattern.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from kaygraph import AsyncNode
from utils.claude_headless import ClaudeHeadless, OutputFormat, PermissionMode


logger = logging.getLogger(__name__)


class TestGeneratorDroid(AsyncNode):
    """Factory AI-style test generation droid.

    **Purpose**: Testing specialist that:
    - Analyzes test coverage gaps
    - Generates comprehensive unit tests
    - Creates integration tests
    - Ensures test quality

    **Tools**: Read, Write, Bash (to run tests)
    **Model**: Inherits or uses Sonnet
    **Output**: Generated test files + coverage report
    """

    TEST_PROMPT_TEMPLATE = """# Test Generator Droid

You are a testing specialist generating comprehensive, high-quality tests.

## Operating Rules
1. Analyze existing code for coverage gaps
2. Follow project's testing conventions
3. Generate realistic test data
4. Cover edge cases and error paths
5. Ensure tests are maintainable

## Code to Test
{code_files}

## Existing Tests
{existing_tests}

## Test Coverage Analysis
Current coverage: {current_coverage}%
Missing coverage areas:
{missing_coverage}

## Test Generation Guidelines

### Test Structure Patterns

**Python (pytest)**:
```python
def test_feature_name_should_behavior():
    # Arrange
    input_data = ...

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result == expected
```

**JavaScript (Jest)**:
```javascript
describe('FeatureName', () => {{
  it('should behavior when condition', () => {{
    // Arrange
    const input = ...;

    // Act
    const result = functionUnderTest(input);

    // Assert
    expect(result).toBe(expected);
  }});
}});
```

### Test Scenarios to Cover

#### 1. Happy Path
- Normal, expected usage
- Valid inputs
- Successful outcomes

#### 2. Edge Cases
- Boundary values (0, max, min, empty)
- Special characters
- Large datasets
- Null/undefined handling

#### 3. Error Paths
- Invalid inputs
- Missing required fields
- Type mismatches
- Network failures (for API calls)
- Database errors

#### 4. Integration Points
- External service calls
- Database operations
- File system operations
- API endpoints

### Test Quality Checklist
- ✅ Tests are independent (no shared state)
- ✅ Clear test names describe behavior
- ✅ Arrange-Act-Assert pattern
- ✅ Mock external dependencies
- ✅ Fast execution (<1s per test)
- ✅ Deterministic (no random failures)
- ✅ Easy to understand and maintain

### Mocking Strategy
- Mock external APIs
- Mock database calls
- Mock file system operations
- Mock time/dates for determinism
- Use fixtures for complex setup

## Tasks

### 1. Analyze Coverage Gaps
Identify functions/methods without tests.

### 2. Generate Unit Tests
Create tests for each untested function with:
- Happy path
- Edge cases
- Error handling

### 3. Generate Integration Tests
Test interactions between components.

### 4. Validate Test Quality
Ensure tests follow best practices.

## Output Format

For each code file, generate:

### Test File: `test_filename.py`
```python
# Full test code here
```

### Coverage Report
- Functions tested: X/Y
- Line coverage: N%
- Branch coverage: N%
- Missing coverage: [list areas]

### Test Execution Commands
```bash
# Commands to run tests
pytest tests/test_filename.py -v
pytest --cov=module tests/
```

## Important
- Follow existing test patterns in the project
- Use appropriate fixtures/mocks
- Generate realistic test data
- Include docstrings explaining test purpose
- Ensure tests actually test the behavior (not just call the function)
"""

    def __init__(
        self,
        working_dir: Optional[Path] = None,
        model: str = "inherit"
    ):
        super().__init__(node_id="test_generator_droid")
        self.working_dir = working_dir
        self.model = model
        # Need Write for creating tests, Bash for running them
        self.allowed_tools = ["Read", "Write", "Bash", "Grep"]

    async def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare test generation inputs."""
        return {
            "code_files": shared.get("code_files", []),
            "existing_tests": shared.get("existing_tests", []),
            "current_coverage": shared.get("current_coverage", 0),
            "missing_coverage": shared.get("missing_coverage", []),
            "target_repo": shared.get("target_repo", "."),
            "task_id": shared.get("task_id", "test-gen")
        }

    async def exec(self, prep_res: Dict[str, Any]) -> Dict[str, Any]:
        """Execute test generation using Claude Code headless."""
        logger.info("🧪 Test Generator Droid starting generation...")

        # Build test generation prompt
        test_prompt = self.TEST_PROMPT_TEMPLATE.format(
            code_files="\n".join(f"- {f}" for f in prep_res["code_files"]),
            existing_tests="\n".join(f"- {f}" for f in prep_res["existing_tests"]),
            current_coverage=prep_res["current_coverage"],
            missing_coverage="\n".join(f"- {area}" for area in prep_res["missing_coverage"])
        )

        # Initialize Claude
        claude = ClaudeHeadless(
            working_dir=Path(prep_res["target_repo"]),
            default_timeout=1800  # 30 minutes for test generation
        )

        # Execute test generation
        result = claude.execute(
            prompt=test_prompt,
            allowed_tools=self.allowed_tools,
            output_format=OutputFormat.JSON,
            permission_mode=PermissionMode.YOLO,  # Need to create files
            timeout=1800
        )

        if not result.success:
            return {
                "success": False,
                "error": result.error,
                "tests_generated": []
            }

        # Parse test generation output
        test_content = result.output.get("result", "") if isinstance(result.output, dict) else str(result.output)

        return {
            "success": True,
            "test_content": test_content,
            "cost_usd": result.cost_usd or 0.0,
            "duration_ms": result.duration_ms
        }

    async def post(self, shared: Dict[str, Any], prep_res: Dict[str, Any], exec_res: Dict[str, Any]):
        """Save test generation report."""
        if not exec_res["success"]:
            logger.error(f"Test generation failed: {exec_res['error']}")
            return "generation_failed"

        # Write test generation artifact
        task_id = prep_res["task_id"]
        test_report_file = Path(f"tasks/{task_id}/test_generation_report.md")
        test_report_file.parent.mkdir(parents=True, exist_ok=True)

        test_report = f"""# Test Generation Report

**Generated**: {datetime.now().isoformat()}
**Duration**: {exec_res['duration_ms']}ms
**Cost**: ${exec_res['cost_usd']:.4f}
**Generator**: Test Generator Droid
**Code Files Analyzed**: {len(prep_res['code_files'])}

---

{exec_res['test_content']}

---

**Generated by**: Test Generator Droid (Factory AI Pattern)
"""

        test_report_file.write_text(test_report)

        # Return metadata
        shared["test_generation"] = {
            "report_path": str(test_report_file),
            "cost_usd": exec_res["cost_usd"],
            "files_analyzed": len(prep_res["code_files"])
        }

        logger.info(f"✅ Test generation complete")
        logger.info(f"   Report: {test_report_file}")

        return "tests_generated"


# Testing
if __name__ == "__main__":
    import asyncio

    async def test_generator_droid():
        """Test test generator droid."""
        print("Testing Test Generator Droid...")

        droid = TestGeneratorDroid()

        shared = {
            "task_id": "test-gen",
            "target_repo": ".",
            "code_files": [
                "src/auth.py",
                "src/api/users.py"
            ],
            "existing_tests": [
                "tests/test_api.py"
            ],
            "current_coverage": 45,
            "missing_coverage": [
                "src/auth.py: login() function",
                "src/api/users.py: update_user() function"
            ]
        }

        prep_res = await droid.prep(shared)
        print(f"✓ Prepared test generation for {len(prep_res['code_files'])} files")
        print(f"✓ Current coverage: {prep_res['current_coverage']}%")

        print("✅ Test Generator Droid test structure valid")

    asyncio.run(test_generator_droid())
