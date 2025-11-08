"""
Domain Organization - Single .kg.yaml files with multiple workflows and concepts.

Allows LLMs to create complete, self-contained workflow files:
- Define all concepts in one place
- Multiple related workflows in same file
- Clear domain boundaries
- Easy to share and version
"""

from typing import Dict, Any, List
from pathlib import Path
from utils.config_loader import load_config
from utils.concepts import get_concept_registry
from workflow_loader import create_config_node_from_step


class Domain:
    """
    Represents a domain with multiple workflows and shared concepts.

    A domain is a collection of related workflows that share concepts and
    can be packaged in a single .kg.yaml file.
    """

    def __init__(self, name: str, version: str = "1.0", description: str = ""):
        """
        Initialize domain.

        Args:
            name: Domain name (e.g., "invoice_processing")
            version: Domain version
            description: What this domain does
        """
        self.name = name
        self.version = version
        self.description = description
        self.workflows = {}
        self.concepts = {}
        self.main_workflow = None

    def add_workflow(self, workflow_name: str, workflow_config: Dict[str, Any],
                     is_main: bool = False):
        """Add a workflow to this domain."""
        self.workflows[workflow_name] = workflow_config
        if is_main:
            self.main_workflow = workflow_name

    def add_concept(self, concept_name: str, concept_definition: Dict[str, Any]):
        """Add a concept to this domain."""
        self.concepts[concept_name] = concept_definition

    def load_concepts(self):
        """Load all concepts into the global concept registry."""
        if self.concepts:
            registry = get_concept_registry()
            registry.load_from_yaml(self.concepts)

    def get_workflow(self, workflow_name: str = None) -> Dict[str, Any]:
        """
        Get workflow config by name.

        Args:
            workflow_name: Name of workflow, or None for main workflow

        Returns:
            Workflow configuration dict

        Raises:
            ValueError: If workflow not found
        """
        if workflow_name is None:
            # Use main workflow
            if self.main_workflow is None:
                raise ValueError(
                    f"Domain '{self.name}' has no main_workflow specified. "
                    f"Available workflows: {list(self.workflows.keys())}"
                )
            workflow_name = self.main_workflow

        if workflow_name not in self.workflows:
            raise ValueError(
                f"Workflow '{workflow_name}' not found in domain '{self.name}'. "
                f"Available: {list(self.workflows.keys())}"
            )

        return self.workflows[workflow_name]

    def list_workflows(self) -> List[str]:
        """Get list of all workflow names in this domain."""
        return list(self.workflows.keys())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert domain to dictionary format.

        Returns:
            Dictionary representation suitable for YAML serialization
        """
        result = {}

        # Domain metadata
        result["domain"] = {
            "name": self.name,
            "version": self.version,
        }

        if self.description:
            result["domain"]["description"] = self.description

        if self.main_workflow:
            result["domain"]["main_workflow"] = self.main_workflow

        # Concepts
        if self.concepts:
            result["concepts"] = {}
            for name, concept_def in self.concepts.items():
                # If concept_def has to_dict() method, use it
                if hasattr(concept_def, 'to_dict'):
                    result["concepts"][name] = concept_def.to_dict()
                else:
                    # Otherwise assume it's already a dict
                    result["concepts"][name] = concept_def

        # Workflows
        if self.workflows:
            result["workflows"] = {}
            for name, workflow_config in self.workflows.items():
                result["workflows"][name] = workflow_config

        return result

    def to_yaml(self, include_metadata: bool = False) -> str:
        """
        Convert domain to YAML string.

        Args:
            include_metadata: Whether to include metadata section for deployment

        Returns:
            YAML string representation
        """
        import yaml

        data = self.to_dict()

        if include_metadata:
            # Add metadata section at the top
            metadata = {
                "metadata": {
                    "title": self.name.replace("_", " ").title(),
                    "description": self.description or f"Domain: {self.name}",
                    "version": self.version,
                    "deployment": {
                        "cli": {"enabled": True},
                        "api": {"enabled": False},
                        "claude_code": {"enabled": True}
                    }
                }
            }
            data = {**metadata, **data}

        return yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)

    def to_file(self, file_path: str, include_metadata: bool = True):
        """
        Save domain to .kg.yaml file.

        Args:
            file_path: Path where to save the file
            include_metadata: Whether to include metadata section
        """
        yaml_content = self.to_yaml(include_metadata=include_metadata)

        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml_content, encoding='utf-8')

        print(f"✓ Domain '{self.name}' saved to: {file_path}")


def load_domain(domain_path: str) -> Domain:
    """
    Load domain from .kg.yaml file.

    Expected structure:
        domain:
          name: invoice_processing
          version: 1.0
          description: "Complete invoice handling"
          main_workflow: process_invoice

        concepts:
          Invoice:
            description: "Commercial invoice"
            structure:
              total:
                type: number
                required: true

        workflows:
          process_invoice:
            steps:
              - node: extract
                ...

          extract_invoice:
            steps:
              - node: ocr
                ...

    Args:
        domain_path: Path to domain .kg.yaml file

    Returns:
        Domain instance with all workflows and concepts loaded

    Raises:
        ValueError: If domain structure is invalid
    """
    config = load_config(domain_path)

    # Check if this is a domain file
    if "domain" not in config:
        # Fall back to single workflow (backward compatibility)
        raise ValueError(
            f"File '{domain_path}' is not a domain file. "
            "Domain files must have a 'domain:' section. "
            "For single workflows, use workflow_loader.load_workflow() instead."
        )

    domain_config = config["domain"]

    # Create domain
    domain = Domain(
        name=domain_config.get("name", "unnamed_domain"),
        version=domain_config.get("version", "1.0"),
        description=domain_config.get("description", "")
    )

    # Set main workflow if specified
    if "main_workflow" in domain_config:
        domain.main_workflow = domain_config["main_workflow"]

    # Load concepts
    concepts_dict = config.get("concepts", {})
    for concept_name, concept_def in concepts_dict.items():
        domain.add_concept(concept_name, concept_def)

    # Load all concepts into registry
    domain.load_concepts()

    # Load workflows
    workflows_dict = config.get("workflows", {})
    if not workflows_dict:
        raise ValueError(
            f"Domain '{domain.name}' has no workflows. "
            "Add a 'workflows:' section with at least one workflow."
        )

    for workflow_name, workflow_config in workflows_dict.items():
        is_main = (workflow_name == domain.main_workflow)
        domain.add_workflow(workflow_name, workflow_config, is_main=is_main)

    return domain


def create_graph_from_domain(domain: Domain, workflow_name: str = None):
    """
    Create a Graph from a domain workflow.

    Args:
        domain: Domain instance
        workflow_name: Name of workflow to create, or None for main

    Returns:
        Graph ready to run

    Raises:
        ValueError: If workflow not found
    """
    from kaygraph import Graph

    # Get workflow config
    workflow_config = domain.get_workflow(workflow_name)

    # Extract steps
    steps = workflow_config.get("steps", [])
    if not steps:
        wf_name = workflow_name or domain.main_workflow
        raise ValueError(
            f"Workflow '{wf_name}' in domain '{domain.name}' "
            f"must have at least one step"
        )

    # Create nodes from steps
    nodes = []
    for i, step in enumerate(steps):
        try:
            node = create_config_node_from_step(step)
            nodes.append(node)
        except Exception as e:
            wf_name = workflow_name or domain.main_workflow
            raise ValueError(
                f"Error creating node for step {i} "
                f"in workflow '{wf_name}': {e}"
            ) from e

    # Create graph with linear sequence
    # Start with first node
    graph = Graph(start=nodes[0])

    # Connect nodes in sequence
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]

    return graph


if __name__ == "__main__":
    # Example: Load and inspect a domain
    import sys

    if len(sys.argv) < 2:
        print("Usage: python domain.py <domain.kg.yaml>")
        print("\nExample domain structure:")
        print(load_domain.__doc__)
        sys.exit(1)

    domain_path = sys.argv[1]
    print(f"Loading domain from: {domain_path}")

    try:
        domain = load_domain(domain_path)

        print(f"\n✓ Domain loaded successfully!")
        print(f"  Name: {domain.name}")
        print(f"  Version: {domain.version}")
        print(f"  Description: {domain.description}")
        print(f"  Main workflow: {domain.main_workflow}")
        print(f"\n  Concepts ({len(domain.concepts)}):")
        for concept_name in domain.concepts.keys():
            print(f"    - {concept_name}")
        print(f"\n  Workflows ({len(domain.workflows)}):")
        for workflow_name in domain.workflows.keys():
            is_main = " (main)" if workflow_name == domain.main_workflow else ""
            print(f"    - {workflow_name}{is_main}")

    except Exception as e:
        print(f"\n✗ Error loading domain: {e}")
        sys.exit(1)
