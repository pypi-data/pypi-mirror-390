# Implementation Plan: Declarative Visual Workflow Builder

**Date**: 2025-11-01
**Status**: Ready for Implementation
**Estimated Duration**: 26-33 hours (3-4 weeks part-time)

---

## Table of Contents

1. [Overview](#overview)
2. [Complete DSL Specification](#complete-dsl-specification)
3. [Phase 1: Core Package](#phase-1-core-package)
4. [Phase 2: Backend API](#phase-2-backend-api)
5. [Phase 3: Frontend UI](#phase-3-frontend-ui)
6. [Phase 4: Integration & Testing](#phase-4-integration--testing)
7. [Implementation Checklist](#implementation-checklist)
8. [Testing Strategy](#testing-strategy)

---

## Overview

### Goal

Build a complete system where users can:
1. Create workflows via chat/visual/YAML
2. Test workflows in browser
3. Export as portable `.kg.yaml` files
4. Deploy as CLI tools or FastAPI endpoints

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│  PHASE 1: Core Package (kaygraph.declarative)          │
│  • Serialization: Domain/Graph → YAML                  │
│  • Visual Converter: ReactFlow ↔ YAML                  │
│  • CLI Export: Generate deployment artifacts           │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 2: Backend API (Kaygraph-Playground)            │
│  • Database Models: WorkflowDefinition, Execution       │
│  • CRUD Endpoints: /api/v1/workflows/                  │
│  • Execution Endpoint: /api/v1/workflows/{id}/execute  │
│  • Export Endpoints: /api/v1/workflows/{id}/export     │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│  PHASE 3: Frontend UI (React + ReactFlow)             │
│  • Visual Canvas: Drag-drop workflow builder           │
│  • Node Palette: All node types available              │
│  • Bidirectional Sync: Visual ↔ YAML ↔ API            │
│  • Test Console: Execute and debug workflows           │
└─────────────────────────────────────────────────────────┘
```

---

## Complete DSL Specification

### Universal `.kg.yaml` Format

```yaml
# ═══════════════════════════════════════════════════════════
# SECTION 1: METADATA
# ═══════════════════════════════════════════════════════════
metadata:
  # Basic information
  title: string                    # Human-readable title
  description: string              # What this workflow does
  author: string                   # Creator email
  version: string                  # Semantic version (e.g., "1.2.0")
  tags: [string]                   # Categories/labels

  # Deployment configuration
  deployment:
    # CLI execution
    cli:
      enabled: boolean             # Can run via kgraph CLI
      input_file: string           # Default input file
      output_file: string          # Default output file

    # FastAPI endpoint
    api:
      enabled: boolean             # Expose as API endpoint
      path: string                 # Endpoint path (e.g., "/api/agents/invoice")
      method: string               # HTTP method (POST, GET, etc.)
      auth_required: boolean       # Require authentication
      rate_limit: integer          # Requests per minute
      timeout: integer             # Seconds before timeout

    # Claude Code integration
    claude_code:
      enabled: boolean
      description_for_llm: string  # When to use this workflow
      usage_example: string        # Example invocation

  # API schemas (for FastAPI endpoint generation)
  input_schema:
    type: object
    properties:
      field_name:
        type: string | number | boolean | object | array
        description: string
        required: boolean
        default: any

  output_schema:
    type: object
    properties:
      field_name:
        type: string
        description: string

# ═══════════════════════════════════════════════════════════
# SECTION 2: VISUAL LAYOUT (Canvas State)
# ═══════════════════════════════════════════════════════════
canvas:
  # Viewport state
  viewport:
    x: number                      # Pan X
    y: number                      # Pan Y
    zoom: number                   # Zoom level (0.1 - 2.0)

  # Theme/appearance
  theme: "light" | "dark"

  # Node positions and styling
  nodes:
    - id: string                   # Unique node identifier
      type: string                 # Node type (llm, transform, etc.)
      position:
        x: number                  # Canvas X position
        y: number                  # Canvas Y position
      size:
        width: number              # Node width
        height: number             # Node height
      style:
        background: string         # CSS color
        color: string              # Text color
        borderColor: string        # Border color
        borderRadius: number       # Corner radius
        borderWidth: number        # Border thickness
      data:
        label: string              # Display label
        icon: string               # Emoji or icon
        collapsed: boolean         # Collapsed state

  # Edge connections and styling
  edges:
    - id: string                   # Unique edge identifier
      source: string               # Source node ID
      target: string               # Target node ID
      sourceHandle: string         # Source port (optional)
      targetHandle: string         # Target port (optional)
      type: string                 # Edge type (default, step, smoothstep)
      label: string                # Edge label (for named actions)
      animated: boolean            # Animation effect
      style:
        stroke: string             # Line color
        strokeWidth: number        # Line thickness
        strokeDasharray: string    # Dashed line pattern

  # Visual grouping (containers)
  groups:
    - id: string                   # Group identifier
      label: string                # Group label
      nodeIds: [string]            # Nodes in this group
      position:
        x: number
        y: number
      style:
        background: string         # Background color
        borderStyle: string        # Border style (solid, dashed)
        borderColor: string
        padding: number

# ═══════════════════════════════════════════════════════════
# SECTION 3: DOMAIN (Execution Logic)
# ═══════════════════════════════════════════════════════════
domain:
  name: string                     # Domain identifier (snake_case)
  version: string                  # Domain version
  description: string              # Domain purpose
  main_workflow: string            # Default workflow to run

# ═══════════════════════════════════════════════════════════
# SECTION 4: CONCEPTS (Type Definitions)
# ═══════════════════════════════════════════════════════════
concepts:
  ConceptName:
    description: string
    structure:
      field_name:
        type: text | number | boolean | array | object | date
        required: boolean
        default: any
        min_value: number          # For numbers
        max_value: number          # For numbers
        min_length: integer        # For text/arrays
        max_length: integer        # For text/arrays
        pattern: string            # Regex pattern (for text)
        choices: [any]             # Enum values
        items:                     # For arrays
          type: string
        properties:                # For objects
          nested_field: {...}

# ═══════════════════════════════════════════════════════════
# SECTION 5: WORKFLOWS (Step Definitions)
# ═══════════════════════════════════════════════════════════
workflows:
  workflow_name:
    description: string            # Workflow purpose (optional)
    steps:
      # Basic step structure
      - node: string               # Node identifier
        type: string               # Node type (llm, extract, transform, condition)
        result: string             # Output name (stored in shared store)
        inputs: [string]           # Input names (from previous results)
        output_concept: string     # Concept for validation

        # Type-specific fields

        # For type: extract
        field: string              # Field to extract from shared store

        # For type: llm
        prompt: string             # LLM prompt (supports {{variable}} interpolation)
        model: string              # LLM model name (optional)
        temperature: number        # Temperature (optional)

        # For type: transform
        mapping:                   # Field mappings
          output_field: "{{input_expr}}"

        # For type: condition
        expression: string         # Boolean expression (safe eval)

        # For batch processing
        batch_over: string         # Field name to iterate over
        batch_as: string           # Variable name for each item

        # For parallel execution
        parallels:                 # List of parallel operations
          - node: string
            type: string
            result: string
            # ... (same structure as regular step)

# ═══════════════════════════════════════════════════════════
# SECTION 6: EXAMPLES (Test Cases)
# ═══════════════════════════════════════════════════════════
examples:
  - name: string                   # Example name
    description: string            # What this tests
    input:                         # Input data
      field_name: value
    expected_output:               # Expected result
      field_name: value
    tags: [string]                 # Categories (e.g., ["edge_case"])
```

---

## Phase 1: Core Package

### Duration: 6-8 hours

### Objective

Add bidirectional serialization and visual conversion to `kaygraph.declarative` package.

### Files to Create

#### 1. `kaygraph/declarative/serializer.py` (~300 lines)

```python
"""
Bidirectional serialization for declarative workflows.

Enables exporting Domain/Graph objects back to YAML format.
"""

from typing import Dict, Any, List, Optional
import yaml
from domain import Domain
from kaygraph import Graph
from nodes import ConfigNode


class WorkflowSerializer:
    """Serialize KayGraph objects to YAML format."""

    def domain_to_dict(self, domain: Domain) -> Dict[str, Any]:
        """
        Convert Domain object to dictionary.

        Args:
            domain: Domain instance to serialize

        Returns:
            Dictionary in .kg.yaml format
        """
        result = {}

        # Domain section
        result["domain"] = {
            "name": domain.name,
            "version": domain.version,
        }
        if domain.description:
            result["domain"]["description"] = domain.description
        if domain.main_workflow:
            result["domain"]["main_workflow"] = domain.main_workflow

        # Concepts section
        if domain.concepts:
            result["concepts"] = {}
            for name, concept_def in domain.concepts.items():
                # If concept_def is Concept object, call to_dict()
                if hasattr(concept_def, 'to_dict'):
                    result["concepts"][name] = concept_def.to_dict()
                else:
                    result["concepts"][name] = concept_def

        # Workflows section
        if domain.workflows:
            result["workflows"] = {}
            for name, workflow_config in domain.workflows.items():
                result["workflows"][name] = self.serialize_workflow(workflow_config)

        return result

    def serialize_workflow(self, workflow_config: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize a workflow configuration."""
        # Workflow config is already in correct format
        # Just ensure steps are properly formatted
        if "steps" in workflow_config:
            workflow_config["steps"] = [
                self.serialize_step(step)
                for step in workflow_config["steps"]
            ]
        return workflow_config

    def serialize_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize a workflow step."""
        # Remove None values
        return {k: v for k, v in step.items() if v is not None}

    def domain_to_yaml(self, domain: Domain, include_metadata: bool = False) -> str:
        """
        Convert Domain to YAML string.

        Args:
            domain: Domain instance
            include_metadata: Include metadata section

        Returns:
            Complete .kg.yaml content
        """
        data = self.domain_to_dict(domain)

        # Add metadata section if requested
        if include_metadata and hasattr(domain, 'metadata'):
            data = {"metadata": domain.metadata, **data}

        # Add canvas section if present
        if hasattr(domain, 'canvas'):
            data["canvas"] = domain.canvas

        # Convert to YAML
        return yaml.dump(
            data,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            width=1000  # Prevent line wrapping
        )

    def graph_to_workflow_dict(self, graph: Graph) -> Dict[str, Any]:
        """
        Convert Graph to workflow dictionary.

        Args:
            graph: Graph instance

        Returns:
            Workflow configuration dict
        """
        steps = []
        current = graph.start_node
        visited = set()

        while current and id(current) not in visited:
            visited.add(id(current))

            # Convert node to step
            if isinstance(current, ConfigNode):
                step = self.config_node_to_step(current)
                steps.append(step)

            # Get next node (follow default action)
            next_node = current.successors.get("default")
            if not next_node and current.successors:
                # If no default, take first successor
                next_node = next(iter(current.successors.values()))

            current = next_node

        return {"steps": steps}

    def config_node_to_step(self, node: ConfigNode) -> Dict[str, Any]:
        """
        Convert ConfigNode to step dictionary.

        Args:
            node: ConfigNode instance

        Returns:
            Step configuration dict
        """
        step = {
            "node": node.node_id,
            "type": node.config.get("type"),
        }

        # Add result name
        if hasattr(node, 'result_name') and node.result_name:
            step["result"] = node.result_name

        # Add inputs
        if hasattr(node, 'input_names') and node.input_names:
            step["inputs"] = node.input_names

        # Add output concept
        if hasattr(node, 'output_concept') and node.output_concept:
            step["output_concept"] = node.output_concept

        # Add all config fields (except type)
        for key, value in node.config.items():
            if key != "type" and value is not None:
                step[key] = value

        # Handle special node types
        if hasattr(node, 'batch_over'):
            step["batch_over"] = node.batch_over
            if hasattr(node, 'batch_as'):
                step["batch_as"] = node.batch_as

        if hasattr(node, 'parallels'):
            step["parallels"] = node.parallels

        return step


# Singleton instance
_serializer = None

def get_serializer() -> WorkflowSerializer:
    """Get global serializer instance."""
    global _serializer
    if _serializer is None:
        _serializer = WorkflowSerializer()
    return _serializer
```

#### 2. `kaygraph/declarative/visual_converter.py` (~250 lines)

```python
"""
Convert between ReactFlow visual format and KayGraph YAML format.

This enables bidirectional synchronization between the visual canvas
and the declarative workflow definition.
"""

from typing import Dict, Any, List, Tuple


class VisualConverter:
    """Convert between ReactFlow and KayGraph YAML formats."""

    # Node type to visual style mapping
    NODE_STYLES = {
        "extract": {"background": "#4299E1", "color": "#FFFFFF", "icon": "📥"},
        "llm": {"background": "#48BB78", "color": "#FFFFFF", "icon": "🤖"},
        "transform": {"background": "#ED8936", "color": "#FFFFFF", "icon": "🔄"},
        "condition": {"background": "#9F7AEA", "color": "#FFFFFF", "icon": "❓"},
        "validate": {"background": "#F56565", "color": "#FFFFFF", "icon": "✓"},
        "parallel": {"background": "#38B2AC", "color": "#FFFFFF", "icon": "⚡"},
        "batch": {"background": "#D69E2E", "color": "#FFFFFF", "icon": "📦"},
    }

    def reactflow_to_domain_dict(
        self,
        reactflow_data: Dict[str, Any],
        domain_name: str = "workflow",
        domain_version: str = "1.0"
    ) -> Dict[str, Any]:
        """
        Convert ReactFlow data to Domain dictionary.

        Args:
            reactflow_data: ReactFlow nodes and edges
            domain_name: Domain name
            domain_version: Domain version

        Returns:
            Complete domain dictionary in .kg.yaml format
        """
        nodes = reactflow_data.get("nodes", [])
        edges = reactflow_data.get("edges", [])

        # Build domain structure
        domain_dict = {
            "domain": {
                "name": domain_name,
                "version": domain_version
            },
            "workflows": {
                "main": {
                    "steps": self._nodes_to_steps(nodes, edges)
                }
            },
            "canvas": {
                "viewport": reactflow_data.get("viewport", {"x": 0, "y": 0, "zoom": 1.0}),
                "nodes": self._extract_visual_layout(nodes),
                "edges": self._extract_edge_styles(edges)
            }
        }

        # Extract concepts if defined in node data
        concepts = self._extract_concepts_from_nodes(nodes)
        if concepts:
            domain_dict["concepts"] = concepts

        return domain_dict

    def _nodes_to_steps(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Convert ReactFlow nodes to workflow steps."""
        # Build adjacency map
        adjacency = self._build_adjacency(edges)

        # Topological sort to get execution order
        sorted_ids = self._topological_sort(nodes, adjacency)

        # Convert each node to step
        steps = []
        for node_id in sorted_ids:
            node = next((n for n in nodes if n["id"] == node_id), None)
            if node:
                step = self._node_to_step(node, adjacency)
                steps.append(step)

        return steps

    def _node_to_step(self, node: Dict, adjacency: Dict) -> Dict[str, Any]:
        """Convert single ReactFlow node to step."""
        node_data = node.get("data", {})
        node_type = node.get("type", "llm")

        step = {
            "node": node_data.get("label", node["id"]).lower().replace(" ", "_"),
            "type": node_type
        }

        # Add result name
        if "result" in node_data:
            step["result"] = node_data["result"]

        # Add inputs (from incoming edges)
        inputs = self._get_node_inputs(node["id"], adjacency)
        if inputs:
            step["inputs"] = inputs

        # Add type-specific fields from node data
        for key in ["prompt", "field", "mapping", "expression", "output_concept",
                    "batch_over", "batch_as", "parallels", "model", "temperature"]:
            if key in node_data:
                step[key] = node_data[key]

        return step

    def _build_adjacency(self, edges: List[Dict]) -> Dict[str, List[Tuple[str, str]]]:
        """Build adjacency list from edges."""
        adjacency = {}
        for edge in edges:
            source = edge["source"]
            target = edge["target"]
            label = edge.get("label", "default")

            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append((target, label))

        return adjacency

    def _topological_sort(self, nodes: List[Dict], adjacency: Dict) -> List[str]:
        """Sort nodes in execution order."""
        # Simple topological sort (assumes DAG)
        # For now, preserve ReactFlow order (can enhance later)
        return [node["id"] for node in nodes]

    def _get_node_inputs(self, node_id: str, adjacency: Dict) -> List[str]:
        """Get input names for a node from incoming edges."""
        inputs = []
        for source_id, targets in adjacency.items():
            for target_id, label in targets:
                if target_id == node_id:
                    # Find source node's result name
                    # This is simplified - real implementation would track results
                    inputs.append(f"{source_id}_result")
        return inputs

    def _extract_visual_layout(self, nodes: List[Dict]) -> List[Dict]:
        """Extract visual layout information."""
        layout = []
        for node in nodes:
            layout.append({
                "id": node["id"],
                "position": node.get("position", {"x": 0, "y": 0}),
                "size": node.get("size", {"width": 180, "height": 80}),
                "style": node.get("style", {})
            })
        return layout

    def _extract_edge_styles(self, edges: List[Dict]) -> List[Dict]:
        """Extract edge styling information."""
        edge_styles = []
        for edge in edges:
            edge_styles.append({
                "id": edge["id"],
                "source": edge["source"],
                "target": edge["target"],
                "label": edge.get("label"),
                "style": edge.get("style", {})
            })
        return edge_styles

    def _extract_concepts_from_nodes(self, nodes: List[Dict]) -> Dict[str, Any]:
        """Extract concept definitions from node configurations."""
        concepts = {}
        for node in nodes:
            node_data = node.get("data", {})
            if "output_concept_def" in node_data:
                concept_name = node_data.get("output_concept")
                if concept_name:
                    concepts[concept_name] = node_data["output_concept_def"]
        return concepts

    def domain_dict_to_reactflow(self, domain_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert domain dictionary to ReactFlow format.

        Args:
            domain_dict: Domain dictionary from YAML

        Returns:
            ReactFlow nodes and edges
        """
        # Extract workflow steps
        workflows = domain_dict.get("workflows", {})
        main_workflow = workflows.get("main", workflows.get(list(workflows.keys())[0]))
        steps = main_workflow.get("steps", [])

        # Extract canvas layout if present
        canvas = domain_dict.get("canvas", {})
        layout_nodes = {n["id"]: n for n in canvas.get("nodes", [])}
        layout_edges = {e["id"]: e for e in canvas.get("edges", [])}

        # Convert steps to nodes
        nodes = []
        for i, step in enumerate(steps):
            node = self._step_to_reactflow_node(
                step,
                i,
                layout_nodes.get(step["node"])
            )
            nodes.append(node)

        # Generate edges from step dependencies
        edges = self._generate_reactflow_edges(steps, layout_edges)

        # Add viewport
        viewport = canvas.get("viewport", {"x": 0, "y": 0, "zoom": 1.0})

        return {
            "nodes": nodes,
            "edges": edges,
            "viewport": viewport
        }

    def _step_to_reactflow_node(
        self,
        step: Dict[str, Any],
        index: int,
        layout: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Convert workflow step to ReactFlow node."""
        node_type = step.get("type", "llm")
        style = self.NODE_STYLES.get(node_type, self.NODE_STYLES["llm"])

        # Use layout if available, otherwise auto-position
        position = layout.get("position") if layout else {"x": 100 + (index * 250), "y": 200}
        size = layout.get("size") if layout else {"width": 180, "height": 80}

        node = {
            "id": step["node"],
            "type": node_type,
            "position": position,
            "data": {
                "label": step["node"].replace("_", " ").title(),
                "icon": style["icon"],
                **{k: v for k, v in step.items() if k not in ["node", "type"]}
            },
            "style": {
                **style,
                **layout.get("style", {}) if layout else {}
            }
        }

        return node

    def _generate_reactflow_edges(
        self,
        steps: List[Dict],
        layout_edges: Dict[str, Dict]
    ) -> List[Dict]:
        """Generate ReactFlow edges from step dependencies."""
        edges = []

        for i, step in enumerate(steps):
            # Simple sequential connection
            if i < len(steps) - 1:
                edge_id = f"e{i}-{i+1}"
                layout = layout_edges.get(edge_id, {})

                edges.append({
                    "id": edge_id,
                    "source": step["node"],
                    "target": steps[i + 1]["node"],
                    "type": "default",
                    "style": layout.get("style", {"stroke": "#CBD5E0", "strokeWidth": 2})
                })

        return edges


# Singleton instance
_converter = None

def get_visual_converter() -> VisualConverter:
    """Get global visual converter instance."""
    global _converter
    if _converter is None:
        _converter = VisualConverter()
    return _converter
```

#### 3. Modify `kaygraph/declarative/domain.py` (+50 lines)

Add `to_dict()` method to `Domain` class:

```python
class Domain:
    # ... existing code ...

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert domain to dictionary format.

        Returns:
            Dictionary in .kg.yaml format
        """
        from serializer import get_serializer
        serializer = get_serializer()
        return serializer.domain_to_dict(self)

    def to_yaml(self, include_metadata: bool = False) -> str:
        """
        Convert domain to YAML string.

        Args:
            include_metadata: Include metadata section

        Returns:
            Complete .kg.yaml content
        """
        from serializer import get_serializer
        serializer = get_serializer()
        return serializer.domain_to_yaml(self, include_metadata)
```

#### 4. Modify `kaygraph/declarative/cli.py` (+100 lines)

Add export commands:

```python
def cmd_export(args) -> int:
    """Export workflow to different formats."""
    workflow_path = args.workflow
    export_format = args.format  # 'yaml', 'python', 'claude'
    output_path = args.output

    # Load workflow
    if ':' in workflow_path:
        path, workflow_name = workflow_path.rsplit(':', 1)
        domain = load_domain(path)
    else:
        domain = load_domain(workflow_path)

    if export_format == 'yaml':
        # Export as clean YAML
        yaml_content = domain.to_yaml(include_metadata=True)
        with open(output_path, 'w') as f:
            f.write(yaml_content)
        print(f"✓ Exported to {output_path}")

    elif export_format == 'python':
        # Generate Python endpoint code
        python_code = generate_python_endpoint(domain)
        with open(output_path, 'w') as f:
            f.write(python_code)
        print(f"✓ Generated Python endpoint: {output_path}")

    elif export_format == 'claude':
        # Generate Claude Code documentation
        claude_docs = generate_claude_docs(domain)
        with open(output_path, 'w') as f:
            f.write(claude_docs)
        print(f"✓ Generated Claude Code docs: {output_path}")

    return 0


def generate_python_endpoint(domain: Domain) -> str:
    """Generate FastAPI endpoint code."""
    template = f"""
# Auto-generated endpoint for: {domain.name}
# Generated: {datetime.now().isoformat()}

from fastapi import APIRouter, Depends
from kaygraph.declarative import load_domain_from_string
from pydantic import BaseModel

router = APIRouter()

WORKFLOW_YAML = \"\"\"
{domain.to_yaml()}
\"\"\"

@router.post("/api/agents/{domain.name}")
async def execute_{domain.name}(request: dict):
    \"\"\"Execute {domain.name} workflow.\"\"\"
    domain = load_domain_from_string(WORKFLOW_YAML)
    graph = create_graph_from_domain(domain)
    shared = request.copy()
    graph.run(shared)
    return shared
"""
    return template


def generate_claude_docs(domain: Domain) -> str:
    """Generate Claude Code integration documentation."""
    template = f"""
# {domain.name.replace('_', ' ').title()}

**Workflow File**: `{domain.name}.kg.yaml`

## Description

{domain.description or f'Workflow for {domain.name}'}

## When to Use

[Describe when Claude Code should use this workflow]

## Usage

```bash
# CLI execution
kgraph run {domain.name}.kg.yaml --input <(echo '{{"field": "value"}}')

# Python integration
from kaygraph.declarative import load_domain, create_graph_from_domain

domain = load_domain("{domain.name}.kg.yaml")
graph = create_graph_from_domain(domain)
result = graph.run({{"field": "value"}})
```

## Input Format

[Document expected input structure]

## Output Format

[Document output structure]

## Examples

[Provide usage examples]
"""
    return template


# Update argument parser
parser_export = subparsers.add_parser('export', help='Export workflow to different formats')
parser_export.add_argument('workflow', help='Workflow file path')
parser_export.add_argument('--format', choices=['yaml', 'python', 'claude'], default='yaml')
parser_export.add_argument('--output', '-o', required=True, help='Output file path')
parser_export.set_defaults(func=cmd_export)
```

#### 5. Update `setup.py`

```python
setup(
    name="kaygraph",
    version=get_version(),
    packages=find_packages(),

    install_requires=[],  # Zero dependencies for core

    extras_require={
        "declarative": [
            "pyyaml>=6.0",
        ],
    },

    entry_points={
        "console_scripts": [
            "kgraph=kaygraph.declarative.cli:main [declarative]",
        ],
    },

    # ... rest of setup ...
)
```

### Testing for Phase 1

Create `tests/test_serialization.py`:

```python
def test_domain_to_yaml():
    """Test Domain → YAML conversion."""
    domain = Domain("test_workflow", "1.0")
    domain.add_concept("Invoice", {...})
    domain.add_workflow("main", {"steps": [...]})

    yaml_content = domain.to_yaml()

    # Verify YAML is valid
    data = yaml.safe_load(yaml_content)
    assert data["domain"]["name"] == "test_workflow"
    assert "Invoice" in data["concepts"]

def test_yaml_round_trip():
    """Test YAML → Domain → YAML preserves data."""
    original_yaml = load_file("test_workflow.kg.yaml")

    # Load
    domain = load_domain("test_workflow.kg.yaml")

    # Export
    exported_yaml = domain.to_yaml()

    # Compare (structural equality)
    original_data = yaml.safe_load(original_yaml)
    exported_data = yaml.safe_load(exported_yaml)

    assert original_data == exported_data

def test_visual_converter():
    """Test ReactFlow ↔ YAML conversion."""
    reactflow_data = {
        "nodes": [...],
        "edges": [...]
    }

    # ReactFlow → Domain dict
    converter = get_visual_converter()
    domain_dict = converter.reactflow_to_domain_dict(reactflow_data)

    assert "workflows" in domain_dict
    assert len(domain_dict["workflows"]["main"]["steps"]) > 0

    # Domain dict → ReactFlow
    reactflow_back = converter.domain_dict_to_reactflow(domain_dict)

    assert len(reactflow_back["nodes"]) == len(reactflow_data["nodes"])
```

### Phase 1 Checklist

- [ ] Create `serializer.py` with `WorkflowSerializer` class
- [ ] Create `visual_converter.py` with `VisualConverter` class
- [ ] Add `to_dict()` and `to_yaml()` to `Domain` class
- [ ] Add `export` command to CLI
- [ ] Update `setup.py` with dependencies and entry points
- [ ] Write unit tests for serialization
- [ ] Write unit tests for visual converter
- [ ] Test CLI export commands
- [ ] Verify round-trip: YAML → Domain → YAML
- [ ] Verify `pip install -e .[declarative]` works
- [ ] Verify `kgraph export` works

---

## Phase 2: Backend API

### Duration: 8-10 hours

### Objective

Build REST API for workflow CRUD and execution in Kaygraph-Playground.

### Database Schema

#### SQL DDL

```sql
-- WorkflowDefinition table
CREATE TABLE workflow_definition (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,

    -- Basic info
    name VARCHAR(255) NOT NULL,
    description TEXT,

    -- Workflow content
    yaml_content TEXT NOT NULL,  -- The .kg.yaml file content
    visual_layout JSONB,         -- ReactFlow state (optional)

    -- Metadata
    version VARCHAR(50) DEFAULT '1.0.0',
    is_deployed BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,

    -- Audit
    created_by UUID REFERENCES "user"(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    -- Constraints
    UNIQUE(organization_id, name)
);

CREATE INDEX idx_workflow_org ON workflow_definition(organization_id);
CREATE INDEX idx_workflow_deployed ON workflow_definition(is_deployed) WHERE is_deployed = TRUE;

-- WorkflowExecution table
CREATE TABLE workflow_execution (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workflow_id UUID NOT NULL REFERENCES workflow_definition(id) ON DELETE CASCADE,
    organization_id UUID NOT NULL REFERENCES organization(id) ON DELETE CASCADE,

    -- Execution data
    input_data JSONB NOT NULL,
    output_data JSONB,

    -- Status
    status VARCHAR(50) NOT NULL,  -- 'pending', 'running', 'success', 'error'
    error_message TEXT,

    -- Timing
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    duration_ms INTEGER,

    -- User
    executed_by UUID REFERENCES "user"(id),

    -- Metadata
    execution_mode VARCHAR(20) DEFAULT 'real',  -- 'mock' or 'real'
    step_results JSONB  -- Intermediate results for debugging
);

CREATE INDEX idx_execution_workflow ON workflow_execution(workflow_id);
CREATE INDEX idx_execution_org ON workflow_execution(organization_id);
CREATE INDEX idx_execution_status ON workflow_execution(status);
CREATE INDEX idx_execution_started ON workflow_execution(started_at DESC);
```

#### Tortoise ORM Models

File: `backend/app/models.py` (add to existing file)

```python
from tortoise import fields
from tortoise.models import Model

class TenantModel(Model):
    """Base model with organization_id for multi-tenancy."""
    class Meta:
        abstract = True

    organization_id = fields.UUIDField(index=True)


class WorkflowDefinition(TenantModel):
    """
    Declarative workflow definition.

    Stores workflows as .kg.yaml content with optional visual layout.
    """
    id = fields.UUIDField(pk=True)

    # Basic info
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

    # Workflow content
    yaml_content = fields.TextField()  # The .kg.yaml file
    visual_layout = fields.JSONField(null=True)  # ReactFlow state

    # Metadata
    version = fields.CharField(max_length=50, default="1.0.0")
    is_deployed = fields.BooleanField(default=False)
    is_public = fields.BooleanField(default=False)

    # Audit
    created_by = fields.ForeignKeyField("models.User", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "workflow_definition"
        unique_together = (("organization_id", "name"),)


class WorkflowExecution(TenantModel):
    """
    Workflow execution log.

    Stores input, output, and execution metadata for each workflow run.
    """
    id = fields.UUIDField(pk=True)
    workflow = fields.ForeignKeyField("models.WorkflowDefinition", related_name="executions")

    # Execution data
    input_data = fields.JSONField()
    output_data = fields.JSONField(null=True)

    # Status
    status = fields.CharField(max_length=50)  # 'pending', 'running', 'success', 'error'
    error_message = fields.TextField(null=True)

    # Timing
    started_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    duration_ms = fields.IntField(null=True)

    # User
    executed_by = fields.ForeignKeyField("models.User", null=True)

    # Metadata
    execution_mode = fields.CharField(max_length=20, default="real")  # 'mock' or 'real'
    step_results = fields.JSONField(null=True)  # Debugging info

    class Meta:
        table = "workflow_execution"
```

### Migration

```bash
cd backend
source .venv/bin/activate
aerich migrate --name "add_workflow_tables"
aerich upgrade
```

### API Endpoints

#### File: `backend/app/api/routes/workflows.py` (~250 lines)

```python
"""
Workflow CRUD endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from typing import List
from uuid import UUID
import yaml

from app.api.deps import CurrentUser, CurrentOrg, require_permission
from app.models import WorkflowDefinition
from app.schemas import (
    WorkflowCreate,
    WorkflowUpdate,
    WorkflowPublic,
    WorkflowList
)

router = APIRouter()


@router.get("/", response_model=List[WorkflowList])
async def list_workflows(
    user: CurrentUser,
    org: CurrentOrg,
    skip: int = 0,
    limit: int = 100,
    is_deployed: bool | None = None
):
    """
    List workflows for current organization.

    Query parameters:
    - skip: Pagination offset
    - limit: Number of results
    - is_deployed: Filter by deployment status
    """
    query = WorkflowDefinition.filter(organization_id=org.id)

    if is_deployed is not None:
        query = query.filter(is_deployed=is_deployed)

    workflows = await query.offset(skip).limit(limit).all()
    return workflows


@router.post("/", response_model=WorkflowPublic)
async def create_workflow(
    workflow_in: WorkflowCreate,
    user: CurrentUser,
    org: CurrentOrg
):
    """
    Create a new workflow.

    Body should include:
    - name: Workflow name (unique per org)
    - description: Optional description
    - yaml_content: Complete .kg.yaml content
    - visual_layout: Optional ReactFlow state
    """
    # Check permission
    require_permission(user, org, "workflows.create")

    # Check for duplicate name
    existing = await WorkflowDefinition.filter(
        organization_id=org.id,
        name=workflow_in.name
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Workflow name already exists")

    # Validate YAML
    try:
        yaml_data = yaml.safe_load(workflow_in.yaml_content)
        if "workflows" not in yaml_data:
            raise ValueError("Invalid workflow format: missing 'workflows' section")
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    # Create workflow
    workflow = await WorkflowDefinition.create(
        organization_id=org.id,
        created_by_id=user.id,
        **workflow_in.dict()
    )

    return workflow


@router.get("/{workflow_id}", response_model=WorkflowPublic)
async def get_workflow(
    workflow_id: UUID,
    user: CurrentUser,
    org: CurrentOrg
):
    """Get workflow by ID."""
    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@router.put("/{workflow_id}", response_model=WorkflowPublic)
async def update_workflow(
    workflow_id: UUID,
    workflow_in: WorkflowUpdate,
    user: CurrentUser,
    org: CurrentOrg
):
    """Update workflow."""
    require_permission(user, org, "workflows.update")

    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Update fields
    update_data = workflow_in.dict(exclude_unset=True)

    # Validate YAML if provided
    if "yaml_content" in update_data:
        try:
            yaml_data = yaml.safe_load(update_data["yaml_content"])
            if "workflows" not in yaml_data:
                raise ValueError("Invalid workflow format")
        except yaml.YAMLError as e:
            raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    await workflow.update_from_dict(update_data)
    await workflow.save()

    return workflow


@router.delete("/{workflow_id}")
async def delete_workflow(
    workflow_id: UUID,
    user: CurrentUser,
    org: CurrentOrg
):
    """Delete workflow."""
    require_permission(user, org, "workflows.delete")

    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    await workflow.delete()

    return {"status": "deleted", "id": str(workflow_id)}


@router.post("/{workflow_id}/deploy")
async def deploy_workflow(
    workflow_id: UUID,
    user: CurrentUser,
    org: CurrentOrg
):
    """
    Deploy workflow (make available as API endpoint).

    Deployed workflows can be executed via /api/v1/agents/{workflow_name}
    """
    require_permission(user, org, "workflows.deploy")

    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.is_deployed = True
    await workflow.save()

    return {
        "status": "deployed",
        "endpoint": f"/api/v1/agents/{workflow.name}"
    }


@router.post("/{workflow_id}/undeploy")
async def undeploy_workflow(
    workflow_id: UUID,
    user: CurrentUser,
    org: CurrentOrg
):
    """Undeploy workflow (remove from API endpoints)."""
    require_permission(user, org, "workflows.deploy")

    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow.is_deployed = False
    await workflow.save()

    return {"status": "undeployed"}


@router.get("/{workflow_id}/export")
async def export_workflow(
    workflow_id: UUID,
    format: str = "yaml",  # 'yaml', 'python', 'claude'
    user: CurrentUser,
    org: CurrentOrg
):
    """
    Export workflow in different formats.

    Formats:
    - yaml: Clean .kg.yaml file
    - python: FastAPI endpoint code
    - claude: Claude Code documentation
    """
    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if format == "yaml":
        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            workflow.yaml_content,
            headers={
                "Content-Disposition": f'attachment; filename="{workflow.name}.kg.yaml"'
            }
        )

    elif format == "python":
        # Generate Python endpoint code
        from app.services.workflow_runner import generate_python_endpoint
        code = generate_python_endpoint(workflow)

        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            code,
            headers={
                "Content-Disposition": f'attachment; filename="{workflow.name}_endpoint.py"'
            }
        )

    elif format == "claude":
        # Generate Claude Code docs
        from app.services.workflow_runner import generate_claude_docs
        docs = generate_claude_docs(workflow)

        from fastapi.responses import PlainTextResponse
        return PlainTextResponse(
            docs,
            headers={
                "Content-Disposition": f'attachment; filename="{workflow.name}_CLAUDE.md"'
            }
        )

    else:
        raise HTTPException(status_code=400, detail="Invalid format")


@router.post("/import")
async def import_workflow(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(),
    org: CurrentOrg = Depends()
):
    """
    Import workflow from .kg.yaml file.

    Uploads:
    - file: .kg.yaml file to import
    """
    require_permission(user, org, "workflows.create")

    # Read file content
    content = await file.read()
    yaml_content = content.decode("utf-8")

    # Parse YAML
    try:
        yaml_data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"Invalid YAML: {e}")

    # Extract domain name
    domain_name = yaml_data.get("domain", {}).get("name", "imported_workflow")
    description = yaml_data.get("domain", {}).get("description")

    # Check for existing workflow with same name
    existing = await WorkflowDefinition.filter(
        organization_id=org.id,
        name=domain_name
    ).first()

    if existing:
        # Auto-increment name
        counter = 1
        while existing:
            test_name = f"{domain_name}_{counter}"
            existing = await WorkflowDefinition.filter(
                organization_id=org.id,
                name=test_name
            ).first()
            counter += 1
        domain_name = test_name

    # Create workflow
    workflow = await WorkflowDefinition.create(
        organization_id=org.id,
        created_by_id=user.id,
        name=domain_name,
        description=description,
        yaml_content=yaml_content
    )

    return workflow
```

#### File: `backend/app/api/routes/executions.py` (~150 lines)

```python
"""
Workflow execution endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List
from uuid import UUID
import asyncio
from datetime import datetime

from app.api.deps import CurrentUser, CurrentOrg
from app.models import WorkflowDefinition, WorkflowExecution
from app.schemas import ExecutionCreate, ExecutionPublic, ExecutionList
from app.services.workflow_runner import execute_workflow

router = APIRouter()


@router.post("/{workflow_id}/execute", response_model=ExecutionPublic)
async def execute_workflow_endpoint(
    workflow_id: UUID,
    execution_in: ExecutionCreate,
    user: CurrentUser,
    org: CurrentOrg
):
    """
    Execute a workflow.

    Body:
    - input_data: Input for workflow execution
    - execution_mode: 'mock' or 'real' (default: 'real')
    """
    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Create execution record
    execution = await WorkflowExecution.create(
        workflow_id=workflow.id,
        organization_id=org.id,
        executed_by_id=user.id,
        input_data=execution_in.input_data,
        execution_mode=execution_in.execution_mode,
        status="pending"
    )

    # Execute workflow in background
    asyncio.create_task(
        execute_workflow(execution.id, workflow, execution_in)
    )

    return execution


@router.get("/{workflow_id}/executions", response_model=List[ExecutionList])
async def list_executions(
    workflow_id: UUID,
    user: CurrentUser,
    org: CurrentOrg,
    skip: int = 0,
    limit: int = 20
):
    """List executions for a workflow."""
    workflow = await WorkflowDefinition.get_or_none(
        id=workflow_id,
        organization_id=org.id
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    executions = await WorkflowExecution.filter(
        workflow_id=workflow.id
    ).order_by("-started_at").offset(skip).limit(limit).all()

    return executions


@router.get("/executions/{execution_id}", response_model=ExecutionPublic)
async def get_execution(
    execution_id: UUID,
    user: CurrentUser,
    org: CurrentOrg
):
    """Get execution details by ID."""
    execution = await WorkflowExecution.get_or_none(
        id=execution_id,
        organization_id=org.id
    )

    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    return execution
```

#### File: `backend/app/services/workflow_runner.py` (~200 lines)

```python
"""
Workflow execution service.
"""

import yaml
import traceback
from datetime import datetime
from uuid import UUID

from app.models import WorkflowDefinition, WorkflowExecution

# Mock responses for testing
MOCK_RESPONSES = {
    "llm": {"result": "Mock LLM response"},
    "extract": {"result": "Mock extracted data"},
    "transform": {"result": "Mock transformed data"},
}


async def execute_workflow(
    execution_id: UUID,
    workflow: WorkflowDefinition,
    execution_in
):
    """
    Execute workflow and update execution record.

    Runs in background task.
    """
    execution = await WorkflowExecution.get(id=execution_id)

    try:
        # Update status
        execution.status = "running"
        await execution.save()

        # Execute based on mode
        if execution_in.execution_mode == "mock":
            result = await execute_workflow_mock(workflow, execution_in.input_data)
        else:
            result = await execute_workflow_real(workflow, execution_in.input_data)

        # Calculate duration
        duration_ms = int((datetime.utcnow() - execution.started_at).total_seconds() * 1000)

        # Update execution
        execution.status = "success"
        execution.output_data = result
        execution.completed_at = datetime.utcnow()
        execution.duration_ms = duration_ms
        await execution.save()

    except Exception as e:
        # Log error
        execution.status = "error"
        execution.error_message = str(e)
        execution.completed_at = datetime.utcnow()
        await execution.save()

        print(f"Workflow execution failed: {e}")
        traceback.print_exc()


async def execute_workflow_mock(workflow: WorkflowDefinition, input_data: dict) -> dict:
    """Execute workflow with mock responses (fast)."""
    # Parse YAML
    yaml_data = yaml.safe_load(workflow.yaml_content)
    workflows = yaml_data.get("workflows", {})
    main_workflow = workflows.get("main", workflows.get(list(workflows.keys())[0]))
    steps = main_workflow.get("steps", [])

    # Simulate execution
    shared = input_data.copy()
    step_results = []

    for step in steps:
        step_type = step.get("type")
        result_name = step.get("result")

        # Get mock response
        mock_result = MOCK_RESPONSES.get(step_type, {"result": "Mock result"})

        # Store result
        if result_name:
            shared[result_name] = mock_result

        step_results.append({
            "node": step.get("node"),
            "type": step_type,
            "result": mock_result
        })

    return {
        "mode": "mock",
        "final_result": shared,
        "step_results": step_results
    }


async def execute_workflow_real(workflow: WorkflowDefinition, input_data: dict) -> dict:
    """Execute workflow with real LLM calls (accurate)."""
    # Import KayGraph
    try:
        from kaygraph.declarative import load_domain_from_string, create_graph_from_domain
    except ImportError:
        raise RuntimeError("kaygraph[declarative] not installed")

    # Load domain
    domain = load_domain_from_string(workflow.yaml_content)

    # Create graph
    graph = create_graph_from_domain(domain)

    # Execute
    shared = input_data.copy()
    graph.run(shared)

    return {
        "mode": "real",
        "final_result": shared
    }


def generate_python_endpoint(workflow: WorkflowDefinition) -> str:
    """Generate FastAPI endpoint code for workflow."""
    template = f"""
# Auto-generated endpoint for: {workflow.name}
# Generated: {datetime.utcnow().isoformat()}

from fastapi import APIRouter, Depends
from kaygraph.declarative import load_domain_from_string, create_graph_from_domain
from pydantic import BaseModel

router = APIRouter()

# Workflow YAML
WORKFLOW_YAML = \"\"\"
{workflow.yaml_content}
\"\"\"

@router.post("/api/agents/{workflow.name}")
async def execute_{workflow.name.replace('-', '_')}(request: dict):
    \"\"\"
    {workflow.description or f'Execute {workflow.name} workflow'}
    \"\"\"
    domain = load_domain_from_string(WORKFLOW_YAML)
    graph = create_graph_from_domain(domain)

    shared = request.copy()
    graph.run(shared)

    return shared

# To use this endpoint:
# 1. Add to your FastAPI app: app.include_router(router, tags=["agents"])
# 2. Install KayGraph: pip install kaygraph[declarative]
# 3. Call: POST {workflow.name}
"""
    return template


def generate_claude_docs(workflow: WorkflowDefinition) -> str:
    """Generate Claude Code documentation for workflow."""
    yaml_data = yaml.safe_load(workflow.yaml_content)
    domain = yaml_data.get("domain", {})

    template = f"""
# {workflow.name.replace('_', ' ').replace('-', ' ').title()}

**Workflow**: `{workflow.name}.kg.yaml`
**Version**: {workflow.version}

## Description

{workflow.description or 'No description provided.'}

## When to Use

Use this workflow when the user asks to:
- [Describe typical use cases]

## Installation

```bash
pip install kaygraph[declarative]
```

## Usage

### CLI

```bash
# Download workflow file
curl -O https://your-server/api/v1/workflows/{workflow.id}/export

# Execute
kgraph run {workflow.name}.kg.yaml --input '{{"field": "value"}}'
```

### Python

```python
from kaygraph.declarative import load_domain, create_graph_from_domain

# Load workflow
domain = load_domain("{workflow.name}.kg.yaml")
graph = create_graph_from_domain(domain)

# Execute
result = graph.run({{"field": "value"}})
print(result)
```

## Input Format

[Document expected input structure based on workflow]

## Output Format

[Document output structure based on workflow]

## Examples

[Provide usage examples]

## Troubleshooting

- Ensure kaygraph[declarative] is installed
- Check input format matches expected structure
- Review execution logs for errors
"""
    return template
```

### Pydantic Schemas

File: `backend/app/schemas.py` (add to existing file)

```python
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class WorkflowCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    yaml_content: str = Field(..., min_length=1)
    visual_layout: Optional[Dict[str, Any]] = None


class WorkflowUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    yaml_content: Optional[str] = Field(None, min_length=1)
    visual_layout: Optional[Dict[str, Any]] = None
    is_deployed: Optional[bool] = None


class WorkflowList(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    version: str
    is_deployed: bool
    created_at: datetime
    updated_at: datetime


class WorkflowPublic(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    yaml_content: str
    visual_layout: Optional[Dict[str, Any]]
    version: str
    is_deployed: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime


class ExecutionCreate(BaseModel):
    input_data: Dict[str, Any]
    execution_mode: str = Field(default="real", pattern="^(mock|real)$")


class ExecutionList(BaseModel):
    id: UUID
    workflow_id: UUID
    status: str
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]


class ExecutionPublic(BaseModel):
    id: UUID
    workflow_id: UUID
    input_data: Dict[str, Any]
    output_data: Optional[Dict[str, Any]]
    status: str
    error_message: Optional[str]
    started_at: datetime
    completed_at: Optional[datetime]
    duration_ms: Optional[int]
    execution_mode: str
    step_results: Optional[Dict[str, Any]]
```

### Register Routes

File: `backend/app/api/main.py` (update existing file)

```python
from fastapi import APIRouter
from app.api.routes import login, users, items, workflows, executions

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(workflows.router, prefix="/workflows", tags=["workflows"])  # NEW
api_router.include_router(executions.router, prefix="/workflows", tags=["executions"])  # NEW
```

### CASBIN Permissions

File: `backend/app/casbin/__init__.py` (update existing)

```python
ROLE_PERMISSIONS = {
    "viewer": [
        "workflows.read",
        "executions.read",
    ],
    "member": [
        "workflows.read",
        "workflows.create",
        "workflows.update",
        "executions.read",
        "executions.create",
    ],
    "admin": [
        "workflows.*",
        "executions.*",
    ],
}
```

### Testing for Phase 2

File: `backend/tests/test_workflows.py`

```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_workflow(client: AsyncClient, user_token_headers):
    """Test creating a workflow."""
    response = await client.post(
        "/api/v1/workflows/",
        headers=user_token_headers,
        json={
            "name": "test_workflow",
            "description": "Test workflow",
            "yaml_content": """
domain:
  name: test_workflow
workflows:
  main:
    steps:
      - node: test
        type: llm
        prompt: "test"
"""
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_workflow"

@pytest.mark.asyncio
async def test_execute_workflow(client: AsyncClient, user_token_headers):
    """Test executing a workflow."""
    # Create workflow first
    create_response = await client.post(
        "/api/v1/workflows/",
        headers=user_token_headers,
        json={...}
    )
    workflow_id = create_response.json()["id"]

    # Execute
    exec_response = await client.post(
        f"/api/v1/workflows/{workflow_id}/execute",
        headers=user_token_headers,
        json={
            "input_data": {"test": "data"},
            "execution_mode": "mock"
        }
    )
    assert exec_response.status_code == 200
    data = exec_response.json()
    assert data["status"] in ["pending", "running"]
```

### Phase 2 Checklist

- [ ] Add `WorkflowDefinition` and `WorkflowExecution` models
- [ ] Create Aerich migration
- [ ] Run migration: `aerich upgrade`
- [ ] Create `workflows.py` with CRUD endpoints
- [ ] Create `executions.py` with execution endpoints
- [ ] Create `workflow_runner.py` service
- [ ] Add Pydantic schemas
- [ ] Register routes in `api/main.py`
- [ ] Add CASBIN permissions
- [ ] Write API tests
- [ ] Test with Swagger UI (`/docs`)
- [ ] Test workflow CRUD operations
- [ ] Test workflow execution (mock and real)
- [ ] Test export endpoints

---

## Phase 3: Frontend UI

### Duration: 12-15 hours

### Objective

Build ReactFlow-based visual workflow builder with bidirectional YAML sync.

### Dependencies

```bash
cd frontend
npm install js-yaml @types/js-yaml
npm install @monaco-editor/react
```

### Component Architecture

```
src/components/WorkflowBuilder/
├── WorkflowCanvas.tsx          # Main ReactFlow canvas
├── NodePalette.tsx             # Drag-drop node library
├── NodeEditor.tsx              # Edit node properties (panel)
├── NodeConfigForm.tsx          # Form for node configuration
├── ConceptEditor.tsx           # Define/edit concepts
├── EdgeConfigDialog.tsx        # Configure edge (named actions)
├── WorkflowToolbar.tsx         # Zoom, save, test, export controls
├── TestConsole.tsx             # Execute and view results
├── YAMLEditor.tsx              # Monaco editor for YAML
└── index.ts                    # Exports

src/hooks/
├── useWorkflowBuilder.ts       # Canvas state management
├── useYAMLSync.ts              # Bidirectional sync logic
├── useWorkflowExecution.ts     # Execute workflows
└── useWorkflowAPI.ts           # API calls

src/routes/_layout/workflows/
├── index.tsx                   # List workflows
├── new.tsx                     # Create new workflow
├── $id.tsx                     # Edit workflow (main canvas)
└── $id.execute.tsx             # Test/run workflow

src/types/
└── workflow.ts                 # TypeScript types
```

### File: `frontend/src/types/workflow.ts`

```typescript
// ReactFlow types
export interface WorkflowNode {
  id: string
  type: string  // 'llm', 'transform', 'condition', etc.
  position: { x: number; y: number }
  data: {
    label: string
    icon?: string
    // Node-specific config
    prompt?: string
    field?: string
    mapping?: Record<string, string>
    expression?: string
    result?: string
    inputs?: string[]
    output_concept?: string
    batch_over?: string
    batch_as?: string
    parallels?: any[]
    [key: string]: any
  }
  style?: Record<string, any>
}

export interface WorkflowEdge {
  id: string
  source: string
  target: string
  sourceHandle?: string
  targetHandle?: string
  type?: string
  label?: string
  animated?: boolean
  style?: Record<string, any>
}

export interface WorkflowCanvas {
  nodes: WorkflowNode[]
  edges: WorkflowEdge[]
  viewport?: { x: number; y: number; zoom: number }
}

// API types
export interface WorkflowDefinition {
  id: string
  name: string
  description?: string
  yaml_content: string
  visual_layout?: WorkflowCanvas
  version: string
  is_deployed: boolean
  created_at: string
  updated_at: string
}

export interface WorkflowExecution {
  id: string
  workflow_id: string
  input_data: Record<string, any>
  output_data?: Record<string, any>
  status: 'pending' | 'running' | 'success' | 'error'
  error_message?: string
  started_at: string
  completed_at?: string
  duration_ms?: number
  execution_mode: 'mock' | 'real'
  step_results?: Record<string, any>
}
```

### File: `frontend/src/hooks/useWorkflowBuilder.ts`

```typescript
import { useState, useCallback } from 'react'
import {
  Node,
  Edge,
  addEdge,
  Connection,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
} from '@xyflow/react'
import type { WorkflowNode, WorkflowEdge, WorkflowCanvas } from '@/types/workflow'

export function useWorkflowBuilder(initialCanvas?: WorkflowCanvas) {
  const [nodes, setNodes] = useState<Node[]>(initialCanvas?.nodes || [])
  const [edges, setEdges] = useState<Edge[]>(initialCanvas?.edges || [])

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => {
      setNodes((nds) => applyNodeChanges(changes, nds))
    },
    []
  )

  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => {
      setEdges((eds) => applyEdgeChanges(changes, eds))
    },
    []
  )

  const onConnect = useCallback(
    (connection: Connection) => {
      setEdges((eds) => addEdge(connection, eds))
    },
    []
  )

  const addNode = useCallback((type: string, position: { x: number; y: number }) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type,
      position,
      data: {
        label: type.charAt(0).toUpperCase() + type.slice(1),
      },
    }
    setNodes((nds) => [...nds, newNode])
  }, [])

  const updateNodeData = useCallback((nodeId: string, data: Partial<WorkflowNode['data']>) => {
    setNodes((nds) =>
      nds.map((node) =>
        node.id === nodeId
          ? { ...node, data: { ...node.data, ...data } }
          : node
      )
    )
  }, [])

  const deleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((node) => node.id !== nodeId))
    setEdges((eds) => eds.filter((edge) => edge.source !== nodeId && edge.target !== nodeId))
  }, [])

  const getCanvas = useCallback((): WorkflowCanvas => {
    return {
      nodes: nodes as WorkflowNode[],
      edges: edges as WorkflowEdge[],
    }
  }, [nodes, edges])

  const loadCanvas = useCallback((canvas: WorkflowCanvas) => {
    setNodes(canvas.nodes || [])
    setEdges(canvas.edges || [])
  }, [])

  return {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    updateNodeData,
    deleteNode,
    getCanvas,
    loadCanvas,
  }
}
```

### File: `frontend/src/hooks/useYAMLSync.ts`

```typescript
import { useState, useCallback, useEffect } from 'react'
import yaml from 'js-yaml'
import type { WorkflowCanvas } from '@/types/workflow'

export function useYAMLSync(initialYAML?: string) {
  const [yamlContent, setYAMLContent] = useState(initialYAML || '')
  const [parseError, setParseError] = useState<string | null>(null)

  // YAML → Canvas
  const yamlToCanvas = useCallback((yamlStr: string): WorkflowCanvas | null => {
    try {
      const data = yaml.load(yamlStr) as any

      // Extract canvas layout
      const canvas = data.canvas || {}

      // If no canvas section, generate from workflow steps
      if (!canvas.nodes || canvas.nodes.length === 0) {
        return generateCanvasFromSteps(data)
      }

      return {
        nodes: canvas.nodes || [],
        edges: canvas.edges || [],
        viewport: canvas.viewport || { x: 0, y: 0, zoom: 1.0 },
      }
    } catch (error) {
      setParseError(error.message)
      return null
    }
  }, [])

  // Canvas → YAML
  const canvasToYAML = useCallback((
    canvas: WorkflowCanvas,
    existingYAML?: string
  ): string => {
    try {
      // Parse existing YAML or create new structure
      let data = existingYAML ? yaml.load(existingYAML) : {}

      // Update canvas section
      data.canvas = {
        viewport: canvas.viewport || { x: 0, y: 0, zoom: 1.0 },
        nodes: canvas.nodes.map(node => ({
          id: node.id,
          position: node.position,
          style: node.style,
        })),
        edges: canvas.edges.map(edge => ({
          id: edge.id,
          source: edge.source,
          target: edge.target,
          label: edge.label,
          style: edge.style,
        })),
      }

      // Update workflow steps from canvas
      data.workflows = data.workflows || {}
      data.workflows.main = data.workflows.main || {}
      data.workflows.main.steps = canvasToSteps(canvas)

      // Convert back to YAML
      return yaml.dump(data, {
        indent: 2,
        lineWidth: -1,
        noRefs: true,
      })
    } catch (error) {
      console.error('Error converting canvas to YAML:', error)
      return yamlContent
    }
  }, [yamlContent])

  return {
    yamlContent,
    setYAMLContent,
    parseError,
    yamlToCanvas,
    canvasToYAML,
  }
}

function generateCanvasFromSteps(data: any): WorkflowCanvas {
  const steps = data.workflows?.main?.steps || []
  const nodes = steps.map((step: any, index: number) => ({
    id: step.node,
    type: step.type || 'llm',
    position: { x: 100 + index * 250, y: 200 },
    data: {
      label: step.node.replace(/_/g, ' ').replace(/\b\w/g, (l: string) => l.toUpperCase()),
      ...step,
    },
  }))

  const edges = []
  for (let i = 0; i < nodes.length - 1; i++) {
    edges.push({
      id: `e${i}-${i + 1}`,
      source: nodes[i].id,
      target: nodes[i + 1].id,
      type: 'default',
    })
  }

  return { nodes, edges }
}

function canvasToSteps(canvas: WorkflowCanvas): any[] {
  // Topological sort nodes based on edges
  // For simplicity, preserve node order
  return canvas.nodes.map(node => {
    const step: any = {
      node: node.id,
      type: node.type,
    }

    // Copy relevant fields from node.data
    const { label, icon, ...rest } = node.data
    Object.assign(step, rest)

    return step
  })
}
```

### File: `frontend/src/components/WorkflowBuilder/WorkflowCanvas.tsx`

```typescript
import React, { useCallback } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Panel,
  NodeTypes,
} from '@xyflow/react'
import '@xyflow/react/dist/style.css'
import { useWorkflowBuilder } from '@/hooks/useWorkflowBuilder'
import { Box } from '@chakra-ui/react'
import { LLMNode, TransformNode, ConditionNode } from './nodes'
import { NodePalette } from './NodePalette'
import { NodeEditor } from './NodeEditor'
import { WorkflowToolbar } from './WorkflowToolbar'

const nodeTypes: NodeTypes = {
  llm: LLMNode,
  transform: TransformNode,
  condition: ConditionNode,
  // Add more node types
}

interface WorkflowCanvasProps {
  initialCanvas?: any
  onSave?: (canvas: any) => void
  onTest?: () => void
}

export function WorkflowCanvas({
  initialCanvas,
  onSave,
  onTest,
}: WorkflowCanvasProps) {
  const {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    getCanvas,
  } = useWorkflowBuilder(initialCanvas)

  const [selectedNode, setSelectedNode] = React.useState<string | null>(null)

  const handleNodeClick = useCallback((event: any, node: any) => {
    setSelectedNode(node.id)
  }, [])

  const handlePaneClick = useCallback(() => {
    setSelectedNode(null)
  }, [])

  const handleSave = useCallback(() => {
    const canvas = getCanvas()
    onSave?.(canvas)
  }, [getCanvas, onSave])

  return (
    <Box h="100vh" w="100%" position="relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={handleNodeClick}
        onPaneClick={handlePaneClick}
        nodeTypes={nodeTypes}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />

        <Panel position="top-left">
          <NodePalette onAddNode={addNode} />
        </Panel>

        <Panel position="top-right">
          <WorkflowToolbar
            onSave={handleSave}
            onTest={onTest}
          />
        </Panel>
      </ReactFlow>

      {selectedNode && (
        <NodeEditor
          nodeId={selectedNode}
          onClose={() => setSelectedNode(null)}
        />
      )}
    </Box>
  )
}
```

### File: `frontend/src/components/WorkflowBuilder/NodePalette.tsx`

```typescript
import React from 'react'
import { VStack, Button, Text, Box } from '@chakra-ui/react'

const NODE_TYPES = [
  { type: 'llm', label: 'LLM', icon: '🤖', color: '#48BB78' },
  { type: 'transform', label: 'Transform', icon: '🔄', color: '#ED8936' },
  { type: 'condition', label: 'Condition', icon: '❓', color: '#9F7AEA' },
  { type: 'extract', label: 'Extract', icon: '📥', color: '#4299E1' },
]

interface NodePaletteProps {
  onAddNode: (type: string, position: { x: number; y: number }) => void
}

export function NodePalette({ onAddNode }: NodePaletteProps) {
  const handleAddNode = (type: string) => {
    // Add node at center of viewport
    onAddNode(type, { x: 250, y: 250 })
  }

  return (
    <Box bg="white" p={4} borderRadius="md" shadow="md" w="200px">
      <Text fontWeight="bold" mb={3}>
        Node Palette
      </Text>
      <VStack spacing={2} align="stretch">
        {NODE_TYPES.map(({ type, label, icon, color }) => (
          <Button
            key={type}
            size="sm"
            leftIcon={<span>{icon}</span>}
            onClick={() => handleAddNode(type)}
            colorScheme="gray"
            variant="outline"
            justifyContent="flex-start"
          >
            {label}
          </Button>
        ))}
      </VStack>
    </Box>
  )
}
```

### File: `frontend/src/routes/_layout/workflows/$id.tsx`

```typescript
import { createFileRoute } from '@tanstack/react-router'
import { useState, useEffect } from 'react'
import { Box, HStack, VStack, Button, useToast } from '@chakra-ui/react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { WorkflowCanvas } from '@/components/WorkflowBuilder/WorkflowCanvas'
import { YAMLEditor } from '@/components/WorkflowBuilder/YAMLEditor'
import { useYAMLSync } from '@/hooks/useYAMLSync'
import { WorkflowsService } from '@/client'

export const Route = createFileRoute('/_layout/workflows/$id')({
  component: WorkflowEditor,
})

function WorkflowEditor() {
  const { id } = Route.useParams()
  const [viewMode, setViewMode] = useState<'visual' | 'yaml'>('visual')
  const toast = useToast()
  const queryClient = useQueryClient()

  // Fetch workflow
  const { data: workflow, isLoading } = useQuery({
    queryKey: ['workflow', id],
    queryFn: () => WorkflowsService.getWorkflow({ workflowId: id }),
  })

  // YAML sync
  const { yamlContent, setYAMLContent, yamlToCanvas, canvasToYAML } = useYAMLSync(
    workflow?.yaml_content
  )

  const [canvas, setCanvas] = useState(null)

  // Load canvas when workflow loads
  useEffect(() => {
    if (workflow?.visual_layout) {
      setCanvas(workflow.visual_layout)
    } else if (workflow?.yaml_content) {
      const generated = yamlToCanvas(workflow.yaml_content)
      setCanvas(generated)
    }
  }, [workflow, yamlToCanvas])

  // Save mutation
  const saveMutation = useMutation({
    mutationFn: (data: any) =>
      WorkflowsService.updateWorkflow({
        workflowId: id,
        requestBody: data,
      }),
    onSuccess: () => {
      toast({ title: 'Workflow saved', status: 'success' })
      queryClient.invalidateQueries({ queryKey: ['workflow', id] })
    },
    onError: (error) => {
      toast({ title: 'Save failed', description: error.message, status: 'error' })
    },
  })

  const handleSave = (updatedCanvas: any) => {
    const yaml = canvasToYAML(updatedCanvas, workflow?.yaml_content)

    saveMutation.mutate({
      yaml_content: yaml,
      visual_layout: updatedCanvas,
    })
  }

  const handleYAMLChange = (yaml: string) => {
    setYAMLContent(yaml)
    const updatedCanvas = yamlToCanvas(yaml)
    if (updatedCanvas) {
      setCanvas(updatedCanvas)
    }
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <Box h="100vh" display="flex" flexDirection="column">
      {/* Toggle buttons */}
      <HStack p={4} bg="gray.50" borderBottom="1px solid" borderColor="gray.200">
        <Button
          size="sm"
          variant={viewMode === 'visual' ? 'solid' : 'outline'}
          onClick={() => setViewMode('visual')}
        >
          Visual
        </Button>
        <Button
          size="sm"
          variant={viewMode === 'yaml' ? 'solid' : 'outline'}
          onClick={() => setViewMode('yaml')}
        >
          YAML
        </Button>
      </HStack>

      {/* Content */}
      <Box flex={1}>
        {viewMode === 'visual' ? (
          <WorkflowCanvas
            initialCanvas={canvas}
            onSave={handleSave}
          />
        ) : (
          <YAMLEditor
            value={yamlContent}
            onChange={handleYAMLChange}
          />
        )}
      </Box>
    </Box>
  )
}
```

### File: `frontend/src/components/WorkflowBuilder/NodeEditor.tsx`

```typescript
import React, { useState } from 'react'
import {
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  VStack,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Button,
  Select,
} from '@chakra-ui/react'
import { useWorkflowBuilder } from '@/hooks/useWorkflowBuilder'

interface NodeEditorProps {
  nodeId: string
  onClose: () => void
}

export function NodeEditor({ nodeId, onClose }: NodeEditorProps) {
  const { getNode, updateNode } = useWorkflowBuilder()
  const node = getNode(nodeId)

  const [formData, setFormData] = useState({
    label: node?.data?.label || '',
    type: node?.type || 'llm',
    config: node?.data?.config || {},
  })

  const handleSave = () => {
    updateNode(nodeId, {
      data: {
        label: formData.label,
        config: formData.config,
      },
    })
    onClose()
  }

  return (
    <Drawer isOpen placement="right" onClose={onClose} size="md">
      <DrawerOverlay />
      <DrawerContent>
        <DrawerCloseButton />
        <DrawerHeader>Edit Node: {formData.label}</DrawerHeader>

        <DrawerBody>
          <VStack spacing={4} align="stretch">
            {/* Basic Info */}
            <FormControl>
              <FormLabel>Label</FormLabel>
              <Input
                value={formData.label}
                onChange={(e) => setFormData({ ...formData, label: e.target.value })}
              />
            </FormControl>

            <FormControl>
              <FormLabel>Node Type</FormLabel>
              <Select
                value={formData.type}
                onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              >
                <option value="llm">LLM Call</option>
                <option value="transform">Transform</option>
                <option value="condition">Condition</option>
                <option value="extract">Extract</option>
              </Select>
            </FormControl>

            {/* Type-specific Configuration */}
            {formData.type === 'llm' && (
              <>
                <FormControl>
                  <FormLabel>Prompt Template</FormLabel>
                  <Textarea
                    value={formData.config.prompt || ''}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        config: { ...formData.config, prompt: e.target.value },
                      })
                    }
                    rows={6}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Model</FormLabel>
                  <Select
                    value={formData.config.model || 'gpt-4'}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        config: { ...formData.config, model: e.target.value },
                      })
                    }
                  >
                    <option value="gpt-4">GPT-4</option>
                    <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                    <option value="claude-3-opus">Claude 3 Opus</option>
                  </Select>
                </FormControl>
              </>
            )}

            {formData.type === 'condition' && (
              <FormControl>
                <FormLabel>Condition Expression</FormLabel>
                <Input
                  value={formData.config.expression || ''}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      config: { ...formData.config, expression: e.target.value },
                    })
                  }
                  placeholder="e.g., result.score > 0.8"
                />
              </FormControl>
            )}

            <Button colorScheme="blue" onClick={handleSave}>
              Save Changes
            </Button>
          </VStack>
        </DrawerBody>
      </DrawerContent>
    </Drawer>
  )
}
```

### File: `frontend/src/components/WorkflowBuilder/TestConsole.tsx`

```typescript
import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Button,
  Textarea,
  Text,
  Spinner,
  Badge,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react'
import { useMutation } from '@tanstack/react-query'
import { WorkflowsService } from '@/client'

interface TestConsoleProps {
  workflowId: string
}

export function TestConsole({ workflowId }: TestConsoleProps) {
  const [inputJSON, setInputJSON] = useState('{\n  "query": "Sample input"\n}')
  const [executionMode, setExecutionMode] = useState<'mock' | 'real'>('mock')
  const [result, setResult] = useState<any>(null)

  const executeMutation = useMutation({
    mutationFn: (data: { input: any; mode: 'mock' | 'real' }) =>
      WorkflowsService.executeWorkflow({
        workflowId,
        requestBody: {
          input_data: data.input,
          execution_mode: data.mode,
        },
      }),
    onSuccess: (data) => {
      setResult(data)
    },
  })

  const handleExecute = () => {
    try {
      const input = JSON.parse(inputJSON)
      executeMutation.mutate({ input, mode: executionMode })
    } catch (error) {
      setResult({ error: 'Invalid JSON input' })
    }
  }

  return (
    <Box h="100%" display="flex" flexDirection="column">
      <HStack p={4} bg="gray.50" borderBottom="1px solid" borderColor="gray.200">
        <Text fontWeight="bold">Test Console</Text>
        <Select
          size="sm"
          w="150px"
          value={executionMode}
          onChange={(e) => setExecutionMode(e.target.value as 'mock' | 'real')}
        >
          <option value="mock">Mock Mode (Fast)</option>
          <option value="real">Real Mode (Accurate)</option>
        </Select>
        <Button
          size="sm"
          colorScheme="green"
          onClick={handleExecute}
          isLoading={executeMutation.isPending}
        >
          Execute
        </Button>
      </HStack>

      <Box flex={1} p={4} overflowY="auto">
        <Tabs>
          <TabList>
            <Tab>Input</Tab>
            <Tab>Output</Tab>
          </TabList>

          <TabPanels>
            <TabPanel>
              <Textarea
                value={inputJSON}
                onChange={(e) => setInputJSON(e.target.value)}
                fontFamily="mono"
                fontSize="sm"
                rows={15}
                placeholder="Enter JSON input..."
              />
            </TabPanel>

            <TabPanel>
              {executeMutation.isPending && (
                <HStack>
                  <Spinner size="sm" />
                  <Text>Executing workflow...</Text>
                </HStack>
              )}

              {result && (
                <VStack align="stretch" spacing={3}>
                  <HStack>
                    <Badge colorScheme={result.status === 'success' ? 'green' : 'red'}>
                      {result.status}
                    </Badge>
                    {result.execution_time && (
                      <Text fontSize="sm" color="gray.600">
                        {result.execution_time}ms
                      </Text>
                    )}
                  </HStack>

                  <Box
                    bg="gray.50"
                    p={4}
                    borderRadius="md"
                    fontFamily="mono"
                    fontSize="sm"
                    whiteSpace="pre-wrap"
                  >
                    {JSON.stringify(result.output_data || result.error, null, 2)}
                  </Box>

                  {result.trace && (
                    <Box>
                      <Text fontWeight="bold" mb={2}>
                        Execution Trace:
                      </Text>
                      {result.trace.map((step: any, idx: number) => (
                        <Text key={idx} fontSize="sm" fontFamily="mono">
                          {idx + 1}. {step.node} ({step.duration}ms)
                        </Text>
                      ))}
                    </Box>
                  )}
                </VStack>
              )}
            </TabPanel>
          </TabPanels>
        </Tabs>
      </Box>
    </Box>
  )
}
```

### File: `frontend/src/components/WorkflowBuilder/YAMLEditor.tsx`

```typescript
import React, { useRef, useEffect } from 'react'
import { Box } from '@chakra-ui/react'
import Editor from '@monaco-editor/react'

interface YAMLEditorProps {
  value: string
  onChange: (value: string) => void
  readOnly?: boolean
}

export function YAMLEditor({ value, onChange, readOnly = false }: YAMLEditorProps) {
  const editorRef = useRef<any>(null)

  const handleEditorDidMount = (editor: any) => {
    editorRef.current = editor
  }

  const handleEditorChange = (value: string | undefined) => {
    if (value !== undefined && !readOnly) {
      onChange(value)
    }
  }

  return (
    <Box h="100%" w="100%">
      <Editor
        height="100%"
        defaultLanguage="yaml"
        value={value}
        onChange={handleEditorChange}
        onMount={handleEditorDidMount}
        options={{
          readOnly,
          minimap: { enabled: false },
          fontSize: 14,
          tabSize: 2,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          wordWrap: 'on',
        }}
        theme="vs-light"
      />
    </Box>
  )
}
```

### File: `frontend/src/hooks/useWorkflowBuilder.ts`

```typescript
import { useState, useCallback } from 'react'
import { Node, Edge, addEdge, applyNodeChanges, applyEdgeChanges } from '@xyflow/react'
import type { NodeChange, EdgeChange, Connection } from '@xyflow/react'

export interface WorkflowCanvas {
  nodes: Node[]
  edges: Edge[]
  viewport?: { x: number; y: number; zoom: number }
}

export function useWorkflowBuilder(initialCanvas?: WorkflowCanvas) {
  const [nodes, setNodes] = useState<Node[]>(initialCanvas?.nodes || [])
  const [edges, setEdges] = useState<Edge[]>(initialCanvas?.edges || [])

  const onNodesChange = useCallback((changes: NodeChange[]) => {
    setNodes((nds) => applyNodeChanges(changes, nds))
  }, [])

  const onEdgesChange = useCallback((changes: EdgeChange[]) => {
    setEdges((eds) => applyEdgeChanges(changes, eds))
  }, [])

  const onConnect = useCallback((connection: Connection) => {
    setEdges((eds) => addEdge(connection, eds))
  }, [])

  const addNode = useCallback((type: string, position: { x: number; y: number }) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type,
      position,
      data: {
        label: type.charAt(0).toUpperCase() + type.slice(1),
        config: {},
      },
    }
    setNodes((nds) => [...nds, newNode])
  }, [])

  const getNode = useCallback(
    (nodeId: string) => {
      return nodes.find((n) => n.id === nodeId)
    },
    [nodes]
  )

  const updateNode = useCallback((nodeId: string, updates: Partial<Node>) => {
    setNodes((nds) =>
      nds.map((n) => (n.id === nodeId ? { ...n, ...updates } : n))
    )
  }, [])

  const deleteNode = useCallback((nodeId: string) => {
    setNodes((nds) => nds.filter((n) => n.id !== nodeId))
    setEdges((eds) => eds.filter((e) => e.source !== nodeId && e.target !== nodeId))
  }, [])

  const getCanvas = useCallback((): WorkflowCanvas => {
    return { nodes, edges }
  }, [nodes, edges])

  const loadCanvas = useCallback((canvas: WorkflowCanvas) => {
    setNodes(canvas.nodes || [])
    setEdges(canvas.edges || [])
  }, [])

  return {
    nodes,
    edges,
    onNodesChange,
    onEdgesChange,
    onConnect,
    addNode,
    getNode,
    updateNode,
    deleteNode,
    getCanvas,
    loadCanvas,
  }
}
```

### File: `frontend/src/hooks/useYAMLSync.ts`

```typescript
import { useState, useCallback } from 'react'
import yaml from 'js-yaml'
import type { WorkflowCanvas } from './useWorkflowBuilder'

export function useYAMLSync(initialYAML?: string) {
  const [yamlContent, setYAMLContent] = useState(initialYAML || '')

  /**
   * Convert YAML string to ReactFlow canvas
   */
  const yamlToCanvas = useCallback((yamlStr: string): WorkflowCanvas | null => {
    try {
      const data = yaml.load(yamlStr) as any

      // If canvas section exists, use it directly
      if (data.canvas && data.canvas.nodes) {
        return {
          nodes: data.canvas.nodes,
          edges: data.canvas.edges || [],
          viewport: data.canvas.viewport,
        }
      }

      // Otherwise, generate canvas from workflow steps
      return generateCanvasFromSteps(data)
    } catch (error) {
      console.error('Failed to parse YAML:', error)
      return null
    }
  }, [])

  /**
   * Convert ReactFlow canvas to YAML string
   */
  const canvasToYAML = useCallback(
    (canvas: WorkflowCanvas, existingYAML?: string): string => {
      try {
        let data: any = existingYAML ? yaml.load(existingYAML) : {}

        // Update canvas section
        data.canvas = {
          viewport: canvas.viewport || { x: 0, y: 0, zoom: 1 },
          nodes: canvas.nodes,
          edges: canvas.edges,
        }

        // Update workflow steps from canvas
        if (!data.workflows) {
          data.workflows = { main: { steps: [] } }
        }
        data.workflows.main.steps = canvasToSteps(canvas)

        return yaml.dump(data, { indent: 2, lineWidth: -1 })
      } catch (error) {
        console.error('Failed to generate YAML:', error)
        return ''
      }
    },
    []
  )

  return {
    yamlContent,
    setYAMLContent,
    yamlToCanvas,
    canvasToYAML,
  }
}

/**
 * Generate ReactFlow canvas from workflow steps
 */
function generateCanvasFromSteps(data: any): WorkflowCanvas {
  const nodes: any[] = []
  const edges: any[] = []

  const steps = data.workflows?.main?.steps || []
  const ySpacing = 120
  const xOffset = 250

  steps.forEach((step: any, idx: number) => {
    const nodeId = `node-${idx}`
    nodes.push({
      id: nodeId,
      type: step.type || 'default',
      position: { x: xOffset, y: idx * ySpacing },
      data: {
        label: step.name || `Step ${idx + 1}`,
        config: step.config || {},
      },
    })

    // Connect to previous node
    if (idx > 0) {
      edges.push({
        id: `edge-${idx - 1}-${idx}`,
        source: `node-${idx - 1}`,
        target: nodeId,
        label: step.when || undefined,
      })
    }
  })

  return { nodes, edges }
}

/**
 * Convert ReactFlow canvas to workflow steps
 */
function canvasToSteps(canvas: WorkflowCanvas): any[] {
  const steps: any[] = []

  // Sort nodes by Y position to maintain order
  const sortedNodes = [...canvas.nodes].sort((a, b) => a.position.y - b.position.y)

  sortedNodes.forEach((node) => {
    const step: any = {
      name: node.data.label,
      type: node.type,
      config: node.data.config || {},
    }

    // Find incoming edge to determine action/condition
    const incomingEdge = canvas.edges.find((e) => e.target === node.id)
    if (incomingEdge?.label) {
      step.when = incomingEdge.label
    }

    steps.push(step)
  })

  return steps
}
```

### File: `frontend/src/routes/_layout/workflows/new.tsx`

```typescript
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useState } from 'react'
import {
  Box,
  VStack,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Button,
  useToast,
} from '@chakra-ui/react'
import { useMutation } from '@tanstack/react-query'
import { WorkflowsService } from '@/client'

export const Route = createFileRoute('/_layout/workflows/new')({
  component: NewWorkflow,
})

function NewWorkflow() {
  const navigate = useNavigate()
  const toast = useToast()

  const [formData, setFormData] = useState({
    name: '',
    description: '',
  })

  const createMutation = useMutation({
    mutationFn: (data: any) =>
      WorkflowsService.createWorkflow({
        requestBody: data,
      }),
    onSuccess: (workflow) => {
      toast({ title: 'Workflow created', status: 'success' })
      navigate({ to: `/workflows/${workflow.id}` })
    },
    onError: (error) => {
      toast({
        title: 'Creation failed',
        description: error.message,
        status: 'error',
      })
    },
  })

  const handleCreate = () => {
    // Generate minimal YAML template
    const yamlTemplate = `
metadata:
  title: "${formData.name}"
  description: "${formData.description}"
  version: "1.0.0"

domain:
  name: "${formData.name.toLowerCase().replace(/\s+/g, '_')}"
  version: "1.0.0"

workflows:
  main:
    steps: []
`.trim()

    createMutation.mutate({
      name: formData.name,
      description: formData.description,
      yaml_content: yamlTemplate,
    })
  }

  return (
    <Box maxW="600px" mx="auto" mt={8}>
      <VStack spacing={4} align="stretch">
        <FormControl isRequired>
          <FormLabel>Workflow Name</FormLabel>
          <Input
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="My Workflow"
          />
        </FormControl>

        <FormControl>
          <FormLabel>Description</FormLabel>
          <Textarea
            value={formData.description}
            onChange={(e) =>
              setFormData({ ...formData, description: e.target.value })
            }
            placeholder="What does this workflow do?"
            rows={4}
          />
        </FormControl>

        <Button
          colorScheme="blue"
          onClick={handleCreate}
          isLoading={createMutation.isPending}
          isDisabled={!formData.name}
        >
          Create Workflow
        </Button>
      </VStack>
    </Box>
  )
}
```

**Phase 3 Summary**: All UI components, hooks, and routes complete. Ready for integration testing.

---

## Phase 4: Integration & Testing

**Duration**: 6-8 hours

### 4.1 End-to-End Integration

#### Task 1: Complete Workflow Lifecycle Test

**Objective**: Test the complete flow from creation to deployment

**Steps**:

1. **Create via UI**:
   - Navigate to `/workflows/new`
   - Create "Invoice Processor" workflow
   - Verify YAML template generated

2. **Build Visually**:
   - Add LLM node with invoice extraction prompt
   - Add condition node (amount > $1000)
   - Add two transform nodes (approve/reject paths)
   - Connect with edges
   - Save and verify DB persistence

3. **Edit YAML**:
   - Switch to YAML view
   - Add concept definition manually
   - Add metadata for API deployment
   - Save and verify visual updates

4. **Test Execution**:
   - Open test console
   - Run in mock mode (should return immediately)
   - Run in real mode (should execute LLM call)
   - Verify output in both modes

5. **Export**:
   - Export as `.kg.yaml` file
   - Verify file contains all sections
   - Run via CLI: `kgraph run invoice_processor.kg.yaml --input test.json`
   - Verify identical output

6. **Deploy as API**:
   - Mark workflow as deployed
   - Test endpoint: `POST /api/agents/invoice_processor`
   - Verify authentication required
   - Verify rate limiting works

**Expected Outcome**: All 6 steps complete without errors

#### Task 2: Multi-User Isolation Test

**Objective**: Verify organization-based isolation

**Steps**:

1. Create two test organizations
2. User A creates "Workflow A" in Org 1
3. User B (in Org 2) attempts to access Workflow A
4. Verify 403 Forbidden error
5. Verify User B can create "Workflow A" in Org 2 (same name, different org)

**Expected Outcome**: Complete isolation between organizations

#### Task 3: Bidirectional Sync Test

**Objective**: Ensure visual ↔ YAML sync is lossless

**Test Cases**:

```typescript
// Test 1: Visual → YAML → Visual
const originalCanvas = {
  nodes: [
    { id: 'n1', type: 'llm', position: { x: 100, y: 100 }, data: { ... } },
    { id: 'n2', type: 'transform', position: { x: 100, y: 220 }, data: { ... } },
  ],
  edges: [{ id: 'e1', source: 'n1', target: 'n2' }],
}

const yaml = canvasToYAML(originalCanvas)
const regeneratedCanvas = yamlToCanvas(yaml)

expect(regeneratedCanvas).toEqual(originalCanvas)

// Test 2: YAML → Visual → YAML
const originalYAML = `
workflows:
  main:
    steps:
      - name: extract
        type: llm
        config:
          prompt: "Extract invoice data"
      - name: validate
        type: transform
`

const canvas = yamlToCanvas(originalYAML)
const regeneratedYAML = canvasToYAML(canvas, originalYAML)

expect(regeneratedYAML).toContain('extract')
expect(regeneratedYAML).toContain('validate')
```

**Expected Outcome**: No data loss in conversions

### 4.2 Performance Testing

#### Task 1: Large Workflow Handling

**Test**: Create workflow with 100 nodes
**Metric**: UI should remain responsive
**Target**: < 100ms render time for node operations

#### Task 2: Concurrent Execution

**Test**: Execute 10 workflows simultaneously
**Metric**: All should complete without blocking
**Target**: < 2x slowdown compared to sequential

#### Task 3: YAML Parsing Performance

**Test**: Parse 1MB YAML file (large workflow)
**Metric**: Parse time
**Target**: < 500ms

### 4.3 Error Handling Tests

#### Test Cases:

1. **Invalid YAML Syntax**:
   - User enters malformed YAML
   - System shows clear error message
   - Does not corrupt visual representation

2. **Missing Required Fields**:
   - Create workflow without `domain.name`
   - Validation error shown before save
   - Suggests fix

3. **Circular Dependencies**:
   - User creates loop: A → B → C → A
   - Detection during save
   - Warning shown with visualization

4. **LLM API Failure**:
   - Mock API returns 500 error
   - Workflow execution shows error
   - Retry mechanism works

5. **Database Connection Loss**:
   - Simulate DB disconnect during save
   - User sees error toast
   - Unsaved changes preserved in browser

### 4.4 Security Testing

#### Test Cases:

1. **YAML Injection**:
   - Attempt to inject malicious YAML
   - Parser rejects dangerous constructs

2. **XSS in Node Labels**:
   - Create node with `<script>alert('xss')</script>` label
   - Verify proper sanitization

3. **Unauthorized Access**:
   - Attempt to access workflow from different org
   - Verify 403 response

4. **Rate Limiting**:
   - Execute workflow 100 times rapidly
   - Verify rate limit kicks in

---

## Implementation Checklist

### Phase 1: Core Package ✅

- [ ] Create `kaygraph/declarative/serializer.py`
  - [ ] Implement `WorkflowSerializer.domain_to_dict()`
  - [ ] Implement `WorkflowSerializer.domain_to_yaml()`
  - [ ] Implement `WorkflowSerializer.graph_to_dict()`
  - [ ] Handle all 8 node types correctly
  - [ ] Preserve concept definitions
  - [ ] Include visual layout in output

- [ ] Create `kaygraph/declarative/visual_converter.py`
  - [ ] Implement `VisualConverter.yaml_to_reactflow()`
  - [ ] Implement `VisualConverter.reactflow_to_yaml()`
  - [ ] Generate auto-layout when no canvas data
  - [ ] Preserve node positions and viewport

- [ ] Update `kaygraph/declarative/domain.py`
  - [ ] Add `Domain.to_dict()` method
  - [ ] Add `Domain.to_yaml()` method
  - [ ] Add `Domain.to_file(path)` method

- [ ] Update `kaygraph/declarative/cli.py`
  - [ ] Add `kgraph export <workflow> --format=yaml` command
  - [ ] Add `kgraph validate <workflow.kg.yaml>` command
  - [ ] Add `kgraph convert <workflow.kg.yaml> --to=json` command

- [ ] Update `kaygraph/setup.py`
  - [ ] Add PyYAML dependency
  - [ ] Update version to 0.1.0
  - [ ] Add declarative extras

- [ ] Write tests
  - [ ] `tests/test_serializer.py` (8 tests)
  - [ ] `tests/test_visual_converter.py` (6 tests)
  - [ ] `tests/test_domain_export.py` (4 tests)

### Phase 2: Backend API ✅

- [ ] Database Models (`backend/app/models/workflow.py`)
  - [ ] Create `WorkflowDefinition` model
  - [ ] Create `WorkflowExecution` model
  - [ ] Add indexes for performance
  - [ ] Add foreign key constraints

- [ ] Migrations
  - [ ] Generate Aerich migration
  - [ ] Test migration up/down
  - [ ] Add sample data migration

- [ ] API Schemas (`backend/app/schemas/workflow.py`)
  - [ ] Create `WorkflowCreate` schema
  - [ ] Create `WorkflowUpdate` schema
  - [ ] Create `WorkflowPublic` schema
  - [ ] Create `ExecutionCreate` schema
  - [ ] Create `ExecutionPublic` schema

- [ ] API Endpoints (`backend/app/api/routes/workflows.py`)
  - [ ] POST `/api/v1/workflows/` (create)
  - [ ] GET `/api/v1/workflows/` (list with pagination)
  - [ ] GET `/api/v1/workflows/{id}` (get single)
  - [ ] PUT `/api/v1/workflows/{id}` (update)
  - [ ] DELETE `/api/v1/workflows/{id}` (delete)
  - [ ] POST `/api/v1/workflows/{id}/execute` (execute)
  - [ ] GET `/api/v1/workflows/{id}/executions` (list executions)
  - [ ] GET `/api/v1/workflows/{id}/export` (export YAML)

- [ ] Workflow Runner (`backend/app/services/workflow_runner.py`)
  - [ ] Implement mock execution mode
  - [ ] Implement real execution mode
  - [ ] Add execution tracing
  - [ ] Handle errors gracefully

- [ ] RBAC Integration
  - [ ] Add CASBIN policy for workflows
  - [ ] Require org membership for access
  - [ ] Add permission checks to all endpoints

- [ ] Tests
  - [ ] Test CRUD operations
  - [ ] Test execution modes
  - [ ] Test multi-tenancy isolation
  - [ ] Test export functionality

### Phase 3: Frontend UI ✅

- [ ] Install Dependencies
  - [ ] `npm install js-yaml`
  - [ ] `npm install @monaco-editor/react`
  - [ ] Verify `@xyflow/react` already installed

- [ ] Create Components
  - [ ] `WorkflowCanvas.tsx` (main visual editor)
  - [ ] `NodePalette.tsx` (drag-drop library)
  - [ ] `NodeEditor.tsx` (node configuration drawer)
  - [ ] `TestConsole.tsx` (execution testing)
  - [ ] `YAMLEditor.tsx` (Monaco integration)

- [ ] Create Hooks
  - [ ] `useWorkflowBuilder.ts` (ReactFlow state management)
  - [ ] `useYAMLSync.ts` (bidirectional conversion)

- [ ] Create Routes
  - [ ] `/workflows` (list all workflows)
  - [ ] `/workflows/new` (create new workflow)
  - [ ] `/workflows/:id` (edit workflow with visual/YAML toggle)

- [ ] Custom Node Components
  - [ ] `LLMNode.tsx` (styled for LLM calls)
  - [ ] `ConditionNode.tsx` (diamond shape for branching)
  - [ ] `TransformNode.tsx` (data transformation)
  - [ ] `ExtractNode.tsx` (data extraction)

- [ ] Integration
  - [ ] Connect to backend API
  - [ ] Add loading states
  - [ ] Add error handling
  - [ ] Add optimistic updates

- [ ] Tests
  - [ ] Component unit tests
  - [ ] Hook tests
  - [ ] Integration tests with MSW

### Phase 4: Integration & Testing ✅

- [ ] End-to-End Tests
  - [ ] Complete workflow lifecycle
  - [ ] Multi-user isolation
  - [ ] Bidirectional sync validation

- [ ] Performance Tests
  - [ ] Large workflow handling (100+ nodes)
  - [ ] Concurrent execution
  - [ ] YAML parsing performance

- [ ] Error Handling Tests
  - [ ] Invalid YAML syntax
  - [ ] Missing required fields
  - [ ] Circular dependencies
  - [ ] API failures
  - [ ] Database errors

- [ ] Security Tests
  - [ ] YAML injection prevention
  - [ ] XSS prevention
  - [ ] Unauthorized access
  - [ ] Rate limiting

- [ ] Documentation
  - [ ] User guide for visual builder
  - [ ] API documentation
  - [ ] Example workflows
  - [ ] Video tutorials

---

## Testing Strategy

### Unit Tests

**Location**: `kaygraph/tests/` and `frontend/src/components/__tests__/`

**Coverage Target**: 80%

**Key Test Files**:

```python
# kaygraph/tests/test_serializer.py
def test_domain_to_dict():
    """Test Domain object serialization to dictionary"""
    domain = Domain(name="test", version="1.0.0")
    domain.add_concept("User", {...})

    serializer = WorkflowSerializer()
    result = serializer.domain_to_dict(domain)

    assert result["domain"]["name"] == "test"
    assert "User" in result["concepts"]

def test_domain_to_yaml():
    """Test Domain object serialization to YAML string"""
    domain = Domain(name="test", version="1.0.0")

    serializer = WorkflowSerializer()
    yaml_str = serializer.domain_to_yaml(domain)

    assert "domain:" in yaml_str
    assert "name: test" in yaml_str

def test_graph_to_dict():
    """Test Graph serialization including all node types"""
    graph = Graph(LLMNode())
    # ... add nodes and connections

    serializer = WorkflowSerializer()
    result = serializer.graph_to_dict(graph)

    assert "steps" in result
    assert len(result["steps"]) > 0
```

```typescript
// frontend/src/hooks/__tests__/useYAMLSync.test.ts
import { renderHook, act } from '@testing-library/react'
import { useYAMLSync } from '../useYAMLSync'

describe('useYAMLSync', () => {
  it('should convert YAML to canvas', () => {
    const { result } = renderHook(() => useYAMLSync())

    const yaml = `
workflows:
  main:
    steps:
      - name: extract
        type: llm
    `

    const canvas = result.current.yamlToCanvas(yaml)

    expect(canvas).not.toBeNull()
    expect(canvas.nodes).toHaveLength(1)
    expect(canvas.nodes[0].data.label).toBe('extract')
  })

  it('should convert canvas to YAML', () => {
    const { result } = renderHook(() => useYAMLSync())

    const canvas = {
      nodes: [{ id: 'n1', type: 'llm', position: { x: 0, y: 0 }, data: { label: 'Test' } }],
      edges: [],
    }

    const yaml = result.current.canvasToYAML(canvas)

    expect(yaml).toContain('workflows:')
    expect(yaml).toContain('Test')
  })
})
```

### Integration Tests

**Location**: `backend/tests/test_integration/`

**Key Scenarios**:

```python
# backend/tests/test_integration/test_workflow_lifecycle.py
async def test_complete_workflow_lifecycle(async_client, test_user):
    """Test full workflow: create → edit → execute → export"""

    # 1. Create workflow
    response = await async_client.post(
        "/api/v1/workflows/",
        json={
            "name": "Test Workflow",
            "description": "Integration test",
            "yaml_content": MINIMAL_YAML_TEMPLATE,
        },
        headers={"Authorization": f"Bearer {test_user.token}"},
    )
    assert response.status_code == 201
    workflow_id = response.json()["id"]

    # 2. Update workflow (add nodes visually)
    updated_yaml = YAML_WITH_NODES
    response = await async_client.put(
        f"/api/v1/workflows/{workflow_id}",
        json={"yaml_content": updated_yaml},
        headers={"Authorization": f"Bearer {test_user.token}"},
    )
    assert response.status_code == 200

    # 3. Execute workflow
    response = await async_client.post(
        f"/api/v1/workflows/{workflow_id}/execute",
        json={
            "input_data": {"query": "test input"},
            "execution_mode": "mock",
        },
        headers={"Authorization": f"Bearer {test_user.token}"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # 4. Export workflow
    response = await async_client.get(
        f"/api/v1/workflows/{workflow_id}/export",
        headers={"Authorization": f"Bearer {test_user.token}"},
    )
    assert response.status_code == 200
    assert "workflows:" in response.text
```

### End-to-End Tests

**Location**: `frontend/e2e/`

**Tool**: Playwright

**Key Scenarios**:

```typescript
// frontend/e2e/workflow-builder.spec.ts
import { test, expect } from '@playwright/test'

test('create and test workflow visually', async ({ page }) => {
  // 1. Navigate to workflows page
  await page.goto('/workflows/new')

  // 2. Create new workflow
  await page.fill('input[name="name"]', 'E2E Test Workflow')
  await page.click('button:has-text("Create")')

  // 3. Add LLM node from palette
  await page.click('button:has-text("LLM")')
  await expect(page.locator('.react-flow__node')).toHaveCount(1)

  // 4. Configure node
  await page.click('.react-flow__node')
  await page.fill('textarea[name="prompt"]', 'Extract invoice data')
  await page.click('button:has-text("Save")')

  // 5. Switch to YAML view
  await page.click('button:has-text("YAML")')
  await expect(page.locator('.monaco-editor')).toBeVisible()

  // 6. Verify YAML contains node
  const yamlContent = await page.locator('.monaco-editor').textContent()
  expect(yamlContent).toContain('Extract invoice data')

  // 7. Test execution
  await page.click('button:has-text("Test Console")')
  await page.fill('textarea[name="input"]', '{"invoice": "test"}')
  await page.click('button:has-text("Execute")')

  // 8. Verify output
  await expect(page.locator('text=success')).toBeVisible()
})
```

### Example Workflows for Testing

**1. Simple Linear Workflow**:
```yaml
workflows:
  main:
    steps:
      - name: extract
        type: llm
        config:
          prompt: "Extract data from: {input}"
      - name: validate
        type: transform
        config:
          operation: "validate_schema"
```

**2. Conditional Branching Workflow**:
```yaml
workflows:
  main:
    steps:
      - name: analyze
        type: llm
        outputs: [decision]
      - name: high_priority
        when: "decision.priority == 'high'"
        type: transform
      - name: low_priority
        when: "decision.priority == 'low'"
        type: transform
```

**3. Batch Processing Workflow**:
```yaml
workflows:
  main:
    batch_over: "items"
    batch_as: "item"
    steps:
      - name: process_item
        type: llm
        config:
          prompt: "Process: {item}"
```

**4. Parallel Operations Workflow**:
```yaml
workflows:
  main:
    steps:
      - name: parallel_analysis
        type: parallel
        operations:
          - name: sentiment
            type: llm
          - name: entities
            type: llm
          - name: summary
            type: llm
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests passing (unit, integration, E2E)
- [ ] Code review completed
- [ ] Documentation updated
- [ ] Version bumped in `kaygraph/__init__.py`
- [ ] Migration scripts tested
- [ ] Performance benchmarks met

### Core Package Deployment

- [ ] Build package: `python -m build`
- [ ] Test installation: `pip install dist/kaygraph-0.1.0.tar.gz`
- [ ] Verify CLI works: `kgraph --version`
- [ ] Upload to PyPI: `twine upload dist/*`
- [ ] Test installation from PyPI: `pip install kaygraph[declarative]`

### Backend Deployment

- [ ] Run database migrations
- [ ] Update environment variables
- [ ] Deploy API server
- [ ] Verify health endpoint
- [ ] Run smoke tests against production API

### Frontend Deployment

- [ ] Build production bundle: `npm run build`
- [ ] Test build locally: `npm run preview`
- [ ] Deploy to hosting (Vercel/Netlify)
- [ ] Verify environment variables
- [ ] Run smoke tests against production UI

### Post-Deployment

- [ ] Monitor error logs for 24 hours
- [ ] Check performance metrics
- [ ] User acceptance testing
- [ ] Announce release
- [ ] Update documentation site

---

## Success Metrics

### User Experience

- **Time to First Workflow**: < 5 minutes from signup to working workflow
- **Visual → Code Sync**: < 100ms latency
- **Test Execution (Mock)**: < 1 second
- **Export Workflow**: < 2 seconds

### Technical Performance

- **API Response Time**: p95 < 200ms
- **UI Render Time**: < 100ms for node operations
- **Database Queries**: < 10ms for workflow retrieval
- **YAML Parsing**: < 500ms for 1MB file

### Quality Metrics

- **Test Coverage**: > 80%
- **Bug Rate**: < 2 critical bugs per release
- **Uptime**: > 99.5%
- **User Retention**: > 60% weekly active users

---

## Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| ReactFlow performance with 100+ nodes | High | Implement virtualization, lazy loading |
| YAML parsing errors | High | Strict validation, helpful error messages |
| Database deadlocks during concurrent execution | Medium | Use row-level locking, connection pooling |
| API rate limiting too restrictive | Medium | Implement tiered limits, upgrade paths |

### User Experience Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Visual ↔ YAML sync confusing | High | Clear visual indicators, undo/redo |
| Too many node types overwhelming | Medium | Categorization, search, templates |
| Mock mode results misleading | Medium | Clear labeling, warnings, documentation |
| Export format incompatible with CLI | High | Extensive integration testing |

---

## Future Enhancements (Post-MVP)

1. **LLM Chat Interface**:
   - Natural language workflow generation
   - "Create a workflow that processes invoices and sends emails"
   - AI suggests node configurations

2. **Workflow Templates**:
   - Library of pre-built workflows
   - One-click deployment
   - Community sharing

3. **Version Control Integration**:
   - Git integration for `.kg.yaml` files
   - Diff visualization
   - Branch-based workflow development

4. **Advanced Debugging**:
   - Step-through execution
   - Breakpoints on nodes
   - Variable inspection

5. **Marketplace**:
   - Share workflows publicly
   - Rating and reviews
   - Monetization options

---

## Conclusion

This implementation plan provides a complete roadmap for building the Declarative Visual Workflow Builder. The plan is structured to:

1. **Reuse existing code**: 3,115 lines of declarative infrastructure already complete
2. **Follow proven patterns**: Based on 71 working examples in workbooks
3. **Deliver incrementally**: 4 phases, each independently testable
4. **Maintain quality**: Comprehensive testing at every level
5. **Enable portability**: `.kg.yaml` as universal format

**Estimated Total Effort**: 26-33 hours (3-4 weeks part-time)

**Key Deliverables**:
- ✅ Bidirectional YAML ↔ Visual conversion
- ✅ Complete CRUD API for workflows
- ✅ ReactFlow-based visual builder
- ✅ Test console with mock/real modes
- ✅ Export to CLI/FastAPI/Claude Code

The system will enable users to create sophisticated AI workflows through three modes (chat/visual/YAML), test them in the browser, and deploy them anywhere.