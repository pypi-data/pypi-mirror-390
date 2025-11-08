#!/usr/bin/env python3
"""
KayGraph Agent Control - Deterministic decision-making patterns.

Demonstrates how to implement routing based on classification,
decision trees, and multi-criteria control logic.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any, List
from kaygraph import Graph
from nodes import (
    # Intent classification
    IntentClassificationNode,
    QuestionHandlerNode,
    RequestHandlerNode,
    ComplaintHandlerNode,
    LowConfidenceHandlerNode,
    # Decision tree
    DecisionTreeNode,
    # Multi-criteria
    MultiCriteriaControlNode,
    # Threshold control
    ThresholdControlNode,
    # Default handlers
    DefaultHandlerNode
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_intent_routing_graph() -> Graph:
    """
    Create intent-based routing control flow.
    
    Routes user input to appropriate handlers based on classified intent.
    """
    # Create nodes
    classifier = IntentClassificationNode(confidence_threshold=0.7)
    question_handler = QuestionHandlerNode()
    request_handler = RequestHandlerNode()
    complaint_handler = ComplaintHandlerNode()
    low_confidence_handler = LowConfidenceHandlerNode()
    default_handler = DefaultHandlerNode()
    
    # Connect routing paths
    classifier - "question" >> question_handler
    classifier - "request" >> request_handler
    classifier - "complaint" >> complaint_handler
    classifier - "statement" >> default_handler
    classifier - "unknown" >> default_handler
    classifier - "low_confidence" >> low_confidence_handler
    
    return Graph(start=classifier)


def create_decision_tree_graph() -> Graph:
    """
    Create decision tree control flow.
    
    Uses a tree structure to make routing decisions.
    """
    # Define decision tree structure
    decision_tree = {
        "root": {
            "question": "Is this request urgent?",
            "yes_path": "check_complexity",
            "no_path": "normal_processing"
        },
        "check_complexity": {
            "question": "Is this request complex (requiring multiple steps)?",
            "yes_path": "expert_handling",
            "no_path": "quick_resolution"
        },
        "expert_handling": {
            "is_leaf": True,
            "action": "route_to_expert"
        },
        "quick_resolution": {
            "is_leaf": True,
            "action": "automated_response"
        },
        "normal_processing": {
            "question": "Does this require human review?",
            "yes_path": "human_review",
            "no_path": "automated_response"
        },
        "human_review": {
            "is_leaf": True,
            "action": "queue_for_review"
        },
        "automated_response": {
            "is_leaf": True,
            "action": "automated_response"
        }
    }
    
    # Create nodes
    tree_node = DecisionTreeNode(decision_tree=decision_tree)
    
    # Action handlers
    expert_handler = DefaultHandlerNode()
    automated_handler = DefaultHandlerNode()
    review_handler = DefaultHandlerNode()
    
    # Connect actions
    tree_node - "route_to_expert" >> expert_handler
    tree_node - "automated_response" >> automated_handler
    tree_node - "queue_for_review" >> review_handler
    tree_node - "default_action" >> automated_handler
    
    return Graph(start=tree_node)


def create_multi_criteria_graph() -> Graph:
    """
    Create multi-criteria control flow.
    
    Makes decisions based on multiple weighted factors.
    """
    # Define factors to evaluate
    factors_config = [
        {
            "name": "urgency",
            "weight": 0.3,
            "description": "How time-sensitive is this request?"
        },
        {
            "name": "complexity",
            "weight": 0.2,
            "description": "How complex is this request to fulfill?"
        },
        {
            "name": "impact",
            "weight": 0.3,
            "description": "What is the potential impact or importance?"
        },
        {
            "name": "sentiment",
            "weight": 0.2,
            "description": "What is the emotional tone (negative needs priority)?"
        }
    ]
    
    # Create nodes
    multi_criteria = MultiCriteriaControlNode(factors_config=factors_config)
    
    # Priority handlers
    high_priority = DefaultHandlerNode()
    normal_priority = DefaultHandlerNode()
    low_priority = DefaultHandlerNode()
    defer_handler = DefaultHandlerNode()
    
    # Connect based on priority decisions
    multi_criteria - "high_priority" >> high_priority
    multi_criteria - "normal_priority" >> normal_priority
    multi_criteria - "low_priority" >> low_priority
    multi_criteria - "defer" >> defer_handler
    
    return Graph(start=multi_criteria)


def create_threshold_control_graph() -> Graph:
    """
    Create threshold-based control flow.
    
    Routes based on metric thresholds.
    """
    # Define thresholds
    thresholds = [
        {
            "metric": "confidence_score",
            "threshold": 0.8,
            "comparison": "greater",
            "action_passed": "process",
            "action_failed": "review",
            "all_must_pass": False
        },
        {
            "metric": "risk_score",
            "threshold": 0.3,
            "comparison": "less",
            "action_passed": "process",
            "action_failed": "escalate"
        }
    ]
    
    # Create nodes
    threshold_control = ThresholdControlNode(thresholds=thresholds)
    process_handler = DefaultHandlerNode()
    review_handler = DefaultHandlerNode()
    escalate_handler = DefaultHandlerNode()
    
    # Connect based on threshold actions
    threshold_control - "process" >> process_handler
    threshold_control - "review" >> review_handler
    threshold_control - "escalate" >> escalate_handler
    
    return Graph(start=threshold_control)


def example_intent_routing():
    """Demonstrate intent-based routing."""
    print("\n=== Intent-Based Routing Example ===")
    
    graph = create_intent_routing_graph()
    
    # Test different intents
    test_inputs = [
        "What is machine learning?",
        "Please schedule a meeting for tomorrow at 3pm",
        "I'm very unhappy with the service I received",
        "The weather is nice today",
        "asdfjkl"  # Gibberish to test low confidence
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        
        shared = {"user_input": test_input}
        graph.run(shared)
        
        # Show results
        if "intent_classification" in shared:
            intent = shared["intent_classification"]
            print(f"Intent: {intent.intent} (confidence: {intent.confidence})")
            print(f"Reasoning: {intent.reasoning}")
        
        if "response" in shared:
            print(f"Response: {shared['response']}")
            print(f"Type: {shared.get('response_type', 'unknown')}")


def example_decision_tree():
    """Demonstrate decision tree control."""
    print("\n=== Decision Tree Control Example ===")
    
    graph = create_decision_tree_graph()
    
    # Test scenarios
    test_cases = [
        {
            "input": "URGENT: Server is down and customers can't access the site!",
            "context": {"severity": "critical"}
        },
        {
            "input": "Can you update my email address in the system?",
            "context": {"severity": "low"}
        },
        {
            "input": "I need help setting up a complex integration with multiple APIs",
            "context": {"technical_complexity": "high"}
        }
    ]
    
    for test_case in test_cases:
        print(f"\nInput: '{test_case['input']}'")
        
        shared = {
            "user_input": test_case["input"],
            "context": test_case.get("context", {})
        }
        graph.run(shared)
        
        if "decision_result" in shared:
            result = shared["decision_result"]
            print(f"Decision path: {shared.get('decision_path', 'N/A')}")
            print(f"Final action: {result.final_action}")
            print(f"Confidence: {result.confidence}")


def example_multi_criteria():
    """Demonstrate multi-criteria control."""
    print("\n=== Multi-Criteria Control Example ===")
    
    graph = create_multi_criteria_graph()
    
    # Test with different inputs
    test_inputs = [
        "URGENT: Critical security vulnerability needs immediate patching!",
        "Could you help me understand how to use the new feature?",
        "I'm extremely frustrated - this is the third time this week the system has failed!",
        "Just wanted to let you know the report looks good"
    ]
    
    for test_input in test_inputs:
        print(f"\nInput: '{test_input}'")
        
        shared = {"user_input": test_input}
        graph.run(shared)
        
        if "multi_criteria_decision" in shared:
            decision = shared["multi_criteria_decision"]
            print(f"Decision: {decision.decision}")
            print(f"Total Score: {decision.total_score:.2f}")
            print("Factor Scores:")
            for factor in decision.factors:
                print(f"  - {factor.factor_name}: {factor.normalized_score:.2f} (weight: {factor.weight})")
            print(f"Reasoning: {decision.reasoning}")


def example_threshold_control():
    """Demonstrate threshold-based control."""
    print("\n=== Threshold-Based Control Example ===")
    
    graph = create_threshold_control_graph()
    
    # Test with different metrics
    test_cases = [
        {
            "input": "Process this standard request",
            "metrics": {"confidence_score": 0.95, "risk_score": 0.1}
        },
        {
            "input": "Suspicious activity detected",
            "metrics": {"confidence_score": 0.6, "risk_score": 0.8}
        },
        {
            "input": "Need clarification on this request",
            "metrics": {"confidence_score": 0.4, "risk_score": 0.2}
        }
    ]
    
    for test_case in test_cases:
        print(f"\nInput: '{test_case['input']}'")
        print(f"Metrics: {test_case['metrics']}")
        
        shared = {
            "user_input": test_case["input"],
            "metrics": test_case["metrics"]
        }
        graph.run(shared)
        
        if "threshold_decision" in shared:
            decision = shared["threshold_decision"]
            print(f"Action: {decision.final_action}")
            print(f"Checks passed: {decision.passed_count}/{decision.total_count}")
            for check in decision.checks:
                status = "✓" if check.passed else "✗"
                print(f"  {status} {check.metric_name}: {check.current_value} {check.comparison} {check.threshold}")


def interactive_mode():
    """Interactive control testing mode."""
    print("\n=== Interactive Control Mode ===")
    print("Test different control patterns:")
    print("  intent - Test intent classification")
    print("  tree - Test decision tree")
    print("  multi - Test multi-criteria")
    print("  quit - Exit")
    
    # Create intent graph for interactive testing
    intent_graph = create_intent_routing_graph()
    
    while True:
        try:
            command = input("\nCommand: ").strip().lower()
            
            if command == "quit":
                break
            elif command == "intent":
                user_input = input("Enter text to classify: ").strip()
                if user_input:
                    shared = {"user_input": user_input}
                    intent_graph.run(shared)
                    
                    if "intent_classification" in shared:
                        intent = shared["intent_classification"]
                        print(f"\nIntent: {intent.intent} ({intent.confidence:.2f})")
                        print(f"Response: {shared.get('response', 'N/A')}")
            
            elif command == "tree":
                print("Decision tree mode - enter scenario")
                user_input = input("Describe situation: ").strip()
                if user_input:
                    tree_graph = create_decision_tree_graph()
                    shared = {"user_input": user_input}
                    tree_graph.run(shared)
                    
                    if "decision_result" in shared:
                        print(f"Decision: {shared['decision_result'].final_action}")
            
            elif command == "multi":
                print("Multi-criteria mode - enter request")
                user_input = input("Enter request: ").strip()
                if user_input:
                    multi_graph = create_multi_criteria_graph()
                    shared = {"user_input": user_input}
                    multi_graph.run(shared)
                    
                    if "multi_criteria_decision" in shared:
                        decision = shared["multi_criteria_decision"]
                        print(f"Priority: {decision.decision} (score: {decision.total_score:.2f})")
            
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all control examples."""
    example_intent_routing()
    example_decision_tree()
    example_multi_criteria()
    example_threshold_control()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Control Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Text input for intent classification"
    )
    parser.add_argument(
        "--example",
        choices=["routing", "decision-tree", "multi-criteria", "threshold", "all"],
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
    elif args.example == "routing":
        example_intent_routing()
    elif args.example == "decision-tree":
        example_decision_tree()
    elif args.example == "multi-criteria":
        example_multi_criteria()
    elif args.example == "threshold":
        example_threshold_control()
    elif args.input:
        # Default to intent routing
        graph = create_intent_routing_graph()
        shared = {"user_input": args.input}
        graph.run(shared)
        
        if "intent_classification" in shared:
            intent = shared["intent_classification"]
            print(f"Intent: {intent.intent} (confidence: {intent.confidence})")
            print(f"Response: {shared.get('response', 'N/A')}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()