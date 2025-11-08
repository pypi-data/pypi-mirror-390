# Implementation Plan: Remaining 5 Patterns

**Task ID**: remaining-six-patterns
**Date**: 2025-11-01
**Estimated Time**: 5-6 hours

---

## Decisions Made

1. **CLI Name**: `kgraph`
2. **File Pattern**: `.kg.yaml`
3. **Expression Routing**: Use current implementation (already done)
4. **Domain Organization**: Single-file workflows
5. **Semantic Typing**: Skip (not implementing)

---

## Overview

Implement 5 remaining patterns to complete LLM-friendly workflow system:

1. ✅ **CLI + Validation Command** (1 hour) - HIGH priority
2. ✅ **Document Expression Routing** (30 min) - Already works
3. ✅ **Batch-in-Sequence** (1 hour) - Cleaner syntax
4. ✅ **Domain Organization** (2 hours) - Single-file workflows
5. ✅ **Auto-Discovery** (1 hour) - Scan for `.kg.yaml` files

**Total New Code**: ~450 lines
**Total Time**: 5.5 hours

---

## Pattern 1: CLI + Validation Command

### Goal
Create `kgraph` command-line tool for validating and running workflows.

### Commands to Implement

```bash
kgraph validate workflow.kg.yaml
kgraph run workflow.kg.yaml
kgraph list
kgraph --help
```

### Implementation Steps

#### Step 1.1: Create CLI Entry Point

**File**: `workbooks/kaygraph-declarative-workflows/cli.py`

```python
#!/usr/bin/env python3
"""
KayGraph CLI - Command-line interface for declarative workflows.

Usage:
    kgraph validate <workflow.kg.yaml>
    kgraph run <workflow.kg.yaml> [--input key=value]...
    kgraph list [--path <directory>]
    kgraph --help
"""

import sys
import argparse
from pathlib import Path
from workflow_loader import validate_workflow, print_validation_report, load_workflow


def cmd_validate(args):
    """Validate workflow file."""
    workflow_path = args.workflow

    if not Path(workflow_path).exists():
        print(f"✗ File not found: {workflow_path}")
        return 1

    print_validation_report(workflow_path)

    errors = validate_workflow(workflow_path)
    return 0 if not errors else 1


def cmd_run(args):
    """Run workflow file."""
    workflow_path = args.workflow

    # Validate first
    errors = validate_workflow(workflow_path)
    if errors:
        print("✗ Validation failed. Fix errors before running:")
        for error in errors:
            print(f"  - {error}")
        return 1

    # Load workflow
    graph = load_workflow(workflow_path)

    # Build shared state from inputs
    shared = {}
    if args.input:
        for input_pair in args.input:
            key, value = input_pair.split('=', 1)
            shared[key] = value

    # Run workflow
    print(f"Running workflow: {workflow_path}")
    result = graph.run(shared)

    # Print results
    print("\n✓ Workflow completed")
    if "__results__" in shared:
        print("\nResults:")
        for name, value in shared["__results__"].items():
            print(f"  {name}: {value}")

    return 0


def cmd_list(args):
    """List all workflows in directory."""
    search_path = Path(args.path) if args.path else Path.cwd()

    # Find all .kg.yaml files
    workflows = list(search_path.rglob("*.kg.yaml"))

    if not workflows:
        print(f"No workflows found in {search_path}")
        return 0

    print(f"Found {len(workflows)} workflow(s):\n")
    for workflow in sorted(workflows):
        rel_path = workflow.relative_to(search_path)
        print(f"  - {rel_path}")

    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='kgraph',
        description='KayGraph CLI - Declarative workflow tools'
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # Validate command
    validate_parser = subparsers.add_parser(
        'validate',
        help='Validate workflow file'
    )
    validate_parser.add_argument('workflow', help='Path to workflow file')

    # Run command
    run_parser = subparsers.add_parser(
        'run',
        help='Run workflow file'
    )
    run_parser.add_argument('workflow', help='Path to workflow file')
    run_parser.add_argument(
        '--input', '-i',
        action='append',
        help='Input key=value pairs'
    )

    # List command
    list_parser = subparsers.add_parser(
        'list',
        help='List all workflows'
    )
    list_parser.add_argument(
        '--path', '-p',
        help='Directory to search (default: current)'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Route to command handlers
    if args.command == 'validate':
        return cmd_validate(args)
    elif args.command == 'run':
        return cmd_run(args)
    elif args.command == 'list':
        return cmd_list(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
```

**Estimated**: 150 lines

#### Step 1.2: Create Entry Point Script

**File**: `setup.py` or `pyproject.toml` update

Add console script entry point:
```python
entry_points={
    'console_scripts': [
        'kgraph=workbooks.kaygraph_declarative_workflows.cli:main',
    ],
}
```

**Estimated**: 10 lines

#### Step 1.3: Make CLI Executable

```bash
chmod +x workbooks/kaygraph-declarative-workflows/cli.py
```

---

## Pattern 2: Document Expression Routing

### Goal
Verify current implementation works and document it.

### Current Implementation

**File**: `nodes.py:296-321` - Safe expression parser exists

**Supports**:
- Operators: `==, !=, <, >, <=, >=`
- Logic: `and, or`
- Types: numbers, strings, booleans

### Implementation Steps

#### Step 2.1: Test Current Implementation

Create test case in `test_new_patterns.py`:

```python
def test_expression_routing():
    """Test expression-based conditional routing."""
    config = {
        "type": "condition",
        "expression": "score > 0.8 and verified == true"
    }

    node = ConfigNode(config)

    # Test with different contexts
    context1 = {"score": 0.9, "verified": True}
    result1 = node._evaluate_comparison("score > 0.8", context1)
    assert result1 == True

    context2 = {"score": 0.7, "verified": True}
    result2 = node._evaluate_comparison("score > 0.8", context2)
    assert result2 == False
```

**Estimated**: 30 lines

#### Step 2.2: Add Example Workflow

**File**: `configs/expression_routing_example.kg.yaml`

```yaml
workflow:
  name: conditional_routing
  description: "Route based on conditions"

  steps:
    - node: analyze
      type: llm
      prompt: "Analyze this: {{text}}"
      result: analysis

    - node: route_by_score
      type: condition
      inputs: [analysis]
      expression: "score > 0.8"
      result: routing_decision

    # High score path
    - node: premium_handler
      type: transform
      inputs: [analysis]
      condition: "routing_decision == true"
      result: premium_result

    # Low score path
    - node: standard_handler
      type: transform
      inputs: [analysis]
      condition: "routing_decision == false"
      result: standard_result
```

**Estimated**: 40 lines

#### Step 2.3: Update Documentation

Add section to `LLM_INTEGRATION_GUIDE.md` showing expression routing.

**Estimated**: 50 lines

---

## Pattern 3: Batch-in-Sequence

### Goal
Allow inline batch operations with `batch_over` syntax.

### Implementation Steps

#### Step 3.1: Extend workflow_loader

**File**: `workflow_loader.py`

Modify `create_config_node_from_step()`:

```python
def create_config_node_from_step(step_config: Dict[str, Any]):
    """Create ConfigNode from step configuration."""
    # ... existing code ...

    # Check for batch operation
    batch_over = step_config.get("batch_over")
    batch_as = step_config.get("batch_as", "item")

    if batch_over:
        # Wrap in batch node
        from nodes_advanced import ConfigurableBatchNode

        inner_node = ConfigNode(
            config=node_config,
            node_id=node_id,
            result_name=result_name,
            input_names=input_names,
            output_concept=output_concept
        )

        # Create batch wrapper
        return ConfigurableBatchNode(
            wrapped_node=inner_node,
            batch_source=batch_over,
            batch_item_name=batch_as,
            node_id=f"{node_id}_batch"
        )

    # Normal node
    return ConfigNode(...)
```

**Estimated**: 40 lines modification

#### Step 3.2: Create ConfigurableBatchNode

**File**: `nodes_advanced.py`

Add if doesn't exist:

```python
class ConfigurableBatchNode(Node):
    """Batch node that wraps another node for batch processing."""

    def __init__(self, wrapped_node, batch_source, batch_item_name="item", **kwargs):
        super().__init__(**kwargs)
        self.wrapped_node = wrapped_node
        self.batch_source = batch_source
        self.batch_item_name = batch_item_name

    def prep(self, shared):
        # Get items to batch over
        if self.batch_source in shared.get("__results__", {}):
            items = shared["__results__"][self.batch_source]
        else:
            items = shared.get(self.batch_source, [])

        return {"items": items, "shared": shared}

    def exec(self, prep_res):
        items = prep_res["items"]
        shared = prep_res["shared"]
        results = []

        for item in items:
            # Create item-specific shared store
            item_shared = shared.copy()
            item_shared[self.batch_item_name] = item

            # Run wrapped node
            prep = self.wrapped_node.prep(item_shared)
            exec_res = self.wrapped_node.exec(prep)
            self.wrapped_node.post(item_shared, prep, exec_res)

            results.append(exec_res)

        return results

    def post(self, shared, prep_res, exec_res):
        # Store batch results
        if self.wrapped_node.result_name:
            if "__results__" not in shared:
                shared["__results__"] = {}
            shared["__results__"][self.wrapped_node.result_name] = exec_res

        return "default"
```

**Estimated**: 60 lines

#### Step 3.3: Example Workflow

**File**: `configs/batch_example.kg.yaml`

```yaml
workflow:
  name: batch_processing
  description: "Process multiple items with batch_over syntax"

  steps:
    - node: fetch_items
      type: extract
      field: items
      result: raw_items

    - node: process_item
      type: llm
      batch_over: raw_items     # Batch this step
      batch_as: item            # Variable name for each item
      prompt: "Process this item: {{item}}"
      result: processed_items   # Array of results
```

**Estimated**: 25 lines

---

## Pattern 4: Domain Organization

### Goal
Single-file workflows with domain metadata.

### YAML Structure

```yaml
domain:
  name: invoice_processing
  version: 1.0.0
  description: "Complete invoice processing workflow"
  author: "Your Team"
  main_workflow: process_invoice

concepts:
  Invoice: ...
  LineItem: ...

workflows:
  process_invoice:
    description: "Main processing workflow"
    steps: [...]

  extract_invoice:
    description: "Extract invoice data"
    steps: [...]
```

### Implementation Steps

#### Step 4.1: Create Domain Class

**File**: `domain.py`

```python
"""Domain management for KayGraph workflows."""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class DomainMetadata:
    """Metadata for a workflow domain."""
    name: str
    version: str
    description: str
    main_workflow: str
    author: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DomainMetadata':
        return cls(
            name=data.get("name", "unnamed"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            main_workflow=data.get("main_workflow"),
            author=data.get("author")
        )


class Domain:
    """Represents a workflow domain with concepts and workflows."""

    def __init__(self, metadata: DomainMetadata):
        self.metadata = metadata
        self.concepts = {}
        self.workflows = {}

    def add_concept(self, name: str, concept):
        """Add a concept to the domain."""
        self.concepts[name] = concept

    def add_workflow(self, name: str, workflow):
        """Add a workflow to the domain."""
        self.workflows[name] = workflow

    def get_main_workflow(self):
        """Get the main workflow for this domain."""
        if self.metadata.main_workflow not in self.workflows:
            raise ValueError(
                f"Main workflow '{self.metadata.main_workflow}' not found"
            )
        return self.workflows[self.metadata.main_workflow]


def load_domain(domain_path: str) -> Domain:
    """Load a domain from a .kg.yaml file."""
    from workflow_loader import load_config
    from utils.concepts import Concept, get_concept_registry

    config = load_config(domain_path)

    # Load domain metadata
    domain_dict = config.get("domain", {})
    metadata = DomainMetadata.from_dict(domain_dict)

    domain = Domain(metadata)

    # Load concepts
    concepts_dict = config.get("concepts", {})
    registry = get_concept_registry()

    for name, definition in concepts_dict.items():
        concept = Concept.from_yaml_dict(name, definition)
        domain.add_concept(name, concept)
        registry.register(name, concept)

    # Load workflows
    workflows_dict = config.get("workflows", {})
    for name, workflow_def in workflows_dict.items():
        # Convert workflow def to loadable format
        workflow_config = {
            "workflow": workflow_def
        }
        # Store workflow config (will be loaded on demand)
        domain.add_workflow(name, workflow_config)

    return domain
```

**Estimated**: 100 lines

#### Step 4.2: Update workflow_loader

**File**: `workflow_loader.py`

Add domain support:

```python
def load_workflow(workflow_path: str, workflow_name: Optional[str] = None):
    """Load workflow from file.

    Args:
        workflow_path: Path to .kg.yaml file
        workflow_name: Optional workflow name if file contains multiple

    Returns:
        Graph ready to run
    """
    config = load_config(workflow_path)

    # Check if this is a domain file
    if "domain" in config and "workflows" in config:
        from domain import load_domain
        domain = load_domain(workflow_path)

        # Get specific workflow or main workflow
        if workflow_name:
            workflow_config = domain.workflows.get(workflow_name)
        else:
            workflow_config = domain.get_main_workflow()

        # Extract workflow section
        workflow_config = workflow_config.get("workflow", workflow_config)
    else:
        # Single workflow file
        workflow_config = config.get("workflow", {})

    # ... rest of loading logic ...
```

**Estimated**: 50 lines modification

#### Step 4.3: Update CLI for Domains

**File**: `cli.py`

Update `cmd_run` to support workflow selection:

```bash
kgraph run domain.kg.yaml
kgraph run domain.kg.yaml --workflow extract_invoice
```

**Estimated**: 20 lines

#### Step 4.4: Example Domain File

**File**: `configs/invoice_domain.kg.yaml`

```yaml
domain:
  name: invoice_processing
  version: 1.0.0
  description: "Complete invoice processing workflows"
  author: "Finance Team"
  main_workflow: process_invoice

concepts:
  Invoice:
    description: "Commercial invoice"
    structure:
      invoice_number: {type: text, required: true}
      total: {type: number, required: true, min_value: 0}

  ValidationResult:
    description: "Validation outcome"
    structure:
      valid: {type: bool, required: true}
      errors: {type: text}

workflows:
  process_invoice:
    description: "Main invoice processing workflow"
    steps:
      - node: extract
        type: extract
        field: pdf_file
        result: raw_data

      - node: parse
        type: llm
        inputs: [raw_data]
        prompt: "Extract invoice: {{raw_data}}"
        output_concept: Invoice
        result: invoice

      - node: validate
        type: validate
        inputs: [invoice]
        concept: Invoice
        result: validation

  extract_invoice:
    description: "Extract invoice data only"
    steps:
      - node: parse
        type: llm
        prompt: "Extract invoice from: {{text}}"
        output_concept: Invoice
        result: invoice
```

**Estimated**: 60 lines

---

## Pattern 5: Auto-Discovery

### Goal
Automatically find and list `.kg.yaml` files.

### Implementation Steps

#### Step 5.1: Add Discovery Function

**File**: `cli.py`

Already implemented in `cmd_list()`, just need to enhance:

```python
def discover_workflows(search_path: Path, exclude_dirs=None):
    """Discover all .kg.yaml files.

    Args:
        search_path: Directory to search
        exclude_dirs: Directories to skip (node_modules, .git, etc.)

    Returns:
        List of workflow file paths
    """
    if exclude_dirs is None:
        exclude_dirs = {
            'node_modules', '.git', 'venv', '.venv',
            '__pycache__', '.pytest_cache', 'dist', 'build'
        }

    workflows = []

    for kg_file in search_path.rglob("*.kg.yaml"):
        # Skip excluded directories
        if any(excluded in kg_file.parts for excluded in exclude_dirs):
            continue

        workflows.append(kg_file)

    return sorted(workflows)
```

**Estimated**: 30 lines

#### Step 5.2: Enhanced List Command

Update `cmd_list()` to show domain info:

```python
def cmd_list(args):
    """List all workflows with metadata."""
    search_path = Path(args.path) if args.path else Path.cwd()

    workflows = discover_workflows(search_path)

    if not workflows:
        print(f"No workflows found in {search_path}")
        return 0

    print(f"Found {len(workflows)} workflow(s):\n")

    for workflow in workflows:
        rel_path = workflow.relative_to(search_path)
        print(f"  📄 {rel_path}")

        # Try to load domain metadata
        try:
            config = load_config(str(workflow))
            if "domain" in config:
                domain_info = config["domain"]
                print(f"     Domain: {domain_info.get('name')}")
                print(f"     Version: {domain_info.get('version')}")
                print(f"     Workflows: {len(config.get('workflows', {}))}")
        except:
            pass

        print()

    return 0
```

**Estimated**: 40 lines

---

## Testing Strategy

### Test Files to Create

1. **test_cli.py** - Test CLI commands
2. **test_batch_syntax.py** - Test batch_over syntax
3. **test_domain.py** - Test domain loading
4. **test_discovery.py** - Test auto-discovery

### Example Test Structure

```python
def test_cli_validate():
    """Test kgraph validate command."""
    result = subprocess.run(
        ["python", "cli.py", "validate", "configs/test.kg.yaml"],
        capture_output=True
    )
    assert result.returncode == 0

def test_batch_over_syntax():
    """Test batch_over creates batch node."""
    step = {
        "node": "process",
        "type": "llm",
        "batch_over": "items",
        "batch_as": "item"
    }

    node = create_config_node_from_step(step)
    assert isinstance(node, ConfigurableBatchNode)

def test_domain_loading():
    """Test domain file loading."""
    domain = load_domain("configs/invoice_domain.kg.yaml")
    assert domain.metadata.name == "invoice_processing"
    assert "Invoice" in domain.concepts
    assert "process_invoice" in domain.workflows
```

---

## Documentation Updates

### Files to Update

1. **README.md** - Add CLI usage section
2. **LLM_INTEGRATION_GUIDE.md** - Add all 5 patterns
3. **IMPLEMENTATION_NOTES.md** - Mark patterns as complete

### Example Documentation Additions

```markdown
## Using the CLI

Install and use the kgraph command:

\`\`\`bash
# Validate workflow
kgraph validate my_workflow.kg.yaml

# Run workflow
kgraph run my_workflow.kg.yaml --input text="Hello world"

# List all workflows
kgraph list

# Run specific workflow from domain
kgraph run domain.kg.yaml --workflow extract_invoice
\`\`\`
```

---

## Implementation Checklist

### Pattern 1: CLI (1 hour)
- [ ] Create `cli.py` with argparse
- [ ] Add `validate` command
- [ ] Add `run` command
- [ ] Add `list` command
- [ ] Make executable
- [ ] Test all commands

### Pattern 2: Expression Routing (30 min)
- [ ] Test current implementation
- [ ] Create example workflow
- [ ] Update documentation

### Pattern 3: Batch-in-Sequence (1 hour)
- [ ] Modify `create_config_node_from_step()`
- [ ] Create/verify `ConfigurableBatchNode`
- [ ] Create example workflow
- [ ] Test batch_over syntax

### Pattern 4: Domain Organization (2 hours)
- [ ] Create `domain.py` with Domain class
- [ ] Update `workflow_loader.py` for domains
- [ ] Update CLI for workflow selection
- [ ] Create example domain file
- [ ] Test domain loading

### Pattern 5: Auto-Discovery (1 hour)
- [ ] Add `discover_workflows()` function
- [ ] Enhance `cmd_list()` with metadata
- [ ] Add exclude directories
- [ ] Test discovery

### Testing (1 hour)
- [ ] Write CLI tests
- [ ] Write batch syntax tests
- [ ] Write domain tests
- [ ] Write discovery tests
- [ ] Run all tests

### Documentation (30 min)
- [ ] Update README with CLI usage
- [ ] Update LLM_INTEGRATION_GUIDE
- [ ] Update IMPLEMENTATION_NOTES
- [ ] Add examples for all patterns

---

## Estimated Code Impact

| Pattern | New Lines | Modified Lines | Files |
|---------|-----------|----------------|-------|
| CLI + Validation | 150 | 20 | 1 new |
| Expression Routing | 70 | 50 | 2 modified |
| Batch-in-Sequence | 85 | 40 | 2 modified |
| Domain Organization | 160 | 50 | 1 new, 2 modified |
| Auto-Discovery | 70 | 40 | 1 modified |
| **Total** | **535** | **200** | **2 new, 4 modified** |

---

## Success Criteria

✅ `kgraph validate` catches all workflow errors
✅ `kgraph run` executes workflows successfully
✅ `kgraph list` finds all `.kg.yaml` files
✅ `batch_over` syntax works for inline batching
✅ Domain files with multiple workflows load correctly
✅ Expression routing documented with examples
✅ All patterns tested and working
✅ Documentation updated for all features

**Result**: 7 of 8 patterns complete (87.5% - skipping Semantic Typing)
