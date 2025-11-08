"""
Visual Converter for KayGraph

Bidirectional conversion between ReactFlow visual representation
and YAML workflow configuration.
"""

from typing import Dict, Any, List, Optional, Tuple


class VisualConverter:
    """
    Convert between ReactFlow canvas format and YAML workflow format.

    Supports:
    - YAML → ReactFlow canvas (auto-layout generation)
    - ReactFlow canvas → YAML (preserving visual positions)
    - Node type mapping
    - Edge/connection preservation
    """

    # Node type styles for ReactFlow
    NODE_STYLES = {
        "llm": {"color": "#48BB78", "icon": "🤖", "label": "LLM"},
        "transform": {"color": "#ED8936", "icon": "🔄", "label": "Transform"},
        "condition": {"color": "#9F7AEA", "icon": "❓", "label": "Condition"},
        "extract": {"color": "#4299E1", "icon": "📥", "label": "Extract"},
        "validate": {"color": "#38B2AC", "icon": "✓", "label": "Validate"},
        "parallel": {"color": "#805AD5", "icon": "⚡", "label": "Parallel"},
        "batch": {"color": "#DD6B20", "icon": "📦", "label": "Batch"},
        "default": {"color": "#718096", "icon": "⚙", "label": "Node"},
    }

    # Default layout settings
    DEFAULT_Y_SPACING = 120
    DEFAULT_X_OFFSET = 250
    DEFAULT_NODE_WIDTH = 180
    DEFAULT_NODE_HEIGHT = 60

    def __init__(self):
        """Initialize visual converter."""
        self.y_spacing = self.DEFAULT_Y_SPACING
        self.x_offset = self.DEFAULT_X_OFFSET

    def yaml_to_reactflow(self, yaml_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert YAML workflow configuration to ReactFlow canvas format.

        Args:
            yaml_dict: Parsed YAML dictionary

        Returns:
            ReactFlow canvas with nodes and edges
        """
        # Check if canvas section exists
        if "canvas" in yaml_dict:
            # Use existing visual layout
            return {
                "nodes": yaml_dict["canvas"].get("nodes", []),
                "edges": yaml_dict["canvas"].get("edges", []),
                "viewport": yaml_dict["canvas"].get("viewport", {"x": 0, "y": 0, "zoom": 1})
            }

        # Generate canvas from workflow steps
        return self._generate_canvas_from_steps(yaml_dict)

    def _generate_canvas_from_steps(self, yaml_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate ReactFlow canvas from workflow steps with auto-layout.

        Args:
            yaml_dict: Parsed YAML dictionary

        Returns:
            ReactFlow canvas with auto-generated layout
        """
        nodes = []
        edges = []

        # Extract steps from main workflow
        workflows = yaml_dict.get("workflows", {})
        main_workflow = yaml_dict.get("domain", {}).get("main_workflow", "main")
        steps = workflows.get(main_workflow, {}).get("steps", [])

        # Generate nodes and edges
        for idx, step in enumerate(steps):
            node_id = f"node-{idx}"

            # Create node
            node = self._create_reactflow_node(
                node_id=node_id,
                step=step,
                position={"x": self.x_offset, "y": idx * self.y_spacing}
            )
            nodes.append(node)

            # Create edge to previous node (for linear flow)
            if idx > 0:
                edge = self._create_reactflow_edge(
                    edge_id=f"edge-{idx-1}-{idx}",
                    source=f"node-{idx-1}",
                    target=node_id,
                    label=step.get("when")  # Conditional routing label
                )
                edges.append(edge)

        return {
            "nodes": nodes,
            "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        }

    def _create_reactflow_node(self, node_id: str, step: Dict[str, Any],
                               position: Dict[str, int]) -> Dict[str, Any]:
        """
        Create a ReactFlow node from a workflow step.

        Args:
            node_id: Unique node identifier
            step: Workflow step configuration
            position: {x, y} position on canvas

        Returns:
            ReactFlow node object
        """
        node_type = step.get("type", "default")
        style_info = self.NODE_STYLES.get(node_type, self.NODE_STYLES["default"])

        return {
            "id": node_id,
            "type": node_type,
            "position": position,
            "data": {
                "label": step.get("name", step.get("description", style_info["label"])),
                "config": step.get("config", {}),
                "icon": style_info["icon"],
                "color": style_info["color"],
                "description": step.get("description"),
                "inputs": step.get("inputs", []),
                "outputs": step.get("outputs", []),
                "concept": step.get("concept") or step.get("output_concept"),
            },
            "style": {
                "background": style_info["color"],
                "color": "#ffffff",
                "border": "1px solid #00000020",
                "borderRadius": "8px",
                "padding": "10px",
                "width": self.DEFAULT_NODE_WIDTH,
                "height": self.DEFAULT_NODE_HEIGHT,
            }
        }

    def _create_reactflow_edge(self, edge_id: str, source: str, target: str,
                               label: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a ReactFlow edge.

        Args:
            edge_id: Unique edge identifier
            source: Source node ID
            target: Target node ID
            label: Optional edge label (for conditional routing)

        Returns:
            ReactFlow edge object
        """
        edge = {
            "id": edge_id,
            "source": source,
            "target": target,
            "type": "smoothstep",
            "animated": False,
        }

        if label:
            edge["label"] = label
            edge["labelStyle"] = {"fill": "#9F7AEA", "fontWeight": 700}

        return edge

    def reactflow_to_yaml(self, canvas: Dict[str, Any],
                         existing_yaml: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Convert ReactFlow canvas to YAML workflow configuration.

        Args:
            canvas: ReactFlow canvas with nodes and edges
            existing_yaml: Optional existing YAML dict to preserve metadata

        Returns:
            YAML-compatible dictionary
        """
        # Start with existing YAML or create new structure
        if existing_yaml:
            result = existing_yaml.copy()
        else:
            result = {
                "domain": {
                    "name": "workflow",
                    "version": "1.0"
                },
                "workflows": {}
            }

        # Add/update canvas section
        result["canvas"] = {
            "viewport": canvas.get("viewport", {"x": 0, "y": 0, "zoom": 1}),
            "nodes": canvas.get("nodes", []),
            "edges": canvas.get("edges", [])
        }

        # Generate workflow steps from canvas
        steps = self._canvas_to_steps(canvas)

        # Update main workflow
        main_workflow_name = result.get("domain", {}).get("main_workflow", "main")
        if "workflows" not in result:
            result["workflows"] = {}

        result["workflows"][main_workflow_name] = {"steps": steps}

        return result

    def _canvas_to_steps(self, canvas: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Convert ReactFlow canvas to workflow steps list.

        Args:
            canvas: ReactFlow canvas

        Returns:
            List of workflow step configurations
        """
        nodes = canvas.get("nodes", [])
        edges = canvas.get("edges", [])

        # Sort nodes by Y position to maintain visual order
        sorted_nodes = sorted(nodes, key=lambda n: n.get("position", {}).get("y", 0))

        steps = []
        for node in sorted_nodes:
            step = self._node_to_step(node, edges)
            steps.append(step)

        return steps

    def _node_to_step(self, node: Dict[str, Any], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Convert ReactFlow node to workflow step.

        Args:
            node: ReactFlow node
            edges: List of all edges (for finding incoming conditions)

        Returns:
            Workflow step configuration
        """
        data = node.get("data", {})
        step = {}

        # Basic fields
        step["type"] = node.get("type", "default")

        if data.get("label"):
            step["name"] = data["label"]

        if data.get("description"):
            step["description"] = data["description"]

        # Configuration
        if data.get("config"):
            step["config"] = data["config"]

        # Named results pattern
        if data.get("outputs"):
            step["outputs"] = data["outputs"]

        if data.get("inputs"):
            step["inputs"] = data["inputs"]

        # Concept validation
        if data.get("concept"):
            step["output_concept"] = data["concept"]

        # Conditional routing - check incoming edge for label
        incoming_edge = next(
            (e for e in edges if e.get("target") == node["id"] and e.get("label")),
            None
        )
        if incoming_edge and incoming_edge.get("label"):
            step["when"] = incoming_edge["label"]

        return step

    def generate_auto_layout(self, steps: List[Dict[str, Any]],
                            layout_type: str = "vertical") -> Dict[str, Any]:
        """
        Generate automatic layout for workflow steps.

        Args:
            steps: List of workflow steps
            layout_type: "vertical", "horizontal", or "tree"

        Returns:
            ReactFlow canvas with positioned nodes
        """
        nodes = []
        edges = []

        if layout_type == "vertical":
            # Vertical linear layout
            for idx, step in enumerate(steps):
                node_id = f"node-{idx}"
                node = self._create_reactflow_node(
                    node_id=node_id,
                    step=step,
                    position={"x": self.x_offset, "y": idx * self.y_spacing}
                )
                nodes.append(node)

                if idx > 0:
                    edge = self._create_reactflow_edge(
                        edge_id=f"edge-{idx-1}-{idx}",
                        source=f"node-{idx-1}",
                        target=node_id
                    )
                    edges.append(edge)

        elif layout_type == "horizontal":
            # Horizontal linear layout
            for idx, step in enumerate(steps):
                node_id = f"node-{idx}"
                node = self._create_reactflow_node(
                    node_id=node_id,
                    step=step,
                    position={"x": idx * 250, "y": 100}
                )
                nodes.append(node)

                if idx > 0:
                    edge = self._create_reactflow_edge(
                        edge_id=f"edge-{idx-1}-{idx}",
                        source=f"node-{idx-1}",
                        target=node_id
                    )
                    edges.append(edge)

        else:
            # Default to vertical
            return self.generate_auto_layout(steps, layout_type="vertical")

        return {
            "nodes": nodes,
            "edges": edges,
            "viewport": {"x": 0, "y": 0, "zoom": 1}
        }

    def detect_layout_type(self, canvas: Dict[str, Any]) -> str:
        """
        Detect the layout type from canvas node positions.

        Args:
            canvas: ReactFlow canvas

        Returns:
            "vertical", "horizontal", or "complex"
        """
        nodes = canvas.get("nodes", [])

        if len(nodes) <= 1:
            return "vertical"

        # Calculate variance in X and Y positions
        x_positions = [n.get("position", {}).get("x", 0) for n in nodes]
        y_positions = [n.get("position", {}).get("y", 0) for n in nodes]

        x_variance = max(x_positions) - min(x_positions)
        y_variance = max(y_positions) - min(y_positions)

        if x_variance < 100:
            return "vertical"
        elif y_variance < 100:
            return "horizontal"
        else:
            return "complex"


# Convenience functions

def yaml_to_canvas(yaml_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to convert YAML to ReactFlow canvas.

    Args:
        yaml_dict: Parsed YAML dictionary

    Returns:
        ReactFlow canvas
    """
    converter = VisualConverter()
    return converter.yaml_to_reactflow(yaml_dict)


def canvas_to_yaml(canvas: Dict[str, Any],
                   existing_yaml: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Convenience function to convert ReactFlow canvas to YAML.

    Args:
        canvas: ReactFlow canvas
        existing_yaml: Optional existing YAML to preserve

    Returns:
        YAML-compatible dictionary
    """
    converter = VisualConverter()
    return converter.reactflow_to_yaml(canvas, existing_yaml)


if __name__ == "__main__":
    # Example usage
    print("VisualConverter - ReactFlow ↔ YAML conversion")
    print("=" * 60)
    print()
    print("Example usage:")
    print()
    print("from kaygraph.declarative import VisualConverter")
    print("converter = VisualConverter()")
    print()
    print("# YAML → ReactFlow")
    print("canvas = converter.yaml_to_reactflow(yaml_dict)")
    print()
    print("# ReactFlow → YAML")
    print("yaml_dict = converter.reactflow_to_yaml(canvas)")
    print()
    print("# Auto-layout generation")
    print("canvas = converter.generate_auto_layout(steps, layout_type='vertical')")
