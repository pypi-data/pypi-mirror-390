# Parallel Execution: What We Have vs What Pipelex Has

**Date**: 2025-11-01
**Question**: How is Pipelex's PipeParallel different from KayGraph's ParallelBatchNode?

---

## 🎯 TL;DR - Key Difference

**KayGraph has**: Parallel execution of **SAME operation** on **MULTIPLE items** (batch parallelism)

**Pipelex has**: Parallel execution of **DIFFERENT operations** on **SAME/DIFFERENT items** (operation parallelism)

**We need**: The Pipelex pattern for declarative workflows!

---

## 📊 Side-by-Side Comparison

### What KayGraph Already Has ✅

**ParallelBatchNode** - Parallel batch processing

```python
class ProcessDocuments(ParallelBatchNode):
    """Process 100 documents in parallel - SAME operation on EACH"""

    def prep(self, shared):
        return shared["documents"]  # Return list of 100 docs

    def exec(self, document):
        # This runs on each document in parallel
        # Same operation: extract_text()
        return extract_text(document)
```

**What it does**:
```
documents = [doc1, doc2, doc3, ..., doc100]

ParallelBatchNode.exec() runs in parallel:
    Thread 1: extract_text(doc1)
    Thread 2: extract_text(doc2)
    Thread 3: extract_text(doc3)
    ...
    Thread N: extract_text(doc100)

All doing THE SAME THING to different items
```

**Use Case**: Processing many items with the same operation
- Extract text from 1000 PDFs
- Resize 500 images
- Validate 200 invoices
- Call API for 100 customers

---

### What Pipelex Has (That We Don't) ❌

**PipeParallel** - Parallel different operations

```toml
[pipe.extract_documents_parallel]
type = "PipeParallel"
inputs = { cv_pdf = "PDF", job_offer_pdf = "PDF" }
parallels = [
    { pipe = "extract_cv_text", result = "cv_pages" },        # Different op
    { pipe = "extract_job_offer_text", result = "job_pages" }, # Different op
]
```

**What it does**:
```
Run DIFFERENT operations in parallel:

Thread 1: extract_cv_text(cv_pdf)      → cv_pages
Thread 2: extract_job_offer_text(job_pdf) → job_pages

Two DIFFERENT things happening simultaneously
```

**Use Case**: Independent operations that can run concurrently
- Extract CV text + Extract job description (parallel I/O)
- Call user API + Call product API + Call order API (parallel API calls)
- Generate summary + Generate tags + Check sentiment (parallel LLM calls)
- Validate invoice + Check inventory + Verify payment (parallel checks)

---

## 🔍 Detailed Comparison

### KayGraph: ParallelBatchNode

**Python Code**:
```python
from kaygraph import ParallelBatchNode

class ExtractMultiplePDFs(ParallelBatchNode):
    max_workers = 10  # Use 10 threads

    def prep(self, shared):
        # Get list of PDFs
        return shared["pdf_files"]  # [pdf1, pdf2, ..., pdf100]

    def exec(self, pdf):
        # Same operation on each PDF
        return extract_text(pdf)

    def post(self, shared, prep_res, exec_res):
        # exec_res is list of all results
        shared["all_texts"] = exec_res
```

**Execution Model**:
```
Input: List of items [item1, item2, ..., itemN]
Operation: Single function exec(item)
Output: List of results [result1, result2, ..., resultN]

Parallelism: Across items (data parallelism)
```

**YAML Equivalent** (from our new patterns):
```yaml
steps:
  - node: extract_pdfs
    type: llm
    batch_over: pdf_files
    batch_as: pdf
    prompt: "Extract text from {{pdf}}"
    result: all_texts
```

**Limitation**: Can't run DIFFERENT operations in parallel

---

### Pipelex: PipeParallel

**TOML Code**:
```toml
[pipe.analyze_candidate_and_job]
type = "PipeParallel"
inputs = { cv = "PDF", job = "PDF", company = "Text" }
parallels = [
    { pipe = "analyze_cv", result = "cv_analysis" },
    { pipe = "analyze_job", result = "job_analysis" },
    { pipe = "research_company", result = "company_info" },
]
add_each_output = true  # Merge all results into shared context
```

**Execution Model**:
```
Input: Shared context (cv, job, company)
Operations: 3 different pipes running simultaneously
Output: 3 different results merged back

Thread 1: analyze_cv(cv) → cv_analysis
Thread 2: analyze_job(job) → job_analysis
Thread 3: research_company(company) → company_info

Parallelism: Across operations (task parallelism)
```

**Benefit**: Dramatically faster for independent operations
- Sequential: 3 seconds + 2 seconds + 4 seconds = 9 seconds
- Parallel: max(3, 2, 4) = 4 seconds
- **Speedup: 2.25x**

---

## 🤔 Why Do We Need Both?

### Scenario 1: Process Many Items (We Have This!)

**Task**: Extract text from 1000 PDFs

**Solution**: `ParallelBatchNode`

```python
class ExtractThousandPDFs(ParallelBatchNode):
    max_workers = 20

    def exec(self, pdf):
        return extract_text(pdf)
```

**Result**: 50x faster than sequential

---

### Scenario 2: Independent Operations (We DON'T Have This!)

**Task**: For a job candidate, we need to:
1. Extract and analyze their CV (3 seconds)
2. Extract and analyze job requirements (2 seconds)
3. Research the company (4 seconds)

**Current KayGraph** (Sequential):
```python
# Step 1
cv_node = ExtractCV()
cv_analysis = analyze_cv_node()

# Step 2
job_node = ExtractJob()
job_analysis = analyze_job_node()

# Step 3
company_node = ResearchCompany()

cv_node >> cv_analysis >> job_node >> job_analysis >> company_node

# Total time: 3 + 2 + 4 = 9 seconds
```

**What We WANT** (Parallel):
```yaml
steps:
  - node: parallel_analysis
    type: parallel
    parallels:
      - node: analyze_cv
        type: llm
        result: cv_analysis

      - node: analyze_job
        type: llm
        result: job_analysis

      - node: research_company
        type: llm
        result: company_info

    # All 3 run simultaneously
    # Total time: max(3, 2, 4) = 4 seconds
```

**Speedup**: 2.25x faster!

---

## 💡 Real-World Use Cases

### Use Case 1: E-commerce Order Processing

**Need**: When order received, we must:
- Validate payment (2s)
- Check inventory (1s)
- Calculate shipping (1s)
- Generate invoice (1s)

**Current** (Sequential): 5 seconds
**With Parallel**: max(2, 1, 1, 1) = 2 seconds
**Speedup**: 2.5x

### Use Case 2: Content Analysis

**Need**: Analyze article for:
- Summarize content (LLM call - 3s)
- Extract keywords (LLM call - 2s)
- Check sentiment (LLM call - 2s)
- Generate tags (LLM call - 2s)

**Current** (Sequential): 9 seconds
**With Parallel**: max(3, 2, 2, 2) = 3 seconds
**Speedup**: 3x
**Cost Savings**: Same LLM calls, 3x faster!

### Use Case 3: Document Processing Pipeline

**Need**: Process invoice
- Extract text via OCR (5s)
- Validate against schema (1s)
- Check for duplicates in DB (2s)

**Current** (Sequential): 8 seconds
**With Parallel**:
- Step 1: Extract text (5s)
- Step 2: Validate + Check DB in parallel → max(1, 2) = 2s
- Total: 7 seconds
**Speedup**: 1.14x (modest but still useful)

---

## 🏗️ How to Add This to KayGraph Declarative Workflows

### Option 1: New Node Type (Recommended)

```yaml
steps:
  # Regular sequential
  - node: prepare_data
    type: transform
    result: prepared

  # NEW: Parallel operations
  - node: parallel_ops
    type: parallel
    parallels:
      - node: operation_a
        type: llm
        inputs: [prepared]
        prompt: "Analyze aspect A"
        result: analysis_a

      - node: operation_b
        type: llm
        inputs: [prepared]
        prompt: "Analyze aspect B"
        result: analysis_b

      - node: operation_c
        type: llm
        inputs: [prepared]
        prompt: "Analyze aspect C"
        result: analysis_c

    # After parallel block, all results available

  - node: synthesize
    type: llm
    inputs: [analysis_a, analysis_b, analysis_c]
    prompt: "Combine analyses"
    result: final
```

### Option 2: Inline Syntax

```yaml
steps:
  - node: prepare
    result: data

  - parallel:
      - { node: op_a, type: llm, result: res_a }
      - { node: op_b, type: llm, result: res_b }
      - { node: op_c, type: llm, result: res_c }

  - node: combine
    inputs: [res_a, res_b, res_c]
```

---

## 🔧 Implementation Plan

### Step 1: Create ParallelConfigNode

```python
# In nodes.py
class ParallelConfigNode(ConfigNode):
    """
    Execute multiple ConfigNodes in parallel.

    Each parallel operation:
    - Runs simultaneously in threads
    - Has its own result name
    - Can access same inputs
    """

    def __init__(self, parallels: List[Dict[str, Any]], **kwargs):
        super().__init__(**kwargs)
        self.parallels = parallels
        self.parallel_nodes = []

        # Create child nodes
        for parallel_config in parallels:
            from workflow_loader import create_config_node_from_step
            node = create_config_node_from_step(parallel_config)
            self.parallel_nodes.append(node)

    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        """All child nodes share same shared context"""
        return shared

    def exec(self, shared: Dict[str, Any]) -> List[Any]:
        """Execute all child nodes in parallel"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        results = []

        with ThreadPoolExecutor(max_workers=len(self.parallel_nodes)) as executor:
            # Submit all nodes
            futures = {
                executor.submit(self._execute_node, node, shared): node
                for node in self.parallel_nodes
            }

            # Collect results
            for future in as_completed(futures):
                node = futures[future]
                try:
                    result = future.result()
                    results.append((node, result))
                except Exception as e:
                    self.logger.error(f"Parallel node {node.node_id} failed: {e}")
                    raise

        return results

    def _execute_node(self, node, shared):
        """Execute a single node"""
        prep_res = node.prep(shared)
        exec_res = node.exec(prep_res)
        return exec_res

    def post(self, shared: Dict[str, Any], prep_res: Any, exec_res: List[Any]) -> str:
        """Store all parallel results"""
        # Each node stored its own result during exec
        for node, result in exec_res:
            if node.result_name:
                if "__results__" not in shared:
                    shared["__results__"] = {}
                shared["__results__"][node.result_name] = result

        return "default"
```

### Step 2: Update workflow_loader.py

```python
def create_config_node_from_step(step_config: Dict[str, Any]) -> ConfigNode:
    # ... existing code ...

    # Check for parallel execution
    if "parallels" in step_config:
        parallels = step_config.get("parallels", [])

        return ParallelConfigNode(
            parallels=parallels,
            node_id=node_id,
            result_name=result_name
        )

    # ... rest of existing code ...
```

### Step 3: Example Workflow

```yaml
domain:
  name: cv_analysis
  main_workflow: analyze_match

concepts:
  CVAnalysis:
    structure:
      skills:
        type: array
      experience:
        type: text

  JobAnalysis:
    structure:
      requirements:
        type: array
      level:
        type: text

workflows:
  analyze_match:
    steps:
      # Load documents
      - node: load_docs
        type: extract
        result: documents

      # Parallel analysis (NEW!)
      - node: parallel_analysis
        type: parallel
        parallels:
          - node: analyze_cv
            type: llm
            prompt: "Analyze CV: {{documents.cv}}"
            output_concept: CVAnalysis
            result: cv_analysis

          - node: analyze_job
            type: llm
            prompt: "Analyze job: {{documents.job}}"
            output_concept: JobAnalysis
            result: job_analysis

      # Synthesize (waits for both)
      - node: compare
        type: llm
        inputs: [cv_analysis, job_analysis]
        prompt: "Compare CV and job requirements"
        result: match_score
```

---

## 📊 Performance Impact

### Batch Parallelism (We Have)

**Scenario**: Process 1000 items
- Sequential: 1000 × 0.1s = 100 seconds
- Parallel (10 workers): 1000 / 10 × 0.1s = 10 seconds
- **Speedup: 10x**

### Operation Parallelism (We Need)

**Scenario**: 5 independent operations
- Sequential: 2s + 3s + 1s + 2s + 2s = 10 seconds
- Parallel: max(2, 3, 1, 2, 2) = 3 seconds
- **Speedup: 3.3x**

### Combined (Powerful!)

**Scenario**: 3 operations on 100 items each
```yaml
- node: parallel_batch
  type: parallel
  parallels:
    - node: process_users
      type: llm
      batch_over: users
      result: user_results

    - node: process_products
      type: llm
      batch_over: products
      result: product_results

    - node: process_orders
      type: llm
      batch_over: orders
      result: order_results
```

- Sequential: (100×0.1s) + (100×0.1s) + (100×0.1s) = 30 seconds
- Parallel operations + batch parallel: max(10s, 10s, 10s) = 10 seconds
- **Speedup: 3x**

---

## ✅ Summary

### What We Have ✅

- **ParallelBatchNode**: Same operation on many items in parallel
- **AsyncNode**: Async I/O operations
- **AsyncParallelBatchNode**: Async + parallel batches

### What We're Missing ❌

- **Parallel operations**: Different operations running simultaneously
- **Declarative syntax**: YAML for parallel blocks
- **Easy configuration**: No Python classes needed

### The Gap

```
Current:  item1 → op → result1
          item2 → op → result2   } In parallel (ParallelBatchNode)
          item3 → op → result3

Missing:  input → op_a → result_a  }
          input → op_b → result_b  } In parallel (PipeParallel style)
          input → op_c → result_c  }
```

### Why Add It?

1. **Performance**: 2-3x faster for independent operations
2. **Cost**: Same LLM calls, less waiting
3. **User Experience**: Feels more responsive
4. **LLM-Friendly**: Natural to describe in YAML
5. **Completes Pattern Set**: Makes 8 of 8 patterns!

---

## 🎯 Recommendation

**YES, we should add this!**

**Effort**: ~150-200 lines (ParallelConfigNode + workflow_loader changes)
**Value**: HIGH - Different use case than ParallelBatchNode
**Complexity**: Medium - Need ThreadPoolExecutor, result merging
**Impact**: Completes the declarative workflow pattern set

**This is Pattern #8 of 8!** 🎉
