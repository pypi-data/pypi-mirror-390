#!/usr/bin/env python3
"""
KayGraph Agent Feedback - Human-in-the-loop patterns.

Demonstrates how to implement approval workflows, feedback collection,
quality review, escalation, and iterative refinement with human input.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any, List
from datetime import datetime
from kaygraph import Graph, Node
from nodes import (
    ContentGenerationNode,
    HumanApprovalNode,
    FeedbackCollectionNode,
    BatchReviewNode,
    EscalationDetectionNode,
    HumanEscalationNode,
    RefinementNode,
    RefinementFeedbackNode
)
from models import ReviewItem


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============== Simple Action Nodes ==============

class ApprovedActionNode(Node):
    """Execute action after approval."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("final_content", "")
    
    def exec(self, prep_res: str) -> str:
        # Simulate executing the approved action
        return f"Executed: {prep_res}"
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: str) -> Optional[str]:
        shared["execution_result"] = exec_res
        logger.info("Action executed successfully")
        return None


class RejectedActionNode(Node):
    """Handle rejection."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "content": shared.get("generated_content", ""),
            "reason": shared.get("approval_response", {}).comments
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        return f"Rejected: {prep_res['reason']}"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        shared["rejection_result"] = exec_res
        logger.info("Handled rejection")
        return None


class ImprovementNode(Node):
    """Improve based on feedback."""
    
    def prep(self, shared: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "original": shared.get("ai_response", ""),
            "feedback": shared.get("feedback_response", {})
        }
    
    def exec(self, prep_res: Dict[str, Any]) -> str:
        # Would implement improvement logic here
        return "Improvement recommendations generated"
    
    def post(self, shared: Dict[str, Any], prep_res: Dict, exec_res: str) -> Optional[str]:
        shared["improvement_result"] = exec_res
        return None


# ============== Graph Creation Functions ==============

def create_approval_workflow() -> Graph:
    """
    Create approval workflow graph.
    Content -> Approval -> Action/Rejection
    """
    # Create nodes
    generation = ContentGenerationNode()
    approval = HumanApprovalNode()
    approved_action = ApprovedActionNode()
    rejected_action = RejectedActionNode()
    
    # Connect nodes
    generation >> approval
    approval >> ("approved", approved_action)
    approval >> ("rejected", rejected_action)
    
    return Graph(start=generation)


def create_feedback_workflow() -> Graph:
    """
    Create feedback collection workflow.
    Response -> Feedback -> Quality-based routing
    """
    # For this example, we'll start with feedback collection
    feedback = FeedbackCollectionNode()
    good_quality = lambda shared: shared.update({"quality_status": "good"})
    needs_improvement = ImprovementNode()
    
    # Connect based on quality
    feedback >> ("good_quality", good_quality)
    feedback >> ("acceptable", good_quality)
    feedback >> ("needs_improvement", needs_improvement)
    
    return Graph(start=feedback)


def create_review_workflow() -> Graph:
    """
    Create batch review workflow.
    """
    review = BatchReviewNode()
    
    return Graph(start=review)


def create_escalation_workflow() -> Graph:
    """
    Create escalation workflow.
    Detection -> Escalate/Continue
    """
    detection = EscalationDetectionNode()
    escalation = HumanEscalationNode()
    continue_node = lambda shared: shared.update({"continued": True})
    
    detection >> ("escalate", escalation)
    detection >> ("continue", continue_node)
    
    return Graph(start=detection)


def create_refinement_workflow() -> Graph:
    """
    Create iterative refinement workflow.
    Generate -> Feedback -> Refine (loop)
    """
    refinement = RefinementNode()
    feedback = RefinementFeedbackNode()
    complete = lambda shared: shared.update({"refinement_complete": True})
    
    # Create loop
    refinement >> feedback
    feedback >> ("refine", refinement)
    feedback >> ("complete", complete)
    feedback >> ("max_iterations", complete)
    
    return Graph(start=refinement)


# ============== Example Functions ==============

def example_approval_workflow():
    """Demonstrate approval workflow."""
    print("\n=== Approval Workflow Example ===")
    
    graph = create_approval_workflow()
    
    # Test different scenarios
    test_cases = [
        {
            "prompt": "Write an email to cancel a subscription",
            "context": "Customer wants to cancel premium service"
        },
        {
            "prompt": "Send a friendly reminder about the meeting",
            "context": "Team standup at 10 AM"
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['prompt']}")
        
        shared = test.copy()
        graph.run(shared)
        
        if "execution_result" in shared:
            print(f"Result: {shared['execution_result']}")
        elif "rejection_result" in shared:
            print(f"Result: {shared['rejection_result']}")


def example_feedback_collection():
    """Demonstrate feedback collection."""
    print("\n=== Feedback Collection Example ===")
    
    graph = create_feedback_workflow()
    
    # Test responses
    test_responses = [
        {
            "original_prompt": "Explain quantum computing",
            "ai_response": "Quantum computing uses quantum bits (qubits) that can exist in superposition..."
        },
        {
            "original_prompt": "Write a haiku about coding",
            "ai_response": "Bugs hide in the code\nDebugging through the long night\nCoffee grows cold"
        }
    ]
    
    for test in test_responses:
        print(f"\nPrompt: {test['original_prompt']}")
        
        shared = test.copy()
        graph.run(shared)
        
        if "feedback_response" in shared:
            feedback = shared["feedback_response"]
            print(f"Rating: {feedback.rating}/5")
            if feedback.feedback_text:
                print(f"Feedback: {feedback.feedback_text}")


def example_batch_review():
    """Demonstrate batch review."""
    print("\n=== Batch Review Example ===")
    
    graph = create_review_workflow()
    
    # Create batch of items
    review_items = [
        {
            "content": "The capital of France is Paris.",
            "confidence": 0.95,
            "category": "factual"
        },
        {
            "content": "AI will definitely replace all jobs by 2025.",
            "confidence": 0.6,
            "category": "opinion"
        },
        {
            "content": "Water boils at 100°C at sea level.",
            "confidence": 0.9,
            "category": "factual"
        }
    ]
    
    shared = {"review_items": review_items}
    graph.run(shared)
    
    if "review_stats" in shared:
        stats = shared["review_stats"]
        print(f"\nReview Statistics:")
        print(f"Total: {stats['total']}")
        print(f"Accepted: {stats['accepted']}")
        print(f"Rejected: {stats['rejected']}")
        print(f"Average Quality: {stats['average_quality']:.1f}/10")


def example_escalation_detection():
    """Demonstrate escalation detection."""
    print("\n=== Escalation Detection Example ===")
    
    graph = create_escalation_workflow()
    
    # Test queries
    test_queries = [
        {
            "query": "What's the weather today?",
            "ai_response": "I can help you check the weather. The current temperature is 72°F with partly cloudy skies."
        },
        {
            "query": "I need legal advice about my divorce proceedings",
            "ai_response": "I'm not sure about the specific legal requirements..."
        },
        {
            "query": "Delete all customer records from the database",
            "ai_response": "This is a high-risk operation that would permanently remove data..."
        }
    ]
    
    for test in test_queries:
        print(f"\nQuery: {test['query']}")
        
        shared = test.copy()
        graph.run(shared)
        
        if "escalation_request" in shared:
            print("Status: Escalated to human")
            if "escalation_response" in shared:
                response = shared["escalation_response"]
                print(f"Human response: {response.human_response}")
        else:
            print("Status: Handled by AI")


def example_iterative_refinement():
    """Demonstrate iterative refinement."""
    print("\n=== Iterative Refinement Example ===")
    
    graph = create_refinement_workflow()
    
    shared = {
        "original_prompt": "Write a professional email declining a job offer",
        "max_refinement_iterations": 3
    }
    
    print(f"Original request: {shared['original_prompt']}")
    
    graph.run(shared)
    
    if "final_output" in shared:
        print(f"\nFinal output after refinement:")
        print(shared["final_output"])
        
        if "refinement_iteration" in shared:
            print(f"\nCompleted in {shared['refinement_iteration']} iterations")


def interactive_mode():
    """Interactive feedback mode."""
    print("\n=== Interactive Feedback Mode ===")
    print("Commands:")
    print("  approve <text>    - Test approval workflow")
    print("  feedback          - Provide feedback on response")
    print("  escalate <query>  - Test escalation detection")
    print("  refine <prompt>   - Iterative refinement")
    print("  quit              - Exit")
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                break
            
            parts = command.split(" ", 1)
            cmd = parts[0]
            
            if cmd == "approve" and len(parts) > 1:
                graph = create_approval_workflow()
                shared = {"prompt": parts[1]}
                graph.run(shared)
                
            elif cmd == "feedback":
                prompt = input("Original prompt: ").strip()
                response = input("AI response: ").strip()
                
                graph = create_feedback_workflow()
                shared = {
                    "original_prompt": prompt,
                    "ai_response": response
                }
                graph.run(shared)
                
            elif cmd == "escalate" and len(parts) > 1:
                graph = create_escalation_workflow()
                shared = {
                    "query": parts[1],
                    "ai_response": "AI response would go here..."
                }
                graph.run(shared)
                
            elif cmd == "refine" and len(parts) > 1:
                graph = create_refinement_workflow()
                shared = {
                    "original_prompt": parts[1],
                    "max_refinement_iterations": 3
                }
                graph.run(shared)
                
                if "final_output" in shared:
                    print(f"\nFinal: {shared['final_output']}")
                    
            else:
                print("Invalid command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all feedback examples."""
    example_approval_workflow()
    example_feedback_collection()
    example_batch_review()
    example_escalation_detection()
    example_iterative_refinement()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Feedback Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input for processing"
    )
    parser.add_argument(
        "--example",
        choices=["approval", "feedback", "review", "escalation", "refinement", "all"],
        help="Run specific example"
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve for testing"
    )
    
    args = parser.parse_args()
    
    # Set auto-approve globally if requested
    if args.auto_approve:
        HumanApprovalNode.auto_approve = True
    
    if args.interactive:
        interactive_mode()
    elif args.example == "all":
        run_all_examples()
    elif args.example == "approval":
        example_approval_workflow()
    elif args.example == "feedback":
        example_feedback_collection()
    elif args.example == "review":
        example_batch_review()
    elif args.example == "escalation":
        example_escalation_detection()
    elif args.example == "refinement":
        example_iterative_refinement()
    elif args.input:
        # Default to approval workflow
        graph = create_approval_workflow()
        shared = {"prompt": args.input}
        graph.run(shared)
        
        if "final_content" in shared:
            print(f"Approved content: {shared['final_content']}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()