"""
Advanced Declarative Workflow Patterns Demo

Demonstrates sophisticated enterprise-grade patterns including:
- Circuit breaker pattern for fault tolerance
- Advanced template engine with Jinja2 support
- Dynamic orchestration with AI-driven planning
- Tool registry for dynamic function calling
- Intelligent caching system
"""

import sys
import logging
import time
from typing import Dict, Any, List

# Add the utils directory to path
sys.path.insert(0, '.')

from kaygraph import Graph
from utils import call_llm
from nodes_advanced import (
    CircuitBreakerNode, AdvancedTemplateNode, ToolRegistryNode,
    DynamicOrchestratorNode, IntelligentCacheNode,
    create_advanced_node, BUILTIN_TOOLS
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_circuit_breaker_pattern():
    """Demonstrate circuit breaker pattern for fault tolerance."""
    print("=" * 70)
    print("⚡ CIRCUIT BREAKER PATTERN DEMO")
    print("=" * 70)

    # Create circuit breaker
    circuit_breaker = CircuitBreakerNode(
        failure_threshold=3,
        recovery_timeout=5.0,
        node_id="api_circuit_breaker"
    )

    print("🔧 Circuit Breaker Configuration:")
    print(f"   Failure Threshold: {circuit_breaker.failure_threshold}")
    print(f"   Recovery Timeout: {circuit_breaker.recovery_timeout}s")
    print(f"   Initial State: {circuit_breaker.state.value}")
    print()

    # Test successful operations
    print("✅ Testing successful operations:")
    for i in range(3):
        shared = {"operation": f"test_{i+1}"}
        try:
            result = circuit_breaker.run(shared)
            metrics = shared["circuit_breaker_metrics"]
            print(f"   Operation {i+1}: SUCCESS (State: {metrics['state']}, Success Rate: {metrics['success_rate']:.1%})")
        except Exception as e:
            print(f"   Operation {i+1}: FAILED - {e}")

    print()

    # Test failure scenarios
    print("❌ Testing failure scenarios:")
    for i in range(5):
        shared = {"operation": f"test_{i+4}", "simulate_failure": True}
        try:
            result = circuit_breaker.run(shared)
            print(f"   Operation {i+4}: SUCCESS (unexpected)")
        except Exception as e:
            metrics = shared.get("circuit_breaker_metrics", {})
            print(f"   Operation {i+4}: BLOCKED - {e} (State: {metrics.get('state', 'unknown')})")

    print()

    # Test recovery
    print("🔄 Testing recovery:")
    print("   Waiting for recovery timeout...")
    time.sleep(6)  # Wait for recovery timeout

    shared = {"operation": "recovery_test"}
    try:
        result = circuit_breaker.run(shared)
        metrics = shared["circuit_breaker_metrics"]
        print(f"   Recovery Test: SUCCESS (State: {metrics['state']}, Success Rate: {metrics['success_rate']:.1%})")
    except Exception as e:
        print(f"   Recovery Test: FAILED - {e}")

    print()


def demo_advanced_template_engine():
    """Demonstrate advanced template engine with Jinja2 support."""
    print("=" * 70)
    print("🎨 ADVANCED TEMPLATE ENGINE DEMO")
    print("=" * 70)

    # Define custom filters
    def format_duration(seconds):
        """Format duration in seconds to human-readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds//60}m {seconds%60}s"
        else:
            return f"{seconds//3600}h {(seconds%3600)//60}m"

    def urgency_color(level):
        """Return color based on urgency level."""
        if level >= 0.8:
            return "🔴 High"
        elif level >= 0.5:
            return "🟡 Medium"
        else:
            return "🟢 Low"

    # Complex template with Jinja2 syntax
    template = """
    📊 ANALYSIS REPORT
    ================================

    User: {{ user.name | title }}
    Date: {{ now.strftime('%Y-%m-%d %H:%M') }}

    {% if tasks %}
    📋 TASKS ({{ tasks|length }} total):
    {% for task in tasks %}
    • {{ task.title|title }} - {{ task.urgency|urgency_color }}
      Duration: {{ task.estimated_time|format_duration }}
      Status: {% if task.completed %}✅ Completed{% else %}⏳ Pending{% endif %}
    {% endfor %}

    {% if high_priority_tasks %}
    🚨 HIGH PRIORITY TASKS:
    {% for task in high_priority_tasks %}
    • {{ task.title }} (Due: {{ task.due_date }})
    {% endfor %}
    {% endif %}
    {% endif %}

    {% if metrics %}
    📈 PERFORMANCE METRICS:
    • Success Rate: {{ "%.1f"|format(metrics.success_rate * 100) }}%
    • Average Response Time: {{ metrics.avg_response_time|format_duration }}
    • Total Operations: {{ metrics.total_operations }}
    {% endif %}

    {% if recommendations %}
    💡 RECOMMENDATIONS:
    {% for rec in recommendations %}
    • {{ rec }}
    {% endfor %}
    {% endif %}
    """

    # Create advanced template node
    template_node = AdvancedTemplateNode(
        template=template,
        template_engine="jinja2",
        filters={
            "format_duration": format_duration,
            "urgency_color": urgency_color
        },
        node_id="advanced_template"
    )

    print("✅ Created Advanced Template Node:")
    print(f"   Template Engine: {template_node.template_engine}")
    print(f"   Custom Filters: {len(template_node.filters)}")
    print()

    # Test data
    shared_data = {
        "user": {"name": "john doe", "role": "developer"},
        "tasks": [
            {
                "title": "implement user authentication",
                "urgency": 0.9,
                "estimated_time": 3600,
                "completed": True,
                "due_date": "2025-01-20"
            },
            {
                "title": "optimize database queries",
                "urgency": 0.6,
                "estimated_time": 1800,
                "completed": False,
                "due_date": "2025-01-25"
            },
            {
                "title": "write documentation",
                "urgency": 0.3,
                "estimated_time": 900,
                "completed": False,
                "due_date": "2025-01-30"
            }
        ],
        "metrics": {
            "success_rate": 0.85,
            "avg_response_time": 150,
            "total_operations": 234
        },
        "recommendations": [
            "Focus on completing high-priority tasks first",
            "Consider breaking down large tasks into smaller ones",
            "Document progress for better tracking"
        ]
    }

    try:
        result = template_node.run(shared_data)
        rendered = shared_data["rendered_template"]
        metadata = shared_data["template_metadata"]

        print("🎨 Rendered Template:")
        print(rendered)
        print()
        print("📊 Template Metadata:")
        print(f"   Engine: {metadata['engine']}")
        print(f"   Variables Used: {metadata['variables_count']}")
        print(f"   Rendered Length: {metadata['rendered_length']} characters")

    except Exception as e:
        print(f"❌ Template rendering failed: {e}")

    print()


def demo_tool_registry():
    """Demonstrate dynamic tool registry and function calling."""
    print("=" * 70)
    print("🔧 TOOL REGISTRY DEMO")
    print("=" * 70)

    # Create custom tools
    def sentiment_analysis_tool(text: str) -> Dict[str, Any]:
        """Analyze sentiment of text (simulated)."""
        positive_words = ["good", "great", "excellent", "amazing", "wonderful"]
        negative_words = ["bad", "terrible", "awful", "horrible", "disappointing"]

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return {
            "sentiment": sentiment,
            "positive_score": positive_count / max(1, len(words)),
            "negative_score": negative_count / max(1, len(words)),
            "word_count": len(words)
        }

    def weather_tool(location: str, units: str = "celsius") -> Dict[str, Any]:
        """Get weather information (simulated)."""
        return {
            "location": location,
            "temperature": 22 if units == "celsius" else 72,
            "condition": "partly cloudy",
            "humidity": 65,
            "units": units
        }

    # Create tool registry
    tool_registry = ToolRegistryNode(
        tools={
            "sentiment_analysis": sentiment_analysis_tool,
            "weather": weather_tool,
            **BUILTIN_TOOLS  # Include built-in tools
        },
        auto_discover=True,
        node_id="tool_registry"
    )

    print("✅ Tool Registry Configuration:")
    print(f"   Registered Tools: {len(tool_registry.tools)}")
    print(f"   Auto-Discover: {tool_registry.auto_discover}")
    print(f"   Available Tools: {list(tool_registry.tools.keys())}")
    print()

    # Test tool calls
    tool_calls = [
        {
            "tool": "sentiment_analysis",
            "parameters": {"text": "This is an absolutely amazing product! I love it!"}
        },
        {
            "tool": "weather",
            "parameters": {"location": "New York", "units": "celsius"}
        },
        {
            "tool": "web_search",
            "parameters": {"query": "KayGraph declarative workflows", "max_results": 5}
        },
        {
            "tool": "data_analysis",
            "parameters": {
                "data": [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}],
                "analysis_type": "summary"
            }
        },
        {
            "tool": "nonexistent_tool",
            "parameters": {"test": "value"}
        }
    ]

    shared_data = {
        "tool_calls": tool_calls
    }

    try:
        result = tool_registry.run(shared_data)
        results = shared_data["tool_results"]
        summary = shared_data["tool_execution_summary"]

        print("🔧 Tool Execution Results:")
        print()

        for tool_result in results:
            tool_name = tool_result.get("tool", "unknown")
            success = tool_result.get("success", False)
            status = "✅" if success else "❌"

            print(f"{status} {tool_name}:")
            if success:
                if "result" in tool_result:
                    result_data = tool_result["result"]
                    if isinstance(result_data, dict):
                        for key, value in result_data.items():
                            print(f"   {key}: {value}")
                    else:
                        print(f"   Result: {result_data}")
            else:
                print(f"   Error: {tool_result.get('error', 'Unknown error')}")
            print()

        print("📊 Execution Summary:")
        print(f"   Total Calls: {summary['total_calls']}")
        print(f"   Successful: {summary['successful_calls']}")
        print(f"   Failed: {summary['failed_calls']}")
        print(f"   Tools Used: {', '.join(summary['tools_used'])}")

    except Exception as e:
        print(f"❌ Tool registry execution failed: {e}")

    print()


def demo_dynamic_orchestrator():
    """Demonstrate dynamic orchestration with AI-driven planning."""
    print("=" * 70)
    print("🎭 DYNAMIC ORCHESTRATOR DEMO")
    print("=" * 70)

    # Define worker pool
    worker_pool = {
        "analyzer": ["analysis", "validation", "research"],
        "generator": ["generation", "creation", "writing"],
        "validator": ["validation", "review", "quality_check"],
        "executor": ["execution", "implementation", "testing"]
    }

    # Create dynamic orchestrator
    orchestrator = DynamicOrchestratorNode(
        objective_template="Create a comprehensive {project_type} for {target_audience}",
        worker_pool=worker_pool,
        planning_strategy="ai_driven",  # Could also be "rule_based"
        node_id="dynamic_orchestrator"
    )

    print("✅ Dynamic Orchestrator Configuration:")
    print(f"   Worker Pool: {len(worker_pool)} workers")
    print(f"   Planning Strategy: {orchestrator.planning_strategy}")
    print(f"   Available Capabilities: {list(set(capability for workers in worker_pool.values() for capability in workers))}")
    print()

    # Test different objectives
    test_objectives = [
        {"project_type": "weather dashboard", "target_audience": "data analysts"},
        {"project_type": "customer support system", "target_audience": "support agents"},
        {"project_type": "learning management system", "target_audience": "educational institutions"}
    ]

    for i, objective_data in enumerate(test_objectives, 1):
        print(f"🎯 Objective {i}: Create a {objective_data['project_type']} for {objective_data['target_audience']}")
        print("-" * 50)

        shared_data = objective_data.copy()

        try:
            result = orchestrator.run(shared_data)
            orchestration_result = shared_data["orchestration_result"]

            print(f"   📋 Planned Tasks: {orchestration_result['orchestration_summary']['tasks_planned']}")
            print(f"   ✅ Executed Tasks: {orchestration_result['orchestration_summary']['tasks_executed']}")
            print(f"   🎯 Successful Tasks: {orchestration_result['orchestration_summary']['successful_tasks']}")

            # Show task details
            tasks = orchestration_result.get("task_plan", {}).get("tasks", [])
            if tasks:
                print("   📝 Task Breakdown:")
                for task in tasks[:3]:  # Show first 3 tasks
                    print(f"   • {task.get('description', 'No description')}")
                    print(f"     Worker: {task.get('assigned_worker', 'unassigned')}")
                    print(f"     Duration: {task.get('estimated_duration', 0)}s")

        except Exception as e:
            print(f"   ❌ Orchestration failed: {e}")

        print()

    print()


def demo_intelligent_caching():
    """Demonstrate intelligent caching system."""
    print("=" * 70)
    print("💾 INTELLIGENT CACHING DEMO")
    print("=" * 70)

    # Test different caching strategies
    strategies = ["memory", "multi_level"]  # Skip Redis unless available

    for strategy in strategies:
        print(f"🔄 Testing {strategy.upper()} Caching Strategy:")
        print("-" * 50)

        # Create cache node
        cache_node = IntelligentCacheNode(
            cache_strategy=strategy,
            ttl=10,  # 10 seconds TTL for demo
            max_size=5,  # Small cache for demo
            node_id=f"{strategy}_cache"
        )

        # Test data
        test_requests = [
            {"data": "user_profile_123", "model": "gpt-4", "temperature": 0.7},
            {"data": "user_profile_123", "model": "gpt-4", "temperature": 0.7},  # Same - should hit cache
            {"data": "user_profile_456", "model": "gpt-4", "temperature": 0.7},  # Different
            {"data": "user_profile_123", "model": "gpt-3.5", "temperature": 0.7},  # Different model
            {"data": "user_profile_789", "model": "gpt-4", "temperature": 0.7},
            {"data": "user_profile_123", "model": "gpt-4", "temperature": 0.7},  # Should hit cache again
        ]

        cache_hits = 0
        cache_misses = 0

        for i, request in enumerate(test_requests, 1):
            shared_data = {
                "cache_input": request["data"],
                "model": request["model"],
                "temperature": request["temperature"],
                "max_tokens": 1000
            }

            try:
                result = cache_node.run(shared_data)
                cache_result = shared_data["cache_result"]

                if cache_result["cache_hit"]:
                    cache_hits += 1
                    status = "✅ HIT"
                else:
                    cache_misses += 1
                    status = "❌ MISS"

                print(f"   Request {i}: {status} (Key: {cache_result['cache_key'][:8]}...)")

            except Exception as e:
                print(f"   Request {i}: ❌ ERROR - {e}")

        # Show cache statistics
        if "cache_statistics" in shared_data:
            stats = shared_data["cache_statistics"]
            print(f"   📊 Cache Statistics:")
            print(f"      Strategy: {stats['cache_strategy']}")
            print(f"      Cache Size: {stats['memory_cache_size']}/{stats['max_cache_size']}")
            print(f"      TTL: {stats['ttl']}s")
            print(f"      Redis Available: {stats['redis_available']}")

        print(f"   🎯 Performance: {cache_hits} hits, {cache_misses} misses ({cache_hits/(cache_hits+cache_misses):.1%} hit rate)")
        print()


def create_advanced_workflow_demo():
    """Demonstrate a workflow combining multiple advanced patterns."""
    print("=" * 70)
    print("🔄 ADVANCED WORKFLOW COMBINATION DEMO")
    print("=" * 70)

    # Create advanced nodes
    template_node = AdvancedTemplateNode(
        template="Generate a {{content_type}} for {{audience}} about {{topic}}",
        template_engine="jinja2",
        node_id="content_generator_template"
    )

    circuit_breaker = CircuitBreakerNode(
        failure_threshold=2,
        recovery_timeout=2.0,
        node_id="api_circuit_breaker"
    )

    cache_node = IntelligentCacheNode(
        cache_strategy="multi_level",
        ttl=30,
        node_id="content_cache"
    )

    # Build workflow
    template_node >> circuit_breaker >> cache_node

    workflow = Graph(start=template_node)

    print("✅ Advanced Workflow Created:")
    print("   Template Generator → Circuit Breaker → Intelligent Cache")
    print()

    # Test workflow
    test_cases = [
        {"content_type": "blog post", "audience": "developers", "topic": "declarative workflows"},
        {"content_type": "tutorial", "audience": "beginners", "topic": "KayGraph basics"},
        {"content_type": "blog post", "audience": "developers", "topic": "declarative workflows"},  # Should hit cache
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"🔄 Test Case {i}:")
        print(f"   Content: {test_case['content_type']}")
        print(f"   Audience: {test_case['audience']}")
        print(f"   Topic: {test_case['topic']}")

        shared_data = test_case.copy()

        try:
            workflow.run(shared_data)

            # Show results
            if "cache_result" in shared_data:
                cache_result = shared_data["cache_result"]
                cache_status = "✅ HIT" if cache_result["cache_hit"] else "❌ MISS"
                print(f"   Cache Status: {cache_status}")

            if "circuit_breaker_metrics" in shared_data:
                cb_metrics = shared_data["circuit_breaker_metrics"]
                print(f"   Circuit Breaker: {cb_metrics['state']} ({cb_metrics['success_rate']:.1%} success rate)")

        except Exception as e:
            print(f"   ❌ Workflow failed: {e}")

        print()

    print("🎉 Advanced workflow demonstration completed!")


def main():
    """Run all advanced pattern demonstrations."""
    print("🚀 KayGraph Advanced Declarative Workflow Patterns")
    print("=" * 70)
    print("This demo showcases enterprise-grade patterns including circuit breakers,")
    print("advanced templates, dynamic orchestration, tool registries, and intelligent caching.")
    print()

    try:
        # Run individual demos
        demo_circuit_breaker_pattern()
        demo_advanced_template_engine()
        demo_tool_registry()
        demo_dynamic_orchestrator()
        demo_intelligent_caching()
        create_advanced_workflow_demo()

        print("=" * 70)
        print("🎉 All advanced pattern demonstrations completed!")
        print("=" * 70)

    except Exception as e:
        logger.error(f"Advanced patterns demo failed: {e}")
        print(f"\n❌ Error: {e}")
        print("\nSome advanced features may require additional dependencies:")
        print("• Jinja2: pip install jinja2")
        print("• Redis: pip install redis")


if __name__ == "__main__":
    main()