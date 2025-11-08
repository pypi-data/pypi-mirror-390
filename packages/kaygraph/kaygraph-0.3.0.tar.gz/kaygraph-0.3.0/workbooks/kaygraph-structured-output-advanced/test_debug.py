#!/usr/bin/env python3
"""Debug test."""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kaygraph import Graph
from nodes import TicketGenerationNode, ContentValidationNode

def test_workflow():
    """Test workflow."""
    print("\n=== Testing workflow ===\n")
    
    # Create nodes
    ticket_gen = TicketGenerationNode(node_id="gen")
    validator = ContentValidationNode(node_id="val")
    
    # Connect
    ticket_gen >> validator
    
    # Create graph
    graph = Graph(start=ticket_gen)
    
    # Run with test data
    shared = {
        "query": "I've been charged twice for my subscription!"
    }
    
    try:
        result = graph.run(shared)
        print(f"Result: {result}")
        print(f"Shared keys: {shared.keys()}")
        print(f"Ticket resolution: {shared.get('ticket_resolution')}")
        print(f"Validation result: {shared.get('validation_result')}")
    except Exception as e:
        print(f"Error: {e}")
        print(f"Shared after error: {shared}")
        if 'ticket_resolution' in shared:
            print(f"Ticket was generated: {shared['ticket_resolution']}")
        else:
            print("No ticket was generated")

if __name__ == "__main__":
    test_workflow()