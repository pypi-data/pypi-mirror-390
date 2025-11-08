#!/usr/bin/env python3
"""
KayGraph Workflow Routing - Intelligent request routing patterns.

Demonstrates how to implement dynamic routing based on content classification,
with confidence thresholds and specialized handlers for different request types.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any, List
from kaygraph import Graph, Node
from nodes import (
    CalendarRouterNode, NewEventHandlerNode, ModifyEventHandlerNode,
    SupportTicketRouterNode, TechnicalSupportNode, BillingSupportNode,
    DocumentRouterNode, PDFProcessorNode,
    MultiLevelRouterNode,
    FallbackHandlerNode, MetricsCollectorNode
)
from models import TicketCategory, DocumentType


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============== Simple Handler Nodes ==============

class QueryEventHandlerNode(Node):
    """Handles calendar query requests."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("calendar_classification", {}).description
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        return {
            "response": f"Searching for events matching: {prep_res}",
            "found_events": ["Meeting with team", "Project deadline"]
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        shared["query_response"] = exec_res
        return None


class GeneralSupportNode(Node):
    """Handles general support tickets."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("ticket_text", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        return {
            "ticket_id": f"GEN-{int(time.time())}",
            "response": "Your inquiry has been received by our general support team.",
            "estimated_response": "48 hours"
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        shared["support_response"] = exec_res
        return None


class ImageProcessorNode(Node):
    """Processes image documents."""
    
    def prep(self, shared: Dict[str, Any]) -> str:
        return shared.get("file_path", "")
    
    def exec(self, prep_res: str) -> Dict[str, Any]:
        return {
            "processor": "ImageProcessor",
            "extracted_text": "Sample text from OCR",
            "detected_objects": ["text", "diagram", "logo"]
        }
    
    def post(self, shared: Dict[str, Any], prep_res: str, exec_res: Dict) -> Optional[str]:
        shared["processing_response"] = exec_res
        return None


# ============== Graph Creation Functions ==============

def create_calendar_routing_graph() -> Graph:
    """
    Create calendar request routing graph.
    Routes: new_event, modify_event, query_event, other → fallback
    """
    # Create nodes
    router = CalendarRouterNode()
    new_event_handler = NewEventHandlerNode()
    modify_event_handler = ModifyEventHandlerNode()
    query_event_handler = QueryEventHandlerNode()
    fallback = FallbackHandlerNode()
    
    # Connect nodes
    router >> ("new_event", new_event_handler)
    router >> ("modify_event", modify_event_handler)
    router >> ("query_event", query_event_handler)
    router >> ("delete_event", fallback)
    router >> ("other", fallback)
    router >> ("low_confidence", fallback)
    
    return Graph(start=router)


def create_support_routing_graph() -> Graph:
    """
    Create support ticket routing graph.
    Routes by category: technical, billing, general, etc.
    """
    # Create nodes
    router = SupportTicketRouterNode()
    technical = TechnicalSupportNode()
    billing = BillingSupportNode()
    general = GeneralSupportNode()
    fallback = FallbackHandlerNode()
    
    # Connect nodes
    router >> (TicketCategory.TECHNICAL.value, technical)
    router >> (TicketCategory.BILLING.value, billing)
    router >> (TicketCategory.GENERAL.value, general)
    router >> (TicketCategory.FEATURE_REQUEST.value, general)
    router >> (TicketCategory.COMPLAINT.value, general)
    
    return Graph(start=router)


def create_document_routing_graph() -> Graph:
    """
    Create document processing routing graph.
    Routes by document type: pdf, image, text, etc.
    """
    # Create nodes
    router = DocumentRouterNode()
    pdf_processor = PDFProcessorNode()
    image_processor = ImageProcessorNode()
    fallback = FallbackHandlerNode()
    
    # Connect nodes
    router >> (DocumentType.PDF.value, pdf_processor)
    router >> (DocumentType.IMAGE.value, image_processor)
    router >> (DocumentType.TEXT.value, fallback)
    router >> (DocumentType.SPREADSHEET.value, fallback)
    router >> (DocumentType.UNKNOWN.value, fallback)
    
    return Graph(start=router)


def create_multi_level_routing_graph() -> Graph:
    """
    Create multi-level hierarchical routing graph.
    Demonstrates routing through multiple decision levels.
    """
    # Create nodes
    router = MultiLevelRouterNode()
    
    # For this example, we'll just use the router
    # In a real system, you'd have handlers for each route
    
    return Graph(start=router)


# ============== Example Functions ==============

def example_calendar_routing():
    """Demonstrate calendar request routing."""
    print("\n=== Calendar Routing Example ===")
    
    graph = create_calendar_routing_graph()
    
    # Test different request types
    test_requests = [
        "Schedule a team meeting next Tuesday at 2pm with Alice and Bob",
        "Move the team meeting to Wednesday at 3pm",
        "What meetings do I have tomorrow?",
        "Delete the recurring standup meeting",
        "What's the weather like?"  # Should go to fallback
    ]
    
    for request in test_requests:
        print(f"\nRequest: {request}")
        
        shared = {"user_input": request}
        graph.run(shared)
        
        # Check what type of response we got
        if "calendar_response" in shared:
            response = shared["calendar_response"]
            print(f"Success: {response.message}")
            if response.calendar_link:
                print(f"Link: {response.calendar_link}")
        elif "query_response" in shared:
            response = shared["query_response"]
            print(f"Query: {response['response']}")
            print(f"Found: {response['found_events']}")
        elif "fallback_response" in shared:
            print(f"Fallback: {shared['fallback_response']}")


def example_support_routing():
    """Demonstrate support ticket routing."""
    print("\n=== Support Ticket Routing Example ===")
    
    graph = create_support_routing_graph()
    
    # Test different ticket types
    test_tickets = [
        "My application crashes when I try to upload files",
        "I was charged twice for my subscription last month",
        "Can you add dark mode to the mobile app?",
        "How do I reset my password?",
        "Your service is terrible and I want to speak to a manager!"
    ]
    
    for ticket in test_tickets:
        print(f"\nTicket: {ticket}")
        
        shared = {"ticket_text": ticket}
        graph.run(shared)
        
        if "ticket_response" in shared:
            response = shared["ticket_response"]
            print(f"Ticket ID: {response.ticket_id}")
            print(f"Routed to: {response.routed_to}")
            print(f"Response time: {response.estimated_response_time}")
            if response.escalated:
                print("⚠️  Escalated for immediate attention")
        elif "support_response" in shared:
            response = shared["support_response"]
            print(f"Ticket ID: {response['ticket_id']}")
            print(f"Response: {response['response']}")


def example_document_routing():
    """Demonstrate document processing routing."""
    print("\n=== Document Routing Example ===")
    
    graph = create_document_routing_graph()
    
    # Test different document types
    test_documents = [
        {"file_name": "report.pdf", "file_path": "/docs/report.pdf"},
        {"file_name": "screenshot.png", "file_path": "/images/screenshot.png"},
        {"file_name": "data.xlsx", "file_path": "/data/spreadsheet.xlsx"},
        {"file_name": "notes.txt", "file_path": "/docs/notes.txt"},
        {"file_name": "unknown.xyz", "file_path": "/misc/unknown.xyz"}
    ]
    
    for doc in test_documents:
        print(f"\nDocument: {doc['file_name']}")
        
        shared = {
            "file_name": doc["file_name"],
            "file_path": doc["file_path"],
            "requested_operations": ["extract_text", "analyze"]
        }
        graph.run(shared)
        
        if "processing_response" in shared:
            response = shared["processing_response"]
            if hasattr(response, 'processor_used'):
                print(f"Processor: {response.processor_used}")
                print(f"Success: {response.success}")
                if response.extracted_data:
                    print(f"Extracted: {json.dumps(response.extracted_data, indent=2)}")
            else:
                print(f"Processor: {response.get('processor', 'Unknown')}")
                print(f"Result: {response}")
        elif "fallback_response" in shared:
            print(f"Fallback: Unable to process {doc['file_name']}")


def example_multi_level_routing():
    """Demonstrate multi-level hierarchical routing."""
    print("\n=== Multi-Level Routing Example ===")
    
    graph = create_multi_level_routing_graph()
    
    # Test queries that route through multiple levels
    test_queries = [
        "I want to buy your enterprise plan for 500 users",
        "Help! The app keeps crashing on startup",
        "I'd like to suggest a new feature for the dashboard",
        "I'm interested in the senior developer position",
        "Can you send me the invoice from last month?"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        
        shared = {"query": query}
        graph.run(shared)
        
        if "routing_decision" in shared:
            decision = shared["routing_decision"]
            print(f"Routing path: {' → '.join(decision.routing_path)}")
            print(f"Final handler: {decision.final_handler}")
            print(f"Confidence: Primary={decision.confidence_scores['primary']:.2f}, "
                  f"Secondary={decision.confidence_scores['secondary']:.2f}")


def interactive_mode():
    """Interactive routing mode."""
    print("\n=== Interactive Routing Mode ===")
    print("Commands:")
    print("  calendar <request>  - Route calendar request")
    print("  support <text>      - Route support ticket")
    print("  document <file>     - Route document processing")
    print("  multi <query>       - Multi-level routing")
    print("  quit                - Exit")
    
    graphs = {
        "calendar": create_calendar_routing_graph(),
        "support": create_support_routing_graph(),
        "document": create_document_routing_graph(),
        "multi": create_multi_level_routing_graph()
    }
    
    while True:
        try:
            command = input("\n> ").strip()
            
            if command == "quit":
                break
            
            parts = command.split(" ", 1)
            if len(parts) < 2:
                print("Please provide input after the command")
                continue
            
            cmd, input_text = parts
            
            if cmd == "calendar":
                shared = {"user_input": input_text}
                graphs["calendar"].run(shared)
                
                if "calendar_response" in shared:
                    print(f"Response: {shared['calendar_response'].message}")
                elif "fallback_response" in shared:
                    print(f"Fallback: {shared['fallback_response']}")
                    
            elif cmd == "support":
                shared = {"ticket_text": input_text}
                graphs["support"].run(shared)
                
                if "ticket_response" in shared:
                    response = shared["ticket_response"]
                    print(f"Routed to: {response.routed_to}")
                    print(f"Response time: {response.estimated_response_time}")
                    
            elif cmd == "document":
                shared = {
                    "file_name": input_text,
                    "file_path": f"/path/to/{input_text}"
                }
                graphs["document"].run(shared)
                
                if "processing_response" in shared:
                    print("Document processed successfully")
                else:
                    print("Unable to process document")
                    
            elif cmd == "multi":
                shared = {"query": input_text}
                graphs["multi"].run(shared)
                
                if "routing_decision" in shared:
                    decision = shared["routing_decision"]
                    print(f"Routed to: {decision.final_handler}")
                    
            else:
                print("Unknown command")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all routing examples."""
    example_calendar_routing()
    example_support_routing()
    example_document_routing()
    example_multi_level_routing()


import time  # Add this import for timestamp generation


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Workflow Routing Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Input text for routing"
    )
    parser.add_argument(
        "--example",
        choices=["calendar", "support", "document", "multi", "all"],
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
    elif args.example == "calendar":
        example_calendar_routing()
    elif args.example == "support":
        example_support_routing()
    elif args.example == "document":
        example_document_routing()
    elif args.example == "multi":
        example_multi_level_routing()
    elif args.input:
        # Default to calendar routing
        graph = create_calendar_routing_graph()
        shared = {"user_input": args.input}
        graph.run(shared)
        
        if "calendar_response" in shared:
            print(f"Response: {shared['calendar_response'].message}")
        elif "fallback_response" in shared:
            print(f"Fallback: {shared['fallback_response']}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()