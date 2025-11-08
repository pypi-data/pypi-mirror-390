# KayGraph-Aider Implementation Plan

**Generated**: 2025-11-05
**Objective**: Complete implementation plan for reimplementing Aider using KayGraph

---

## Executive Summary

We'll build **KayGraph-Aider** in phases:
1. **Week 1**: Core enhancements + foundation
2. **Week 2**: Edit system + first working version
3. **Week 3**: Multiple coders + advanced features
4. **Week 4**: Polish + production readiness

**Key Innovation**: Using KayGraph's declarative workflow system to make Aider's coder system modular and extensible.

---

## Repository Structure

```
kaygraph-aider/
├── README.md                           # Project overview & quick start
├── requirements.txt                    # Dependencies (tree-sitter, etc.)
├── setup.py                           # Package setup
├── .env.example                       # API keys template
│
├── kaygraph_aider/                    # Main package
│   ├── __init__.py
│   ├── cli.py                        # CLI entry point (like Aider's main.py)
│   │
│   ├── lib/                          # KayGraph enhancements
│   │   ├── __init__.py
│   │   ├── persistent_graph.py       # State persistence
│   │   ├── interactive_graph.py      # Interactive loops
│   │   ├── subgraph_node.py         # Composable subgraphs
│   │   ├── stream_node.py           # Streaming support
│   │   └── typed_node.py            # Type-safe nodes
│   │
│   ├── nodes/                        # Core nodes
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── user_input_node.py   # Get user input/commands
│   │   │   ├── command_handler.py   # Handle /commands
│   │   │   └── router_node.py       # Route to appropriate flow
│   │   ├── context/
│   │   │   ├── repomap_node.py      # Build codebase context
│   │   │   ├── file_selector.py     # Select relevant files
│   │   │   └── context_builder.py   # Assemble full context
│   │   ├── coders/
│   │   │   ├── base_coder.py        # Base coder node
│   │   │   ├── coder_selector.py    # Pick best coder
│   │   │   ├── editblock_coder.py   # Search/replace blocks
│   │   │   ├── wholefile_coder.py   # Whole file replacement
│   │   │   ├── udiff_coder.py       # Unified diff format
│   │   │   ├── architect_coder.py   # Planning mode
│   │   │   └── ask_coder.py         # Q&A only
│   │   ├── edit/
│   │   │   ├── edit_parser.py       # Parse LLM responses
│   │   │   ├── file_updater.py      # Apply edits to files
│   │   │   ├── fuzzy_matcher.py     # Fuzzy string matching
│   │   │   └── syntax_validator.py  # Validate syntax
│   │   └── git/
│   │       ├── git_manager.py       # Git operations
│   │       ├── commit_node.py       # Create commits
│   │       └── diff_viewer.py       # Show diffs
│   │
│   ├── workflows/                     # Composed workflows
│   │   ├── __init__.py
│   │   ├── main_workflow.py         # Main Aider workflow
│   │   ├── edit_workflow.py         # Edit cycle subgraph
│   │   ├── command_workflow.py      # Command handling subgraph
│   │   └── coder_workflows/         # Per-coder workflows
│   │       ├── editblock_flow.py
│   │       ├── wholefile_flow.py
│   │       └── architect_flow.py
│   │
│   ├── utils/                        # Utilities
│   │   ├── __init__.py
│   │   ├── repomap/
│   │   │   ├── builder.py          # RepoMap builder
│   │   │   ├── tree_sitter_parser.py # AST parsing
│   │   │   ├── ranking.py          # Relevance ranking
│   │   │   └── cache.py            # Caching layer
│   │   ├── parsers/
│   │   │   ├── editblock_parser.py # Parse SEARCH/REPLACE
│   │   │   ├── udiff_parser.py     # Parse unified diffs
│   │   │   └── wholefile_parser.py # Parse whole files
│   │   ├── llm/
│   │   │   ├── model_router.py     # Route to different LLMs
│   │   │   ├── claude_client.py    # Claude integration
│   │   │   ├── openai_client.py    # OpenAI integration
│   │   │   └── cost_tracker.py     # Track API costs
│   │   └── terminal/
│   │       ├── rich_display.py     # Rich terminal UI
│   │       ├── progress.py         # Progress bars
│   │       └── syntax_highlight.py # Code highlighting
│   │
│   ├── prompts/                      # Prompt templates
│   │   ├── system/
│   │   │   ├── base_system.md      # Base system prompt
│   │   │   ├── conventions.md      # Coding conventions
│   │   │   └── languages/          # Language-specific
│   │   ├── coders/
│   │   │   ├── editblock.md       # EditBlock format
│   │   │   ├── wholefile.md       # WholeFile format
│   │   │   ├── architect.md       # Architect mode
│   │   │   └── examples/          # Format examples
│   │   └── commands/               # Command-specific prompts
│   │
│   └── config/                       # Configuration
│       ├── __init__.py
│       ├── settings.py             # Global settings
│       ├── models.yaml             # Model configurations
│       └── default_config.yaml     # Default configuration
│
├── tests/                            # Test suite
│   ├── unit/
│   │   ├── test_nodes/
│   │   ├── test_parsers/
│   │   └── test_utils/
│   ├── integration/
│   │   ├── test_workflows/
│   │   ├── test_coders/
│   │   └── test_commands/
│   └── fixtures/
│       ├── sample_repos/           # Test repositories
│       ├── edit_responses/         # Sample LLM responses
│       └── expected_outputs/       # Expected results
│
├── examples/                         # Example usage
│   ├── basic_usage.py              # Simple example
│   ├── multi_file_edit.py          # Multi-file editing
│   ├── custom_coder.py             # Adding custom coder
│   └── batch_processing.py         # Batch mode
│
├── docs/                            # Documentation
│   ├── getting_started.md         # Quick start guide
│   ├── architecture.md            # System architecture
│   ├── extending_coders.md        # How to add coders
│   ├── api_reference.md           # API documentation
│   └── comparison_to_aider.md     # Aider comparison
│
└── scripts/                         # Utility scripts
    ├── setup_dev.sh                # Development setup
    ├── run_tests.sh                # Test runner
    └── benchmark.py                # Performance benchmarks
```

---

## Implementation Phases

### Phase 0: Foundation (Days 1-2)

**Goal**: Set up project and core enhancements

```bash
# Create project structure
mkdir -p kaygraph-aider/{kaygraph_aider,tests,docs,examples}
cd kaygraph-aider

# Initialize project
git init
python -m venv venv
source venv/activate
```

**Tasks**:
1. Create enhanced KayGraph classes in `lib/`:
   - `PersistentGraph` for state management
   - `InteractiveGraph` for chat loops
   - `SubGraphNode` for composable workflows
   - `StreamNode` for real-time output

2. Set up project structure:
   - Create all directories
   - Write setup.py and requirements.txt
   - Initialize git repository

**Deliverable**: Working project structure with enhanced KayGraph classes

### Phase 1: Core Infrastructure (Days 3-5)

**Goal**: Implement foundational nodes

**Key Files to Create**:

```python
# kaygraph_aider/nodes/base/user_input_node.py
from kaygraph_aider.lib import InteractiveNode

class UserInputNode(InteractiveNode):
    """Get user input and route to appropriate handler."""

    def exec(self, prep_res):
        prompt = prep_res.get("prompt", "\n> ")
        user_input = input(prompt).strip()

        # Parse for commands
        if user_input.startswith("/"):
            parts = user_input[1:].split()
            return {
                "type": "command",
                "command": parts[0],
                "args": parts[1:] if len(parts) > 1 else []
            }

        return {
            "type": "message",
            "content": user_input
        }

    def post(self, shared, prep_res, exec_res):
        if exec_res["type"] == "command":
            shared["last_command"] = exec_res
            return exec_res["command"]  # Route to command handler

        shared["user_message"] = exec_res["content"]
        shared["messages"].append({"role": "user", "content": exec_res["content"]})
        return "process"  # Route to main processing
```

```python
# kaygraph_aider/nodes/context/repomap_node.py
from pathlib import Path
from kaygraph import AsyncNode

class RepoMapNode(AsyncNode):
    """Build codebase context for LLM."""

    def __init__(self):
        super().__init__(node_id="repomap")
        self.cache = {}

    async def prep(self, shared):
        return {
            "repo_path": Path(shared.get("repo_path", ".")),
            "target_files": shared.get("files_to_edit", []),
            "user_query": shared.get("user_message", "")
        }

    async def exec(self, prep_res):
        # Simple version first (no tree-sitter)
        repo_path = prep_res["repo_path"]
        files = prep_res["target_files"]

        context_parts = []

        # Add file contents
        for file in files:
            filepath = repo_path / file
            if filepath.exists():
                content = filepath.read_text()
                context_parts.append(f"```{file}\n{content}\n```")

        return {
            "context": "\n\n".join(context_parts),
            "tokens": len("\n\n".join(context_parts).split())
        }

    def post(self, shared, prep_res, exec_res):
        shared["repomap_context"] = exec_res["context"]
        shared["context_tokens"] = exec_res["tokens"]
        return None
```

**Deliverable**: Basic input and context building working

### Phase 2: First Working Coder (Days 6-8)

**Goal**: Implement EditBlock coder end-to-end

```python
# kaygraph_aider/nodes/coders/editblock_coder.py
from kaygraph import AsyncNode
from kaygraph_aider.utils.llm import call_llm

class EditBlockCoder(AsyncNode):
    """Search/replace block edit format."""

    def __init__(self):
        super().__init__(node_id="editblock_coder")
        self.edit_format = "editblock"

    async def prep(self, shared):
        return {
            "context": shared.get("repomap_context"),
            "user_message": shared.get("user_message"),
            "files": shared.get("files_to_edit", [])
        }

    async def exec(self, prep_res):
        # Build prompt
        prompt = self._build_prompt(prep_res)

        # Call LLM
        response = await call_llm(
            model="claude-3-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=4000
        )

        return {"llm_response": response}

    def _build_prompt(self, prep_res):
        return f"""You are an AI coding assistant.

Current files:
{prep_res['context']}

User request: {prep_res['user_message']}

Instructions:
1. Make the requested changes using SEARCH/REPLACE blocks
2. Use this exact format:

```
path/to/file.py
<<<<<<< SEARCH
old code to search for
=======
new code to replace with
>>>>>>> REPLACE
```

Be precise with the SEARCH section - it must match exactly.
"""

    def post(self, shared, prep_res, exec_res):
        shared["llm_response"] = exec_res["llm_response"]
        return "parse_edits"
```

**Deliverable**: Can edit files using search/replace blocks

### Phase 3: Edit System (Days 9-11)

**Goal**: Parse and apply edits

```python
# kaygraph_aider/nodes/edit/edit_parser.py
import re
from pathlib import Path
from kaygraph import Node

class EditParser(Node):
    """Parse LLM edit responses."""

    def prep(self, shared):
        return {
            "response": shared.get("llm_response", ""),
            "format": shared.get("edit_format", "editblock")
        }

    def exec(self, prep_res):
        if prep_res["format"] == "editblock":
            return self._parse_editblock(prep_res["response"])
        # Add other formats later
        return {"edits": []}

    def _parse_editblock(self, response):
        """Parse SEARCH/REPLACE blocks."""
        edits = []

        # Pattern for edit blocks
        pattern = r'```(?:\w*\n)?(.*?)\n<<<<<<< SEARCH\n(.*?)\n=======\n(.*?)\n>>>>>>> REPLACE'

        for match in re.finditer(pattern, response, re.DOTALL):
            filepath = match.group(1).strip()
            search = match.group(2)
            replace = match.group(3)

            edits.append({
                "file": filepath,
                "search": search,
                "replace": replace
            })

        return {"edits": edits}

    def post(self, shared, prep_res, exec_res):
        shared["parsed_edits"] = exec_res["edits"]

        if exec_res["edits"]:
            return "apply_edits"
        else:
            return "no_edits"
```

### Phase 4: Main Workflow (Days 12-14)

**Goal**: Wire everything together

```python
# kaygraph_aider/workflows/main_workflow.py
from kaygraph_aider.lib import InteractiveGraph, PersistentGraph
from kaygraph_aider.nodes.base import UserInputNode, CommandHandler
from kaygraph_aider.nodes.context import RepoMapNode
from kaygraph_aider.nodes.coders import EditBlockCoder, CoderSelector
from kaygraph_aider.nodes.edit import EditParser, FileUpdater
from kaygraph_aider.nodes.git import CommitNode

def create_aider_workflow():
    """Create the main Aider workflow."""

    # Create nodes
    user_input = UserInputNode()
    cmd_handler = CommandHandler()
    repomap = RepoMapNode()
    coder_selector = CoderSelector()
    editblock = EditBlockCoder()
    parser = EditParser()
    updater = FileUpdater()
    committer = CommitNode()

    # Wire the graph

    # User input routing
    user_input - "add" >> cmd_handler
    user_input - "drop" >> cmd_handler
    user_input - "exit" >> None  # Exit
    user_input - "process" >> repomap  # Main flow

    # Command handler loops back
    cmd_handler >> user_input

    # Main edit flow
    repomap >> coder_selector

    # Coder selection (for now just editblock)
    coder_selector >> editblock

    # Edit parsing and application
    editblock >> parser
    parser - "apply_edits" >> updater
    parser - "no_edits" >> user_input

    # Commit and loop back
    updater >> committer >> user_input

    # Create persistent, interactive graph
    graph = PersistentGraph(
        checkpoint_dir=".aider/sessions",
        start_node=user_input
    )

    return InteractiveGraph(graph)
```

### Phase 5: CLI Integration (Days 15-16)

**Goal**: Create usable CLI

```python
# kaygraph_aider/cli.py
import click
from pathlib import Path
from kaygraph_aider.workflows import create_aider_workflow

@click.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True))
@click.option('--model', default='claude-3-sonnet', help='LLM model to use')
@click.option('--no-git', is_flag=True, help='Disable git integration')
@click.option('--message', '-m', help='Initial message to send')
def main(files, model, no_git, message):
    """KayGraph-Aider: AI pair programming in your terminal."""

    # Initialize shared context
    shared = {
        "files_to_edit": list(files),
        "model": model,
        "git_enabled": not no_git,
        "messages": [],
        "repo_path": Path.cwd()
    }

    # Create and run workflow
    workflow = create_aider_workflow()

    if message:
        # Non-interactive mode
        shared["user_message"] = message
        result = workflow.run(shared)
        print("Changes applied.")
    else:
        # Interactive mode
        print("KayGraph-Aider v0.1.0")
        print(f"Model: {model}")
        print(f"Files: {', '.join(files) if files else 'none'}")
        print("Enter /help for commands, or /exit to quit.\n")

        workflow.run_interactive(shared)

if __name__ == '__main__':
    main()
```

---

## Testing Strategy

### Unit Tests
```python
# tests/unit/test_nodes/test_edit_parser.py
def test_parse_editblock():
    parser = EditParser()

    response = """Here's the change:

```python
main.py
<<<<<<< SEARCH
def old_function():
    pass
=======
def new_function():
    return "updated"
>>>>>>> REPLACE
```"""

    result = parser.exec({"response": response, "format": "editblock"})

    assert len(result["edits"]) == 1
    assert result["edits"][0]["file"] == "main.py"
    assert "old_function" in result["edits"][0]["search"]
    assert "new_function" in result["edits"][0]["replace"]
```

### Integration Tests
```python
# tests/integration/test_workflows/test_edit_workflow.py
async def test_full_edit_cycle():
    """Test complete edit from user input to file update."""

    # Create test repo
    test_repo = create_test_repo()

    # Run workflow
    shared = {
        "repo_path": test_repo,
        "files_to_edit": ["main.py"],
        "user_message": "Add a hello world function"
    }

    workflow = create_edit_workflow()
    result = await workflow.run(shared)

    # Check file was modified
    assert "def hello_world" in (test_repo / "main.py").read_text()
```

---

## Performance Benchmarks

### Target Metrics
- **Response time**: < 2s for simple edits
- **Multi-file edits**: Handle 10+ files simultaneously
- **Context size**: Support 50K+ tokens of context
- **Memory usage**: < 500MB for typical session

### Benchmark Suite
```python
# scripts/benchmark.py
def benchmark_edit_performance():
    """Benchmark edit parsing and application."""

    times = []
    for i in range(100):
        start = time.time()

        # Parse complex edit response
        parser = EditParser()
        parser.exec({"response": COMPLEX_EDIT, "format": "editblock"})

        times.append(time.time() - start)

    print(f"Average parse time: {sum(times)/len(times):.3f}s")
```

---

## Documentation Plan

### User Documentation
1. **Getting Started** (30 min tutorial)
2. **Command Reference** (all /commands)
3. **Coder Formats** (with examples)
4. **Configuration Guide**
5. **Troubleshooting**

### Developer Documentation
1. **Architecture Overview**
2. **Adding Custom Coders**
3. **Extending Commands**
4. **Plugin System**
5. **API Reference**

---

## Success Criteria

### MVP (Week 2)
- [ ] Can edit files with search/replace
- [ ] Basic git integration
- [ ] Interactive chat loop works
- [ ] /add and /drop commands
- [ ] Runs on real codebase

### Full Version (Week 4)
- [ ] 3+ coder formats
- [ ] RepoMap with tree-sitter
- [ ] Multi-model support
- [ ] Cost tracking
- [ ] Session persistence
- [ ] Rich terminal UI
- [ ] Test coverage > 80%

---

## Risk Mitigation

### Risk 1: LLM Response Parsing
**Mitigation**: Start with strict prompts, add fuzzy matching later

### Risk 2: Performance on Large Repos
**Mitigation**: Implement caching early, optimize RepoMap incrementally

### Risk 3: User Experience
**Mitigation**: Copy Aider's UI patterns initially, innovate later

---

## Next Steps

1. **Today**: Create project structure
2. **Tomorrow**: Implement core enhanced classes
3. **This Week**: Get first edit working end-to-end
4. **Next Week**: Add more coders and polish

Ready to start building? Let's create the foundation!