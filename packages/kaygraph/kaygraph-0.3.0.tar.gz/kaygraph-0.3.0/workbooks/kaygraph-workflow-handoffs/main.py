#!/usr/bin/env python3
"""
KayGraph Workflow Handoffs - Agent Handoff Patterns
"""

import argparse
import logging
from typing import Dict, Any
from datetime import datetime

from kaygraph import Graph
from nodes import (
    TriageAgentNode, TechSupportAgentNode, BillingAgentNode,
    SalesAgentNode, GeneralAgentNode, EscalationAgentNode,
    ManagerAgentNode, DocumentAnalyzerNode, HandoffResponseNode,
    TaskCompletionNode
)
from models import CustomerRequest, AgentType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_support():
    """Customer support handoff example."""
    logger.info("\n=== Customer Support Handoff Example ===")
    
    # Create agent nodes
    triage = TriageAgentNode()
    tech_support = TechSupportAgentNode()
    billing = BillingAgentNode()
    sales = SalesAgentNode()
    general = GeneralAgentNode()
    escalation = EscalationAgentNode()
    response = HandoffResponseNode()
    
    # Connect with KayGraph conditional routing
    # Triage routes to specialists
    triage - AgentType.TECH_SUPPORT.value >> tech_support
    triage - AgentType.BILLING.value >> billing
    triage - AgentType.SALES.value >> sales
    triage - AgentType.GENERAL.value >> general
    
    # Specialists can escalate or complete
    for agent in [tech_support, billing, sales]:
        agent - "complete" >> response
        agent - "followup" >> response
        agent - AgentType.ESCALATION.value >> escalation
        agent - AgentType.BILLING.value >> billing  # Tech can handoff to billing
        agent - AgentType.TECH_SUPPORT.value >> tech_support  # Billing can handoff to tech
    
    # General always completes
    general - "complete" >> response
    
    # Escalation always completes
    escalation - "complete" >> response
    
    # Create graph
    graph = Graph(start=triage)
    
    # Test various requests
    test_requests = [
        {
            "content": "My app keeps crashing when I try to login",
            "customer_id": "cust_123"
        },
        {
            "content": "I was charged twice for my subscription",
            "customer_id": "cust_456"
        },
        {
            "content": "What products do you have for fitness tracking?",
            "customer_id": "cust_789"
        },
        {
            "content": "How do I contact support?",
            "customer_id": "cust_101"
        }
    ]
    
    for req in test_requests:
        logger.info(f"\n--- Processing: {req['content']} ---")
        shared = {"request": req}
        graph.run(shared)
        
        response = shared.get("final_response", "No response")
        logger.info(f"Response: {response}")
        
        # Show handoff metrics
        context = shared.get("handoff_context")
        if context:
            logger.info(f"Agents involved: {len(context.previous_agents)}")
            logger.info(f"Handoffs: {context.handoff_count}")


def example_escalation():
    """Escalation workflow example."""
    logger.info("\n=== Escalation Workflow Example ===")
    
    # Create nodes
    triage = TriageAgentNode()
    tech_support = TechSupportAgentNode()
    billing = BillingAgentNode()
    escalation = EscalationAgentNode()
    response = HandoffResponseNode()
    
    # Connect with escalation paths
    triage - AgentType.TECH_SUPPORT.value >> tech_support
    triage - AgentType.BILLING.value >> billing
    
    # Both can escalate
    tech_support - AgentType.ESCALATION.value >> escalation
    billing - AgentType.ESCALATION.value >> escalation
    
    # Completion paths
    tech_support - "complete" >> response
    billing - "complete" >> response
    escalation - "complete" >> response
    
    graph = Graph(start=triage)
    
    # Complex issue that requires escalation
    complex_request = {
        "content": "I've been trying to fix this issue for weeks. The app crashes, I can't access my data, and I was charged three times! This is unacceptable!",
        "customer_id": "angry_customer",
        "metadata": {"vip": True}
    }
    
    logger.info(f"Processing complex request: {complex_request['content']}")
    shared = {"request": complex_request}
    
    # Force escalation by modifying tech support response
    graph.run(shared)
    
    response = shared.get("final_response", "No response")
    logger.info(f"\nFinal Resolution:\n{response}")


def example_delegation():
    """Task delegation example."""
    logger.info("\n=== Task Delegation Example ===")
    
    # Create nodes
    manager = ManagerAgentNode()
    completion = TaskCompletionNode()
    
    # Simple linear flow
    manager >> completion
    
    graph = Graph(start=manager)
    
    # Complex tasks to delegate
    tasks = [
        "Analyze Q4 sales data, create visualizations, and prepare executive presentation",
        "Process customer feedback surveys, extract insights, and generate improvement recommendations",
        "Review all support tickets from last month, categorize issues, and create training materials"
    ]
    
    for task in tasks:
        logger.info(f"\n--- Task: {task} ---")
        shared = {"task_description": task}
        graph.run(shared)
        
        summary = shared.get("completion_summary", "No summary")
        logger.info(f"\n{summary}")


def example_document():
    """Document processing handoff example."""
    logger.info("\n=== Document Processing Handoff Example ===")
    
    # Create nodes
    analyzer = DocumentAnalyzerNode()
    response = HandoffResponseNode()
    
    # Simple flow for now
    analyzer - "extract" >> response
    analyzer - "validate" >> response
    
    graph = Graph(start=analyzer)
    
    # Test documents
    documents = [
        {
            "content": "Invoice #12345\nDate: 2024-01-15\nAmount: $1,250.00\nDue: 2024-02-15",
            "type": "invoice"
        },
        {
            "content": "Dear Customer,\nThank you for your order. Your tracking number is ABC123...",
            "type": "email"
        },
        {
            "content": "CONTRACT AGREEMENT\nThis agreement is between Party A and Party B...",
            "type": "contract"
        }
    ]
    
    for doc in documents:
        logger.info(f"\n--- Processing {doc['type']} ---")
        shared = {"document": doc}
        graph.run(shared)
        
        analysis = shared.get("document_analysis")
        if analysis:
            logger.info(f"Type: {analysis.document_type}")
            logger.info(f"Summary: {analysis.summary}")
            logger.info(f"Entities: {analysis.key_entities}")


def example_multi_handoff():
    """Multi-stage handoff example."""
    logger.info("\n=== Multi-Stage Handoff Example ===")
    
    # Create all nodes
    triage = TriageAgentNode()
    tech = TechSupportAgentNode()
    billing = BillingAgentNode()
    escalation = EscalationAgentNode()
    response = HandoffResponseNode()
    
    # Complex routing allowing multiple handoffs
    triage - AgentType.TECH_SUPPORT.value >> tech
    triage - AgentType.BILLING.value >> billing
    
    # Tech can handoff to billing or escalate
    tech - AgentType.BILLING.value >> billing
    tech - AgentType.ESCALATION.value >> escalation
    tech - "complete" >> response
    
    # Billing can handoff to tech or escalate
    billing - AgentType.TECH_SUPPORT.value >> tech
    billing - AgentType.ESCALATION.value >> escalation
    billing - "complete" >> response
    
    # Escalation completes
    escalation - "complete" >> response
    
    graph = Graph(start=triage)
    
    # Request that requires multiple handoffs
    complex_request = {
        "content": "My app crashed after payment failed. Need technical help and billing adjustment.",
        "customer_id": "multi_issue_customer"
    }
    
    logger.info(f"Processing multi-issue request: {complex_request['content']}")
    shared = {"request": complex_request}
    graph.run(shared)
    
    response_text = shared.get("final_response", "No response")
    logger.info(f"\nFinal Response:\n{response_text}")
    
    # Show handoff chain
    context = shared.get("handoff_context")
    if context:
        logger.info(f"\nHandoff Chain:")
        for i, agent in enumerate(context.previous_agents):
            logger.info(f"  {i+1}. {agent.value}")


def run_interactive():
    """Run interactive mode."""
    logger.info("\n=== Interactive Handoff Mode ===")
    logger.info("Enter customer requests to see agent handoffs in action.")
    logger.info("Type 'exit' to quit.\n")
    
    # Create full support system
    triage = TriageAgentNode()
    tech = TechSupportAgentNode()
    billing = BillingAgentNode()
    sales = SalesAgentNode()
    general = GeneralAgentNode()
    escalation = EscalationAgentNode()
    response = HandoffResponseNode()
    
    # Full routing
    triage - AgentType.TECH_SUPPORT.value >> tech
    triage - AgentType.BILLING.value >> billing
    triage - AgentType.SALES.value >> sales
    triage - AgentType.GENERAL.value >> general
    
    for agent in [tech, billing, sales]:
        agent - "complete" >> response
        agent - "followup" >> response
        agent - AgentType.ESCALATION.value >> escalation
        agent - AgentType.BILLING.value >> billing
        agent - AgentType.TECH_SUPPORT.value >> tech
    
    general - "complete" >> response
    escalation - "complete" >> response
    
    graph = Graph(start=triage)
    
    while True:
        request_text = input("\nCustomer request: ").strip()
        if request_text.lower() == 'exit':
            break
        
        if not request_text:
            continue
        
        request = {
            "content": request_text,
            "customer_id": f"interactive_{datetime.now().timestamp()}"
        }
        
        shared = {"request": request}
        graph.run(shared)
        
        response_text = shared.get("final_response", "No response generated")
        print(f"\n{response_text}")
        
        # Show routing details
        context = shared.get("handoff_context")
        if context and context.handoff_count > 0:
            print(f"\n[Routing: {' → '.join(a.value for a in context.previous_agents)}]")


def main():
    parser = argparse.ArgumentParser(description="KayGraph Workflow Handoffs Examples")
    parser.add_argument("request", nargs="?", help="Customer request to process")
    parser.add_argument("--example", choices=["support", "escalation", "delegation", 
                                               "document", "multi", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    
    elif args.request:
        # Process single request
        logger.info(f"Processing request: {args.request}")
        
        # Use support example setup
        triage = TriageAgentNode()
        tech = TechSupportAgentNode()
        billing = BillingAgentNode()
        sales = SalesAgentNode()
        general = GeneralAgentNode()
        escalation = EscalationAgentNode()
        response = HandoffResponseNode()
        
        triage - AgentType.TECH_SUPPORT.value >> tech
        triage - AgentType.BILLING.value >> billing
        triage - AgentType.SALES.value >> sales
        triage - AgentType.GENERAL.value >> general
        
        for agent in [tech, billing, sales]:
            agent - "complete" >> response
            agent - "followup" >> response
            agent - AgentType.ESCALATION.value >> escalation
        
        general - "complete" >> response
        escalation - "complete" >> response
        
        graph = Graph(start=triage)
        
        request = {
            "content": args.request,
            "customer_id": "cli_user"
        }
        
        shared = {"request": request}
        graph.run(shared)
        
        logger.info(f"\nResponse:\n{shared.get('final_response', 'No response')}")
    
    elif args.example:
        if args.example == "support" or args.example == "all":
            example_support()
        
        if args.example == "escalation" or args.example == "all":
            example_escalation()
        
        if args.example == "delegation" or args.example == "all":
            example_delegation()
        
        if args.example == "document" or args.example == "all":
            example_document()
        
        if args.example == "multi" or args.example == "all":
            example_multi_handoff()
    
    else:
        # Run all examples
        logger.info("Running all handoff examples...")
        example_support()
        example_escalation()
        example_delegation()
        example_document()
        example_multi_handoff()


if __name__ == "__main__":
    main()