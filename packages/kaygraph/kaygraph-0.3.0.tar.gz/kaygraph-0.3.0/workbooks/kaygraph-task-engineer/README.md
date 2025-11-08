# KayGraph Task Engineer

A lightweight, fast task execution system built with KayGraph that can handle various software engineering tasks using fast LLMs.

## Features

- **File Operations**: Find one-time use files, search for patterns, edit specific lines
- **Code Generation**: Create new code using fast LLMs (2000+ tokens/s)
- **Task Decomposition**: Break large features into executable steps
- **Bidirectional Flow**: Can plan for humans OR execute autonomously
- **Generalizable**: Handles wide variety of engineering tasks with ~300 lines

## Architecture

```
TaskAnalyzer → Route by Task Type → Specialized Handlers → Completion
                                     ├── FileCleanupFinder
                                     ├── CodeEditor
                                     ├── FileSearcher
                                     └── LLMPlanner → Executor
```

## Task Types

1. **File Cleanup**: Finds temporary/one-time use files
   - Pattern matching (tmp, test, backup, timestamps, UUIDs)
   - Age-based detection
   - Location analysis

2. **Code Editing**: Precise file modifications
   - Line-specific edits
   - Global replacements
   - Pattern-based removal
   - Content insertion

3. **File Search**: Advanced file and content search
   - File pattern matching
   - Content grep with context
   - Multi-criteria search

4. **LLM Tasks**: Complex operations using Cerebras API
   - Task planning and decomposition
   - Code generation
   - Step-by-step execution
   - Human review when needed

## Usage

```python
from main import build_task_engineer

# Build the graph
graph = build_task_engineer()

# Execute a task
shared = {
    "task": "Find all Python files containing TODO comments",
    "context": {}
}

graph.run(shared, start_node="analyzer")
```

## Example Tasks

```python
# Find cleanup candidates
"Find all temporary files in the project that look like one-time use"

# Edit specific lines
"Find config.py and edit line 42 to change DEBUG=True to DEBUG=False"

# Search for patterns
"Search for all Python files containing TODO comments"

# Generate code
"Create a simple REST API endpoint for user authentication"
```

## LLM Integration

Configure Cerebras API for fast execution:

```python
import openai

client = openai.OpenAI(
    base_url="https://api.cerebras.ai/v1",
    api_key=os.environ.get("CEREBRAS_API_KEY")
)

# Use qwen-3-32b for 2000+ tokens/s performance
```

## Extending

Add new task types by:

1. Adding detection pattern to `TaskAnalyzer`
2. Creating specialized node for the task
3. Connecting to the graph with appropriate routing

## Key Benefits

- **Lightweight**: ~300 lines of core code
- **Fast**: Leverages 2000 token/s LLMs
- **Flexible**: Handles diverse engineering tasks
- **Extensible**: Easy to add new capabilities
- **Production-Ready**: Built on KayGraph patterns