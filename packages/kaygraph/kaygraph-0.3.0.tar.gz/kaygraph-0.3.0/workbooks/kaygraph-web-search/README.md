# KayGraph Web Search - Search Integration Patterns

This workbook demonstrates web search integration patterns using KayGraph, including real-time search, result processing, and answer synthesis.

## Key Concepts

1. **Multi-Provider Search**: Support for SERP API, DuckDuckGo, and mock search
2. **Result Processing**: Extract, filter, and rank search results
3. **Answer Synthesis**: Combine search results into coherent answers
4. **Source Attribution**: Track and cite sources properly
5. **Search Refinement**: Iterative search with query reformulation

## Supported Search Providers

### 1. SERP API (Recommended)
- Supports Google, Bing, DuckDuckGo, and more
- Requires API key: `SERP_API_KEY`
- Rich results with snippets, links, and metadata

### 2. DuckDuckGo (Free)
- No API key required
- Limited to basic web search
- Good for testing and development

### 3. Mock Search
- For testing without API calls
- Returns predefined results

## Examples

### 1. Basic Web Search
- Simple query → search → synthesize answer
- Automatic source citation

### 2. Research Assistant
- Multi-step research process
- Fact verification across sources
- Comprehensive report generation

### 3. Real-time Information
- Current events and news
- Stock prices and weather
- Time-sensitive queries

### 4. Comparison Search
- Search multiple topics
- Compare and contrast results
- Structured analysis

## Usage

```bash
# Run all examples
python main.py

# Run specific example
python main.py --example basic

# Search for specific query
python main.py "What are the latest developments in quantum computing?"

# Interactive mode
python main.py --interactive

# Use specific search provider
python main.py --provider serp "your query"
```

## Configuration

Set environment variables for API access:
```bash
# For SERP API
export SERP_API_KEY="your-serpapi-key"

# For other providers (if needed)
export BING_API_KEY="your-bing-key"
```

## Implementation Details

The search system uses:
- Query analysis to determine search intent
- Parallel searches for comprehensive results
- Result deduplication and ranking
- LLM-based answer synthesis
- Proper source attribution
- Error handling and fallbacks