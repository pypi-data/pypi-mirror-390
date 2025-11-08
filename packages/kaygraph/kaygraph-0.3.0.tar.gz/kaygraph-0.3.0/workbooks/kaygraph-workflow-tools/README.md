# KayGraph Workflow Tools - Advanced Tool Integration

This example demonstrates how to build workflows with advanced tool integration in KayGraph, including tool calling, chaining, parallel execution, and error handling.

## Overview

Advanced tool integration enables:
- Dynamic tool selection based on context
- Tool chaining for complex operations
- Parallel tool execution for efficiency
- Retry and fallback strategies
- Tool result validation and transformation
- Tool registry and discovery

## Key Features

1. **Tool Registry** - Centralized tool management and discovery
2. **Dynamic Tool Selection** - AI-driven tool selection based on task
3. **Tool Chaining** - Sequential tool execution with data flow
4. **Parallel Tools** - Concurrent execution for independent tools
5. **Error Handling** - Robust retry and fallback mechanisms

## Running the Examples

```bash
# Run all examples
python main.py --example all

# Specific examples
python main.py --example basic        # Basic tool calling
python main.py --example dynamic      # Dynamic tool selection
python main.py --example chain        # Tool chaining
python main.py --example parallel     # Parallel execution
python main.py --example orchestrated # Complex orchestration

# Interactive mode
python main.py --interactive

# Process specific query
python main.py "What's the weather in Paris and New York?"
```

## Available Tools

### Weather Tool
- Get current weather for any location
- Supports coordinates and city names
- Returns temperature, conditions, wind speed

### Calculator Tool
- Perform mathematical calculations
- Supports basic and advanced operations
- Expression evaluation

### Search Tool
- Web search functionality
- Returns relevant results
- Supports filtering and ranking

### Time Tool
- Get current time in any timezone
- Date calculations
- Time zone conversions

### Database Tool
- Query structured data
- CRUD operations
- Transaction support

## Implementation Patterns

### 1. Basic Tool Calling
Simple tool invocation with structured inputs/outputs:
```python
weather_tool >> format_result >> response
```

### 2. Dynamic Tool Selection
AI selects appropriate tool based on user query:
```python
analyze_query >> select_tool >> execute_tool >> format_response
```

### 3. Tool Chaining
Sequential tool execution with data dependencies:
```python
get_location >> get_weather >> get_forecast >> summarize
```

### 4. Parallel Tool Execution
Concurrent execution for independent operations:
```python
ParallelToolNode([weather_tool, news_tool, events_tool]) >> aggregate
```

### 5. Orchestrated Workflows
Complex multi-tool workflows with conditions:
```python
router >> ("weather", weather_flow)
router >> ("search", search_flow)
router >> ("calculate", calc_flow)
```

## Architecture

```
User Query → Tool Selector → Tool Executor → Result Validator → Response
                    ↓              ↓               ↓
                Tool Registry  Error Handler  Transformer
```

## Tool Definition Format

```python
@tool_decorator
def my_tool(param1: str, param2: int) -> ToolResult:
    """Tool description for AI selection.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        ToolResult with status and data
    """
    # Implementation
    return ToolResult(success=True, data={...})
```

## Best Practices

1. **Tool Documentation** - Clear descriptions for AI selection
2. **Input Validation** - Validate all tool inputs
3. **Error Handling** - Graceful degradation on failures
4. **Result Caching** - Cache expensive tool calls
5. **Rate Limiting** - Respect API limits
6. **Monitoring** - Track tool usage and performance

## Use Cases

- **Information Gathering** - Aggregate data from multiple sources
- **Task Automation** - Chain tools for complex workflows
- **Decision Support** - Use tools to gather decision inputs
- **Data Processing** - Transform data through tool pipelines
- **Integration Hub** - Connect various services through tools

## Security Considerations

1. **Input Sanitization** - Clean all user inputs
2. **Access Control** - Limit tool access by context
3. **API Key Management** - Secure credential storage
4. **Rate Limiting** - Prevent abuse
5. **Audit Logging** - Track all tool usage