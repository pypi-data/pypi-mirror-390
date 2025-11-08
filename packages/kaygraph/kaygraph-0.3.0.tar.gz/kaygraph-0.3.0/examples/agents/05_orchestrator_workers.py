"""
Example 5: Orchestrator-Workers (Multi-File Code Refactoring)

This example shows dynamic task orchestration where:
- Orchestrator breaks down unpredictable tasks
- Delegates to specialized worker LLMs
- Coordinates multi-step operations

Pattern: Orchestrator analyzes → Breaks into subtasks → Delegates to workers
"""

import asyncio
from kaygraph.agent import create_orchestrator_workers
from kaygraph import AsyncNode


# =============================================================================
# WORKER NODES
# =============================================================================

class CodeEditorWorker(AsyncNode):
    """Worker that edits code files"""
    edited_files = []

    async def exec_async(self, task_data):
        file_path = task_data.get("file", "unknown.py")
        change_type = task_data.get("type", "edit")

        self.edited_files.append(file_path)

        return {
            "file": file_path,
            "status": "edited",
            "changes": f"Applied {change_type} to {file_path}",
            "lines_changed": 15
        }

    async def post_async(self, shared, prep_res, exec_res):
        results = shared.get("orchestrator_results", [])
        results.append(f"✓ Edited {exec_res['file']} ({exec_res['lines_changed']} lines)")
        shared["orchestrator_results"] = results
        return None


class TestRunnerWorker(AsyncNode):
    """Worker that runs tests"""

    async def exec_async(self, task_data):
        test_path = task_data.get("test_path", "tests/")

        return {
            "status": "passed",
            "tests_run": 45,
            "tests_passed": 44,
            "tests_failed": 1,
            "message": "1 test failed - needs fixing"
        }

    async def post_async(self, shared, prep_res, exec_res):
        results = shared.get("orchestrator_results", [])
        status_icon = "✓" if exec_res["tests_failed"] == 0 else "⚠️"
        results.append(f"{status_icon} Ran tests: {exec_res['tests_passed']}/{exec_res['tests_run']} passed")
        shared["orchestrator_results"] = results
        return None


class GitWorker(AsyncNode):
    """Worker that performs git operations"""

    async def exec_async(self, task_data):
        operation = task_data.get("operation", "commit")

        if operation == "commit":
            return {
                "status": "committed",
                "commit_hash": "abc123f",
                "message": "Committed changes"
            }
        else:
            return {"status": "completed", "operation": operation}

    async def post_async(self, shared, prep_res, exec_res):
        results = shared.get("orchestrator_results", [])
        results.append(f"✓ Git: {exec_res['message']}")
        shared["orchestrator_results"] = results
        return None


# =============================================================================
# MOCK LLM FOR ORCHESTRATOR
# =============================================================================

async def mock_llm(messages):
    """Mock LLM that plans subtasks"""
    user_content = ""
    for msg in messages:
        if msg["role"] == "user":
            user_content += msg["content"]

    # Generate a realistic plan based on the request
    if "error handling" in user_content.lower():
        return {"content": """```json
[
  {"worker": "code_editor", "task": "Add try-except blocks to api.py", "file": "api.py", "type": "error_handling"},
  {"worker": "code_editor", "task": "Add error handling to database.py", "file": "database.py", "type": "error_handling"},
  {"worker": "code_editor", "task": "Update tests for new error cases", "file": "test_api.py", "type": "test_update"},
  {"worker": "test_runner", "task": "Run updated test suite", "test_path": "tests/"},
  {"worker": "git", "task": "Commit changes", "operation": "commit"}
]
```"""}
    else:
        return {"content": '```json\n[{"worker": "code_editor", "task": "Generic edit"}]\n```'}


# =============================================================================
# CREATE AND RUN ORCHESTRATOR
# =============================================================================

async def main():
    print("=" * 70)
    print("Orchestrator-Workers Example: Multi-File Code Refactoring")
    print("=" * 70)
    print()

    # Create workers
    workers = {
        "code_editor": CodeEditorWorker(),
        "test_runner": TestRunnerWorker(),
        "git": GitWorker()
    }

    print("✓ Created 3 specialized workers:")
    for worker_type in workers.keys():
        print(f"  - {worker_type}")
    print()

    # Create orchestrator
    orchestrator = create_orchestrator_workers(mock_llm, workers)

    print("✓ Created orchestrator")
    print()

    # User request
    user_request = "Add comprehensive error handling to all API endpoints and update the tests"

    print("User Request:")
    print("-" * 70)
    print(user_request)
    print()

    print("Orchestrator Planning...")
    print("-" * 70)

    # Run orchestration
    result = await orchestrator.run_async({
        "user_input": user_request
    })

    # Display the plan
    print()
    print("Generated Plan:")
    print("-" * 70)
    plan = result.get("orchestrator_plan", [])
    for i, subtask in enumerate(plan, 1):
        worker = subtask.get("worker", "unknown")
        task = subtask.get("task", "")
        print(f"{i}. [{worker:15}] {task}")
    print()

    # Display execution results
    print("Execution Results:")
    print("=" * 70)
    results = result.get("orchestrator_results", [])
    for result_line in results:
        print(result_line)
    print()

    print(f"✓ Completed {len(plan)} subtasks")
    print()


# =============================================================================
# WHY USE ORCHESTRATOR-WORKERS?
# =============================================================================

def show_comparison():
    print("=" * 70)
    print("When to Use Orchestrator-Workers vs Other Patterns")
    print("=" * 70)
    print()

    print("PROMPT CHAINING:")
    print("  Use when: Steps are known and fixed")
    print("  Example: Draft → Translate → Format")
    print()

    print("PARALLELIZATION:")
    print("  Use when: Independent tasks known ahead of time")
    print("  Example: Run 4 different validation checks")
    print()

    print("ORCHESTRATOR-WORKERS:")
    print("  Use when: Task structure is UNPREDICTABLE")
    print("  Example: 'Fix all bugs' - could need 2 files or 20 files")
    print("  Example: 'Add feature X' - don't know which components need changes")
    print()

    print("Key Advantage:")
    print("  ✓ Handles variable-complexity tasks")
    print("  ✓ Dynamically determines what's needed")
    print("  ✓ Scales subtasks based on actual requirements")
    print()


if __name__ == "__main__":
    asyncio.run(main())
    show_comparison()
