# Implementation Notes: KayGraph Declarative Workflows

**Goal**: Make KayGraph the best toolkit for LLMs to create workflows

---

## What We Built (2025-11-01)

### Security Fix ✅
- **Fixed**: `eval()` vulnerability in `nodes.py:278`
- **Replaced with**: Safe expression parser (==, !=, <, >, <=, >=, and, or)

### Simplifications ✅
- **DynamicOrchestratorNode → SimplePlannerNode** (170→80 lines): LLM task planning only
- **IntelligentCacheNode → SimpleCacheNode** (200→120 lines): In-memory only, no Redis
- **Removed AdvancedTemplateNode**: Use Python f-strings instead

### Code Reduction
- Before: 5,326 lines
- After: ~2,530 lines
- Reduction: 52%

---

## Patterns We're Using

### ✅ Already Implemented
1. **Multiplicity System** - `Document[]`, `Image[3]` notation
2. **Concept Validation** - Type-safe schemas catch LLM errors
3. **Config Loading** - YAML/TOML workflows
4. **CircuitBreakerNode** - Automatic fault tolerance
5. **ToolRegistryNode** - Dynamic function calling for agents
6. **SimpleCacheNode** - Save money on redundant LLM calls
7. **SimplePlannerNode** - LLM-driven task planning
8. **ConfigNode** - Behavior defined in config, not code
9. **✨ Named Intermediate Results** - Explicit data flow (2025-11-01)
10. **✨ Inline Schema Definitions** - YAML concepts (2025-11-01)
11. **✨ CLI + Validation Command** - `kgraph validate/run/list` (2025-11-01)
12. **✨ Expression-Based Routing** - Safe conditionals in YAML (2025-11-01)
13. **✨ Batch-in-Sequence** - `batch_over: items` syntax (2025-11-01)
14. **✨ Domain Organization** - Multi-workflow .kg.yaml files (2025-11-01)
15. **✨ Parallel Operations** - `parallels:` task parallelism (2025-11-01)

---

## Recently Implemented (2025-11-01)

### ✅ Named Intermediate Results

**Files Modified**:
- `nodes.py` - Added `result_name`, `input_names`, `output_concept` parameters
- `workflow_loader.py` - Created loader with validation

**Example**:
```yaml
steps:
  - node: extract_text
    result: raw_text

  - node: analyze
    inputs: [raw_text]
    result: analysis
```

**Benefits**:
- Explicit data dependencies (no more guessing shared store keys)
- Validation catches missing inputs before runtime
- Self-documenting workflows
- LLMs can see clear data flow

---

### ✅ Inline Schema Definitions

**Files Modified**:
- `utils/concepts.py` - Added `Concept.from_yaml_dict()` and `ConceptRegistry`
- `workflow_loader.py` - Integrated concept loading
- `nodes.py` - Added output validation

**Example**:
```yaml
concepts:
  Invoice:
    description: "Commercial invoice"
    structure:
      total:
        type: number
        required: true
        min_value: 0.0
```

**Benefits**:
- LLMs generate schemas in YAML (no Python needed)
- Automatic validation of outputs
- Type-safe workflows
- Self-contained workflow files

---

### ✅ CLI + Validation Command

**Files Created**:
- `cli.py` (~170 lines) - Command-line interface
- `test_remaining_patterns.py` - Test suite

**Commands**:
```bash
kgraph validate workflow.kg.yaml     # Validate before running
kgraph run workflow.kg.yaml          # Run workflow
kgraph run domain.kg.yaml:extract    # Run specific workflow in domain
kgraph list                          # Discover .kg.yaml files
```

**Benefits**:
- LLMs can validate workflows without running them
- Catch errors before execution
- Auto-discovery of workflow files
- Support for both single workflows and domains

---

### ✅ Expression-Based Routing

**Already Implemented**: Safe expression parser in `nodes.py:301-360`

**Documentation Added**: Comprehensive section in `LLM_INTEGRATION_GUIDE.md`

**Example**:
```yaml
- node: check_quality
  type: condition
  expression: "score >= 0.8 and confidence > 0.7"
  inputs: [quality_assessment]
  result: is_premium
```

**Security**:
- No `eval()` - prevents code injection
- Whitelisted operators: `==, !=, <, >, <=, >=, and, or`
- Type-safe evaluation

**Benefits**:
- LLMs can generate conditional logic in YAML
- Safe for untrusted workflows
- Human-readable decision logic

---

### ✅ Batch-in-Sequence

**Files Modified**:
- `nodes.py` - Added `BatchConfigNode` class (~75 lines)
- `workflow_loader.py` - Added `batch_over` detection

**Example**:
```yaml
steps:
  - node: process_document
    type: llm
    batch_over: documents     # Batch over this list
    batch_as: doc            # Variable name for each item
    prompt: "Analyze: {{doc}}"
    result: analyses
```

**Benefits**:
- No Python code needed for batch processing
- Cleaner than separate BatchNode class
- LLM-friendly syntax
- Results automatically collected

---

### ✅ Domain Organization

**Files Created**:
- `domain.py` (~270 lines) - Domain loading and management

**Example**:
```yaml
domain:
  name: invoice_processing
  version: 1.0
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

  validate_invoice:
    steps:
      - node: check
        ...
```

**Benefits**:
- Single file contains complete domain
- Shared concepts across workflows
- Clear main workflow designation
- Easy to version and distribute
- LLMs can generate entire domain in one file

---

### ✅ Parallel Operations

**Files Modified**:
- `nodes.py` - Added `ParallelConfigNode` class (~150 lines)
- `workflow_loader.py` - Added `parallels` detection

**Example**:
```yaml
steps:
  - node: parallel_analysis
    type: parallel
    parallels:
      - node: analyze_cv
        type: llm
        prompt: "Analyze CV..."
        result: cv_analysis

      - node: analyze_job
        type: llm
        prompt: "Analyze job..."
        result: job_analysis

      - node: research_company
        type: llm
        prompt: "Research company..."
        result: company_info

    # All 3 operations run simultaneously in threads
```

**Benefits**:
- Task parallelism - different operations simultaneously
- 2-3x speedup for independent operations
- Same LLM cost, less waiting
- Natural YAML syntax
- Complements batch parallelism (ParallelBatchNode)

**Difference from Batch Processing**:
- **Batch**: Same operation on many items (data parallelism)
- **Parallel**: Different operations (task parallelism)

---

## Pattern Comparison

| Pattern | What We Have | What We Could Add | Effort | Value |
|---------|--------------|-------------------|--------|-------|
| Named Results | Implicit shared store | Explicit `result:` | Low | High |
| Inline Structures | Python dicts | YAML definitions | Low | High |
| Batch-in-Sequence | Separate BatchNode | `batch_over:` syntax | Medium | Medium |
| Validation CLI | Runtime errors | Pre-execution check | Medium | High |
| Domain Organization | Manual structure | Single-file workflows | Medium | Medium |
| Auto-Discovery | Manual imports | Scan for `*.yaml` | Low | Medium |

---

## Recommendations

### Implement Now (Before Commit)
1. **Named Intermediate Results** - Makes data flow explicit (30 min)
2. **Inline Structure Definitions** - YAML schemas (1 hour)

### Implement Next (After Commit)
3. **Validation Command** - Catch errors early (2-3 hours)
4. **Batch-in-Sequence** - Simpler syntax (1 hour)

### Consider Later
5. Domain Organization - Single-file workflows
6. Auto-Discovery - Scan for workflow files

---

## Files in This Workbook

**For LLMs**:
- **README.md** - Overview and quick start
- **LLM_INTEGRATION_GUIDE.md** - Complete guide for generating workflows
- **IMPLEMENTATION_NOTES.md** - This file - what's implemented and what's next

**Code**:
- **utils/** - Multiplicity, concepts, config loading, LLM calls
- **nodes.py** - ConfigNode, MapperNode, ConceptNode, ConditionalNode
- **nodes_advanced.py** - CircuitBreaker, ToolRegistry, SimpleCache, SimplePlanner
- **configs/** - Example YAML/TOML workflow files
- **main.py**, **resume_workflow.py** - Example implementations

---

## Key Insight

We were missing: **Explicit data flow** (named results) and **LLM-friendly schemas** (YAML definitions)

These make the BIGGEST difference for LLM workflow generation.
