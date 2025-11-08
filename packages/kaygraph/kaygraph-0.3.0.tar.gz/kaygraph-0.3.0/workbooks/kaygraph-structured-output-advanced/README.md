# KayGraph Advanced Structured Output - Production-Ready Structured Generation

This workbook demonstrates advanced structured output patterns using KayGraph, including complex schemas, validation, content filtering, and production-ready error handling.

## Key Concepts

1. **Advanced Schema Design**
   - Complex nested Pydantic models
   - Self-referential and recursive schemas
   - Union types and discriminated unions
   - Custom validators and constraints

2. **Robust Generation Patterns**
   - Retry with progressive schema relaxation
   - Fallback schemas for reliability
   - Partial result handling
   - Schema versioning

3. **Content Safety & Validation**
   - Business rule validation
   - Harmful content filtering
   - PII detection and masking
   - Prompt injection protection

4. **Performance Optimization**
   - Schema caching strategies
   - Batch generation patterns
   - Streaming structured outputs
   - Parallel schema validation

5. **Production Features**
   - Error tracking and metrics
   - Schema evolution support
   - Compliance validation
   - Audit logging

## Examples

### 1. Customer Support Ticket System
- Complex ticket schemas with validation
- Automatic categorization and routing
- Response generation with safety checks
- Escalation workflow integration

### 2. Report Generation Pipeline
- Multi-section structured reports
- Dynamic schema based on report type
- Data extraction and summarization
- Quality assurance validation

### 3. Form Processing System
- Dynamic form schema generation
- Multi-step validation workflow
- Error correction suggestions
- Compliance checking

### 4. API Response Generation
- OpenAPI schema compliance
- Version-aware generation
- Error response formatting
- Rate limit handling

## Usage

```bash
# Run all examples
python main.py

# Run specific example
python main.py --example ticket

# Generate structured output for input
python main.py "Create a support ticket for a billing issue"

# Interactive mode
python main.py --interactive

# Test with specific schema
python main.py --schema ticket "I need help with my subscription"
```

## Implementation Details

The system uses:
- Pydantic v2 for schema definition and validation
- KayGraph's retry mechanisms for robustness
- Custom validators for business rules
- Progressive schema relaxation strategies
- Comprehensive error handling and fallbacks