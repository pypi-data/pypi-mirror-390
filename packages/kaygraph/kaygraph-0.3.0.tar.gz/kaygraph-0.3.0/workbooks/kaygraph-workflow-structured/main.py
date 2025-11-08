#!/usr/bin/env python3
"""
KayGraph Workflow Structured - Type-Safe Data Processing Pipelines
"""

import argparse
import logging
from datetime import date, time
from typing import Dict, Any, List

from kaygraph import Graph
from nodes import (
    MeetingExtractorNode, InvoiceExtractorNode, ContactExtractorNode,
    SchemaValidatorNode, BusinessRuleValidatorNode,
    DataTransformerNode, PipelineMonitorNode, PipelineStageNode,
    PipelineFinalizerNode, BatchValidatorNode, DataQualityAnalyzerNode
)
from models import (
    MeetingEvent, Invoice, ContactInfo, Product,
    SchemaMapping, DataTransformation, PipelineStage,
    InvoiceLineItem, InvoiceAddress
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_extraction():
    """Demonstrate data extraction pipeline."""
    logger.info("\n=== Data Extraction Pipeline ===")
    
    # Nodes
    meeting_extractor = MeetingExtractorNode()
    meeting_validator = SchemaValidatorNode(MeetingEvent, "extracted_meeting")
    
    # Connect
    meeting_extractor >> meeting_validator
    
    # Create extraction graph
    graph = Graph(start=meeting_extractor)
    
    # Test data
    shared = {
        "text": """Team sync meeting on Friday December 15th at 2:00 PM - 3:30 PM.
        Participants: Alice Johnson (alice@company.com, Engineering Lead), 
        Bob Smith (bob@company.com, Product Manager), 
        Charlie Brown (charlie@company.com, Designer).
        Meeting will be held virtually via Zoom: https://zoom.us/j/123456789
        
        Agenda:
        1. Sprint review
        2. Q1 planning discussion
        3. Design mockup review
        
        Please prepare your updates beforehand."""
    }
    
    # Run
    result = graph.run(shared)
    
    # Display results
    if "extracted_meeting_validated" in shared:
        validated = shared["extracted_meeting_validated"]
        logger.info(f"Meeting: {validated['name']}")
        logger.info(f"Date: {validated['date']}")
        logger.info(f"Time: {validated['start_time']} - {validated.get('end_time', 'TBD')}")
        logger.info(f"Participants: {len(validated.get('participants', []))}")
        logger.info(f"Location: {validated.get('location', {}).get('type', 'Unknown')}")
    
    return shared


def example_transformation():
    """Demonstrate schema transformation."""
    logger.info("\n=== Schema Transformation Pipeline ===")
    
    # Create transformation mapping
    mapping = SchemaMapping(
        source_schema="v1_contact",
        target_schema="v2_contact",
        version="v2",
        transformations=[
            DataTransformation(
                source_field="name",
                target_field="full_name",
                transform_type="rename"
            ),
            DataTransformation(
                source_field="email",
                target_field="primary_email",
                transform_type="rename"
            ),
            DataTransformation(
                source_field="phone",
                target_field="phone_number",
                transform_type="cast",
                parameters={"type": "str"}
            ),
            DataTransformation(
                source_field="first_name",
                target_field="display_name",
                transform_type="merge",
                parameters={"fields": ["first_name", "last_name"], "separator": " "}
            )
        ]
    )
    
    # Nodes
    transformer = DataTransformerNode(mapping, "v1_contact", "v2_contact")
    
    # Create graph
    graph = Graph(start=transformer)
    
    # Test data
    shared = {
        "v1_contact": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": 5551234567,
            "first_name": "John",
            "last_name": "Doe"
        }
    }
    
    # Run
    result = graph.run(shared)
    
    # Display results
    if "v2_contact_data" in shared:
        transformed = shared["v2_contact_data"]
        logger.info(f"Transformed data: {transformed}")
    
    return shared


def example_validation():
    """Demonstrate multi-stage validation."""
    logger.info("\n=== Multi-Stage Validation Pipeline ===")
    
    # Define business rules
    invoice_rules = [
        {
            "name": "due_date_check",
            "type": "date_range",
            "start_field": "invoice_date",
            "end_field": "due_date"
        },
        {
            "name": "minimum_total",
            "type": "custom",
            "function": lambda data: {
                "valid": sum(item.get("quantity", 0) * item.get("unit_price", 0) 
                           for item in data.get("line_items", [])) > 0,
                "message": "Invoice total must be greater than 0"
            }
        }
    ]
    
    # Nodes
    extractor = InvoiceExtractorNode()
    schema_validator = SchemaValidatorNode(Invoice, "extracted_invoice")
    business_validator = BusinessRuleValidatorNode(invoice_rules, "extracted_invoice")
    
    # Connect
    extractor >> schema_validator >> business_validator
    
    # Create graph
    graph = Graph(start=extractor)
    
    # Test data
    shared = {
        "invoice_text": """
        Invoice #INV-2024-001
        Date: 2024-01-15
        Due Date: 2024-02-15
        
        Bill To:
        Acme Corp
        John Smith
        123 Main St
        New York, NY 10001
        
        Items:
        - Widget Pro x 5 @ $99.99 each
        - Service Fee x 1 @ $50.00 each
        
        Subtotal: $549.95
        Tax (8%): $44.00
        Total: $593.95
        
        Payment Terms: Net 30
        """
    }
    
    # Run
    result = graph.run(shared)
    
    # Display results
    if "extracted_invoice_business_validation" in shared:
        validation = shared["extracted_invoice_business_validation"]
        logger.info(f"Business rules valid: {validation['valid']}")
        if not validation['valid']:
            logger.info(f"Violations: {validation['violations']}")
    
    return shared


def example_migration():
    """Demonstrate schema migration pipeline."""
    logger.info("\n=== Schema Migration Pipeline ===")
    
    # Stage 1: Extract from old format
    old_extractor = ContactExtractorNode()
    
    # Stage 2: Validate old schema
    old_validator = SchemaValidatorNode(ContactInfo, "extracted_contact")
    
    # Stage 3: Transform to new schema
    migration_mapping = SchemaMapping(
        source_schema="contact_v1",
        target_schema="contact_v2",
        version="v2",
        transformations=[
            DataTransformation(
                source_field="emails",
                target_field="email_addresses",
                transform_type="rename"
            ),
            DataTransformation(
                source_field="phones",
                target_field="phone_numbers",
                transform_type="rename"
            )
        ]
    )
    migrator = DataTransformerNode(migration_mapping, "extracted_contact_validated", "migrated_contact")
    
    # Connect
    old_extractor >> old_validator >> migrator
    
    # Create graph
    graph = Graph(start=old_extractor)
    
    # Test data
    shared = {
        "contact_text": """
        Contact: Sarah Johnson
        Title: Senior Marketing Manager
        Company: TechCorp Inc.
        
        Email: sarah.johnson@techcorp.com (work)
        Phone: +1 (555) 123-4567 (mobile)
        
        LinkedIn: linkedin.com/in/sarahjohnson
        """
    }
    
    # Run
    result = graph.run(shared)
    
    # Display results
    if "migrated_contact" in shared:
        migration_result = shared["migrated_contact"]
        logger.info(f"Migration success: {migration_result.get('success')}")
        if migration_result.get('success'):
            logger.info(f"Migrated data: {migration_result['transformed_data']}")
    
    return shared


def example_analytics():
    """Demonstrate end-to-end analytics pipeline."""
    logger.info("\n=== Analytics Pipeline ===")
    
    # Pipeline stages
    stages = [
        PipelineStage(
            stage_name="data_ingestion",
            stage_type="extract",
            output_schema="raw_records"
        ),
        PipelineStage(
            stage_name="data_validation",
            stage_type="validate",
            input_schema="raw_records",
            output_schema="validated_records",
            error_handling="skip"
        ),
        PipelineStage(
            stage_name="data_transformation",
            stage_type="transform",
            input_schema="validated_records",
            output_schema="transformed_records"
        ),
        PipelineStage(
            stage_name="quality_analysis",
            stage_type="validate",
            input_schema="batch_records"
        )
    ]
    
    # Nodes
    monitor = PipelineMonitorNode("analytics_pipeline_001")
    
    # Stage implementations
    def ingest_data(data):
        # Simulate data ingestion
        return [
            {
                "invoice_number": "INV-001",
                "invoice_date": "2024-01-01",
                "due_date": "2024-02-01",
                "billing_address": {
                    "company_name": "Test Co",
                    "street": "123 Main St",
                    "city": "Boston",
                    "postal_code": "02101",
                    "country": "USA"
                },
                "line_items": [
                    {
                        "description": "Product A",
                        "quantity": 5,
                        "unit_price": 100
                    }
                ]
            },
            {
                "invoice_number": "INV-002",
                "invoice_date": "2024-01-02",
                "due_date": "2024-02-02",
                "billing_address": {
                    "company_name": "Another Co",
                    "street": "456 Oak Ave",
                    "city": "New York",
                    "postal_code": "10001",
                    "country": "USA"
                },
                "line_items": [
                    {
                        "description": "Service B",
                        "quantity": 1,
                        "unit_price": 500
                    }
                ]
            },
            {
                "invoice_number": "INV-003",
                "invoice_date": "2024-01-03",
                "due_date": "2024-01-02",  # Invalid: due before invoice
                "billing_address": {
                    "street": "789 Pine Rd",  # Missing company
                    "city": "Chicago"
                    # Missing postal code
                },
                "line_items": []  # No items
            }
        ]
    
    ingestion = PipelineStageNode(stages[0], ingest_data)
    
    # Batch validator
    batch_validator = BatchValidatorNode(Invoice)
    
    # Quality analyzer
    quality_analyzer = DataQualityAnalyzerNode()
    
    # Finalizer
    finalizer = PipelineFinalizerNode()
    
    # Connect pipeline
    monitor >> ingestion >> batch_validator >> quality_analyzer >> finalizer
    
    # Create graph
    graph = Graph(start=monitor)
    
    # Prepare shared context
    shared = {}
    
    # Run pipeline
    result = graph.run(shared)
    
    # Display results
    if "pipeline_result" in shared:
        pipeline_result = shared["pipeline_result"]
        logger.info(f"\nPipeline Summary:")
        logger.info(f"  ID: {pipeline_result.pipeline_id}")
        logger.info(f"  Duration: {pipeline_result.duration_seconds:.2f}s")
        logger.info(f"  Success: {pipeline_result.success}")
        
        quality = pipeline_result.data_quality
        logger.info(f"\nData Quality:")
        logger.info(f"  Total records: {quality.total_records}")
        logger.info(f"  Valid: {quality.valid_records}")
        logger.info(f"  Invalid: {quality.invalid_records}")
        logger.info(f"  Success rate: {quality.success_rate:.2%}")
        logger.info(f"  Overall quality: {quality.overall_quality_score:.2%}")
    
    return shared


def run_interactive():
    """Run interactive mode."""
    logger.info("\n=== Interactive Mode ===")
    
    print("\nEnter text to extract structured data from.")
    print("Type 'exit' to quit.\n")
    
    while True:
        text = input("Enter text: ").strip()
        if text.lower() == 'exit':
            break
        
        # Detect content type and extract
        if any(word in text.lower() for word in ["meeting", "sync", "call", "discussion"]):
            logger.info("Detected meeting content...")
            extractor = MeetingExtractorNode()
            validator = SchemaValidatorNode(MeetingEvent, "extracted_meeting")
            extractor >> validator
            graph = Graph(start=extractor)
            
            shared = {"text": text}
            graph.run(shared)
            
            if "extracted_meeting_validated" in shared:
                logger.info(f"Extracted: {shared['extracted_meeting_validated']}")
        
        elif any(word in text.lower() for word in ["invoice", "bill", "payment"]):
            logger.info("Detected invoice content...")
            extractor = InvoiceExtractorNode()
            validator = SchemaValidatorNode(Invoice, "extracted_invoice")
            extractor >> validator
            graph = Graph(start=extractor)
            
            shared = {"invoice_text": text}
            graph.run(shared)
            
            if "extracted_invoice_validated" in shared:
                logger.info(f"Extracted: {shared['extracted_invoice_validated']}")
        
        elif any(word in text.lower() for word in ["contact", "email", "phone"]):
            logger.info("Detected contact content...")
            extractor = ContactExtractorNode()
            validator = SchemaValidatorNode(ContactInfo, "extracted_contact")
            extractor >> validator
            graph = Graph(start=extractor)
            
            shared = {"contact_text": text}
            graph.run(shared)
            
            if "extracted_contact_validated" in shared:
                logger.info(f"Extracted: {shared['extracted_contact_validated']}")
        
        else:
            logger.info("Could not detect content type. Please be more specific.")
        
        print()


def main():
    parser = argparse.ArgumentParser(description="KayGraph Workflow Structured Examples")
    parser.add_argument("text", nargs="?", help="Text to extract data from")
    parser.add_argument("--example", choices=["extraction", "transformation", "validation", 
                                               "migration", "analytics", "all"],
                        help="Run specific example")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        run_interactive()
    elif args.text:
        # Process provided text
        logger.info(f"Processing: {args.text}")
        
        # Try meeting extraction
        extractor = MeetingExtractorNode()
        validator = SchemaValidatorNode(MeetingEvent, "extracted_meeting")
        extractor >> validator
        graph = Graph(start=extractor)
        
        shared = {"text": args.text}
        result = graph.run(shared)
        
        if "extracted_meeting_validated" in shared:
            logger.info(f"Extracted meeting: {shared['extracted_meeting_validated']}")
        else:
            logger.info("Could not extract meeting information")
    
    elif args.example:
        if args.example == "extraction" or args.example == "all":
            example_extraction()
        
        if args.example == "transformation" or args.example == "all":
            example_transformation()
        
        if args.example == "validation" or args.example == "all":
            example_validation()
        
        if args.example == "migration" or args.example == "all":
            example_migration()
        
        if args.example == "analytics" or args.example == "all":
            example_analytics()
    
    else:
        # Run all examples
        logger.info("Running all examples...")
        example_extraction()
        example_transformation()
        example_validation()
        example_migration()
        example_analytics()


if __name__ == "__main__":
    main()