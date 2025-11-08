# Claude Agent SDK Integration with KayGraph

This directory contains comprehensive examples demonstrating how to integrate the **Claude Agent SDK** with **KayGraph** for building sophisticated AI applications. The examples showcase various patterns from basic chat agents to complex multi-agent systems.

## 🚀 Quick Start

### 1. Installation

```bash
# Install required dependencies
pip install claude-agent-sdk kaygraph aiohttp scikit-learn numpy

# For development with additional tools
pip install -e .[dev]
```

### 2. Environment Setup

Choose your preferred provider and set the corresponding environment variables:

#### Option A: Anthropic Claude (Default)
```bash
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"
```

#### Option B: io.net Models
```bash
export API_KEY="io-v2-your-io-net-api-key"
export ANTHROPIC_BASE_URL="https://api.intelligence.io.solutions/api/v1"
export ANTHROPIC_MODEL="glm-4.6"
```

#### Option C: Z.ai Models
```bash
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="your-z-auth-token"
export ANTHROPIC_MODEL="glm-4.6"
```

### 3. Configuration Check

```bash
# Check your configuration
python claude_config_utils.py

# This will show:
# - Detected provider
# - Configuration validity
# - Available models
# - Current model information
```

## 📁 Example Structure

```
examples/
├── README.md                           # This file
├── kaygraph_claude_base.py             # Base integration components
├── claude_config_utils.py              # Configuration utilities
├── claude_chat_agent.py                # Basic chat agents
├── claude_reasoning_workflow.py        # Multi-step reasoning workflows
├── claude_rag_system.py                # RAG with embeddings
├── claude_tool_agent.py                # Tool-using agents
└── claude_multi_agent_system.py        # Multi-agent coordination
```

## 🎯 Examples Overview

### 1. Base Integration (`kaygraph_claude_base.py`)

**Purpose**: Foundational components for integrating Claude with KayGraph

**Key Components**:
- `ClaudeConfig`: Configuration management for different providers
- `ClaudeNode`: Basic Claude integration node
- `AsyncClaudeNode`: Async version for better performance
- `ValidatedClaudeNode`: Node with input/output validation

**Usage**:
```python
from kaygraph_claude_base import ClaudeNode, ClaudeConfig

config = ClaudeConfig.from_env()
node = ClaudeNode(
    prompt_template="Answer: {question}",
    config=config
)
```

### 2. Chat Agents (`claude_chat_agent.py`)

**Purpose**: Demonstrate conversational AI agents with context management

**Examples**:
- `basic_chat`: Simple one-turn conversations
- `contextual_chat`: Multi-turn conversations with memory
- `different_models`: Testing various model configurations
- `error_handling`: Robust error handling patterns

**Run**:
```bash
python claude_chat_agent.py all                    # Run all examples
python claude_chat_agent.py basic_chat             # Run specific example
```

### 3. Reasoning Workflows (`claude_reasoning_workflow.py`)

**Purpose**: Complex multi-step reasoning and decision-making workflows

**Examples**:
- `problem_analysis`: Break down complex problems systematically
- `decision_tree`: Multi-path decision making
- `creative_process`: Structured creative ideation
- `research_synthesis`: Academic research workflows

**Run**:
```bash
python claude_reasoning_workflow.py all
python claude_reasoning_workflow.py problem_analysis
```

### 4. RAG System (`claude_rag_system.py`)

**Purpose**: Retrieval-Augmented Generation with semantic search

**Features**:
- Document embedding with external APIs
- Semantic search with cosine similarity
- Multi-source document synthesis
- Source attribution and citation

**Requirements**:
```bash
# Additional dependencies
pip install scikit-learn numpy aiohttp

# For embeddings (io.net example)
export EMBEDDING_MODEL="BAAI/bge-multilingual-gemma2"
```

**Run**:
```bash
python claude_rag_system.py all
python claude_rag_system.py basic_rag
```

### 5. Tool-Using Agents (`claude_tool_agent.py`)

**Purpose**: Claude agents with external tool and API integration

**Tools Included**:
- `web_search`: Web search capabilities
- `calculator`: Mathematical computations
- `weather`: Weather information
- `data_analyzer`: Statistical analysis
- `api_request`: Custom API integration

**Run**:
```bash
python claude_tool_agent.py all
python claude_tool_agent.py multi_tool_agent
```

### 6. Multi-Agent Systems (`claude_multi_agent_system.py`)

**Purpose**: Sophisticated multi-agent coordination and collaboration

**Agent Types**:
- `CoordinatorAgent`: Orchestrates specialist agents
- `SpecialistAgent`: Domain-specific expertise
- `AnalystAgent`: Synthesizes multi-agent inputs
- `ReviewerAgent`: Quality assurance and validation
- `DelegationAgent`: Intelligent task distribution

**Run**:
```bash
python claude_multi_agent_system.py all
python claude_multi_agent_system.py specialist_agents
```

## 🔧 Configuration Guide

### Using Configuration Utilities

```python
from claude_config_utils import (
    setup_claude_config,
    get_available_models,
    validate_configuration
)

# Setup configuration with automatic provider detection
config = setup_claude_config()

# Get available models for a specific use case
models = get_available_models(category=ModelCategory.CHAT)

# Validate your current setup
validation = validate_configuration()
print(f"Configuration valid: {validation['valid']}")
```

### Creating Configuration Files

```python
from claude_config_utils import create_env_file, create_config_file

# Create environment file for io.net
env_path = create_env_file(
    provider=Provider.IO_NET,
    api_key="your-api-key",
    model="glm-4.6",
    output_path=".env.io_net"
)

# Create JSON configuration file
config_path = create_config_file(
    provider=Provider.ANTHROPIC,
    model="claude-3-sonnet-20240229",
    max_tokens=4000,
    temperature=0.7,
    output_path="claude_config.json"
)
```

## 🎨 Common Patterns

### 1. Basic Claude Node

```python
from kaygraph import Graph
from kaygraph_claude_base import ClaudeNode

# Create a simple Claude node
node = ClaudeNode(
    prompt_template="You are a helpful assistant. Question: {question}",
    system_prompt="You are Claude, a helpful AI assistant."
)

# Create and run graph
graph = Graph(nodes={"chat": node})
shared_context = {"question": "What is AI?"}
result = await graph.run(start_node="chat", shared=shared_context)
```

### 2. Async Multi-Step Workflow

```python
from kaygraph import Graph
from kaygraph_claude_base import AsyncClaudeNode

class Step1Node(AsyncClaudeNode):
    def __init__(self):
        super().__init__(prompt_template="Step 1: {input}")

class Step2Node(AsyncClaudeNode):
    def __init__(self):
        super().__init__(prompt_template="Step 2: {step1_result}")

# Create workflow
graph = Graph(nodes={
    "step1": Step1Node(),
    "step2": Step2Node()
})

# Execute workflow
shared = {"input": "Starting data"}
await graph.run(start_node="step1", shared=shared)
# Step 1 result is automatically stored in shared context
await graph.run(start_node="step2", shared=shared)
```

### 3. Tool Integration

```python
from claude_agent_sdk import tool, create_sdk_mcp_server

@tool("my_tool", "Tool description", {"param": "string"})
async def my_tool(args):
    # Tool implementation
    return {"content": [{"type": "text", "text": "Result"}]}

# Create tool server
tool_server = create_sdk_mcp_server(
    name="my-tools",
    version="1.0.0",
    tools=[my_tool]
)

# Use in Claude node
node = ClaudeNode(tools=["my_tool"])
```

## 🌐 Provider-Specific Setup

### Anthropic Claude

```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export ANTHROPIC_MODEL="claude-3-sonnet-20240229"
```

**Available Models**:
- `claude-3-sonnet-20240229` (balanced)
- `claude-3-haiku-20240307` (fast)
- `claude-3-opus-20240229` (capable)

### io.net Integration

```bash
export API_KEY="io-v2-eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
export ANTHROPIC_BASE_URL="https://api.intelligence.io.solutions/api/v1"
export ANTHROPIC_MODEL="glm-4.6"
```

**Available Models**:
- `glm-4.6` (general purpose)
- `Qwen2.5-VL-32B-Instruct` (vision)
- `DeepSeek-R1-0528` (reasoning)
- `Llama-3.3-70B-Instruct` (chat)
- `Qwen3-Next-80B-A3B-Instruct` (advanced)

### Z.ai Integration

```bash
export ANTHROPIC_BASE_URL="https://api.z.ai/api/anthropic"
export ANTHROPIC_AUTH_TOKEN="0d141d0d717d4030be9bf12d79f42ea7.ufd8xyzwQHB4WybG"
export ANTHROPIC_MODEL="glm-4.6"
```

## 🔍 Troubleshooting

### Common Issues

1. **Authentication Errors**
   ```bash
   # Check if API key is set
   echo $API_KEY
   echo $ANTHROPIC_API_KEY

   # Validate configuration
   python claude_config_utils.py
   ```

2. **Model Not Available**
   ```bash
   # List available models
   python -c "from claude_config_utils import get_available_models; print([m.name for m in get_available_models()])"
   ```

3. **Import Errors**
   ```bash
   # Install missing dependencies
   pip install claude-agent-sdk kaygraph aiohttp scikit-learn numpy
   ```

4. **Network Issues**
   ```bash
   # Test API connectivity
   curl -H "Authorization: Bearer $API_KEY" https://api.intelligence.io.solutions/api/v1/models
   ```

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Or for specific modules
logging.getLogger('claude_agent_sdk').setLevel(logging.DEBUG)
logging.getLogger('kaygraph').setLevel(logging.DEBUG)
```

## 📚 Advanced Topics

### Custom Node Types

```python
class CustomClaudeNode(AsyncClaudeNode):
    def __init__(self, custom_param=None, **kwargs):
        self.custom_param = custom_param
        super().__init__(**kwargs)

    async def prep(self, shared):
        # Custom preparation logic
        return self.prompt_template.format(**shared)

    async def post(self, shared, prep_res, exec_res):
        # Custom post-processing
        shared["custom_result"] = exec_res.upper()
        return "next_action"
```

### Error Handling Patterns

```python
class RobustClaudeNode(ClaudeNode):
    async def exec(self, prepared_prompt):
        try:
            return await super().exec(prepared_prompt)
        except Exception as e:
            # Retry logic
            for attempt in range(3):
                try:
                    return await super().exec(prepared_prompt)
                except Exception:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
            raise e  # Re-raise if all retries fail
```

### Performance Optimization

```python
# Use async nodes for better performance
class OptimizedNode(AsyncClaudeNode):
    async def exec(self, prepared_prompt):
        # Stream responses for large outputs
        response_parts = []
        async for message in query(prepared_prompt, self.options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_parts.append(block.text)
        return "".join(response_parts)
```

## 🤝 Contributing

To add new examples:

1. Follow the established patterns in existing examples
2. Include comprehensive docstrings with usage instructions
3. Add error handling and validation
4. Test with multiple providers when applicable
5. Update this README with new examples

## 📄 License

These examples are provided under the same license as the Claude Agent SDK and KayGraph projects.

## 🆘 Support

For issues related to:
- **Claude Agent SDK**: Check the [Claude Agent SDK documentation](https://docs.claude.com/)
- **KayGraph**: Check the [KayGraph repository](https://github.com/your-org/kaygraph)
- **These Examples**: Create an issue in the respective repository

---

**Happy coding!** 🚀

These examples demonstrate the powerful combination of Claude's advanced reasoning capabilities with KayGraph's robust workflow orchestration, enabling you to build sophisticated AI applications with ease.