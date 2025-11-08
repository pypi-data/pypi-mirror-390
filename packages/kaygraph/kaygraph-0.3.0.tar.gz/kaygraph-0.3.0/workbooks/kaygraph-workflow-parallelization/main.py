#!/usr/bin/env python3
"""
KayGraph Workflow Parallelization - Performance optimization through parallel execution.

Demonstrates how to implement concurrent processing patterns for improved performance,
including parallel validation, data enrichment, batch processing, and map-reduce.
"""

import sys
import json
import logging
import argparse
import time
from typing import Dict, Any, List
from datetime import datetime
from kaygraph import Graph, ParallelBatchGraph
from nodes import (
    ParallelValidationNode,
    ParallelEnrichmentNode,
    BatchProcessingNode,
    MapNode,
    ReduceNode,
    ParallelPipelineNode,
    PerformanceMetricsNode
)
from models import (
    EnrichmentSource,
    BatchConfiguration,
    PipelineStage
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============== Graph Creation Functions ==============

def create_validation_graph() -> Graph:
    """
    Create parallel validation workflow.
    Runs multiple validation checks concurrently.
    """
    validation = ParallelValidationNode(max_workers=4)
    metrics = PerformanceMetricsNode()
    
    validation >> metrics
    
    return Graph(start=validation)


def create_enrichment_graph() -> Graph:
    """
    Create parallel data enrichment workflow.
    Fetches data from multiple sources concurrently.
    """
    enrichment = ParallelEnrichmentNode(
        sources=[
            EnrichmentSource.USER_PROFILE,
            EnrichmentSource.LOCATION,
            EnrichmentSource.COMPANY,
            EnrichmentSource.SOCIAL_MEDIA
        ]
    )
    metrics = PerformanceMetricsNode()
    
    enrichment >> metrics
    
    return Graph(start=enrichment)


def create_batch_processing_graph() -> ParallelBatchGraph:
    """
    Create batch processing workflow.
    Uses ParallelBatchGraph for automatic parallel processing.
    """
    batch_processor = BatchProcessingNode(worker_count=4)
    
    return ParallelBatchGraph(start=batch_processor)


def create_mapreduce_graph() -> Graph:
    """
    Create map-reduce workflow.
    Demonstrates distributed processing pattern.
    """
    map_node = MapNode(mapper_count=4)
    reduce_node = ReduceNode(reducer_count=2)
    
    map_node >> reduce_node
    
    return Graph(start=map_node)


def create_pipeline_graph() -> Graph:
    """
    Create parallel pipeline workflow.
    Each stage can have different parallelism levels.
    """
    # Define custom pipeline stages
    stages = [
        PipelineStage(stage_name="validation", parallelism=4, timeout_ms=5000),
        PipelineStage(stage_name="transformation", parallelism=3, timeout_ms=10000),
        PipelineStage(stage_name="enrichment", parallelism=2, timeout_ms=15000),
        PipelineStage(stage_name="output", parallelism=1, timeout_ms=5000)
    ]
    
    pipeline = ParallelPipelineNode(pipeline_stages=stages)
    metrics = PerformanceMetricsNode()
    
    pipeline >> ("success", metrics)
    pipeline >> ("failure", metrics)
    
    return Graph(start=pipeline)


# ============== Example Functions ==============

def example_parallel_validation():
    """Demonstrate parallel validation checks."""
    print("\n=== Parallel Validation Example ===")
    
    graph = create_validation_graph()
    
    # Test data
    test_data = [
        {
            "email": "user@example.com",
            "name": "John Doe",
            "date": "2024-01-01",
            "content": "Normal user input"
        },
        {
            "email": "invalid-email",
            "name": "A",
            "date": "invalid-date",
            "content": "'; DROP TABLE users; --"
        },
        {
            "email": "test@test.com",
            "name": "Test User",
            "date": "2024-12-31",
            "content": "<script>alert('XSS')</script>"
        }
    ]
    
    for i, data in enumerate(test_data):
        print(f"\nValidating data {i+1}:")
        print(f"Data: {json.dumps(data, indent=2)}")
        
        shared = {"input_data": data}
        graph.run(shared)
        
        if "validation_summary" in shared:
            summary = shared["validation_summary"]
            print(f"\nResults:")
            print(f"✓ Passed: {summary.passed_checks}/{summary.total_checks}")
            print(f"⚡ Speedup: {summary.speedup_factor:.2f}x")
            print(f"⏱️  Time: {summary.parallel_execution_time_ms:.0f}ms (vs {summary.total_execution_time_ms:.0f}ms sequential)")
            
            # Show individual results
            for validation in summary.all_validations:
                status = "✓" if validation.passed else "✗"
                print(f"  {status} {validation.check_name}: {validation.details[:50]}...")


def example_data_enrichment():
    """Demonstrate parallel data enrichment."""
    print("\n=== Parallel Data Enrichment Example ===")
    
    graph = create_enrichment_graph()
    
    # Base data to enrich
    base_data = {
        "user_id": "12345",
        "email": "user@company.com",
        "name": "Jane Smith",
        "ip_address": "192.168.1.1"
    }
    
    print(f"Base data: {json.dumps(base_data, indent=2)}")
    
    shared = {"base_data": base_data}
    graph.run(shared)
    
    if "enriched_data" in shared:
        enriched = shared["enriched_data"]
        print(f"\nEnrichment Results:")
        print(f"✓ Successful: {enriched.successful_sources}/{enriched.total_sources} sources")
        print(f"⏱️  Total time: {enriched.total_enrichment_time_ms:.0f}ms")
        print(f"📊 Success rate: {enriched.enrichment_rate*100:.0f}%")
        
        # Show enrichments
        for source, result in enriched.enrichments.items():
            if result.success:
                print(f"\n{source.value}:")
                print(f"  Confidence: {result.confidence_score:.2f}")
                print(f"  Time: {result.fetch_time_ms:.0f}ms")
                print(f"  Data: {json.dumps(result.data, indent=4)[:200]}...")
            else:
                print(f"\n{source.value}: ❌ Failed - {result.error}")


def example_batch_processing():
    """Demonstrate parallel batch processing."""
    print("\n=== Parallel Batch Processing Example ===")
    
    graph = create_batch_processing_graph()
    
    # Create batch of items
    batch_items = [f"Item-{i:03d}" for i in range(50)]
    
    print(f"Processing batch of {len(batch_items)} items...")
    
    shared = {
        "batch_items": batch_items,
        "batch_config": BatchConfiguration(
            batch_size=50,
            worker_count=4,
            max_retries=2
        )
    }
    
    start_time = time.time()
    graph.run(shared)
    elapsed = time.time() - start_time
    
    if "batch_result" in shared:
        result = shared["batch_result"]
        progress = result.progress
        
        print(f"\nBatch Processing Results:")
        print(f"✓ Processed: {progress.processed_items}/{progress.total_items}")
        print(f"✓ Successful: {progress.successful_items} ({progress.success_rate*100:.1f}%)")
        print(f"✗ Failed: {progress.failed_items}")
        print(f"⚡ Throughput: {progress.current_throughput:.1f} items/second")
        print(f"⏱️  Total time: {elapsed:.2f}s")
        
        # Show worker distribution
        worker_stats = {}
        for item_result in result.items_processed:
            worker = item_result.worker_id
            if worker not in worker_stats:
                worker_stats[worker] = {"count": 0, "time": 0}
            worker_stats[worker]["count"] += 1
            worker_stats[worker]["time"] += item_result.processing_time_ms
        
        print("\nWorker Statistics:")
        for worker, stats in worker_stats.items():
            print(f"  {worker}: {stats['count']} items, {stats['time']:.0f}ms total")


def example_mapreduce():
    """Demonstrate map-reduce pattern."""
    print("\n=== Map-Reduce Example ===")
    
    graph = create_mapreduce_graph()
    
    # Input data (documents for word count)
    documents = [
        "The quick brown fox jumps over the lazy dog",
        "The dog was not lazy but the fox was quick",
        "Python is great for data processing and parallel computing",
        "Parallel computing makes data processing much faster",
        "KayGraph supports parallel batch processing"
    ]
    
    print(f"Processing {len(documents)} documents for word count...")
    
    shared = {"mapreduce_input": documents}
    graph.run(shared)
    
    if "reduce_results" in shared and "top_results" in shared:
        results = shared["reduce_results"]
        top_words = shared["top_results"]
        
        print(f"\nMap-Reduce Results:")
        print(f"✓ Unique words: {len(results)}")
        print(f"✓ Total words: {sum(r.result for r in results)}")
        
        print("\nTop 10 words by frequency:")
        for i, word_result in enumerate(top_words[:10]):
            print(f"  {i+1}. '{word_result.key}': {word_result.result} occurrences")


def example_pipeline_parallelization():
    """Demonstrate parallel pipeline execution."""
    print("\n=== Parallel Pipeline Example ===")
    
    graph = create_pipeline_graph()
    
    # Input data for pipeline
    pipeline_input = [
        {"id": 1, "value": "data-1", "type": "A"},
        {"id": 2, "value": "data-2", "type": "B"},
        {"id": 3, "value": "data-3", "type": "A"},
        {"id": 4, "value": "data-4", "type": "C"},
        {"id": 5, "value": "data-5", "type": "B"}
    ]
    
    print(f"Processing {len(pipeline_input)} items through parallel pipeline...")
    
    shared = {"pipeline_input": pipeline_input}
    graph.run(shared)
    
    if "pipeline_execution" in shared:
        execution = shared["pipeline_execution"]
        
        print(f"\nPipeline Execution Results:")
        print(f"✓ Status: {'Success' if execution.overall_success else 'Failed'}")
        print(f"⚡ Speedup: {execution.parallel_speedup:.2f}x")
        print(f"⏱️  Total time: {execution.total_execution_time_ms:.0f}ms")
        print(f"🔧 Bottleneck: {execution.bottleneck_stage}")
        
        print("\nStage Performance:")
        for stage_result in execution.stage_results:
            print(f"\n  {stage_result.stage_name}:")
            print(f"    Parallelism: {stage_result.parallel_executions}")
            print(f"    Time: {stage_result.execution_time_ms:.0f}ms")
            print(f"    Success: {stage_result.success}")
            if stage_result.errors:
                print(f"    Errors: {len(stage_result.errors)}")
    
    # Show performance metrics
    if "performance_metrics" in shared:
        metrics = shared["performance_metrics"]
        print(f"\nOverall Performance Metrics:")
        print(f"  Speedup: {metrics.speedup_percentage:.0f}% faster")
        print(f"  Efficiency: {metrics.efficiency*100:.0f}%")
        print(f"  Optimal workers: {metrics.optimal_worker_count}")


def interactive_mode():
    """Interactive parallelization testing mode."""
    print("\n=== Interactive Parallelization Mode ===")
    print("Commands:")
    print("  validate <json>    - Run parallel validation")
    print("  enrich             - Run data enrichment")
    print("  batch <count>      - Process batch of items")
    print("  mapreduce <text>   - Run map-reduce on text")
    print("  pipeline <count>   - Run pipeline on items")
    print("  quit               - Exit")
    
    graphs = {
        "validation": create_validation_graph(),
        "enrichment": create_enrichment_graph(),
        "batch": create_batch_processing_graph(),
        "mapreduce": create_mapreduce_graph(),
        "pipeline": create_pipeline_graph()
    }
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                break
            
            parts = command.split(" ", 1)
            cmd = parts[0]
            
            if cmd == "validate" and len(parts) > 1:
                try:
                    data = json.loads(parts[1])
                    shared = {"input_data": data}
                    graphs["validation"].run(shared)
                    
                    if "validation_summary" in shared:
                        summary = shared["validation_summary"]
                        print(f"Validation: {summary.passed_checks}/{summary.total_checks} passed")
                        print(f"Speedup: {summary.speedup_factor:.2f}x")
                except json.JSONDecodeError:
                    print("Invalid JSON")
                    
            elif cmd == "enrich":
                shared = {"base_data": {"user_id": "123", "email": "test@example.com"}}
                graphs["enrichment"].run(shared)
                
                if "enriched_data" in shared:
                    enriched = shared["enriched_data"]
                    print(f"Enriched from {enriched.successful_sources}/{enriched.total_sources} sources")
                    
            elif cmd == "batch" and len(parts) > 1:
                try:
                    count = int(parts[1])
                    items = [f"item-{i}" for i in range(count)]
                    shared = {"batch_items": items}
                    graphs["batch"].run(shared)
                    
                    if "batch_result" in shared:
                        result = shared["batch_result"]
                        print(f"Processed {result.progress.processed_items} items")
                        print(f"Throughput: {result.progress.current_throughput:.1f} items/sec")
                except ValueError:
                    print("Invalid count")
                    
            elif cmd == "mapreduce" and len(parts) > 1:
                text = parts[1]
                shared = {"mapreduce_input": [text]}
                graphs["mapreduce"].run(shared)
                
                if "top_results" in shared:
                    top = shared["top_results"][:5]
                    print("Top words:", ", ".join(f"{r.key}:{r.result}" for r in top))
                    
            elif cmd == "pipeline" and len(parts) > 1:
                try:
                    count = int(parts[1])
                    items = [{"id": i, "value": f"data-{i}"} for i in range(count)]
                    shared = {"pipeline_input": items}
                    graphs["pipeline"].run(shared)
                    
                    if "pipeline_execution" in shared:
                        execution = shared["pipeline_execution"]
                        print(f"Pipeline: {'Success' if execution.overall_success else 'Failed'}")
                        print(f"Speedup: {execution.parallel_speedup:.2f}x")
                except ValueError:
                    print("Invalid count")
                    
            else:
                print("Invalid command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all parallelization examples."""
    example_parallel_validation()
    example_data_enrichment()
    example_batch_processing()
    example_mapreduce()
    example_pipeline_parallelization()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Workflow Parallelization Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input data for processing"
    )
    parser.add_argument(
        "--example",
        choices=["validation", "enrichment", "batch", "mapreduce", "pipeline", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="Number of parallel workers"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example == "all":
        run_all_examples()
    elif args.example == "validation":
        example_parallel_validation()
    elif args.example == "enrichment":
        example_data_enrichment()
    elif args.example == "batch":
        example_batch_processing()
    elif args.example == "mapreduce":
        example_mapreduce()
    elif args.example == "pipeline":
        example_pipeline_parallelization()
    elif args.input:
        # Default to validation
        try:
            data = json.loads(args.input)
            graph = create_validation_graph()
            shared = {"input_data": data}
            graph.run(shared)
            
            if "validation_summary" in shared:
                summary = shared["validation_summary"]
                print(f"Validation: {summary.passed_checks}/{summary.total_checks} passed")
                print(f"Speedup: {summary.speedup_factor:.2f}x")
        except json.JSONDecodeError:
            print("Invalid JSON input")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()