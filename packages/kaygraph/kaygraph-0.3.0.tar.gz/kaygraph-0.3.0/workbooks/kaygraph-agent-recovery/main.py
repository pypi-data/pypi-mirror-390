#!/usr/bin/env python3
"""
KayGraph Agent Recovery - Resilient error handling patterns.

Demonstrates how to build fault-tolerant AI systems with retry logic,
fallback strategies, circuit breakers, and graceful degradation.
"""

import sys
import json
import logging
import argparse
import time
from typing import Dict, Any, List
from kaygraph import Graph
from nodes import (
    RetryNode,
    FallbackNode,
    CircuitBreakerNode,
    GracefulDegradationNode,
    ErrorAggregationNode,
    HealthCheckNode
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_retry_graph() -> Graph:
    """
    Create a graph with retry pattern.
    Demonstrates automatic retry with exponential backoff.
    """
    # Create retry node with configuration
    retry_node = RetryNode(
        max_retries=3,
        initial_backoff=1.0,
        backoff_multiplier=2.0,
        max_backoff=10.0
    )
    
    # Simple success/failure handlers
    success_handler = lambda shared: shared.update({"status": "completed"})
    failure_handler = lambda shared: shared.update({"status": "failed"})
    
    # Connect based on retry result
    # Note: We'd normally use proper Node classes for handlers
    
    return Graph(start=retry_node)


def create_fallback_graph() -> Graph:
    """
    Create a graph with fallback pattern.
    Demonstrates graceful degradation through multiple methods.
    """
    fallback_node = FallbackNode()
    
    return Graph(start=fallback_node)


def create_circuit_breaker_graph() -> Graph:
    """
    Create a graph with circuit breaker pattern.
    Prevents cascading failures by blocking calls after threshold.
    """
    circuit_node = CircuitBreakerNode(
        failure_threshold=3,
        success_threshold=2,
        timeout_seconds=5.0
    )
    
    return Graph(start=circuit_node)


def create_degradation_graph() -> Graph:
    """
    Create a graph with graceful degradation.
    Provides partial functionality when full features fail.
    """
    degradation_node = GracefulDegradationNode()
    
    return Graph(start=degradation_node)


def create_error_aggregation_graph() -> Graph:
    """
    Create a graph that aggregates errors.
    Useful for batch processing with error analysis.
    """
    aggregation_node = ErrorAggregationNode()
    
    return Graph(start=aggregation_node)


def create_health_check_graph() -> Graph:
    """
    Create a graph for system health monitoring.
    Checks multiple services and reports overall health.
    """
    services = ["auth_service", "llm_service", "database", "cache", "queue"]
    health_node = HealthCheckNode(services=services)
    
    return Graph(start=health_node)


def example_retry_pattern():
    """Demonstrate retry with backoff."""
    print("\n=== Retry Pattern Example ===")
    print("Testing automatic retry with exponential backoff...")
    
    graph = create_retry_graph()
    shared = {
        "input": "Important data that must be processed reliably"
    }
    
    print("\nProcessing with potential failures...")
    graph.run(shared)
    
    if "recovery_result" in shared:
        result = shared["recovery_result"]
        print(f"\nResult: {'Success' if result.success else 'Failed'}")
        print(f"Attempts: {result.attempts_made}")
        print(f"Duration: {result.total_duration_seconds:.2f}s")
        
        if result.success:
            print(f"Output: {result.result[:100]}...")
        else:
            print(f"Error: {result.error.message}")


def example_fallback_pattern():
    """Demonstrate fallback strategies."""
    print("\n=== Fallback Pattern Example ===")
    print("Testing cascading fallback methods...")
    
    graph = create_fallback_graph()
    
    test_inputs = [
        "John Smith, john@example.com, 30 years old, phone: 555-1234",
        "Contact Jane Doe at jane@test.com",
        "Bob mentioned something",
        ""
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        
        shared = {"input": test_input}
        graph.run(shared)
        
        if "fallback_result" in shared:
            result = shared["fallback_result"]
            print(f"Method used: {result.method_used} (level {result.fallback_level})")
            print(f"Result: {result.result}")
            if result.missing_features:
                print(f"Missing: {result.missing_features}")


def example_circuit_breaker():
    """Demonstrate circuit breaker pattern."""
    print("\n=== Circuit Breaker Pattern Example ===")
    print("Testing circuit breaker with failing service...")
    
    graph = create_circuit_breaker_graph()
    
    # Simulate multiple calls to show circuit breaker behavior
    for i in range(10):
        print(f"\nAttempt {i+1}:")
        
        shared = {"input": f"Request {i+1}"}
        
        try:
            graph.run(shared)
            
            if "circuit_result" in shared:
                result = shared["circuit_result"]
                state = shared.get("circuit_state", "unknown")
                
                print(f"Circuit State: {state}")
                print(f"Success: {result['success']}")
                
                if not result['success']:
                    print(f"Error: {result.get('error', 'Unknown')}")
                    
        except RuntimeError as e:
            print(f"Circuit breaker blocked call: {e}")
        
        # Small delay between calls
        time.sleep(0.5)


def example_graceful_degradation():
    """Demonstrate graceful degradation."""
    print("\n=== Graceful Degradation Example ===")
    print("Testing progressive feature degradation...")
    
    graph = create_degradation_graph()
    
    queries = [
        "Analyze the impact of climate change on global agriculture",
        "What are the benefits of renewable energy?",
        "Hello world"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        
        shared = {"query": query}
        graph.run(shared)
        
        if "degradation_result" in shared:
            result = shared["degradation_result"]
            print(f"Degradation level: {result['degradation_level']}")
            print(f"Available features: {result['features_available']}")
            
            # Show what we got
            if result["full_analysis"]:
                print(f"Full analysis: Available")
            elif result["summary"]:
                print(f"Summary: {result['summary']}")
            elif result["keywords"]:
                print(f"Keywords: {result['keywords']}")
            else:
                print(f"Basic: {result['basic_response']}")


def example_error_aggregation():
    """Demonstrate error aggregation for batch processing."""
    print("\n=== Error Aggregation Example ===")
    print("Processing batch with error tracking...")
    
    graph = create_error_aggregation_graph()
    
    # Create batch of items
    batch_items = [f"Item_{i}" for i in range(20)]
    
    shared = {"batch_items": batch_items}
    graph.run(shared)
    
    if "batch_result" in shared:
        result = shared["batch_result"]
        print(f"\nBatch Processing Summary:")
        print(f"Total items: {result['total_items']}")
        print(f"Successful: {result['successful']}")
        print(f"Failed: {result['failed']}")
        print(f"Success rate: {result['successful']/result['total_items']*100:.1f}%")
        
        if result["failed"] > 0:
            analysis = result["error_analysis"]
            print(f"\nError Analysis:")
            print(f"Error types: {analysis['error_types']}")
            print(f"Most common: {analysis['most_common_type']}")
            print(f"Trend: {analysis['recent_trend']}")


def example_health_monitoring():
    """Demonstrate health check monitoring."""
    print("\n=== Health Monitoring Example ===")
    print("Checking system health...")
    
    graph = create_health_check_graph()
    
    # Run health check multiple times
    for i in range(3):
        print(f"\nHealth Check {i+1}:")
        
        shared = {}
        graph.run(shared)
        
        if "system_health" in shared:
            health = shared["system_health"]
            print(f"Overall Health: {'✅ Healthy' if health.overall_health else '❌ Degraded'}")
            
            # Show service details
            for service_name, service_health in health.services.items():
                status = "✅" if service_health.healthy else "❌"
                print(f"  {status} {service_name}", end="")
                
                if service_health.healthy:
                    print(f" ({service_health.response_time_ms:.0f}ms)")
                else:
                    print(f" - {service_health.error_message}")
            
            if health.degraded_services:
                print(f"\nDegraded services: {', '.join(health.degraded_services)}")
        
        time.sleep(1)


def interactive_mode():
    """Interactive recovery testing mode."""
    print("\n=== Interactive Recovery Mode ===")
    print("Commands:")
    print("  retry <text>     - Test retry pattern")
    print("  fallback <text>  - Test fallback pattern")
    print("  circuit          - Test circuit breaker")
    print("  degrade <query>  - Test degradation")
    print("  health           - Check system health")
    print("  quit             - Exit")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                break
                
            parts = command.split(" ", 1)
            cmd = parts[0]
            
            if cmd == "retry" and len(parts) > 1:
                graph = create_retry_graph()
                shared = {"input": parts[1]}
                graph.run(shared)
                
                if "recovery_result" in shared:
                    result = shared["recovery_result"]
                    print(f"Success: {result.success} (attempts: {result.attempts_made})")
                    
            elif cmd == "fallback" and len(parts) > 1:
                graph = create_fallback_graph()
                shared = {"input": parts[1]}
                graph.run(shared)
                
                if "fallback_result" in shared:
                    result = shared["fallback_result"]
                    print(f"Used: {result.method_used}")
                    print(f"Result: {result.result}")
                    
            elif cmd == "circuit":
                graph = create_circuit_breaker_graph()
                shared = {"input": "Test request"}
                
                try:
                    graph.run(shared)
                    if "circuit_state" in shared:
                        print(f"Circuit: {shared['circuit_state']}")
                except RuntimeError as e:
                    print(f"Blocked: {e}")
                    
            elif cmd == "degrade" and len(parts) > 1:
                graph = create_degradation_graph()
                shared = {"query": parts[1]}
                graph.run(shared)
                
                if "degradation_level" in shared:
                    print(f"Degradation: {shared['degradation_level']}")
                    
            elif cmd == "health":
                graph = create_health_check_graph()
                shared = {}
                graph.run(shared)
                
                if "system_health" in shared:
                    health = shared["system_health"]
                    print(f"System: {'Healthy' if health.overall_health else 'Degraded'}")
                    
            else:
                print("Invalid command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all recovery examples."""
    example_retry_pattern()
    example_fallback_pattern()
    example_circuit_breaker()
    example_graceful_degradation()
    example_error_aggregation()
    example_health_monitoring()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Recovery Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Text input for recovery testing"
    )
    parser.add_argument(
        "--example",
        choices=["retry", "fallback", "circuit-breaker", "degradation", "aggregation", "health", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    elif args.example == "all":
        run_all_examples()
    elif args.example == "retry":
        example_retry_pattern()
    elif args.example == "fallback":
        example_fallback_pattern()
    elif args.example == "circuit-breaker":
        example_circuit_breaker()
    elif args.example == "degradation":
        example_graceful_degradation()
    elif args.example == "aggregation":
        example_error_aggregation()
    elif args.example == "health":
        example_health_monitoring()
    elif args.input:
        # Default to retry pattern
        graph = create_retry_graph()
        shared = {"input": args.input}
        graph.run(shared)
        
        if "recovery_result" in shared:
            result = shared["recovery_result"]
            print(f"Result: {'Success' if result.success else 'Failed'}")
            print(f"Attempts: {result.attempts_made}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()