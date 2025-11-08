# Implementation Plan: Named Results & Inline Schemas

**Task ID**: named-results-and-inline-schemas
**Date**: 2025-11-01
**Estimated Time**: 2-3 hours

---

## Overview

Implement 2 foundational patterns that make KayGraph more LLM-friendly:
1. **Named Intermediate Results** - Explicit data flow
2. **Inline Structure Definitions** - YAML schema definitions

---

## Pattern 1: Named Intermediate Results

### Design Decisions

**Q: Where to store named results?**
**A**: Store in `shared["__results__"]` to avoid collisions with user data

**Q: Validation at construction or runtime?**
**A**: Runtime - allows dynamic workflows, but provide clear errors

**Q: How to reference results?**
**A**: By name in `inputs: [result_name]` list

### Implementation Steps

#### Step 1.1: Extend ConfigNode for Named Results (nodes.py)

**Location**: `workbooks/kaygraph-declarative-workflows/nodes.py`

**Changes**:
```python
class ConfigNode(ValidatedNode):
    def __init__(self, config, node_id=None, result_name=None, input_names=None, **kwargs):
        # ... existing code ...
        self.result_name = result_name  # NEW: Output result name
        self.input_names = input_names or []  # NEW: Input dependencies

    def prep(self, shared):
        # NEW: Resolve input dependencies
        inputs = {}

        # Get inputs from named results
        if self.input_names:
            results_store = shared.get("__results__", {})
            for input_name in self.input_names:
                if input_name not in results_store:
                    raise ValueError(f"Required input '{input_name}' not found in results")
                inputs[input_name] = results_store[input_name]

        # Merge with config inputs
        config_inputs = self.config.get("inputs", {})
        for key, value in config_inputs.items():
            if isinstance(value, str) and value.startswith("@"):
                # Reference to shared store
                var_name = value[1:]
                inputs[key] = shared.get(var_name)
            else:
                inputs[key] = value

        return inputs

    def post(self, shared, prep_res, exec_res):
        # NEW: Store named result
        if self.result_name:
            if "__results__" not in shared:
                shared["__results__"] = {}
            shared["__results__"][self.result_name] = exec_res

        # ... existing post logic ...
        return action
```

**Estimated**: 30 lines

#### Step 1.2: Update ConfigNode Factory (nodes.py)

**Add helper function**:
```python
def create_config_node_from_step(step_config):
    """Create ConfigNode from step configuration.

    Args:
        step_config: Dict with keys:
            - node: Node type or name
            - result: Optional output name
            - inputs: Optional list of input names
            - ... other config

    Returns:
        ConfigNode instance
    """
    node_type = step_config.get("node")
    result_name = step_config.get("result")
    input_names = step_config.get("inputs", [])

    # Extract node config (everything except 'result' and 'inputs')
    node_config = {k: v for k, v in step_config.items()
                   if k not in ["node", "result", "inputs"]}

    return ConfigNode(
        config=node_config,
        node_id=node_type,
        result_name=result_name,
        input_names=input_names
    )
```

**Estimated**: 20 lines

#### Step 1.3: Add Workflow Loader (new file)

**Location**: `workbooks/kaygraph-declarative-workflows/workflow_loader.py`

**Purpose**: Load YAML workflows with named results

```python
"""Workflow loader for declarative YAML workflows."""
from typing import Dict, Any, List
from kaygraph import Graph, Node
from .nodes import create_config_node_from_step
from .utils.config_loader import load_config


def load_workflow(workflow_path: str) -> Graph:
    """Load workflow from YAML file.

    Expected YAML structure:
        workflow:
          name: my_workflow
          steps:
            - node: extract_text
              result: raw_text
            - node: analyze
              inputs: [raw_text]
              result: analysis

    Args:
        workflow_path: Path to YAML workflow file

    Returns:
        Graph ready to run
    """
    config = load_config(workflow_path)
    workflow_config = config.get("workflow", {})
    steps = workflow_config.get("steps", [])

    if not steps:
        raise ValueError("Workflow must have at least one step")

    # Create nodes from steps
    nodes = []
    for step in steps:
        node = create_config_node_from_step(step)
        nodes.append(node)

    # Build graph - chain nodes sequentially
    graph = Graph(nodes[0])
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]

    return graph


def validate_workflow(workflow_path: str) -> List[str]:
    """Validate workflow for common errors.

    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    config = load_config(workflow_path)
    workflow_config = config.get("workflow", {})
    steps = workflow_config.get("steps", [])

    # Track produced results
    available_results = set()

    for i, step in enumerate(steps):
        step_name = step.get("node", f"step_{i}")

        # Check required inputs exist
        required_inputs = step.get("inputs", [])
        for input_name in required_inputs:
            if input_name not in available_results:
                errors.append(
                    f"Step '{step_name}': Required input '{input_name}' "
                    f"not produced by previous steps"
                )

        # Track result production
        result_name = step.get("result")
        if result_name:
            if result_name in available_results:
                errors.append(
                    f"Step '{step_name}': Result name '{result_name}' "
                    f"already used by previous step"
                )
            available_results.add(result_name)

    return errors
```

**Estimated**: 80 lines

#### Step 1.4: Example YAML Workflow

**Location**: `workbooks/kaygraph-declarative-workflows/configs/named_results_example.yaml`

```yaml
workflow:
  name: document_analysis
  description: "Extract and analyze document with named results"

  steps:
    - node: extract_text
      type: extract
      field: document
      result: raw_text

    - node: clean_text
      type: transform
      inputs: [raw_text]
      operation: strip
      result: cleaned_text

    - node: analyze_sentiment
      type: llm
      inputs: [cleaned_text]
      prompt: "Analyze sentiment of: {{cleaned_text}}"
      model: deepseek-chat
      result: sentiment

    - node: summarize
      type: llm
      inputs: [cleaned_text, sentiment]
      prompt: |
        Text: {{cleaned_text}}
        Sentiment: {{sentiment}}

        Provide a brief summary.
      model: deepseek-chat
      result: summary
```

**Estimated**: 30 lines

---

## Pattern 2: Inline Structure Definitions

### Design Decisions

**Q: Replace Python dicts or coexist?**
**A**: Coexist - allow both YAML and Python definitions

**Q: YAML and TOML support?**
**A**: Yes - config_loader already supports both

**Q: Cross-file concept references?**
**A**: Phase 2 - start with single-file workflows

### Implementation Steps

#### Step 2.1: Extend Concept Class (utils/concepts.py)

**Add class method for YAML parsing**:

```python
class Concept:
    # ... existing code ...

    @classmethod
    def from_yaml_dict(cls, name: str, definition: Dict[str, Any]) -> 'Concept':
        """Create Concept from YAML dictionary.

        Args:
            name: Concept name
            definition: Dict with 'description' and 'structure' keys
                structure: Dict of field_name -> field_spec
                    field_spec can be:
                        - str: type name ("text", "number", etc.)
                        - dict: {type, required, min_value, etc.}

        Example YAML:
            Invoice:
              description: "Commercial invoice"
              structure:
                total:
                  type: number
                  required: true
                  min_value: 0.0
                status:
                  type: text
                  choices: ["pending", "paid"]

        Returns:
            Concept instance
        """
        description = definition.get("description", "")
        structure_def = definition.get("structure", {})

        # Convert YAML structure to internal format
        structure = {}
        for field_name, field_spec in structure_def.items():
            if isinstance(field_spec, str):
                # Simple type: "field: text"
                structure[field_name] = {"type": field_spec}
            elif isinstance(field_spec, dict):
                # Full spec: "field: {type: number, required: true}"
                structure[field_name] = field_spec
            else:
                raise ValueError(
                    f"Invalid field spec for '{field_name}': {field_spec}"
                )

        # Create concept using existing __init__
        return cls(
            name=name,
            description=description,
            structure=structure
        )
```

**Estimated**: 50 lines

#### Step 2.2: Add Concept Registry (utils/concepts.py)

**New class to manage concepts**:

```python
class ConceptRegistry:
    """Registry for managing concepts defined in workflows."""

    def __init__(self):
        self._concepts: Dict[str, Concept] = {}

    def register(self, name: str, concept: Concept):
        """Register a concept."""
        self._concepts[name] = concept

    def get(self, name: str) -> Concept:
        """Get concept by name."""
        if name not in self._concepts:
            raise ValueError(f"Concept '{name}' not defined")
        return self._concepts[name]

    def load_from_yaml(self, concepts_dict: Dict[str, Any]):
        """Load concepts from YAML dictionary.

        Args:
            concepts_dict: Dict of concept_name -> concept_definition
        """
        for name, definition in concepts_dict.items():
            concept = Concept.from_yaml_dict(name, definition)
            self.register(name, concept)

    def validate(self, concept_name: str, data: Any) -> Dict[str, Any]:
        """Validate data against concept.

        Returns:
            Validation result dict
        """
        concept = self.get(concept_name)
        validator = ConceptValidator(concept)
        return validator.validate(data)


# Global registry
_default_registry = ConceptRegistry()

def get_concept_registry() -> ConceptRegistry:
    """Get the default concept registry."""
    return _default_registry
```

**Estimated**: 50 lines

#### Step 2.3: Integrate with Workflow Loader (workflow_loader.py)

**Update load_workflow function**:

```python
def load_workflow(workflow_path: str) -> Graph:
    """Load workflow from YAML file with concepts."""
    config = load_config(workflow_path)

    # Load concepts if defined
    concepts_dict = config.get("concepts", {})
    if concepts_dict:
        registry = get_concept_registry()
        registry.load_from_yaml(concepts_dict)

    # ... rest of workflow loading ...
```

**Estimated**: 10 lines (addition to existing function)

#### Step 2.4: Update ConfigNode to Use Concepts (nodes.py)

**Add concept validation to ConfigNode**:

```python
class ConfigNode(ValidatedNode):
    def __init__(self, config, node_id=None, result_name=None,
                 input_names=None, output_concept=None, **kwargs):
        # ... existing code ...
        self.output_concept = output_concept  # NEW: Output concept name

    def exec(self, inputs):
        # ... existing exec logic ...
        result = self._execute_node_type(inputs)

        # NEW: Validate against output concept if specified
        if self.output_concept:
            from .utils.concepts import get_concept_registry
            registry = get_concept_registry()
            validation = registry.validate(self.output_concept, result)

            if not validation.get("valid", False):
                errors = validation.get("errors", [])
                raise ValueError(
                    f"Output validation failed for concept '{self.output_concept}': "
                    f"{errors}"
                )

        return result
```

**Estimated**: 20 lines

#### Step 2.5: Example YAML Workflow with Concepts

**Location**: `workbooks/kaygraph-declarative-workflows/configs/inline_schemas_example.yaml`

```yaml
# Define concepts inline
concepts:
  Invoice:
    description: "A commercial invoice document"
    structure:
      invoice_number:
        type: text
        required: true
        pattern: "^INV-\\d{6}$"

      date:
        type: text
        required: true
        description: "Invoice date in YYYY-MM-DD"

      total_amount:
        type: number
        required: true
        min_value: 0.0

      status:
        type: text
        choices: ["pending", "paid", "cancelled"]
        default: "pending"

  SentimentAnalysis:
    description: "Sentiment analysis result"
    structure:
      sentiment:
        type: text
        choices: ["positive", "negative", "neutral"]
        required: true

      score:
        type: number
        min_value: 0.0
        max_value: 1.0
        required: true

# Use concepts in workflow
workflow:
  name: invoice_processing

  steps:
    - node: extract_invoice
      type: llm
      prompt: "Extract invoice data from: {{text}}"
      model: deepseek-chat
      output_concept: Invoice  # Validate against Invoice concept
      result: invoice

    - node: analyze_sentiment
      type: llm
      inputs: [invoice]
      prompt: "Analyze sentiment of invoice status"
      model: deepseek-chat
      output_concept: SentimentAnalysis  # Validate against SentimentAnalysis
      result: sentiment
```

**Estimated**: 50 lines

---

## Testing Strategy

### Test 1: Named Results

**File**: `workbooks/kaygraph-declarative-workflows/test_named_results.py`

```python
from workflow_loader import load_workflow, validate_workflow

def test_named_results():
    # Load workflow
    graph = load_workflow("configs/named_results_example.yaml")

    # Run workflow
    shared = {"document": "This is a test document with positive sentiment."}
    result = graph.run(shared)

    # Check results stored
    assert "__results__" in shared
    assert "raw_text" in shared["__results__"]
    assert "cleaned_text" in shared["__results__"]
    assert "sentiment" in shared["__results__"]
    assert "summary" in shared["__results__"]

    print("✓ Named results test passed")

def test_validation():
    # Test missing input error
    errors = validate_workflow("configs/invalid_workflow.yaml")
    assert len(errors) > 0
    assert "not produced by previous steps" in errors[0]

    print("✓ Validation test passed")
```

### Test 2: Inline Schemas

**File**: `workbooks/kaygraph-declarative-workflows/test_inline_schemas.py`

```python
from utils.concepts import Concept, get_concept_registry
from workflow_loader import load_workflow

def test_yaml_concept_parsing():
    # Test concept creation from YAML
    concept_def = {
        "description": "Test invoice",
        "structure": {
            "total": {"type": "number", "required": True},
            "status": {"type": "text", "choices": ["pending", "paid"]}
        }
    }

    concept = Concept.from_yaml_dict("Invoice", concept_def)
    assert concept.name == "Invoice"
    assert "total" in concept.structure

    print("✓ YAML concept parsing test passed")

def test_workflow_with_concepts():
    # Load workflow with inline concepts
    graph = load_workflow("configs/inline_schemas_example.yaml")

    # Check concepts registered
    registry = get_concept_registry()
    invoice_concept = registry.get("Invoice")
    assert invoice_concept is not None

    print("✓ Workflow with concepts test passed")

def test_concept_validation():
    registry = get_concept_registry()

    # Valid invoice
    valid_data = {
        "invoice_number": "INV-123456",
        "date": "2025-01-01",
        "total_amount": 100.0,
        "status": "pending"
    }
    result = registry.validate("Invoice", valid_data)
    assert result["valid"] == True

    # Invalid invoice (missing required field)
    invalid_data = {
        "date": "2025-01-01",
        "total_amount": 100.0
    }
    result = registry.validate("Invoice", invalid_data)
    assert result["valid"] == False

    print("✓ Concept validation test passed")
```

---

## Documentation Updates

### Update IMPLEMENTATION_NOTES.md

Add completed patterns:
- ✅ Named Intermediate Results
- ✅ Inline Structure Definitions

### Update LLM_INTEGRATION_GUIDE.md

Add new sections:
- Using named results for explicit data flow
- Defining concepts inline in YAML
- Example complete workflow with both features

### Create Usage Examples

**File**: `workbooks/kaygraph-declarative-workflows/examples/complete_workflow.yaml`

Complete example showing both patterns together.

---

## Implementation Checklist

### Named Results (Steps 1.1-1.4)
- [ ] Extend ConfigNode with result_name and input_names
- [ ] Add result storage in post()
- [ ] Add input resolution in prep()
- [ ] Create workflow_loader.py
- [ ] Implement load_workflow() function
- [ ] Implement validate_workflow() function
- [ ] Create named_results_example.yaml
- [ ] Write test_named_results.py

### Inline Schemas (Steps 2.1-2.5)
- [ ] Add Concept.from_yaml_dict() class method
- [ ] Create ConceptRegistry class
- [ ] Integrate registry with workflow loader
- [ ] Update ConfigNode with output_concept validation
- [ ] Create inline_schemas_example.yaml
- [ ] Write test_inline_schemas.py

### Documentation
- [ ] Update IMPLEMENTATION_NOTES.md
- [ ] Update LLM_INTEGRATION_GUIDE.md
- [ ] Create complete_workflow.yaml example

### Testing
- [ ] Run all tests
- [ ] Validate error messages are clear
- [ ] Test with LLM-generated workflows

---

## Estimated Total

- **Code**: ~350 lines
- **Tests**: ~100 lines
- **Examples**: ~150 lines
- **Docs**: ~200 lines updates
- **Total**: ~800 lines
- **Time**: 2-3 hours

---

## Success Criteria

✅ LLMs can generate workflows with explicit named results
✅ LLMs can define concepts entirely in YAML
✅ Validation catches missing inputs before runtime
✅ Validation enforces concept schemas
✅ Examples demonstrate both patterns
✅ Clear error messages for debugging
