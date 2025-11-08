"""
Workflow loader for declarative YAML workflows.

Enables loading complete workflows from YAML/TOML files with named
intermediate results and validation.
"""

from typing import Dict, Any, List
from pathlib import Path
from kaygraph import Graph
from nodes import ConfigNode
from utils.config_loader import load_config


def create_config_node_from_step(step_config: Dict[str, Any]) -> ConfigNode:
    """Create ConfigNode from step configuration.

    Args:
        step_config: Dict with keys:
            - node: Node type or name
            - type: Node type (llm, extract, transform, etc.)
            - result: Optional output name
            - inputs: Optional list of input names
            - output_concept: Optional concept for validation
            ... other config

    Returns:
        ConfigNode instance

    Example:
        step_config = {
            "node": "extract_text",
            "type": "extract",
            "field": "document",
            "result": "raw_text"
        }
    """
    node_id = step_config.get("node", "unnamed_node")
    result_name = step_config.get("result")
    input_names = step_config.get("inputs", [])
    output_concept = step_config.get("output_concept")
    batch_over = step_config.get("batch_over")
    batch_as = step_config.get("batch_as")

    # Extract node config (everything except metadata fields)
    metadata_fields = {"node", "result", "inputs", "output_concept", "batch_over", "batch_as", "parallels"}
    node_config = {k: v for k, v in step_config.items() if k not in metadata_fields}

    # Ensure 'type' is in config
    if "type" not in node_config:
        raise ValueError(f"Step '{node_id}' missing required 'type' field")

    # Check for parallel execution
    parallels = step_config.get("parallels")
    if parallels:
        # Create parallel node wrapper
        from nodes import ParallelConfigNode

        return ParallelConfigNode(
            parallels=parallels,
            config=node_config,
            node_id=node_id,
            result_name=result_name,
            input_names=input_names,
            output_concept=output_concept
        )

    # Check if batch processing requested
    if batch_over:
        # Create batch node wrapper
        from nodes import BatchConfigNode

        # Determine batch variable name
        if not batch_as:
            # Default: remove 's' from batch_over (e.g., items -> item)
            batch_as = batch_over.rstrip('s') if batch_over.endswith('s') else batch_over

        return BatchConfigNode(
            config=node_config,
            node_id=node_id,
            result_name=result_name,
            input_names=input_names,
            output_concept=output_concept,
            batch_over=batch_over,
            batch_as=batch_as
        )

    return ConfigNode(
        config=node_config,
        node_id=node_id,
        result_name=result_name,
        input_names=input_names,
        output_concept=output_concept
    )


def load_workflow(workflow_path: str) -> Graph:
    """Load workflow from YAML/TOML file.

    Expected structure:
        workflow:
          name: my_workflow
          description: "What this workflow does"
          steps:
            - node: extract_text
              type: extract
              field: document
              result: raw_text

            - node: analyze
              type: llm
              inputs: [raw_text]
              prompt: "Analyze: {{raw_text}}"
              result: analysis

    Args:
        workflow_path: Path to YAML/TOML workflow file

    Returns:
        Graph ready to run

    Raises:
        ValueError: If workflow structure is invalid
    """
    config = load_config(workflow_path)

    # Load concepts if defined
    concepts_dict = config.get("concepts", {})
    if concepts_dict:
        from utils.concepts import get_concept_registry
        registry = get_concept_registry()
        registry.load_from_yaml(concepts_dict)

    # Extract workflow section
    workflow_config = config.get("workflow", {})
    if not workflow_config:
        raise ValueError(
            f"Workflow file '{workflow_path}' missing 'workflow' section"
        )

    steps = workflow_config.get("steps", [])
    if not steps:
        raise ValueError(
            f"Workflow '{workflow_config.get('name', 'unnamed')}' "
            f"must have at least one step"
        )

    # Create nodes from steps
    nodes = []
    for i, step in enumerate(steps):
        try:
            node = create_config_node_from_step(step)
            nodes.append(node)
        except Exception as e:
            raise ValueError(
                f"Error creating node for step {i} "
                f"({step.get('node', 'unnamed')}): {e}"
            )

    # Build graph - chain nodes sequentially
    graph = Graph(nodes[0])
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]

    return graph


def validate_workflow(workflow_path: str) -> List[str]:
    """Validate workflow for common errors before execution.

    Checks:
    - All referenced inputs are produced by previous steps
    - No duplicate result names
    - All required fields present
    - Valid node types

    Args:
        workflow_path: Path to YAML/TOML workflow file

    Returns:
        List of error messages (empty if valid)

    Example:
        errors = validate_workflow("my_workflow.yaml")
        if errors:
            for error in errors:
                print(f"✗ {error}")
        else:
            print("✓ Workflow is valid")
    """
    errors = []

    try:
        config = load_config(workflow_path)
    except Exception as e:
        return [f"Failed to load workflow file: {e}"]

    # Check workflow structure
    workflow_config = config.get("workflow", {})
    if not workflow_config:
        errors.append("Missing 'workflow' section")
        return errors

    workflow_name = workflow_config.get("name", "unnamed")
    steps = workflow_config.get("steps", [])

    if not steps:
        errors.append(f"Workflow '{workflow_name}' has no steps")
        return errors

    # Track produced results
    available_results = set()
    valid_node_types = {"llm", "extract", "transform", "validate", "condition"}

    for i, step in enumerate(steps):
        step_name = step.get("node", f"step_{i}")
        step_type = step.get("type")

        # Check node type is present
        if not step_type:
            errors.append(
                f"Step '{step_name}': Missing required 'type' field"
            )
            continue

        # Check node type is valid
        if step_type not in valid_node_types:
            errors.append(
                f"Step '{step_name}': Invalid type '{step_type}'. "
                f"Valid types: {', '.join(valid_node_types)}"
            )

        # Check required inputs exist
        required_inputs = step.get("inputs", [])
        for input_name in required_inputs:
            if input_name not in available_results:
                errors.append(
                    f"Step '{step_name}': Required input '{input_name}' "
                    f"not produced by previous steps. "
                    f"Available: {sorted(available_results) if available_results else 'none'}"
                )

        # Check for duplicate result names
        result_name = step.get("result")
        if result_name:
            if result_name in available_results:
                errors.append(
                    f"Step '{step_name}': Result name '{result_name}' "
                    f"already used by a previous step"
                )
            available_results.add(result_name)

        # Check type-specific requirements
        if step_type == "llm" and "prompt" not in step:
            errors.append(
                f"Step '{step_name}': LLM node requires 'prompt' field"
            )

        if step_type == "extract" and "field" not in step:
            errors.append(
                f"Step '{step_name}': Extract node requires 'field' field"
            )

    return errors


def print_validation_report(workflow_path: str):
    """Print a formatted validation report.

    Args:
        workflow_path: Path to workflow file
    """
    print(f"\nValidating workflow: {workflow_path}")
    print("=" * 60)

    errors = validate_workflow(workflow_path)

    if not errors:
        print("✓ Workflow is valid")
        print("✓ All inputs are satisfied")
        print("✓ No duplicate result names")
        print("\nReady to run!")
    else:
        print(f"✗ Found {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print("\nPlease fix these errors before running.")

    print("=" * 60)
