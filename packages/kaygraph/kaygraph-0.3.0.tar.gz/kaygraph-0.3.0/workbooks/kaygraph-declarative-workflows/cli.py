#!/usr/bin/env python3
"""
KayGraph CLI - Command-line interface for declarative workflows.

Usage:
    kgraph validate <workflow.kg.yaml>
    kgraph run <workflow.kg.yaml> [--input key=value]...
    kgraph list [--path <directory>]
    kgraph export <workflow.kg.yaml> [--output path] [--format yaml|json]
    kgraph --help
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any
from workflow_loader import validate_workflow, print_validation_report, load_workflow


def cmd_validate(args) -> int:
    """Validate workflow file."""
    workflow_path = args.workflow

    if not Path(workflow_path).exists():
        print(f"✗ File not found: {workflow_path}")
        return 1

    print_validation_report(workflow_path)

    errors = validate_workflow(workflow_path)
    return 0 if not errors else 1


def cmd_run(args) -> int:
    """Run workflow file or domain workflow."""
    workflow_spec = args.workflow

    # Parse workflow specification
    # Format: path/to/file.kg.yaml[:workflow_name]
    if ':' in workflow_spec:
        workflow_path, workflow_name = workflow_spec.rsplit(':', 1)
    else:
        workflow_path = workflow_spec
        workflow_name = None

    # Check if it's a domain file
    from utils.config_loader import load_config
    from domain import load_domain, create_graph_from_domain

    try:
        config = load_config(workflow_path)
        is_domain = "domain" in config
    except Exception as e:
        print(f"✗ Error loading file: {e}")
        return 1

    # Parse input arguments
    shared = {}
    if args.input:
        for input_arg in args.input:
            if '=' not in input_arg:
                print(f"✗ Invalid input format: {input_arg}")
                print("  Expected format: key=value")
                return 1

            key, value = input_arg.split('=', 1)
            # Try to parse as number or boolean
            if value.lower() == 'true':
                shared[key] = True
            elif value.lower() == 'false':
                shared[key] = False
            elif value.replace('.', '').replace('-', '').isdigit():
                shared[key] = float(value) if '.' in value else int(value)
            else:
                shared[key] = value

    # Load and run workflow
    try:
        if is_domain:
            # Domain file
            domain = load_domain(workflow_path)

            # Determine which workflow to run
            if workflow_name:
                print(f"Running workflow '{workflow_name}' from domain '{domain.name}'...")
            else:
                workflow_name = domain.main_workflow
                print(f"Running main workflow '{workflow_name}' from domain '{domain.name}'...")

            graph = create_graph_from_domain(domain, workflow_name)
        else:
            # Single workflow file
            if workflow_name:
                print(f"✗ Workflow name specified but '{workflow_path}' is not a domain file")
                return 1

            print(f"Running workflow from {workflow_path}...")

            # Validate first
            errors = validate_workflow(workflow_path)
            if errors:
                print("✗ Validation failed:")
                for error in errors:
                    print(f"  - {error}")
                return 1

            graph = load_workflow(workflow_path)

        # Run the graph
        result = graph.run(shared)

        print("\n" + "=" * 60)
        print("Workflow completed successfully!")
        print("=" * 60)

        # Print results if any
        if "__results__" in shared:
            print("\nNamed Results:")
            for name, value in shared["__results__"].items():
                print(f"  {name}: {value}")

        return 0

    except Exception as e:
        print(f"\n✗ Workflow execution failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_list(args) -> int:
    """List all discovered workflow files."""
    search_path = Path(args.path) if args.path else Path.cwd()

    if not search_path.exists():
        print(f"✗ Path not found: {search_path}")
        return 1

    print(f"Searching for .kg.yaml files in: {search_path}")
    print("=" * 60)

    # Search for .kg.yaml files
    workflows = list(search_path.rglob("*.kg.yaml"))

    # Exclude common directories
    exclude_dirs = {'node_modules', '.git', 'venv', '__pycache__', '.pytest_cache', 'dist', 'build'}
    workflows = [
        w for w in workflows
        if not any(part in exclude_dirs for part in w.parts)
    ]

    if not workflows:
        print("No .kg.yaml files found")
        return 1

    print(f"Found {len(workflows)} workflow(s):\n")

    for workflow in sorted(workflows):
        rel_path = workflow.relative_to(search_path)
        print(f"  {rel_path}")

        # Try to extract workflow name from file
        try:
            from workflow_loader import load_config
            config = load_config(str(workflow))

            # Check if it's a domain file with multiple workflows
            if "domain" in config:
                domain_name = config["domain"].get("name", "unknown")
                print(f"    Domain: {domain_name}")
                if "workflows" in config:
                    workflow_names = list(config["workflows"].keys())
                    print(f"    Workflows: {', '.join(workflow_names)}")
            elif "workflow" in config:
                print(f"    Type: Single workflow")

        except Exception as e:
            print(f"    (Could not parse: {e})")

        print()

    return 0


def cmd_export(args) -> int:
    """Export workflow to various formats."""
    workflow_path = args.workflow

    if not Path(workflow_path).exists():
        print(f"✗ File not found: {workflow_path}")
        return 1

    output_format = args.format or 'yaml'
    output_path = args.output

    # Load workflow/domain
    try:
        from utils.config_loader import load_config
        from domain import load_domain
        import json

        config = load_config(workflow_path)
        is_domain = "domain" in config

        if is_domain:
            # Load as domain and export
            domain = load_domain(workflow_path)

            if output_format == 'yaml':
                # Export with metadata
                yaml_content = domain.to_yaml(include_metadata=True)

                if output_path:
                    Path(output_path).write_text(yaml_content, encoding='utf-8')
                    print(f"✓ Exported to: {output_path}")
                else:
                    print(yaml_content)

            elif output_format == 'json':
                # Export as JSON
                domain_dict = domain.to_dict()
                json_content = json.dumps(domain_dict, indent=2)

                if output_path:
                    Path(output_path).write_text(json_content, encoding='utf-8')
                    print(f"✓ Exported to: {output_path}")
                else:
                    print(json_content)

            else:
                print(f"✗ Unsupported format: {output_format}")
                print("  Supported formats: yaml, json")
                return 1

        else:
            # Single workflow file - just copy with metadata
            import yaml

            if output_format == 'yaml':
                # Add metadata wrapper if not present
                if "metadata" not in config:
                    config = {
                        "metadata": {
                            "title": Path(workflow_path).stem.replace("_", " ").title(),
                            "version": "1.0.0",
                            "deployment": {
                                "cli": {"enabled": True},
                                "api": {"enabled": False}
                            }
                        },
                        **config
                    }

                yaml_content = yaml.dump(config, default_flow_style=False, sort_keys=False)

                if output_path:
                    Path(output_path).write_text(yaml_content, encoding='utf-8')
                    print(f"✓ Exported to: {output_path}")
                else:
                    print(yaml_content)

            elif output_format == 'json':
                json_content = json.dumps(config, indent=2)

                if output_path:
                    Path(output_path).write_text(json_content, encoding='utf-8')
                    print(f"✓ Exported to: {output_path}")
                else:
                    print(json_content)

        return 0

    except Exception as e:
        print(f"✗ Export failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='kgraph',
        description='KayGraph CLI - Declarative workflow tool for LLM-friendly graph operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kgraph validate my_workflow.kg.yaml
  kgraph run my_workflow.kg.yaml --input document="data.txt"
  kgraph list --path ./workflows
  kgraph export my_workflow.kg.yaml --output exported.kg.yaml
  kgraph export my_workflow.kg.yaml --format json --output workflow.json

For more information: https://github.com/yourusername/kaygraph
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a workflow file')
    validate_parser.add_argument('workflow', help='Path to workflow file (.kg.yaml)')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run a workflow file')
    run_parser.add_argument('workflow', help='Path to workflow file (.kg.yaml)')
    run_parser.add_argument('--input', '-i', action='append',
                          help='Input values as key=value pairs (can be used multiple times)')

    # List command
    list_parser = subparsers.add_parser('list', help='List all workflow files')
    list_parser.add_argument('--path', '-p', help='Directory to search (default: current directory)')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export workflow to various formats')
    export_parser.add_argument('workflow', help='Path to workflow file (.kg.yaml)')
    export_parser.add_argument('--output', '-o', help='Output file path (prints to stdout if not specified)')
    export_parser.add_argument('--format', '-f', choices=['yaml', 'json'], default='yaml',
                               help='Output format (default: yaml)')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'run':
        return cmd_run(args)
    elif args.command == 'list':
        return cmd_list(args)
    elif args.command == 'export':
        return cmd_export(args)
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
