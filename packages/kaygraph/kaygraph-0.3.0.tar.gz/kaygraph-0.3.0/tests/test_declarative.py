"""Test declarative workflow functionality."""

from kaygraph import Node, load_workflow, export_workflow, validate_workflow

# Define simple test nodes
class GreeterNode(Node):
    """Node that greets a person."""
    def prep(self, shared):
        return shared.get("name", "World")

    def exec(self, prep_res):
        return f"Hello, {prep_res}!"

    def post(self, shared, prep_res, exec_res):
        shared["greeting"] = exec_res
        return None


class FormatterNode(Node):
    """Node that formats the greeting."""
    def prep(self, shared):
        return shared.get("greeting", "")

    def exec(self, prep_res):
        return prep_res.upper()

    def post(self, shared, prep_res, exec_res):
        shared["formatted"] = exec_res
        return None


# Test 1: Create a workflow YAML file
test_yaml = """workflows:
  main:
    description: "Simple greeting workflow"
    concepts:
      greeter: GreeterNode
      formatter: FormatterNode
    graph:
      greeter >> formatter
"""

with open("test_workflow.kg.yaml", "w") as f:
    f.write(test_yaml)

print("✓ Created test_workflow.kg.yaml")

# Test 2: Validate the workflow
print("\nTest 2: Validating workflow...")
errors = validate_workflow("test_workflow.kg.yaml")
if errors:
    print("✗ Validation failed:")
    for error in errors:
        print(f"  - {error}")
else:
    print("✓ Workflow is valid!")

# Test 3: Load and run the workflow
print("\nTest 3: Loading and running workflow...")
try:
    workflow = load_workflow("test_workflow.kg.yaml")
    print("✓ Workflow loaded successfully")

    # Run with test data
    shared = {"name": "Alice"}
    result = workflow.run(shared)

    print(f"✓ Workflow executed successfully")
    print(f"  Input: {shared.get('name')}")
    print(f"  Greeting: {shared.get('greeting')}")
    print(f"  Formatted: {shared.get('formatted')}")

    # Verify results
    assert shared["greeting"] == "Hello, Alice!"
    assert shared["formatted"] == "HELLO, ALICE!"
    print("✓ Results verified!")

except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Export workflow back to YAML
print("\nTest 4: Exporting workflow...")
try:
    export_workflow(workflow, "exported_workflow.kg.yaml")
    print("✓ Workflow exported successfully")
except Exception as e:
    print(f"✗ Export error: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
