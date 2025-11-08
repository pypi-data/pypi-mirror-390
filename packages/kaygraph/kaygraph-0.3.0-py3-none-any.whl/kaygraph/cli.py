#!/usr/bin/env python3
"""
KayGraph CLI - Command-line interface for declarative workflows.

Usage:
    kaygraph validate <workflow.kg.yaml>
    kaygraph run <workflow.kg.yaml> [--input key=value]...
    kaygraph list [--path <directory>]
"""

import sys
import argparse
from pathlib import Path
from typing import Dict, Any


def cmd_validate(args) -> int:
    """Validate workflow file."""
    from kaygraph import validate_workflow

    workflow_path = args.workflow

    if not Path(workflow_path).exists():
        print(f"✗ File not found: {workflow_path}")
        return 1

    print(f"\nValidating workflow: {workflow_path}")
    print("=" * 60)

    errors = validate_workflow(workflow_path)

    if not errors:
        print("✓ Workflow is valid")
        print("✓ All node references are satisfied")
        print("✓ Graph syntax is correct")
        print("\nReady to run!")
        print("=" * 60)
        return 0
    else:
        print(f"✗ Found {len(errors)} error(s):\n")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error}")
        print("\nPlease fix these errors before running.")
        print("=" * 60)
        return 1


def cmd_run(args) -> int:
    """Run workflow file."""
    from kaygraph import load_workflow

    workflow_path = args.workflow

    if not Path(workflow_path).exists():
        print(f"✗ File not found: {workflow_path}")
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
        print(f"Loading workflow from {workflow_path}...")
        workflow = load_workflow(workflow_path)

        print("Running workflow...")
        result = workflow.run(shared)

        print("\n" + "=" * 60)
        print("✓ Workflow completed successfully!")
        print("=" * 60)

        # Print shared state
        if shared:
            print("\nFinal state:")
            for key, value in shared.items():
                # Skip internal keys
                if not key.startswith('_'):
                    print(f"  {key}: {value}")

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

        # Try to extract workflow info
        try:
            from kaygraph.workflow_loader import load_yaml_file
            config = load_yaml_file(str(workflow))

            if "workflows" in config:
                workflow_names = list(config["workflows"].keys())
                print(f"    Workflows: {', '.join(workflow_names)}")

            if "domain" in config:
                domain_name = config["domain"].get("name", "unknown")
                print(f"    Domain: {domain_name}")

        except Exception as e:
            print(f"    (Could not parse: {e})")

        print()

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='kaygraph',
        description='KayGraph CLI - Declarative workflow tool for graph operations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kaygraph validate my_workflow.kg.yaml
  kaygraph run my_workflow.kg.yaml --input name="Alice"
  kaygraph list --path ./workflows

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
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
