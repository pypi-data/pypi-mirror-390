#!/usr/bin/env python3
"""
KayGraph Agent Validation - Structured output validation examples.

Demonstrates how to ensure LLM outputs match expected schemas using
Pydantic models for type safety and validation.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any
from kaygraph import Graph
from nodes import (
    BasicValidationNode,
    RetryValidationNode, 
    ComplexValidationNode,
    CustomValidatorNode,
    FallbackValidationNode
)
from models import TaskResult, Meeting, Order, SupportTicket


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def example_basic_validation(input_text: str):
    """Example: Basic task extraction with validation."""
    print("\n=== Basic Validation Example ===")
    print(f"Input: {input_text}")
    
    # Create nodes
    validator = BasicValidationNode(model_class=TaskResult)
    
    # Create graph with starting node
    graph = Graph(start=validator)
    
    # Run extraction
    shared = {"input": input_text}
    graph.run(shared)
    
    if shared.get("validation_success"):
        task = shared["extracted_data"]
        print(f"\nExtracted Task:")
        print(f"  Task: {task.task}")
        print(f"  Completed: {task.completed}")
        print(f"  Priority: {task.priority}")
    else:
        print(f"\nValidation failed: {shared.get('validation_error')}")
        print(f"Raw response: {shared.get('raw_response')}")


def example_retry_validation(input_text: str):
    """Example: Meeting extraction with retry on failure."""
    print("\n=== Retry Validation Example ===")
    print(f"Input: {input_text}")
    
    # Create nodes
    validator = RetryValidationNode(model_class=Meeting, max_retries=3)
    
    # Create graph with starting node
    graph = Graph(start=validator)
    
    # Run extraction
    shared = {"input": input_text}
    graph.run(shared)
    
    if shared.get("validation_success"):
        meeting = shared["extracted_data"]
        print(f"\nExtracted Meeting (after {shared['attempts']} attempts):")
        print(f"  Title: {meeting.title}")
        print(f"  Date: {meeting.date}")
        print(f"  Time: {meeting.time}")
        print(f"  Duration: {meeting.duration_minutes} minutes")
        print(f"  Attendees: {', '.join(meeting.attendees)}")
        if meeting.location:
            print(f"  Location: {meeting.location}")
    else:
        print(f"\nValidation failed after {shared['attempts']} attempts")
        print("Errors:")
        for i, error in enumerate(shared.get("validation_errors", [])):
            print(f"  {i+1}. {error}")


def example_complex_validation(input_text: str):
    """Example: Complex order extraction with nested items."""
    print("\n=== Complex Validation Example ===")
    print(f"Input: {input_text}")
    
    # Create nodes
    validator = ComplexValidationNode()
    
    # Create graph with starting node
    graph = Graph(start=validator)
    
    # Run extraction
    shared = {"input": input_text}
    graph.run(shared)
    
    if shared.get("validation_success"):
        order = shared["order"]
        summary = shared["order_summary"]
        print(f"\nExtracted Order:")
        print(f"  Customer: {order.customer_name or 'Not specified'}")
        print(f"  Total items: {summary['total_items']}")
        print(f"  Total price: ${summary['total_price'] or 'Not calculated'}")
        print(f"\nItems:")
        for item in order.items:
            price_str = f"${item.unit_price:.2f}" if item.unit_price else "Price not specified"
            print(f"  - {item.product}: {item.quantity} @ {price_str}")
        if order.notes:
            print(f"\nNotes: {order.notes}")
    else:
        print(f"\nValidation failed: {shared.get('validation_error')}")


def example_custom_validation(input_text: str):
    """Example: Support ticket with custom business rules."""
    print("\n=== Custom Validation Example ===")
    print(f"Input: {input_text}")
    
    # Create nodes
    validator = CustomValidatorNode()
    
    # Create graph with starting node
    graph = Graph(start=validator)
    
    # Run extraction
    shared = {"input": input_text}
    graph.run(shared)
    
    if shared.get("validation_success"):
        ticket = shared["ticket"]
        print(f"\nExtracted Support Ticket:")
        print(f"  Type: {ticket.issue_type}")
        print(f"  Severity: {ticket.severity}")
        print(f"  Product: {ticket.affected_product or 'Not specified'}")
        print(f"  Description: {ticket.description}")
        if shared.get("auto_adjusted"):
            print("\n⚠️  Severity was auto-adjusted based on business rules")
    else:
        print(f"\nValidation failed: {shared.get('validation_error')}")


def example_fallback_validation(input_text: str):
    """Example: Meeting extraction with fallback to unstructured."""
    print("\n=== Fallback Validation Example ===")
    print(f"Input: {input_text}")
    
    # Create nodes
    validator = FallbackValidationNode()
    
    # Create graph with starting node
    graph = Graph(start=validator)
    
    # Run extraction
    shared = {"input": input_text}
    graph.run(shared)
    
    extraction_type = shared.get("extraction_type")
    
    if extraction_type == "structured":
        meeting = shared["meeting"]
        print(f"\n✅ Structured extraction succeeded:")
        print(f"  Title: {meeting.title}")
        print(f"  Date: {meeting.date}")
        print(f"  Time: {meeting.time}")
        print(f"  Attendees: {', '.join(meeting.attendees)}")
    elif extraction_type == "fallback":
        print(f"\n⚠️  Structured extraction failed, using fallback:")
        print(shared["unstructured_data"])
    else:
        print("\n❌ Both structured and fallback extraction failed")


def interactive_mode():
    """Interactive validation testing."""
    print("\n=== Interactive Validation Mode ===")
    print("Commands:")
    print("  task <text>    - Extract task with basic validation")
    print("  meeting <text> - Extract meeting with retry validation")
    print("  order <text>   - Extract order with complex validation")
    print("  ticket <text>  - Extract support ticket with custom rules")
    print("  fallback <text> - Test fallback validation")
    print("  quit          - Exit")
    
    while True:
        try:
            user_input = input("\n> ").strip()
            
            if not user_input or user_input.lower() == "quit":
                break
            
            parts = user_input.split(" ", 1)
            if len(parts) < 2:
                print("Please provide a command and text")
                continue
            
            command, text = parts
            
            if command == "task":
                example_basic_validation(text)
            elif command == "meeting":
                example_retry_validation(text)
            elif command == "order":
                example_complex_validation(text)
            elif command == "ticket":
                example_custom_validation(text)
            elif command == "fallback":
                example_fallback_validation(text)
            else:
                print(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all validation examples."""
    # Basic validation
    example_basic_validation(
        "Finish the quarterly report by end of week - high priority"
    )
    
    # Retry validation
    example_retry_validation(
        "Schedule team sync tomorrow at 2:30pm with Sarah, Mike, and Lisa "
        "for 45 minutes in the main conference room"
    )
    
    # Complex validation
    example_complex_validation(
        "I need to order 3 laptops at $1200 each, 5 monitors for $300 each, "
        "and 10 USB keyboards. Ship to our Boston office."
    )
    
    # Custom validation
    example_custom_validation(
        "URGENT: The payment system is completely down and customers can't "
        "checkout. This is affecting all online orders!"
    )
    
    # Fallback validation
    example_fallback_validation(
        "Let's have a casual coffee chat sometime next week, maybe Tuesday "
        "or Wednesday afternoon if you're free"
    )


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Agent Validation Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Text to extract structured data from"
    )
    parser.add_argument(
        "--example",
        choices=["basic", "retry", "complex", "custom", "fallback", "all"],
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
    elif args.example and args.input:
        if args.example == "basic":
            example_basic_validation(args.input)
        elif args.example == "retry":
            example_retry_validation(args.input)
        elif args.example == "complex":
            example_complex_validation(args.input)
        elif args.example == "custom":
            example_custom_validation(args.input)
        elif args.example == "fallback":
            example_fallback_validation(args.input)
    elif args.input:
        # Default to basic validation
        example_basic_validation(args.input)
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()