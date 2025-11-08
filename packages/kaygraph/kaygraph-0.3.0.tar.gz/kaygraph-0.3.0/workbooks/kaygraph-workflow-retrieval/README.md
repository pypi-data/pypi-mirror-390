# KayGraph Workflow Retrieval - Tool-Based Knowledge Retrieval

This example demonstrates tool-based retrieval workflows in KayGraph, where the LLM decides when and how to search a knowledge base.

## Overview

Unlike full RAG systems, this pattern focuses on:
- LLM-driven retrieval decisions
- Simple knowledge base lookups (no embeddings)
- Structured responses with source attribution
- Graceful handling when information isn't available
- Multiple retrieval strategies (exact match, keyword, category)

## Key Features

1. **Smart Retrieval** - LLM decides if KB search is needed
2. **Multiple KB Types** - Support for FAQ, products, policies, etc.
3. **Source Tracking** - Always know where answers came from
4. **Fallback Handling** - Graceful responses when info not found
5. **Query Routing** - Different retrieval strategies based on query type

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example faq          # FAQ retrieval
python main.py --example product      # Product catalog search
python main.py --example policy       # Policy document lookup
python main.py --example multi        # Multi-source retrieval
python main.py --example routing      # Smart query routing

# Interactive mode
python main.py --interactive

# Process specific query
python main.py "What is your return policy?"
```

## Knowledge Base Structure

The system includes several mock knowledge bases:

### FAQ Knowledge Base
```json
{
  "id": 1,
  "question": "What is the return policy?",
  "answer": "Returns accepted within 30 days...",
  "category": "returns"
}
```

### Product Catalog
```json
{
  "id": "PROD-001",
  "name": "Wireless Headphones",
  "price": 79.99,
  "description": "Premium wireless headphones...",
  "category": "electronics"
}
```

### Policy Documents
```json
{
  "id": "POL-001",
  "title": "Privacy Policy",
  "content": "We value your privacy...",
  "last_updated": "2024-01-01"
}
```

## Implementation Patterns

### 1. Basic Retrieval
Simple KB lookup with tool calling:
```
analyze_query >> search_kb >> format_response
```

### 2. Routed Retrieval
Query analysis determines KB type:
```
router >> ("faq", faq_search)
router >> ("product", product_search)
router >> ("policy", policy_search)
```

### 3. Multi-Source Retrieval
Search multiple KBs in parallel:
```
analyzer >> parallel_search([faq_kb, product_kb, policy_kb]) >> aggregator
```

### 4. Conditional Retrieval
Only search when needed:
```
query_analyzer >> ("needs_search", kb_search)
query_analyzer >> ("direct_answer", response_generator)
```

### 5. Hierarchical Retrieval
Try specific then fallback to general:
```
specific_search >> ("not_found", general_search) >> formatter
```

## Architecture

```
User Query → Query Analyzer → Retrieval Decision
                    ↓                ↓
                KB Search      Direct Response
                    ↓
              Source Tracking
                    ↓
            Response Formatter
```

## Best Practices

1. **Let LLM Decide** - Don't force retrieval for every query
2. **Track Sources** - Always include source references
3. **Handle Not Found** - Graceful responses when info missing
4. **Cache Results** - Avoid redundant KB searches
5. **Validate Results** - Ensure retrieved info matches query

## Use Cases

- **Customer Support** - FAQ and policy retrieval
- **E-commerce** - Product information lookup
- **Documentation** - Technical docs search
- **Knowledge Management** - Corporate KB access
- **Chatbots** - Context-aware responses

## Comparison with Full RAG

| Feature | This Pattern | Full RAG |
|---------|-------------|----------|
| Embeddings | No | Yes |
| Vector Search | No | Yes |
| Setup Complexity | Low | High |
| Accuracy | Exact/Keyword | Semantic |
| Use Case | Known KB | Any Documents |

This pattern is ideal when you have structured knowledge bases and want the LLM to intelligently decide when to search.