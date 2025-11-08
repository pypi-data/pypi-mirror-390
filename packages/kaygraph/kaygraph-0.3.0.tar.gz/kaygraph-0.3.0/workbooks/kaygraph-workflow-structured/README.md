# KayGraph Workflow Structured - Type-Safe Data Processing Pipelines

This example demonstrates how to build structured data processing workflows in KayGraph with strong type safety, validation, and transformation capabilities.

## Overview

Structured workflows enable:
- Type-safe data extraction from unstructured sources
- Multi-stage transformation pipelines with validation
- Schema evolution and migration patterns
- Error handling with partial results
- Data quality monitoring throughout the pipeline

## Key Features

1. **Type-Safe Extraction** - Extract structured data from text/documents
2. **Schema Validation** - Validate data at each pipeline stage
3. **Data Transformation** - Transform between schemas with type safety
4. **Pipeline Composition** - Compose complex pipelines from simple stages
5. **Error Recovery** - Handle partial failures gracefully

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example extraction     # Data extraction pipeline
python main.py --example transformation # Schema transformation
python main.py --example validation     # Multi-stage validation
python main.py --example migration      # Schema migration
python main.py --example analytics      # Analytics pipeline

# Interactive mode
python main.py --interactive

# Process specific text
python main.py "Extract meeting details from: Team sync on Friday at 2pm with Alice, Bob, and Charlie"
```

## Implementation Patterns

### 1. Data Extraction Pipeline
Extracts structured data from unstructured text:
- Meeting extraction (participants, time, location)
- Invoice processing (line items, totals, dates)
- Contact information extraction
- Product catalog parsing

### 2. Schema Transformation
Transforms data between different schemas:
- API response mapping
- Database schema migration
- Format conversion (CSV → JSON → Parquet)
- Field normalization

### 3. Multi-Stage Validation
Validates data through multiple stages:
- Schema validation
- Business rule validation
- Cross-reference validation
- Consistency checks

### 4. Schema Migration
Handles schema evolution:
- Version management
- Backward compatibility
- Migration strategies
- Rollback support

### 5. Analytics Pipeline
End-to-end analytics workflow:
- Data ingestion
- Cleaning and normalization
- Feature extraction
- Aggregation and reporting

## Architecture

```
Raw Input → ExtractorNode → ValidatorNode → TransformerNode → OutputNode
                ↓               ↓                ↓
            ErrorHandler    ErrorHandler    ErrorHandler
                ↓               ↓                ↓
            PartialResult   PartialResult   PartialResult
```

## Type Safety Features

1. **Pydantic Models** - Strong typing throughout
2. **Schema Versioning** - Handle schema changes
3. **Validation Layers** - Multiple validation points
4. **Type Coercion** - Safe type conversions
5. **Error Types** - Typed error handling

## Use Cases

- **Data Integration** - ETL pipelines with type safety
- **API Processing** - Structured API response handling
- **Document Processing** - Extract structured data from documents
- **Data Migration** - Migrate between systems/schemas
- **Quality Assurance** - Ensure data quality throughout pipeline

## Best Practices

1. **Define Clear Schemas** - Use Pydantic for all data models
2. **Validate Early** - Catch errors as soon as possible
3. **Handle Partial Results** - Don't fail entire pipeline for one bad record
4. **Version Your Schemas** - Plan for schema evolution
5. **Monitor Data Quality** - Track validation failures and data quality metrics