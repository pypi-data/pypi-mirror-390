# Research: Remaining 6 LLM-Friendly Patterns

**Task ID**: remaining-six-patterns
**Date**: 2025-11-01
**Goal**: Plan implementation of 6 remaining patterns to maximize LLM-friendliness

---

## Context

We've implemented 2 of 8 high-value patterns:
- ✅ Named Intermediate Results
- ✅ Inline Schema Definitions

Remaining 6 patterns to evaluate and plan:
1. Batch-in-Sequence
2. Validation Command
3. Domain Organization
4. Auto-Discovery
5. Expression-Based Routing
6. Semantic Typing

---

## Pattern 1: Batch-in-Sequence

### Current State
Requires separate `BatchNode` class:
```python
class ProcessItems(BatchNode):
    def prep(self, shared):
        return shared["items"]

    def exec(self, item):
        return process(item)
```

### Proposed Pattern
```yaml
steps:
  - node: process_item
    batch_over: items      # Batch this step
    batch_as: item         # Variable name for each item
    result: results
```

### Existing Code References
- **File**: `nodes.py:722` - `ConfigurableBatchNode` already exists
- **File**: `utils/multiplicity.py` - Multiplicity parsing for `Type[]` notation
- **Pattern**: We already have batch processing infrastructure

### Implementation Complexity
- **Effort**: LOW (~50 lines)
- **Files**: `workflow_loader.py` (detect `batch_over`), minimal changes
- **Value**: MEDIUM (syntactic sugar over existing functionality)

### Research Notes
- KayGraph already supports `BatchNode` - this is just cleaner syntax
- Existing `ConfigurableBatchNode` can be reused
- Just need workflow loader to detect `batch_over` and wrap node

---

## Pattern 2: Validation Command

### Current State
No pre-execution validation. Errors discovered at runtime.

### Proposed Pattern
```bash
kaygraph validate workflow.yaml

# Output:
✓ All inputs satisfied
✓ All concepts defined
✗ Step 'analyze': Missing input 'raw_text'
✗ Concept 'Invoice' has invalid field type
```

### Existing Code References
- **File**: `workflow_loader.py:118-206` - `validate_workflow()` already exists!
- We already have validation logic built
- Just need CLI wrapper

### Implementation Complexity
- **Effort**: LOW (~100 lines)
- **Files**: New `cli.py` file, add CLI interface
- **Value**: HIGH (enables LLM iteration without running workflows)

### Research Notes
- Validation logic already implemented in `validate_workflow()`
- Need to add:
  - CLI entry point (`kaygraph` command)
  - Concept validation (check all concepts exist)
  - Type compatibility checking
  - Pretty error formatting (already have `print_validation_report()`)

---

## Pattern 3: Domain Organization

### Current State
No formal domain concept. Workflows scattered across files.

### Proposed Pattern
```yaml
domain:
  name: invoice_processing
  version: 1.0
  description: "Complete invoice handling"
  main_workflow: process_invoice

concepts:
  Invoice: ...

workflows:
  process_invoice: ...
  extract_invoice: ...
```

### Existing Code References
- **File**: `workflow_loader.py` - Already loads workflows
- **File**: `utils/concepts.py` - `ConceptRegistry` manages concepts
- No existing domain abstraction

### Implementation Complexity
- **Effort**: MEDIUM (~200 lines)
- **Files**: New `domain.py`, modify `workflow_loader.py`
- **Value**: MEDIUM (better organization, single-file workflows)

### Research Notes
- This is mostly organizational - single YAML file with everything
- Could enable cross-domain concept references later
- `main_workflow` designation useful for CLI (`kaygraph run domain_name`)

---

## Pattern 4: Auto-Discovery

### Current State
Manual imports:
```python
from workflow import my_workflow
```

### Proposed Pattern
```bash
kaygraph list    # Auto-discover all *.kaygraph.yaml files
kaygraph run invoice_processing  # Run by name
```

### Existing Code References
- No existing auto-discovery
- Would scan project for `*.kaygraph.yaml` files

### Implementation Complexity
- **Effort**: LOW (~100 lines)
- **Files**: `cli.py` (discovery logic)
- **Value**: MEDIUM (convenience, consistency)

### Research Notes
- Simple file scanning with `pathlib.glob("**/*.kaygraph.yaml")`
- Exclude common directories: `node_modules`, `.git`, `venv`, etc.
- Build registry of discovered workflows
- Depends on Pattern 2 (CLI) being implemented

---

## Pattern 5: Expression-Based Routing

### Current State
Simple string comparison in `ConditionalNode`:
```python
def _evaluate_comparison(self, expr: str, context: Dict):
    # Supports: ==, !=, <, >, <=, >=, and, or
```

### Proposed Pattern (Option A - Keep Simple)
```yaml
node: route_by_score
type: condition
expression: "score > 0.8"
outcomes:
  true: high_score_path
  false: low_score_path
```

### Proposed Pattern (Option B - Template Support)
```yaml
expression: |
  {% if score > 0.8 %}
    high
  {% elif score > 0.5 %}
    medium
  {% else %}
    low
  {% endif %}
outcomes:
  high: premium_path
  medium: standard_path
  low: basic_path
```

### Existing Code References
- **File**: `nodes.py:263-346` - Safe expression parser already exists!
- **File**: `nodes.py:296-321` - `_evaluate_comparison()` supports operators
- We already removed `eval()` vulnerability and have safe parser

### Implementation Complexity
- **Option A (Current)**: DONE - We already have this!
- **Option B (Templates)**: MEDIUM (~150 lines) - Would need template engine
- **Value**: Option A is sufficient for most cases

### Research Notes
- We REMOVED Jinja2 dependency for simplicity
- Current safe expression parser handles: `==, !=, <, >, <=, >=, and, or`
- This is probably ALREADY IMPLEMENTED in ConfigNode condition type
- May just need documentation/examples

---

## Pattern 6: Semantic Typing

### Current State
Concepts are just validation schemas. No semantic meaning.

### Proposed Pattern
```yaml
concepts:
  Character:
    description: "A person (not a symbol)"
    semantic_type: person
    structure: ...

  Invoice:
    refines: Document  # Inheritance
    structure: ...
```

### Existing Code References
- **File**: `utils/concepts.py` - `Concept` class exists
- No semantic layer or refinement currently

### Implementation Complexity
- **Effort**: HIGH (~300 lines)
- **Files**: `utils/concepts.py` (add semantics), validation logic
- **Value**: LOW (Nice-to-have, not critical for LLMs)

### Research Notes
- This adds conceptual complexity
- LLMs don't really need semantic types - validation is enough
- Could be future enhancement but not priority
- Refinement/inheritance might be useful but adds complexity

---

## Priority Assessment

### High Priority (Implement Next)
1. **Validation Command** - LOW effort, HIGH value
   - Enables LLM iteration
   - Already have validation logic
   - Just need CLI wrapper

2. **Expression-Based Routing** - ALREADY DONE?
   - Need to verify ConfigNode condition type works
   - May just need documentation

### Medium Priority
3. **Batch-in-Sequence** - LOW effort, MEDIUM value
   - Cleaner syntax
   - Reuses existing BatchNode

4. **Domain Organization** - MEDIUM effort, MEDIUM value
   - Single-file workflows
   - Better organization

5. **Auto-Discovery** - LOW effort, MEDIUM value
   - Convenience feature
   - Depends on CLI

### Low Priority
6. **Semantic Typing** - HIGH effort, LOW value
   - Not critical for LLMs
   - Adds complexity
   - Consider for v2.0

---

## Implementation Strategy

### Phase 1 (Quick Wins - 1-2 hours)
1. Verify Expression-Based Routing works with ConfigNode
2. Add CLI with validation command
3. Document both patterns

### Phase 2 (Enhancements - 2-3 hours)
4. Add batch-in-sequence syntax
5. Implement auto-discovery in CLI
6. Add domain organization

### Phase 3 (Future)
7. Semantic typing (if needed)

---

## Key Findings

**What We Already Have**:
- ✅ Expression evaluation (safe, no eval)
- ✅ Validation logic
- ✅ Batch processing infrastructure
- ✅ Concept validation

**What We Need**:
- CLI wrapper (100 lines)
- Batch-in-sequence detection (50 lines)
- Domain YAML structure (200 lines)
- Auto-discovery scanning (100 lines)

**Total Estimated**: ~450 lines for patterns 1-5
**Time Estimate**: 3-5 hours total

---

## Questions for Planning

1. **Validation Command**: Should it be a separate command or integrated with workflow loading?
2. **Expression Routing**: Is current implementation sufficient or do we need templates?
3. **Domain Organization**: Single file with everything, or allow multi-file domains?
4. **Auto-Discovery**: What file pattern? `*.kaygraph.yaml` or just `*.yaml` in specific directory?
5. **Semantic Typing**: Skip for now or implement basic refinement?

---

## Recommendation

**Implement in this order**:
1. CLI + Validation Command (1 hour) - HIGH value
2. Verify/Document Expression Routing (30 min) - May be done
3. Batch-in-Sequence (1 hour) - Clean syntax
4. Domain Organization (2 hours) - Single-file workflows
5. Auto-Discovery (1 hour) - Convenience

**Skip for now**:
6. Semantic Typing - Future enhancement

**Total**: ~5.5 hours for 5 patterns
**Result**: 7 of 8 patterns complete (87.5%)
