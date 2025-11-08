# KayGraph Performance Optimization Guide

This guide shows how to optimize KayGraph applications using the framework's built-in primitives and patterns. No new features needed - just smart usage of what's already there.

## Performance Principles

1. **Minimize Shared Store Size** - Store references, not data
2. **Choose the Right Node Type** - Batch vs Parallel vs Async
3. **Optimize prep/exec/post Phases** - Each has a specific purpose
4. **Profile Before Optimizing** - Use MetricsNode to find bottlenecks

## Shared Store Optimization

### ❌ BAD: Storing Large Objects

```python
class DataLoaderNode(Node):
    def post(self, shared, prep_res, exec_res):
        # Storing entire documents in shared store
        shared["documents"] = [
            {"id": 1, "content": "Very long document text..." * 1000},
            {"id": 2, "content": "Another long document..." * 1000},
            # ... thousands more
        ]
        shared["embeddings"] = [[0.1, 0.2, ...] * 768 for _ in range(10000)]
```

### ✅ GOOD: Store References and Load on Demand

```python
class DataLoaderNode(Node):
    def post(self, shared, prep_res, exec_res):
        # Store only references
        shared["document_ids"] = [1, 2, 3, ...]
        shared["document_cache"] = {}  # Load as needed
        shared["embedding_path"] = "/path/to/embeddings.npz"
```

### ✅ BETTER: Use External Storage

```python
class OptimizedDataNode(Node):
    def prep(self, shared):
        # Get only what this node needs
        return shared.get("document_ids", [])[:10]  # Process in batches
    
    def exec(self, doc_ids):
        # Load from disk/database only when needed
        documents = []
        for doc_id in doc_ids:
            with open(f"data/doc_{doc_id}.txt", "r") as f:
                documents.append(f.read())
        return documents
    
    def post(self, shared, prep_res, exec_res):
        # Store results externally, keep reference in shared
        result_id = str(uuid.uuid4())
        with open(f"results/{result_id}.json", "w") as f:
            json.dump(exec_res, f)
        shared["latest_result_id"] = result_id
```

## Node Type Selection Guide

### When to Use Each Node Type

| Node Type | Best For | Memory | Speed | Example Use Case |
|-----------|----------|--------|-------|------------------|
| **Node** | Single operations | Low | Fast | API calls, calculations |
| **BatchNode** | Sequential processing | Medium | Medium | Process list of items |
| **ParallelBatchNode** | I/O-bound operations | High | Fast | Multiple API calls |
| **AsyncNode** | Async operations | Low | Fast | WebSocket, async APIs |
| **AsyncParallelBatchNode** | Async + parallel | High | Fastest | Bulk async operations |

### Performance Comparison Example

```python
# Processing 100 API calls

# SLOW: Sequential processing (100 seconds)
class SequentialNode(Node):
    def exec(self, items):
        results = []
        for item in items:
            result = call_api(item)  # 1 second each
            results.append(result)
        return results

# FAST: Parallel processing (10 seconds with 10 workers)
class ParallelNode(ParallelBatchNode):
    def __init__(self):
        super().__init__(max_workers=10)
    
    def prep(self, shared):
        return shared["items"]  # Returns iterable
    
    def exec(self, item):
        return call_api(item)  # Called for each item in parallel

# FASTEST: Async parallel (2 seconds with async)
class AsyncParallelNode(AsyncParallelBatchNode):
    async def exec_async(self, item):
        return await call_api_async(item)  # Non-blocking
```

## Optimizing Node Phases

### prep() Phase - Data Access

```python
class OptimizedPrepNode(Node):
    def prep(self, shared):
        # ✅ GOOD: Minimal data extraction
        item_ids = shared.get("item_ids", [])
        filter_criteria = shared.get("filter", {})
        
        # ✅ GOOD: Filter early
        filtered_ids = [
            id for id in item_ids 
            if self.matches_criteria(id, filter_criteria)
        ]
        
        # ✅ GOOD: Return only what exec needs
        return {
            "ids": filtered_ids[:100],  # Limit batch size
            "config": shared.get("config", {})
        }
```

### exec() Phase - Computation

```python
class OptimizedExecNode(Node):
    def exec(self, prep_res):
        # ✅ GOOD: Bulk operations when possible
        ids = prep_res["ids"]
        
        # Instead of individual calls
        # results = [fetch_one(id) for id in ids]
        
        # Use bulk API
        results = fetch_bulk(ids)
        
        # ✅ GOOD: Process in chunks for memory efficiency
        processed = []
        for chunk in self.chunks(results, size=10):
            processed.extend(self.process_chunk(chunk))
        
        return processed
    
    def chunks(self, lst, size):
        """Yield successive chunks from list."""
        for i in range(0, len(lst), size):
            yield lst[i:i + size]
```

### post() Phase - Result Storage

```python
class OptimizedPostNode(Node):
    def post(self, shared, prep_res, exec_res):
        # ✅ GOOD: Store summary, not full results
        shared["result_summary"] = {
            "count": len(exec_res),
            "status": "completed",
            "sample": exec_res[:5]  # Small sample
        }
        
        # ✅ GOOD: Use efficient data structures
        if "results_by_type" not in shared:
            shared["results_by_type"] = {}
        
        for result in exec_res:
            result_type = result["type"]
            if result_type not in shared["results_by_type"]:
                shared["results_by_type"][result_type] = []
            # Store only essential fields
            shared["results_by_type"][result_type].append({
                "id": result["id"],
                "score": result["score"]
            })
        
        # ✅ GOOD: Return specific action for routing
        if len(exec_res) > 100:
            return "batch_process"
        else:
            return "quick_process"
```

## Memory Management Patterns

### Pattern 1: Streaming Large Data

```python
class StreamingNode(Node):
    def prep(self, shared):
        # Return file path, not file contents
        return shared["large_file_path"]
    
    def exec(self, file_path):
        # Process file in chunks
        results = []
        with open(file_path, 'r') as f:
            chunk = []
            for line in f:
                chunk.append(line.strip())
                if len(chunk) >= 1000:
                    results.append(self.process_chunk(chunk))
                    chunk = []
            if chunk:
                results.append(self.process_chunk(chunk))
        return results
```

### Pattern 2: Lazy Loading

```python
class LazyLoadNode(Node):
    def __init__(self):
        super().__init__()
        self._cache = {}
    
    def get_data(self, key):
        """Load data only when needed"""
        if key not in self._cache:
            self._cache[key] = self.load_from_disk(key)
        return self._cache[key]
    
    def exec(self, prep_res):
        results = []
        for item_id in prep_res["ids"]:
            # Load only if processing is needed
            if self.needs_processing(item_id):
                data = self.get_data(item_id)
                results.append(self.process(data))
        return results
```

### Pattern 3: Result Pagination

```python
class PaginatedResultNode(Node):
    def post(self, shared, prep_res, exec_res):
        # Don't store all results at once
        page_size = 100
        total_results = len(exec_res)
        
        # Store metadata
        shared["result_metadata"] = {
            "total": total_results,
            "page_size": page_size,
            "pages": (total_results + page_size - 1) // page_size
        }
        
        # Store only first page
        shared["current_page"] = 0
        shared["page_0"] = exec_res[:page_size]
        
        # Store rest in temp files
        for i in range(1, shared["result_metadata"]["pages"]):
            start = i * page_size
            end = min(start + page_size, total_results)
            with open(f"temp/page_{i}.json", "w") as f:
                json.dump(exec_res[start:end], f)
```

## Profiling with MetricsNode

### Basic Performance Tracking

```python
from kaygraph import MetricsNode

class ProfiledProcessingNode(MetricsNode):
    def __init__(self):
        super().__init__(collect_metrics=True, max_retries=3)
    
    def exec(self, prep_res):
        # Your processing logic
        return process_data(prep_res)

# Usage
node = ProfiledProcessingNode()
graph = Graph(start=node)
graph.run(shared)

# Get performance stats
stats = node.get_stats()
print(f"Average execution time: {stats['avg_execution_time']:.3f}s")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Total retries: {stats['total_retries']}")
```

### Comprehensive Graph Profiling

```python
class ProfilingGraph(Graph):
    def __init__(self):
        super().__init__()
        self.node_metrics = {}
    
    def start(self, start_node):
        # Wrap all nodes with metrics collection
        wrapped_node = self.wrap_with_metrics(start_node)
        return super().start(wrapped_node)
    
    def wrap_with_metrics(self, node):
        """Recursively wrap all nodes with metrics"""
        if isinstance(node, MetricsNode):
            return node
        
        # Create metrics wrapper
        class MetricsWrapper(MetricsNode):
            def __init__(self, wrapped):
                super().__init__(collect_metrics=True)
                self.wrapped = wrapped
                self.node_id = wrapped.node_id
            
            def prep(self, shared):
                return self.wrapped.prep(shared)
            
            def exec(self, prep_res):
                return self.wrapped.exec(prep_res)
            
            def post(self, shared, prep_res, exec_res):
                return self.wrapped.post(shared, prep_res, exec_res)
        
        wrapped = MetricsWrapper(node)
        self.node_metrics[node.node_id] = wrapped
        
        # Wrap successors
        for action, successor in node.successors.items():
            wrapped.successors[action] = self.wrap_with_metrics(successor)
        
        return wrapped
    
    def get_performance_report(self):
        """Generate performance report for all nodes"""
        report = []
        for node_id, node in self.node_metrics.items():
            stats = node.get_stats()
            report.append({
                "node_id": node_id,
                "stats": stats
            })
        return report
```

## Optimization Strategies

### 1. Batch Similar Operations

```python
# ❌ BAD: Individual operations
class InefficientNode(Node):
    def exec(self, items):
        results = []
        for item in items:
            # Individual API call for each item
            embedding = get_embedding(item["text"])
            results.append(embedding)
        return results

# ✅ GOOD: Batch operations
class EfficientNode(Node):
    def exec(self, items):
        # Single API call for all items
        texts = [item["text"] for item in items]
        embeddings = get_embeddings_batch(texts)
        return embeddings
```

### 2. Cache Expensive Computations

```python
class CachedComputationNode(Node):
    def prep(self, shared):
        # Initialize cache in shared store
        if "computation_cache" not in shared:
            shared["computation_cache"] = {}
        return shared["items"]
    
    def exec(self, items):
        # Access cache from closure or class attribute
        cache = {}
        results = []
        
        for item in items:
            cache_key = self.get_cache_key(item)
            if cache_key in cache:
                results.append(cache[cache_key])
            else:
                result = self.expensive_computation(item)
                cache[cache_key] = result
                results.append(result)
        
        return results, cache
    
    def post(self, shared, prep_res, exec_res):
        results, cache = exec_res
        # Update shared cache
        shared["computation_cache"].update(cache)
        shared["results"] = results
```

### 3. Early Termination

```python
class EarlyTerminationNode(Node):
    def exec(self, items):
        results = []
        error_count = 0
        
        for item in items:
            try:
                result = process_item(item)
                results.append(result)
            except Exception as e:
                error_count += 1
                if error_count > 10:
                    # Stop processing if too many errors
                    self.logger.warning("Too many errors, stopping early")
                    break
        
        return results
```

## Common Performance Pitfalls

### 1. Shared Store Bloat

```python
# ❌ BAD: Accumulating data without cleanup
def post(self, shared, prep_res, exec_res):
    if "all_results" not in shared:
        shared["all_results"] = []
    shared["all_results"].extend(exec_res)  # Grows unbounded!

# ✅ GOOD: Bounded storage with cleanup
def post(self, shared, prep_res, exec_res):
    # Keep only recent results
    if "recent_results" not in shared:
        shared["recent_results"] = []
    
    shared["recent_results"].extend(exec_res)
    # Keep only last 1000 results
    shared["recent_results"] = shared["recent_results"][-1000:]
```

### 2. Blocking Operations in Async Nodes

```python
# ❌ BAD: Blocking call in async node
class BadAsyncNode(AsyncNode):
    async def exec_async(self, prep_res):
        # This blocks the event loop!
        result = requests.get("http://api.example.com/data")
        return result.json()

# ✅ GOOD: Proper async operations
class GoodAsyncNode(AsyncNode):
    async def exec_async(self, prep_res):
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get("http://api.example.com/data") as resp:
                return await resp.json()
```

### 3. Inefficient Graph Structure

```python
# ❌ BAD: Sequential processing of independent tasks
node1 >> node2 >> node3 >> node4  # Each waits for previous

# ✅ GOOD: Parallel processing where possible
# Use a coordinator node that triggers parallel execution
coordinator >> ("task1", node1)
coordinator >> ("task2", node2)
coordinator >> ("task3", node3)
# Then merge results
merge_node = MergeNode()
node1 >> merge_node
node2 >> merge_node
node3 >> merge_node
```

## Performance Checklist

Before deploying to production, verify:

- [ ] Shared store contains only essential data
- [ ] Large data is stored externally with references
- [ ] Appropriate node types used (Batch/Parallel/Async)
- [ ] Bulk operations used where possible
- [ ] Caching implemented for expensive operations
- [ ] Memory usage is bounded
- [ ] Error handling doesn't cause memory leaks
- [ ] Profiling shows acceptable performance
- [ ] No blocking operations in async nodes
- [ ] Graph structure minimizes sequential bottlenecks

## Benchmarking Template

```python
import time
from kaygraph import Graph, MetricsNode

def benchmark_graph(graph, shared, iterations=10):
    """Benchmark graph performance"""
    times = []
    
    for i in range(iterations):
        start = time.time()
        graph.run(shared.copy())  # Fresh shared state
        end = time.time()
        times.append(end - start)
    
    return {
        "avg_time": sum(times) / len(times),
        "min_time": min(times),
        "max_time": max(times),
        "std_dev": statistics.stdev(times) if len(times) > 1 else 0
    }

# Usage
results = benchmark_graph(my_graph, shared_data)
print(f"Average execution time: {results['avg_time']:.3f}s")
```

Remember: Profile first, optimize second. KayGraph's simple design means performance issues are usually in your code, not the framework.