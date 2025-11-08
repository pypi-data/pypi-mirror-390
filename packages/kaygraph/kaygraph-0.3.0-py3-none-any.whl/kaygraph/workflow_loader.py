"""
Declarative workflow support for KayGraph.

Enables loading workflows from YAML files using a simple, LLM-friendly format.

Example .kg.yaml file:
    workflows:
      main:
        description: "Simple greeting workflow"
        concepts:
          greeter: GreeterNode
          formatter: FormatterNode
        graph:
          greeter >> formatter

Usage:
    from kaygraph import load_workflow

    workflow = load_workflow("my_workflow.kg.yaml")
    result = workflow.run(shared={"input": "data"})
"""

__version__ = "0.1.0"

from typing import Dict, Any, List, Optional
from pathlib import Path
import sys
import inspect
import json

# Make yaml optional - KayGraph has zero dependencies
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load and parse YAML or JSON file.

    Args:
        file_path: Path to YAML or JSON file

    Returns:
        Parsed content as dictionary

    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML is invalid (when PyYAML installed)
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Workflow file not found: {file_path}")

    # Try JSON first (always available)
    if file_path.endswith('.json'):
        with open(path, 'r') as f:
            return json.load(f)

    # For YAML files, check if PyYAML is available
    if file_path.endswith(('.yaml', '.yml')):
        if not YAML_AVAILABLE:
            raise ImportError(
                "PyYAML is required for YAML workflow files. "
                "Install it with: pip install pyyaml\n"
                "Or use JSON format instead (.json files)"
            )

    with open(path, 'r', encoding='utf-8') as f:
        try:
            content = yaml.safe_load(f)
            if not isinstance(content, dict):
                raise ValueError("YAML content must be a dictionary")
            return content
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path}: {e}")


def discover_node_class(node_type: str, search_modules: Optional[List] = None) -> type:
    """
    Discover node class by name.

    Searches for Node classes in:
    1. Provided search_modules
    2. sys.modules (already imported)
    3. Common locations (nodes.py, app.nodes, etc.)

    Args:
        node_type: Name of node class (e.g., "GreeterNode")
        search_modules: Optional list of module names to search

    Returns:
        Node class

    Raises:
        ValueError: If node class not found
    """
    from kaygraph import BaseNode

    # Try common module patterns
    module_patterns = [
        'nodes',
        '__main__',
        'app.nodes',
        'workflow.nodes',
    ]

    if search_modules:
        module_patterns = search_modules + module_patterns

    # Search in sys.modules for already-imported classes
    for module_name, module in sys.modules.items():
        if module is None:
            continue

        try:
            if hasattr(module, node_type):
                cls = getattr(module, node_type)
                if inspect.isclass(cls) and issubclass(cls, BaseNode):
                    return cls
        except (AttributeError, TypeError):
            continue

    # Try importing from common patterns
    for pattern in module_patterns:
        try:
            if '.' in pattern:
                # Full module path
                parts = pattern.rsplit('.', 1)
                module = __import__(parts[0], fromlist=[parts[1]])
            else:
                # Simple module name
                module = __import__(pattern)

            if hasattr(module, node_type):
                cls = getattr(module, node_type)
                if inspect.isclass(cls) and issubclass(cls, BaseNode):
                    return cls
        except (ImportError, AttributeError):
            continue

    raise ValueError(
        f"Node class '{node_type}' not found. "
        f"Make sure to import the module containing {node_type} before loading the workflow, "
        f"or add it to search_modules parameter."
    )


def parse_graph_syntax(graph_str: str, concepts: Dict[str, str]) -> List[tuple]:
    """
    Parse simple graph syntax string into connections.

    Supports:
        node1 >> node2          # Connect with default action
        node1 - "action" >> node2   # Connect with named action (future)

    Args:
        graph_str: Graph definition string
        concepts: Dict mapping concept names to node types

    Returns:
        List of (source, target, action) tuples

    Example:
        graph_str = "start >> process >> end"
        concepts = {"start": "StartNode", "process": "ProcessNode", "end": "EndNode"}

        Returns: [("start", "process", None), ("process", "end", None)]
    """
    connections = []

    # Split by '>>' to get node connections
    parts = [p.strip() for p in graph_str.split('>>')]

    # Create sequential connections
    for i in range(len(parts) - 1):
        source = parts[i].strip()
        target = parts[i + 1].strip()

        # Validate node names exist in concepts
        if source not in concepts:
            raise ValueError(f"Node '{source}' not defined in concepts")
        if target not in concepts:
            raise ValueError(f"Node '{target}' not defined in concepts")

        connections.append((source, target, None))  # None = default action

    return connections


def yaml_to_graph(yaml_content: Dict[str, Any], search_modules: Optional[List] = None):
    """
    Convert YAML workflow definition to KayGraph Graph.

    Args:
        yaml_content: Parsed YAML content
        search_modules: Optional list of module names to search for node classes

    Returns:
        Graph instance ready to run

    Raises:
        ValueError: If workflow structure is invalid
    """
    from kaygraph import Graph

    # Check for 'workflows' section
    if 'workflows' not in yaml_content:
        raise ValueError("YAML must contain 'workflows' section")

    workflows = yaml_content['workflows']

    # Get main workflow (first one by default, or specified)
    domain_config = yaml_content.get('domain', {})
    main_workflow_name = domain_config.get('main_workflow', list(workflows.keys())[0])

    if main_workflow_name not in workflows:
        raise ValueError(f"Main workflow '{main_workflow_name}' not found")

    workflow = workflows[main_workflow_name]

    # Extract concepts (node definitions)
    concepts = workflow.get('concepts', {})
    if not concepts:
        raise ValueError(f"Workflow '{main_workflow_name}' must define 'concepts'")

    # Extract graph definition
    graph_def = workflow.get('graph', '')
    if not graph_def:
        raise ValueError(f"Workflow '{main_workflow_name}' must define 'graph'")

    # Parse graph syntax
    connections = parse_graph_syntax(graph_def, concepts)

    # Create node instances
    nodes = {}
    for concept_name, node_type in concepts.items():
        # Discover and instantiate node class
        node_class = discover_node_class(node_type, search_modules)
        nodes[concept_name] = node_class(node_id=concept_name)

    # Get start node (first node in first connection)
    if not connections:
        raise ValueError("Graph must have at least one connection")

    start_node_name = connections[0][0]
    start_node = nodes[start_node_name]

    # Create graph
    graph = Graph(start=start_node)

    # Connect nodes according to graph definition
    for source_name, target_name, action in connections:
        source_node = nodes[source_name]
        target_node = nodes[target_name]

        if action:
            # Named action
            source_node.successors[action] = target_node
        else:
            # Default action
            source_node >> target_node

    return graph


def load_workflow(file_path: str, search_modules: Optional[List] = None):
    """
    Load workflow from .kg.yaml file.

    This is the main entry point for declarative workflows.

    Args:
        file_path: Path to .kg.yaml file
        search_modules: Optional list of module names to search for node classes

    Returns:
        Graph instance ready to run

    Example:
        # Define nodes first
        from kaygraph import Node

        class GreeterNode(Node):
            def prep(self, shared):
                return shared.get("name", "World")

            def exec(self, prep_res):
                return f"Hello, {prep_res}!"

            def post(self, shared, prep_res, exec_res):
                shared["greeting"] = exec_res
                return None

        # Load workflow
        workflow = load_workflow("greeting.kg.yaml")
        result = workflow.run(shared={"name": "Alice"})
        print(result["greeting"])  # "Hello, Alice!"

    YAML file format:
        workflows:
          main:
            description: "Greet a user"
            concepts:
              greeter: GreeterNode
            graph:
              greeter
    """
    yaml_content = load_yaml_file(file_path)
    return yaml_to_graph(yaml_content, search_modules)


def graph_to_yaml(graph, workflow_name: str = "main") -> str:
    """
    Export KayGraph Graph to YAML format.

    Args:
        graph: Graph instance to export
        workflow_name: Name for the workflow (default: "main")

    Returns:
        YAML string representation

    Note:
        This is a simplified export that captures node names and connections.
        Complex node configurations may not be fully preserved.
    """
    # Extract nodes and connections from graph
    visited = set()
    concepts = {}
    connections = []

    def traverse(node, depth=0):
        if node.node_id in visited or depth > 100:  # Prevent infinite loops
            return

        visited.add(node.node_id)

        # Add to concepts
        node_type = node.__class__.__name__
        concepts[node.node_id] = node_type

        # Add connections
        for action, successor in node.successors.items():
            connections.append((node.node_id, successor.node_id, action))
            traverse(successor, depth + 1)

    # Get start node - handle both Graph instances and raw nodes
    if hasattr(graph, 'start'):
        start_node = graph.start
        # If start is a property/method, call it
        if callable(start_node):
            try:
                start_node = start_node()
            except:
                pass
    else:
        start_node = graph

    # Start traversal
    if start_node and hasattr(start_node, 'node_id'):
        traverse(start_node)
    else:
        raise ValueError(f"Cannot export: invalid start node type {type(start_node)}")

    # Build graph string from connections
    if connections:
        # Simple linear graph for now
        graph_str = " >> ".join([conn[0] for conn in connections] + [connections[-1][1]])
    else:
        # Single node
        graph_str = list(concepts.keys())[0]

    # Build YAML structure
    workflow_def = {
        "workflows": {
            workflow_name: {
                "description": f"Exported workflow: {workflow_name}",
                "concepts": concepts,
                "graph": graph_str
            }
        }
    }

    return yaml.dump(workflow_def, default_flow_style=False, sort_keys=False)


def export_workflow(graph, output_path: str, workflow_name: str = "main"):
    """
    Export workflow to .kg.yaml file.

    Args:
        graph: Graph instance to export
        output_path: Path where to save the .kg.yaml file
        workflow_name: Name for the workflow
    """
    yaml_str = graph_to_yaml(graph, workflow_name)

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml_str, encoding='utf-8')

    print(f"✓ Workflow exported to: {output_path}")


def validate_workflow(file_path: str) -> List[str]:
    """
    Validate workflow file for common errors.

    Checks:
    - File exists and is valid YAML
    - Required sections present (workflows, concepts, graph)
    - All referenced nodes are defined
    - Graph syntax is valid

    Args:
        file_path: Path to .kg.yaml file

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check file exists
    if not Path(file_path).exists():
        return [f"File not found: {file_path}"]

    # Load YAML
    try:
        yaml_content = load_yaml_file(file_path)
    except Exception as e:
        return [f"Failed to load YAML: {e}"]

    # Check workflows section
    if 'workflows' not in yaml_content:
        errors.append("Missing 'workflows' section")
        return errors

    workflows = yaml_content['workflows']

    if not workflows:
        errors.append("No workflows defined")
        return errors

    # Check each workflow
    for workflow_name, workflow in workflows.items():
        # Check concepts
        if 'concepts' not in workflow:
            errors.append(f"Workflow '{workflow_name}': Missing 'concepts' section")
            continue

        concepts = workflow['concepts']
        if not concepts:
            errors.append(f"Workflow '{workflow_name}': No concepts defined")
            continue

        # Check graph
        if 'graph' not in workflow:
            errors.append(f"Workflow '{workflow_name}': Missing 'graph' section")
            continue

        graph_str = workflow['graph']
        if not graph_str:
            errors.append(f"Workflow '{workflow_name}': Empty graph definition")
            continue

        # Validate graph syntax
        try:
            connections = parse_graph_syntax(graph_str, concepts)
            if not connections and len(concepts) > 1:
                errors.append(
                    f"Workflow '{workflow_name}': Graph must connect multiple nodes"
                )
        except ValueError as e:
            errors.append(f"Workflow '{workflow_name}': {e}")

    return errors


# Convenience re-exports for common use
__all__ = [
    'load_workflow',
    'export_workflow',
    'validate_workflow',
    'graph_to_yaml',
    'yaml_to_graph',
]
