# README Template for KayGraph Examples

This template should be used for all KayGraph example READMEs to ensure consistency and clarity across the project.

---

# KayGraph [Example Name]

**Category**: [🟢 Pure Python | 🟡 Requires Setup]

[One-line description of what this example demonstrates]

> [If 🟡] 📋 **Requirements**: This example requires [list external services/APIs needed]. See [Setup](#setup) for configuration instructions.

## What You'll Learn

- [Key concept 1 - e.g., "How to structure async workflows"]
- [Key concept 2 - e.g., "Managing shared state between nodes"]
- [Key concept 3 - e.g., "Error handling and retries"]

## Prerequisites

- Python 3.8+
- [If 🟡] [External service] account and API key
- [Any other requirements]

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. [If 🟡] Set up environment variables
export OPENAI_API_KEY="your-key-here"
export DATABASE_URL="postgresql://..."

# 3. Run the example
python main.py

# Or with options
python main.py --option value
```

## How It Works

### Architecture

```
[ASCII diagram showing node connections]
┌─────────────────┐     ┌─────────────────┐
│   Node Name 1   │────▶│   Node Name 2   │
└─────────────────┘     └─────────────────┘
```

### Key Components

1. **[Component Name]** (`path/to/file.py`)
   - [What it does]
   - [Key methods/features]

2. **[Component Name]** (`path/to/file.py`)
   - [What it does]
   - [Key methods/features]

### Data Flow

1. **Input Stage**: [Description]
2. **Processing Stage**: [Description]
3. **Output Stage**: [Description]

## Code Structure

```
kaygraph-[example-name]/
├── main.py              # Entry point
├── nodes/               # KayGraph node implementations
│   ├── __init__.py
│   └── [node_name].py   # [Description]
├── utils/               # Helper functions
│   └── [utility].py     # [Description]
├── requirements.txt     # Dependencies
└── README.md           # This file
```

## Configuration

[If applicable, show configuration options]

```python
# config.py or in main.py
CONFIG = {
    "option1": "value1",
    "option2": "value2"
}
```

## Example Usage

### Basic Example

```python
# Show a simple usage example
from nodes import MyNode

node = MyNode()
result = node.run({"input": "data"})
print(result)
```

### Advanced Example

```python
# Show a more complex usage pattern
```

## Techniques Demonstrated

This example showcases these KayGraph techniques:

1. **[Technique Name]**: See `[file.py:line]` - [Brief description]
2. **[Technique Name]**: See `[file.py:line]` - [Brief description]
3. **[Technique Name]**: See `[file.py:line]` - [Brief description]

## Common Modifications

### 1. [Modification Name]
[Description of what to change and why]

```python
# Original
original_code = "example"

# Modified
modified_code = "example"
```

### 2. [Modification Name]
[Description]

## Performance Characteristics

- **Execution Time**: [Typical range, e.g., "1-5 seconds for 100 items"]
- **Memory Usage**: [Typical usage, e.g., "~50MB for standard workload"]
- **API Calls**: [If applicable, e.g., "1 LLM call per item"]
- **Concurrency**: [e.g., "Processes 10 items in parallel"]

## Troubleshooting

### Common Issues

1. **[Error/Issue Name]**
   - **Symptom**: [What user sees]
   - **Cause**: [Why it happens]
   - **Solution**: [How to fix]

2. **[Error/Issue Name]**
   - **Symptom**: [What user sees]
   - **Cause**: [Why it happens]
   - **Solution**: [How to fix]

### Debug Tips

- Enable verbose logging: `python main.py --debug`
- Check shared state: Add `print(shared)` in `post()` methods
- Monitor node execution: Use `-- graph` operator


## Related Examples

- [kaygraph-[related-example]](../kaygraph-[related-example]): [How it relates]
- [kaygraph-[related-example]](../kaygraph-[related-example]): [How it relates]

## Next Steps

After understanding this example:

1. [Suggested next action]
2. [Another suggestion]
3. [Advanced exploration]

## Resources

- [KayGraph Documentation](https://kaygraph.com/docs)
- [Specific API Documentation](https://...)
- [Related Tutorial](https://...)

---

## Template Usage Instructions

When using this template:

1. **Choose the correct category** (🟢 or 🟡)
2. **Remove sections** that don't apply to your example
3. **Keep descriptions concise** - aim for clarity over completeness
4. **Include real code snippets** from the example
5. **Test all commands** in the Quick Start section
6. **Verify external links** work correctly
7. **Add ASCII diagrams** to visualize architecture
8. **Include performance metrics** from actual testing

### Category Guidelines

- **🟢 Production-Ready**: No external dependencies, works out-of-box
- **🟡 Integration Template**: Requires API keys/services but production-quality code

### Required Sections by Category

| Section | 🟢 Required | 🟡 Required |
|---------|------------|------------|
| Category Badge | ✓ | ✓ |
| Prerequisites | ✓ | ✓ |
| Quick Start | ✓ | ✓ |
| How It Works | ✓ | ✓ |
| External Service Setup | | ✓ |