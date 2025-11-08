#!/usr/bin/env python3
"""Simple test for structured output generation."""

import sys
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from kaygraph import Graph
from nodes import TicketGenerationNode

def test_ticket_generation():
    """Test ticket generation directly."""
    print("Testing ticket generation...")
    
    # Create a simple graph with just the generation node - KayGraph uses operator overloading
    node = TicketGenerationNode(node_id="ticket_gen")
    
    # Create graph with start node
    graph = Graph(start=node)
    
    # Run with test data
    shared = {
        "query": "I've been charged twice for my subscription!"
    }
    
    result = graph.run(shared)
    print(f"Result: {result}")
    print(f"Shared keys: {shared.keys()}")
    if "ticket_resolution" in shared:
        ticket = shared["ticket_resolution"]
        print(f"Ticket ID: {ticket.ticket_id}")
        print(f"Priority: {ticket.priority}")
        print(f"Category: {ticket.category}")
    else:
        print("No ticket resolution found in shared")

if __name__ == "__main__":
    test_ticket_generation()