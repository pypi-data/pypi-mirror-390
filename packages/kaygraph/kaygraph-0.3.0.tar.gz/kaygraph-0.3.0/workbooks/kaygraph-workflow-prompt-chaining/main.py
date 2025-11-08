#!/usr/bin/env python3
"""
KayGraph Workflow Prompt Chaining - Sequential processing patterns.

Demonstrates how to chain multiple LLM calls where each step's output
feeds into the next, with gate checks and conditional routing.
"""

import sys
import json
import logging
import argparse
from typing import Dict, Any
from kaygraph import Graph
from nodes import (
    # Event chain nodes
    EventExtractionNode,
    EventDetailsNode,
    EventConfirmationNode,
    NotCalendarEventNode,
    # Document chain nodes
    DocumentExtractionNode,
    DocumentSummaryNode,
    # Analysis chain nodes
    InitialAnalysisNode,
    CategoryAnalysisNode,
    IncompleteDataNode
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_event_extraction_chain() -> Graph:
    """
    Create calendar event extraction chain with gate check.
    
    Flow:
    1. Extract and check if calendar event (gate)
    2. If yes: Parse details → Generate confirmation
    3. If no: Return not-calendar message
    """
    # Create nodes
    extraction = EventExtractionNode(confidence_threshold=0.7)
    details = EventDetailsNode()
    confirmation = EventConfirmationNode()
    not_calendar = NotCalendarEventNode()
    
    # Connect chain with conditional routing
    extraction - "parse_details" >> details >> confirmation
    extraction - "not_calendar" >> not_calendar
    
    return Graph(start=extraction)


def create_document_processing_chain() -> Graph:
    """
    Create document processing chain.
    
    Flow:
    1. Extract document metadata
    2. Generate summary based on type
    3. Format output
    """
    # Create nodes
    extraction = DocumentExtractionNode()
    summary = DocumentSummaryNode()
    
    # Simple linear chain
    extraction >> summary
    
    return Graph(start=extraction)


def create_analysis_chain() -> Graph:
    """
    Create data analysis chain with quality gate.
    
    Flow:
    1. Initial analysis with quality check
    2. If sufficient: Categorize → Score → Report
    3. If insufficient: Return error
    """
    # Create nodes
    initial = InitialAnalysisNode()
    category = CategoryAnalysisNode()
    incomplete = IncompleteDataNode()
    
    # Connect with gate check
    initial >> category  # Default path
    initial - "incomplete_data" >> incomplete
    
    return Graph(start=initial)


def example_calendar_event():
    """Run calendar event extraction example."""
    print("\n=== Calendar Event Extraction Chain ===")
    
    # Test with valid calendar event
    valid_input = "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob to discuss the project roadmap."
    print(f"\nInput: {valid_input}")
    
    graph = create_event_extraction_chain()
    shared = {"user_input": valid_input}
    graph.run(shared)
    
    if shared.get("chain_complete"):
        confirmation = shared.get("event_confirmation")
        print(f"\n✅ Confirmation: {confirmation.confirmation_message}")
        print(f"Summary: {confirmation.summary}")
    else:
        print(f"\n❌ {shared.get('response', 'Processing failed')}")
    
    # Test with non-calendar input
    invalid_input = "Can you send an email to Alice about the project status?"
    print(f"\n\nInput: {invalid_input}")
    
    shared = {"user_input": invalid_input}
    graph.run(shared)
    
    if shared.get("chain_complete"):
        print("✅ Event processed")
    else:
        print(f"❌ {shared.get('response', 'Not a calendar event')}")


def example_document_processing():
    """Run document processing chain example."""
    print("\n=== Document Processing Chain ===")
    
    document = """
    Quarterly Performance Report
    By: John Smith
    Date: Q4 2024
    
    Executive Summary:
    Our team has exceeded expectations this quarter with a 25% increase in productivity
    and successful delivery of three major projects. Customer satisfaction scores
    reached an all-time high of 94%.
    
    Key Achievements:
    - Launched new product feature ahead of schedule
    - Reduced operational costs by 15%
    - Expanded team by hiring 5 new engineers
    - Improved deployment frequency by 40%
    
    Recommendations:
    1. Continue investing in automation tools
    2. Expand training programs for new hires
    3. Consider additional headcount for Q1 2025
    """
    
    print("Processing document...")
    
    graph = create_document_processing_chain()
    shared = {"document_text": document}
    graph.run(shared)
    
    extraction = shared.get("document_extraction")
    summary = shared.get("document_summary")
    
    if extraction and summary:
        print(f"\n📄 Document Type: {extraction.content_type}")
        print(f"Topics: {', '.join(extraction.main_topics)}")
        print(f"\n📝 Summary: {summary.executive_summary}")
        print("\nKey Points:")
        for point in summary.key_points:
            print(f"  • {point}")
        print(f"\nSentiment: {summary.sentiment}")


def example_data_analysis():
    """Run data analysis chain example."""
    print("\n=== Data Analysis Chain ===")
    
    # Test with good data
    good_data = """
    Sales Data Q4 2024:
    - Product A: $1.2M (500 units)
    - Product B: $800K (300 units)
    - Product C: $600K (150 units)
    - Total Revenue: $2.6M
    - Growth: +18% YoY
    - Customer Count: 950
    - Retention Rate: 87%
    """
    
    print("Analyzing complete data...")
    graph = create_analysis_chain()
    shared = {"analysis_data": good_data}
    graph.run(shared)
    
    initial = shared.get("initial_analysis")
    category = shared.get("category_analysis")
    
    if initial:
        print(f"\n📊 Data Quality: {initial.data_quality}")
        print(f"Completeness: {initial.completeness:.0%}")
        
    if category:
        print(f"\n🏷️ Primary Category: {category.primary_category}")
        print(f"Reasoning: {category.reasoning}")
    
    # Test with incomplete data
    print("\n\nAnalyzing incomplete data...")
    bad_data = "Sales: Some products sold"
    
    shared = {"analysis_data": bad_data}
    graph.run(shared)
    
    if shared.get("error_message"):
        print(f"❌ {shared['error_message']}")


def example_multi_stage_chain():
    """
    Run a complex multi-stage chain example.
    This shows how outputs flow through multiple stages.
    """
    print("\n=== Multi-Stage Processing Chain ===")
    
    # Create a research-style chain
    research_input = """
    Research the impact of artificial intelligence on software development.
    Focus on productivity improvements and potential challenges.
    """
    
    print(f"Research Query: {research_input}")
    
    # For this example, we'll use the document chain to simulate stages
    # In real implementation, you'd have dedicated research nodes
    
    # Stage 1: Process as document
    graph = create_document_processing_chain()
    shared = {"document_text": research_input}
    graph.run(shared)
    
    # Stage 2: Use summary for further analysis
    if shared.get("document_summary"):
        summary = shared["document_summary"]
        print(f"\n📚 Stage 1 - Topic Extraction Complete")
        print(f"Topics: {shared['document_extraction'].main_topics}")
        
        # Stage 3: Analyze the summary
        analysis_graph = create_analysis_chain()
        analysis_shared = {"analysis_data": summary.executive_summary}
        analysis_graph.run(analysis_shared)
        
        if analysis_shared.get("category_analysis"):
            print(f"\n🔍 Stage 2 - Analysis Complete")
            print(f"Category: {analysis_shared['category_analysis'].primary_category}")
            
        print(f"\n✅ Multi-stage chain completed")


def interactive_mode():
    """Interactive prompt chaining mode."""
    print("\n=== Interactive Prompt Chaining Mode ===")
    print("Commands:")
    print("  calendar <text>  - Process calendar event")
    print("  document <text>  - Process document")
    print("  analyze <text>   - Analyze data")
    print("  quit            - Exit")
    
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
            
            if command == "calendar":
                graph = create_event_extraction_chain()
                shared = {"user_input": text}
                graph.run(shared)
                
                if shared.get("event_confirmation"):
                    print(f"✅ {shared['event_confirmation'].confirmation_message}")
                else:
                    print(f"❌ {shared.get('response', 'Not processed')}")
                    
            elif command == "document":
                graph = create_document_processing_chain()
                shared = {"document_text": text}
                graph.run(shared)
                
                if shared.get("document_summary"):
                    print(f"📝 {shared['document_summary'].executive_summary}")
                    
            elif command == "analyze":
                graph = create_analysis_chain()
                shared = {"analysis_data": text}
                graph.run(shared)
                
                if shared.get("category_analysis"):
                    cat = shared["category_analysis"]
                    print(f"📊 Category: {cat.primary_category}")
                elif shared.get("error_message"):
                    print(f"❌ {shared['error_message']}")
                    
            else:
                print(f"Unknown command: {command}")
                
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_all_examples():
    """Run all prompt chaining examples."""
    example_calendar_event()
    example_document_processing()
    example_data_analysis()
    example_multi_stage_chain()


def main():
    parser = argparse.ArgumentParser(
        description="KayGraph Prompt Chaining Examples"
    )
    parser.add_argument(
        "input",
        nargs="?",
        help="Text input for calendar event processing"
    )
    parser.add_argument(
        "--example",
        choices=["calendar", "document", "analysis", "multi", "all"],
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
        example_calendar_event()
    elif args.example == "document":
        example_document_processing()
    elif args.example == "analysis":
        example_data_analysis()
    elif args.example == "multi":
        example_multi_stage_chain()
    elif args.input:
        # Default to calendar event processing
        graph = create_event_extraction_chain()
        shared = {"user_input": args.input}
        graph.run(shared)
        
        if shared.get("event_confirmation"):
            conf = shared["event_confirmation"]
            print(f"✅ {conf.confirmation_message}")
        else:
            print(f"❌ {shared.get('response', 'Not a calendar event')}")
    else:
        print("Running all examples...")
        run_all_examples()


if __name__ == "__main__":
    main()