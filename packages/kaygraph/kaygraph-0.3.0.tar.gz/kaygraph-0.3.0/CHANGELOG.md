# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-11-07

### Added
- **PersistentGraph** - State persistence and checkpointing for workflows (343 lines, 14 tests)
  - Auto-save workflow state to disk with JSON serialization
  - Resume execution from checkpoints after crashes or interruptions
  - Configurable checkpoint intervals and cleanup policies
- **InteractiveGraph** - Interactive loop execution for chat and continuous workflows (289 lines, 14 tests)
  - Support for chat loops and event-driven workflows
  - Exit condition handling with configurable iteration limits
  - Transient data cleanup between iterations
  - `UserInputNode` for user input handling and command parsing
- **AsyncInteractiveGraph** - Async version of InteractiveGraph for async workflows
- **SubGraphNode** - Graph composition and modularity (327 lines, 11 tests)
  - Encapsulate entire graphs as reusable node components
  - Input/output mapping for isolated execution contexts
  - `ConditionalSubGraphNode` for conditional graph execution
  - `ParallelSubGraphNode` for parallel graph execution
  - `compose_graphs()` utility for sequential graph composition
- **Agent Module** - Complete LLM agent framework with ReAct pattern (1,814 lines)
  - **Tools System** (`agent/tools.py`)
    - `ToolRegistry` for centralized tool management
    - `Tool` base class and `SimpleTool` function wrapper
  - **Agent Nodes** (`agent/nodes.py`)
    - `ThinkNode` for LLM reasoning and decision-making
    - `ActNode` for tool execution and observation
    - `OutputNode` for final output formatting
  - **Pre-built Patterns** (`agent/patterns.py`)
    - `create_react_agent()` - General-purpose ReAct agent
    - `create_coding_agent()` - Code assistant with file tools
    - `create_research_agent()` - Research workflows
    - `create_debugging_agent()` - Debug assistant
    - `create_data_analysis_agent()` - Data analysis workflows
  - **Anthropic Workflow Patterns** (`agent/anthropic_patterns.py`)
    - Prompt chaining for sequential transformations
    - Routing and classification workflows
    - Parallel sectioning and voting mechanisms
    - Orchestrator-workers coordination pattern
    - Evaluator-optimizer iterative improvement loops

### Changed
- Updated type annotations to use `from __future__ import annotations` for better forward compatibility
- Improved type safety with explicit Dict, Optional, List, Union imports for Python 3.11 compatibility
- Enhanced InteractiveGraph to properly handle Graph.run() return values

### Fixed
- Fixed InteractiveGraph.run_interactive() to handle None return from Graph.run()
- Fixed ParallelSubGraphNode.prep() to properly prepare input for parallel execution

## [0.2.0] - 2025-11-02

### Added
- Enhanced node lifecycle with execution context management
- Declarative workflow support with JSON/YAML serialization
- Visual workflow converter for n8n/Zapier-style definitions
- Node parameter validation with defensive copying
- Execution context tracking per node (`get_context`/`set_context`)
- CLI module for command-line workflow execution
- Workflow loader for dynamic workflow imports
- Better support for conditional routing between nodes
- Improved error handling with detailed error messages

### Changed
- Enhanced BaseNode with generic type parameters for better type safety
- Improved Graph execution with more informative error messages
- More robust successor management in nodes
- Better handling of async node execution
- Internal architecture improvements for extensibility

### Fixed
- Fixed issues with node parameter handling
- Improved error messages for debugging workflows
- Better handling of shared context mutations

## [0.0.2] - 2025-07-31

### Changed
- **BREAKING**: Updated minimum Python version requirement from 3.8 to 3.11
- Modernized type hints to use Python 3.10+ syntax:
  - `Dict[str, Any]` → `dict[str, Any]`
  - `List[Any]` → `list[Any]`
  - `Optional[str]` → `str | None`
- Updated development tooling to target Python 3.11

### Added
- Added support for Python 3.12 and 3.13 in classifiers

### Removed
- Removed support for Python versions 3.8, 3.9, and 3.10

## [0.0.1] - 2025-07-29

### Added
- Initial release of KayGraph
- Core abstractions: BaseNode, Node, Graph
- Async support with AsyncNode and AsyncGraph
- Batch processing with BatchNode and ParallelBatchNode
- Built-in resilience with retries and fallbacks
- Thread-safe execution with node copying
- Zero dependencies - pure Python implementation