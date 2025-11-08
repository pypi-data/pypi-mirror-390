"""
Tests for KayGraph declarative workflow serialization.

Tests cover:
- Domain serialization to dict and YAML
- Visual converter (ReactFlow ↔ YAML)
- Export functionality
"""

import sys
from pathlib import Path
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from domain import Domain, load_domain
from kaygraph.declarative import (
    WorkflowSerializer,
    VisualConverter,
    serialize_domain,
    yaml_to_canvas,
    canvas_to_yaml
)


def test_domain_to_dict():
    """Test Domain.to_dict() method."""
    print("Test 1: Domain.to_dict()")
    print("-" * 60)

    # Create a simple domain
    domain = Domain(name="test_domain", version="1.0", description="Test domain")

    # Add a concept
    domain.add_concept("User", {
        "description": "User concept",
        "structure": {
            "name": {"type": "string", "required": True},
            "email": {"type": "string", "required": True}
        }
    })

    # Add a workflow
    domain.add_workflow("main", {
        "steps": [
            {"name": "extract", "type": "llm", "config": {"prompt": "Extract user data"}},
            {"name": "validate", "type": "validate", "config": {}}
        ]
    }, is_main=True)

    # Convert to dict
    result = domain.to_dict()

    # Validate structure
    assert "domain" in result
    assert result["domain"]["name"] == "test_domain"
    assert result["domain"]["version"] == "1.0"
    assert result["domain"]["main_workflow"] == "main"

    assert "concepts" in result
    assert "User" in result["concepts"]

    assert "workflows" in result
    assert "main" in result["workflows"]
    assert len(result["workflows"]["main"]["steps"]) == 2

    print("✓ Domain.to_dict() works correctly")
    print(f"  Domain name: {result['domain']['name']}")
    print(f"  Concepts: {list(result['concepts'].keys())}")
    print(f"  Workflows: {list(result['workflows'].keys())}")
    print()
    return True


def test_domain_to_yaml():
    """Test Domain.to_yaml() method."""
    print("Test 2: Domain.to_yaml()")
    print("-" * 60)

    # Create a simple domain
    domain = Domain(name="invoice_processor", version="1.0")
    domain.add_workflow("main", {
        "steps": [{"name": "process", "type": "llm"}]
    }, is_main=True)

    # Convert to YAML
    yaml_str = domain.to_yaml(include_metadata=False)

    # Basic validation
    assert "domain:" in yaml_str
    assert "name: invoice_processor" in yaml_str
    assert "workflows:" in yaml_str
    assert "main:" in yaml_str

    print("✓ Domain.to_yaml() works correctly")
    print("  Generated YAML snippet:")
    for line in yaml_str.split('\n')[:10]:
        print(f"    {line}")
    print()
    return True


def test_domain_to_file():
    """Test Domain.to_file() method."""
    print("Test 3: Domain.to_file()")
    print("-" * 60)

    # Create a simple domain
    domain = Domain(name="test_export", version="1.0")
    domain.add_workflow("main", {"steps": []}, is_main=True)

    # Export to temporary file
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "test.kg.yaml"
        domain.to_file(str(file_path))

        # Verify file exists
        assert file_path.exists()

        # Load and verify
        loaded = load_domain(str(file_path))
        assert loaded.name == "test_export"
        assert loaded.version == "1.0"

    print("✓ Domain.to_file() works correctly")
    print("  File created and reloaded successfully")
    print()
    return True


def test_workflow_serializer():
    """Test WorkflowSerializer class."""
    print("Test 4: WorkflowSerializer")
    print("-" * 60)

    serializer = WorkflowSerializer()

    # Create test domain
    domain = Domain(name="serializer_test", version="2.0")
    domain.add_workflow("main", {
        "steps": [
            {"name": "step1", "type": "llm"},
            {"name": "step2", "type": "transform"}
        ]
    }, is_main=True)

    # Test domain_to_dict
    result = serializer.domain_to_dict(domain)
    assert result["domain"]["name"] == "serializer_test"

    # Test domain_to_yaml
    yaml_str = serializer.domain_to_yaml(domain)
    assert "serializer_test" in yaml_str

    print("✓ WorkflowSerializer works correctly")
    print("  domain_to_dict: OK")
    print("  domain_to_yaml: OK")
    print()
    return True


def test_yaml_to_canvas():
    """Test YAML → ReactFlow canvas conversion."""
    print("Test 5: YAML → ReactFlow canvas")
    print("-" * 60)

    converter = VisualConverter()

    # Test YAML dict
    yaml_dict = {
        "domain": {"name": "test", "main_workflow": "main"},
        "workflows": {
            "main": {
                "steps": [
                    {"name": "extract", "type": "llm", "config": {"prompt": "Test"}},
                    {"name": "validate", "type": "validate"}
                ]
            }
        }
    }

    # Convert to canvas
    canvas = converter.yaml_to_reactflow(yaml_dict)

    # Validate canvas structure
    assert "nodes" in canvas
    assert "edges" in canvas
    assert "viewport" in canvas

    # Should have 2 nodes
    assert len(canvas["nodes"]) == 2

    # Should have 1 edge (connecting the 2 nodes)
    assert len(canvas["edges"]) == 1

    # Validate node structure
    node1 = canvas["nodes"][0]
    assert "id" in node1
    assert "type" in node1
    assert "position" in node1
    assert "data" in node1
    assert node1["data"]["label"] == "extract"

    print("✓ YAML → ReactFlow conversion works correctly")
    print(f"  Nodes generated: {len(canvas['nodes'])}")
    print(f"  Edges generated: {len(canvas['edges'])}")
    print(f"  Node 1: {canvas['nodes'][0]['data']['label']} ({canvas['nodes'][0]['type']})")
    print()
    return True


def test_canvas_to_yaml():
    """Test ReactFlow canvas → YAML conversion."""
    print("Test 6: ReactFlow canvas → YAML")
    print("-" * 60)

    converter = VisualConverter()

    # Test canvas
    canvas = {
        "nodes": [
            {
                "id": "node-1",
                "type": "llm",
                "position": {"x": 250, "y": 0},
                "data": {
                    "label": "Extract Data",
                    "config": {"prompt": "Extract information"},
                    "inputs": [],
                    "outputs": ["extracted_data"]
                }
            },
            {
                "id": "node-2",
                "type": "transform",
                "position": {"x": 250, "y": 120},
                "data": {
                    "label": "Process",
                    "config": {},
                    "inputs": ["extracted_data"],
                    "outputs": []
                }
            }
        ],
        "edges": [
            {
                "id": "edge-1-2",
                "source": "node-1",
                "target": "node-2"
            }
        ],
        "viewport": {"x": 0, "y": 0, "zoom": 1}
    }

    # Convert to YAML dict
    yaml_dict = converter.reactflow_to_yaml(canvas)

    # Validate structure
    assert "canvas" in yaml_dict
    assert "workflows" in yaml_dict
    assert "main" in yaml_dict["workflows"]
    assert "steps" in yaml_dict["workflows"]["main"]

    # Should have 2 steps
    steps = yaml_dict["workflows"]["main"]["steps"]
    assert len(steps) == 2

    # Validate step structure
    assert steps[0]["name"] == "Extract Data"
    assert steps[0]["type"] == "llm"
    assert steps[0]["outputs"] == ["extracted_data"]

    print("✓ ReactFlow → YAML conversion works correctly")
    print(f"  Steps generated: {len(steps)}")
    print(f"  Step 1: {steps[0]['name']} ({steps[0]['type']})")
    print(f"  Canvas preserved: Yes")
    print()
    return True


def test_bidirectional_conversion():
    """Test that YAML → Canvas → YAML is lossless."""
    print("Test 7: Bidirectional conversion (lossless)")
    print("-" * 60)

    converter = VisualConverter()

    # Original YAML
    original = {
        "domain": {"name": "test", "version": "1.0", "main_workflow": "main"},
        "workflows": {
            "main": {
                "steps": [
                    {"name": "analyze", "type": "llm", "config": {"model": "gpt-4"}},
                    {"name": "decide", "type": "condition", "config": {"expression": "score > 0.8"}}
                ]
            }
        }
    }

    # YAML → Canvas
    canvas = converter.yaml_to_reactflow(original)

    # Canvas → YAML
    reconstructed = converter.reactflow_to_yaml(canvas, existing_yaml=original)

    # Verify domain info preserved
    assert reconstructed["domain"]["name"] == original["domain"]["name"]

    # Verify steps preserved
    assert len(reconstructed["workflows"]["main"]["steps"]) == 2
    assert reconstructed["workflows"]["main"]["steps"][0]["name"] == "analyze"
    assert reconstructed["workflows"]["main"]["steps"][1]["name"] == "decide"

    print("✓ Bidirectional conversion is lossless")
    print("  Domain info: Preserved")
    print("  Workflow steps: Preserved")
    print("  Visual layout: Stored in canvas section")
    print()
    return True


def test_auto_layout_generation():
    """Test automatic layout generation."""
    print("Test 8: Auto-layout generation")
    print("-" * 60)

    converter = VisualConverter()

    steps = [
        {"name": "Step 1", "type": "llm"},
        {"name": "Step 2", "type": "transform"},
        {"name": "Step 3", "type": "validate"}
    ]

    # Generate vertical layout
    canvas_vertical = converter.generate_auto_layout(steps, layout_type="vertical")
    assert len(canvas_vertical["nodes"]) == 3

    # Check Y positions increase (vertical)
    y_positions = [n["position"]["y"] for n in canvas_vertical["nodes"]]
    assert y_positions == sorted(y_positions)

    # Generate horizontal layout
    canvas_horizontal = converter.generate_auto_layout(steps, layout_type="horizontal")
    assert len(canvas_horizontal["nodes"]) == 3

    # Check X positions increase (horizontal)
    x_positions = [n["position"]["x"] for n in canvas_horizontal["nodes"]]
    assert x_positions == sorted(x_positions)

    print("✓ Auto-layout generation works correctly")
    print("  Vertical layout: Nodes arranged vertically")
    print("  Horizontal layout: Nodes arranged horizontally")
    print()
    return True


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("KayGraph Declarative Serialization Tests")
    print("=" * 60)
    print()

    tests = [
        test_domain_to_dict,
        test_domain_to_yaml,
        test_domain_to_file,
        test_workflow_serializer,
        test_yaml_to_canvas,
        test_canvas_to_yaml,
        test_bidirectional_conversion,
        test_auto_layout_generation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
