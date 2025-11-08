# Research: Named Results & Inline Schema Definitions

**Task ID**: named-results-and-inline-schemas
**Date**: 2025-11-01
**Goal**: Implement 2 high-value patterns to make KayGraph more LLM-friendly

---

## Pattern 1: Named Intermediate Results

### Problem
Current approach uses implicit shared store updates, making data flow unclear for LLMs.

### Current Implementation
```python
class ExtractNode(Node):
    def post(self, shared, prep_res, exec_res):
        shared["raw_text"] = exec_res  # Implicit key
        return "default"

class AnalyzeNode(Node):
    def prep(self, shared):
        return shared["raw_text"]  # Must know the key
```

### Proposed Solution
```yaml
steps:
  - node: extract_text
    result: raw_text          # Explicit output name

  - node: analyze
    inputs: [raw_text]         # Explicit dependency
    result: analysis
```

### Research Findings

**Existing Patterns in Codebase**:
- `ConfigNode` in `nodes.py` already supports config-driven behavior
- Shared store is a plain dict
- Graph executes nodes sequentially
- No explicit result naming currently exists

**Similar Patterns in Industry**:
- Airflow: XCom for task outputs
- Prefect: Task return values automatically tracked
- Declarative pipelines: Named outputs standard

**Benefits for LLMs**:
- Clear data dependencies (A produces X, B consumes X)
- Validation possible (does result exist before use?)
- Easier to generate correct workflows
- Self-documenting data flow

---

## Pattern 2: Inline Structure Definitions

### Problem
Schemas must be defined as Python dicts, making it harder for LLMs to generate.

### Current Implementation
```python
# utils/concepts.py
INVOICE_CONCEPT = {
    "description": "A commercial invoice",
    "structure": {
        "invoice_number": {"type": "text", "required": True},
        "total_amount": {"type": "number", "required": True}
    }
}
```

### Proposed Solution
```yaml
# workflow.yaml
concepts:
  Invoice:
    description: "A commercial invoice"
    structure:
      invoice_number:
        type: text
        required: true
        pattern: "^INV-\\d{6}$"

      total_amount:
        type: number
        required: true
        min_value: 0.0
```

### Research Findings

**Existing Patterns in Codebase**:
- `utils/concepts.py` has `Concept` class and `ConceptValidator`
- Already supports: type, required, min_value, max_value, choices, pattern
- Validation happens at runtime
- Currently requires Python dict definitions

**Similar Patterns in Industry**:
- JSON Schema: Standard for structure definitions
- Pydantic: Python class definitions
- OpenAPI: YAML schema definitions
- GraphQL: SDL for type definitions

**Benefits for LLMs**:
- Generate complete schemas in YAML
- No Python code needed for simple structures
- Easier to read and modify
- Self-contained workflow files

---

## Implementation Scope

### Named Results
**Files to Modify**:
- `nodes.py` - ConfigNode to support `result` and `inputs`
- Graph execution logic (if needed)

**Estimated Lines**: 30-50 lines

### Inline Schemas
**Files to Modify**:
- `utils/concepts.py` - Add YAML parsing
- `utils/config_loader.py` - Parse `concepts` section

**Estimated Lines**: 100-150 lines

---

## Related Patterns (Lower Priority)

From research, these 6 other patterns could enhance LLM-friendliness:

3. **Batch-in-Sequence** - `batch_over: items` syntax
4. **Validation Command** - `kaygraph validate workflow.yaml`
5. **Domain Organization** - Single-file workflows with `domain:` section
6. **Auto-Discovery** - Scan for `*.kaygraph.yaml` files
7. **Expression-Based Routing** - Template-based conditionals
8. **Semantic Typing** - Concept-based validation

---

## Questions for Planning

1. Should named results be stored in `shared["__results__"]` or top-level?
2. Should we validate inputs exist at graph construction time or runtime?
3. Should inline schemas completely replace Python dicts or coexist?
4. Should we support both YAML and TOML for schemas?
5. How should we handle concept references across files?

---

## Recommendation

**Implement both patterns now** - they're high value, low effort, and foundational for the other 6 patterns.
