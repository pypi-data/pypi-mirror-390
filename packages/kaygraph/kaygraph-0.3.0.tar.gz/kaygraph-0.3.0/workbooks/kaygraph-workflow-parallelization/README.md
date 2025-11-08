# KayGraph Workflow Parallelization - Performance Optimization Patterns

This example demonstrates how to implement parallel execution patterns in KayGraph for improved performance through concurrent processing of independent tasks.

## Overview

The parallelization patterns enable:
- Concurrent execution of independent validations
- Parallel data enrichment from multiple sources
- Batch processing with parallel workers
- Fan-out/fan-in patterns for distributed work
- Async operations with proper coordination

## Key Features

1. **Parallel Validation** - Run multiple checks concurrently
2. **Data Enrichment** - Fetch from multiple APIs in parallel
3. **Batch Processing** - Process items concurrently with worker pools
4. **Map-Reduce Pattern** - Distribute work and aggregate results
5. **Async Coordination** - Manage async operations effectively

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example validation     # Parallel validation checks
python main.py --example enrichment     # Parallel data enrichment
python main.py --example batch          # Batch processing with workers
python main.py --example mapreduce      # Map-reduce pattern
python main.py --example pipeline       # Parallel pipeline stages

# Interactive mode
python main.py --interactive

# Process specific data
python main.py "Validate and enrich this user data"
```

## Implementation Patterns

### 1. Parallel Validation
Runs multiple validation checks simultaneously:
- Security validation
- Format validation
- Business rule validation
- External API validation

### 2. Data Enrichment
Enriches data from multiple sources in parallel:
- User profile enrichment
- Location data enrichment
- Social media enrichment
- Company data enrichment

### 3. Batch Processing
Processes batches with parallel workers:
- Configurable worker pool size
- Load balancing across workers
- Result aggregation
- Error handling per item

### 4. Map-Reduce Pattern
Distributes work and aggregates results:
- Map phase: parallel processing
- Reduce phase: result aggregation
- Supports custom mappers/reducers

### 5. Pipeline Parallelization
Parallel stages in processing pipeline:
- Stage-level parallelism
- Inter-stage coordination
- Backpressure handling

## Architecture

```
Input → ParallelValidationNode → [ValidationWorker1]
                               → [ValidationWorker2]
                               → [ValidationWorker3]
                               → AggregationNode → Output

Batch → BatchSplitterNode → [Worker1] → ResultAggregator
                         → [Worker2] →
                         → [Worker3] →
```

## Performance Considerations

1. **Optimal Worker Count** - Balance between parallelism and overhead
2. **Memory Usage** - Monitor memory with large batches
3. **Error Handling** - Graceful degradation on partial failures
4. **Timeout Management** - Set appropriate timeouts for parallel ops
5. **Resource Limits** - Respect API rate limits and system resources

## Use Cases

- **Data Validation** - Validate records against multiple criteria
- **API Aggregation** - Fetch data from multiple services
- **Report Generation** - Generate reports with parallel data fetching
- **ETL Pipelines** - Extract, transform, load with parallelism
- **Real-time Processing** - Process streaming data concurrently

## Best Practices

1. **Identify Independent Tasks** - Only parallelize truly independent work
2. **Handle Partial Failures** - Design for resilience
3. **Monitor Performance** - Track actual speedup vs overhead
4. **Use Appropriate Patterns** - Choose the right parallel pattern
5. **Test Thoroughly** - Parallel code is harder to debug