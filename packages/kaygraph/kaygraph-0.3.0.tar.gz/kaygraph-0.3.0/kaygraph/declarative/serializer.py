"""
Workflow Serialization for KayGraph

Provides bidirectional conversion between KayGraph Domain/Graph objects and
YAML format, enabling portable workflow definitions.
"""

import yaml
from typing import Dict, Any, List, Optional
from pathlib import Path


class WorkflowSerializer:
    """
    Serialize KayGraph workflows to YAML format.

    Supports:
    - Domain → YAML conversion
    - Graph → workflow steps conversion
    - Concept preservation
    - Visual layout metadata
    """

    def __init__(self):
        """Initialize serializer with default configuration."""
        self.include_metadata = True
        self.preserve_visual_layout = True

    def domain_to_dict(self, domain) -> Dict[str, Any]:
        """
        Convert Domain object to dictionary.

        Args:
            domain: Domain object instance

        Returns:
            Dictionary representation suitable for YAML serialization
        """
        result = {}

        # Domain metadata
        result["domain"] = {
            "name": domain.name,
            "version": domain.version,
        }

        if domain.description:
            result["domain"]["description"] = domain.description

        if domain.main_workflow:
            result["domain"]["main_workflow"] = domain.main_workflow

        # Concepts
        if domain.concepts:
            result["concepts"] = {}
            for name, concept_def in domain.concepts.items():
                # If concept_def has to_dict() method, use it
                if hasattr(concept_def, 'to_dict'):
                    result["concepts"][name] = concept_def.to_dict()
                else:
                    # Otherwise assume it's already a dict
                    result["concepts"][name] = concept_def

        # Workflows
        if domain.workflows:
            result["workflows"] = {}
            for name, workflow_config in domain.workflows.items():
                result["workflows"][name] = workflow_config

        return result

    def domain_to_yaml(self, domain, include_metadata: bool = False) -> str:
        """
        Convert Domain to YAML string.

        Args:
            domain: Domain object instance
            include_metadata: Whether to include metadata section

        Returns:
            YAML string representation
        """
        data = self.domain_to_dict(domain)

        if include_metadata:
            # Add metadata section at the top
            metadata = {
                "metadata": {
                    "title": domain.name.replace("_", " ").title(),
                    "description": domain.description or f"Domain: {domain.name}",
                    "version": domain.version,
                    "deployment": {
                        "cli": {"enabled": True},
                        "api": {"enabled": False},
                        "claude_code": {"enabled": True}
                    }
                }
            }
            data = {**metadata, **data}

        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def graph_to_workflow_dict(self, graph, workflow_name: str = "main") -> Dict[str, Any]:
        """
        Convert Graph to workflow configuration dictionary.

        Args:
            graph: Graph object instance
            workflow_name: Name for the workflow

        Returns:
            Dictionary with workflow steps
        """
        steps = []

        # Extract steps from graph nodes
        # This is a simplified version - full implementation would traverse the graph
        current_node = graph.start
        visited = set()

        while current_node and id(current_node) not in visited:
            visited.add(id(current_node))

            step = self._node_to_step(current_node)
            steps.append(step)

            # Try to get next node (simplified - doesn't handle branching)
            next_nodes = graph.next.get(current_node, {})
            if "default" in next_nodes:
                current_node = next_nodes["default"]
            else:
                current_node = None

        return {
            "steps": steps
        }

    def _node_to_step(self, node) -> Dict[str, Any]:
        """
        Convert a Node instance to a workflow step dictionary.

        Args:
            node: Node instance

        Returns:
            Step configuration dictionary
        """
        step = {}

        # Get node type
        node_type = getattr(node, 'node_type', None) or type(node).__name__

        # Basic step structure
        step["type"] = node_type.lower().replace("node", "").replace("config", "")

        # Add node_id if available
        if hasattr(node, 'node_id') and node.node_id:
            step["name"] = node.node_id

        # Add description if available
        if hasattr(node, 'description') and node.description:
            step["description"] = node.description

        # Add configuration if available (ConfigNode)
        if hasattr(node, 'config') and node.config:
            step["config"] = node.config.copy()
            # Remove redundant fields
            step["config"].pop("type", None)
            step["config"].pop("node_id", None)
            step["config"].pop("description", None)

        # Add result_name if available (Named Results pattern)
        if hasattr(node, 'result_name') and node.result_name:
            step["outputs"] = [node.result_name]

        # Add input_names if available (Named Results pattern)
        if hasattr(node, 'input_names') and node.input_names:
            step["inputs"] = node.input_names

        # Add concept information if available
        if hasattr(node, 'output_concept') and node.output_concept:
            step["output_concept"] = node.output_concept

        if hasattr(node, 'concept_name') and node.concept_name:
            step["concept"] = node.concept_name

        return step

    def workflow_to_yaml(self, workflow_config: Dict[str, Any],
                        domain_name: str = "workflow",
                        domain_version: str = "1.0") -> str:
        """
        Convert a standalone workflow configuration to YAML.

        Args:
            workflow_config: Workflow configuration dictionary
            domain_name: Name for the domain wrapper
            domain_version: Version for the domain

        Returns:
            YAML string
        """
        data = {
            "domain": {
                "name": domain_name,
                "version": domain_version,
            },
            "workflows": {
                "main": workflow_config
            }
        }

        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def dict_to_yaml(self, data: Dict[str, Any], **yaml_options) -> str:
        """
        Convert dictionary to YAML with consistent formatting.

        Args:
            data: Dictionary to convert
            **yaml_options: Additional options for yaml.dump

        Returns:
            YAML string
        """
        defaults = {
            "default_flow_style": False,
            "sort_keys": False,
            "allow_unicode": True,
            "indent": 2
        }
        options = {**defaults, **yaml_options}

        return yaml.dump(data, **options)

    def yaml_to_dict(self, yaml_str: str) -> Dict[str, Any]:
        """
        Convert YAML string to dictionary.

        Args:
            yaml_str: YAML string to parse

        Returns:
            Parsed dictionary

        Raises:
            yaml.YAMLError: If YAML is invalid
        """
        return yaml.safe_load(yaml_str)

    def save_domain_to_file(self, domain, file_path: str,
                           include_metadata: bool = True):
        """
        Save Domain to .kg.yaml file.

        Args:
            domain: Domain object instance
            file_path: Path where to save the file
            include_metadata: Whether to include metadata section
        """
        yaml_content = self.domain_to_yaml(domain, include_metadata=include_metadata)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml_content, encoding='utf-8')

    def load_domain_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Load domain dictionary from .kg.yaml file.

        Args:
            file_path: Path to the file

        Returns:
            Domain configuration dictionary

        Note:
            This returns a dictionary. To create a Domain object,
            use the domain.load_domain() function from the declarative workflows module.
        """
        path = Path(file_path)
        yaml_content = path.read_text(encoding='utf-8')
        return self.yaml_to_dict(yaml_content)

    def add_visual_layout(self, domain_dict: Dict[str, Any],
                         visual_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add visual layout information to domain dictionary.

        Args:
            domain_dict: Domain configuration dictionary
            visual_data: Visual layout data (ReactFlow format)

        Returns:
            Updated domain dictionary with canvas section
        """
        result = domain_dict.copy()
        result["canvas"] = {
            "viewport": visual_data.get("viewport", {"x": 0, "y": 0, "zoom": 1}),
            "nodes": visual_data.get("nodes", []),
            "edges": visual_data.get("edges", [])
        }
        return result

    def extract_visual_layout(self, domain_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract visual layout information from domain dictionary.

        Args:
            domain_dict: Domain configuration dictionary

        Returns:
            Visual layout data if present, None otherwise
        """
        if "canvas" in domain_dict:
            return {
                "viewport": domain_dict["canvas"].get("viewport"),
                "nodes": domain_dict["canvas"].get("nodes", []),
                "edges": domain_dict["canvas"].get("edges", [])
            }
        return None


# Convenience functions for common operations

def serialize_domain(domain, include_metadata: bool = False) -> str:
    """
    Convenience function to serialize a domain to YAML.

    Args:
        domain: Domain object instance
        include_metadata: Whether to include metadata section

    Returns:
        YAML string
    """
    serializer = WorkflowSerializer()
    return serializer.domain_to_yaml(domain, include_metadata=include_metadata)


def serialize_workflow(workflow_config: Dict[str, Any],
                      domain_name: str = "workflow") -> str:
    """
    Convenience function to serialize a workflow configuration to YAML.

    Args:
        workflow_config: Workflow configuration dictionary
        domain_name: Name for the domain wrapper

    Returns:
        YAML string
    """
    serializer = WorkflowSerializer()
    return serializer.workflow_to_yaml(workflow_config, domain_name=domain_name)


def save_domain(domain, file_path: str, include_metadata: bool = True):
    """
    Convenience function to save a domain to file.

    Args:
        domain: Domain object instance
        file_path: Path where to save the file
        include_metadata: Whether to include metadata section
    """
    serializer = WorkflowSerializer()
    serializer.save_domain_to_file(domain, file_path, include_metadata=include_metadata)


if __name__ == "__main__":
    # Example usage
    print("WorkflowSerializer - Convert KayGraph objects to YAML")
    print("=" * 60)
    print()
    print("Example usage:")
    print()
    print("from kaygraph.declarative import WorkflowSerializer")
    print("serializer = WorkflowSerializer()")
    print()
    print("# Serialize domain to YAML")
    print("yaml_str = serializer.domain_to_yaml(domain)")
    print()
    print("# Save domain to file")
    print("serializer.save_domain_to_file(domain, 'workflow.kg.yaml')")
    print()
    print("# Load domain from file")
    print("domain_dict = serializer.load_domain_from_file('workflow.kg.yaml')")
