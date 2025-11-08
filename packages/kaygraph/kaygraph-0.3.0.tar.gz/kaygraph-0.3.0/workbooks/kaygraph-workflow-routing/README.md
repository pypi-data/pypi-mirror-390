# KayGraph Workflow Routing - Intelligent Request Routing

This example demonstrates how to implement intelligent routing patterns in KayGraph, where requests are dynamically routed to specialized handlers based on content analysis.

## Overview

The routing pattern enables:
- Dynamic classification of incoming requests
- Confidence-based routing decisions
- Specialized handlers for different request types
- Fallback handling for low-confidence or unknown requests
- Type-safe data flow between routing and handling nodes

## Key Features

1. **Router Node** - Classifies requests and determines routing
2. **Specialized Handlers** - Type-specific processing nodes
3. **Confidence Thresholds** - Route only high-confidence requests
4. **Structured Data Models** - Pydantic models for type safety
5. **Fallback Mechanisms** - Handle unrecognized requests gracefully

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example calendar      # Calendar routing example
python main.py --example support       # Support ticket routing
python main.py --example document      # Document processing routing
python main.py --example multi        # Multi-level routing

# Interactive mode
python main.py --interactive

# Process specific request
python main.py "Schedule a meeting with Alice next Tuesday at 2pm"
```

## Implementation Patterns

### 1. Calendar Request Routing
Routes calendar requests to appropriate handlers:
- New event creation
- Event modification
- Query handling
- Invalid request rejection

### 2. Support Ticket Routing
Routes support tickets by priority and type:
- Technical issues → Technical support
- Billing questions → Billing department
- Feature requests → Product team
- General inquiries → General support

### 3. Document Processing Routing
Routes documents for processing:
- PDFs → PDF processor
- Images → OCR processor
- Text files → Text analyzer
- Spreadsheets → Data extractor

### 4. Multi-Level Routing
Demonstrates hierarchical routing:
- Primary classification
- Secondary routing within categories
- Specialized sub-handlers

## Architecture

```
Input → RouterNode → (route_1) → Handler1Node
                  → (route_2) → Handler2Node
                  → (route_3) → Handler3Node
                  → (fallback) → FallbackNode
```

The router analyzes input and selects the appropriate handler based on:
- Content classification
- Confidence scores
- Business rules
- Available handlers

## Use Cases

- **API Gateway** - Route requests to appropriate microservices
- **Customer Support** - Direct inquiries to specialized teams
- **Document Processing** - Send files to appropriate processors
- **Task Distribution** - Assign tasks to qualified workers
- **Intent-Based Systems** - Route based on user intent

## Best Practices

1. **Set Appropriate Thresholds** - Balance precision vs recall
2. **Design Clear Categories** - Avoid overlapping classifications
3. **Implement Fallbacks** - Always handle unknown cases
4. **Log Routing Decisions** - For debugging and analytics
5. **Monitor Performance** - Track routing accuracy over time