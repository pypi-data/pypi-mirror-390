# KayGraph Feature Implementation Priorities (Based on Aider Analysis)

## Overview
This document prioritizes which Aider features would have the highest impact on KayGraph. Prioritization is based on: user impact, implementation complexity, and integration difficulty.

---

## TIER 1: Critical Features (Implement First)

### 1. Reasoning Tag Support for Claude API
**Impact:** HIGH | Complexity: LOW | Time: 2-3 hours

**Why:** Claude's extended thinking is becoming standard. Users need to see reasoning steps.

**Files to Add:**
- `/kaygraph/reasoning_tags.py` - Tag handling
- Update `base_coder.py` to extract `reasoning_content` from responses

**Implementation Pattern:**
```python
# In response handling
if hasattr(response.content, 'reasoning_content'):
    reasoning = response.content.reasoning_content
    formatted = format_reasoning_content(reasoning)
    output.append(f"[THINKING]\n{formatted}")
```

**Test Needs:**
- `test_reasoning_extraction.py` - Non-streaming
- `test_reasoning_streaming.py` - Streaming (if implemented)

---

### 2. Multi-Model Management (Editor & Weak Models)
**Impact:** HIGH | Complexity: MEDIUM | Time: 4-6 hours

**Why:** Different models excel at different tasks. Architect mode needs separate editor model.

**Implementation:**
```python
class Node:
    def __init__(self, main_model=None, editor_model=None, weak_model=None):
        self.main_model = main_model or Model()
        self.editor_model = editor_model or main_model
        self.weak_model = weak_model or main_model

class Graph:
    def run(self, shared, use_editor_model=False):
        # Switch models mid-execution
        current_model = editor_model if use_editor_model else main_model
```

**Pattern from Aider:**
```python
# Switch models for different phases
kwargs["main_model"] = editor_model or main_model
new_coder = Coder.create(**kwargs)
```

**Test Needs:**
- `test_multi_model.py` - Model switching
- `test_model_fallback.py` - Fallback chains

---

### 3. Git Integration (Change Tracking)
**Impact:** HIGH | Complexity: MEDIUM | Time: 5-8 hours

**Why:** Users need to see what changed, commit tracking is essential.

**Implementation:**
```python
class GitRepoTracker:
    def __init__(self, root):
        self.repo = git.Repo(root)
    
    def track_changes(self, node_name):
        # Get diffs since last tracking
    
    def commit_changes(self, message):
        # Auto-commit with AI-generated message
    
    def get_diff(self, fname):
        # Return structured diff
```

**Integration Points:**
- After each node execution
- Optional automatic commits
- Diff visualization in output

**Test Needs:**
- `test_git_tracking.py` - Basic tracking
- `test_git_commit.py` - Auto-commit
- `test_git_diff.py` - Diff generation

---

### 4. Node-Level Prompt Templates
**Impact:** MEDIUM | Complexity: LOW | Time: 2-3 hours

**Why:** Different node types should have specialized system prompts.

**Implementation:**
```python
class Node:
    system_prompt = ""  # Default empty
    system_reminder = ""  # Optional reminder

class CodeGenNode(Node):
    system_prompt = """You are an expert software engineer.
Write clean, well-documented code."""

class ValidationNode(Node):
    system_prompt = """You are a strict code reviewer.
Check for bugs, style, and best practices."""
```

**Integration:**
- Include in message preparation
- Pass to LLM as system message
- Support override per instance

**Test Needs:**
- `test_node_prompts.py` - Prompt injection

---

## TIER 2: High-Value Additions (Next Priority)

### 5. Streaming Response Handling
**Impact:** MEDIUM | Complexity: HIGH | Time: 8-12 hours

**Why:** Real-time feedback is critical for long operations.

**Challenges:**
- Token counting during streaming
- Partial response handling
- Error recovery mid-stream

**Implementation Pattern:**
```python
def send_stream(self, messages):
    # Yield chunks as they arrive
    for chunk in api.stream(messages):
        self.partial_response += chunk.text
        yield chunk
        # Update token counts
```

**Test Needs:**
- `test_streaming_basics.py`
- `test_streaming_tokens.py`
- `test_stream_error_handling.py`

---

### 6. RepoMap-Style Context Selection
**Impact:** MEDIUM | Complexity: HIGH | Time: 12-16 hours

**Why:** Handles large codebases efficiently without full file inclusion.

**Core Features:**
- AST parsing for code structure
- Tag-based summarization (functions, classes)
- Token-aware selection
- SQLite caching

**Implementation:**
```python
class RepoContextMapper:
    def __init__(self, root, max_tokens=1024):
        self.max_tokens = max_tokens
        self.cache = {}  # Or SQLite
    
    def get_context(self, target_file, max_tokens=None):
        # Return structured map of relevant code
        return {
            'files': {
                'file.py': {
                    'classes': ['MyClass'],
                    'functions': ['my_func'],
                    'summary': '...'
                }
            }
        }
```

**Integration:**
- Replace full file inclusion in large repos
- Use in prep() phase of nodes
- Integrate with shared store

**Test Needs:**
- `test_repomap_basics.py`
- `test_repomap_caching.py`
- `test_repomap_tokenization.py`

---

### 7. Multiple Edit Formats
**Impact:** MEDIUM | Complexity: HIGH | Time: 10-14 hours

**Why:** Different formats work better for different models and use cases.

**Formats to Support:**
1. **Search/Replace** - Simple, reliable
2. **EditBlocks** - Marked sections
3. **Unified Diff** - Standard format
4. **Whole File** - Full replacement

**Implementation Pattern:**
```python
class EditFormat(ABC):
    @abstractmethod
    def parse(self, response):
        # Parse format -> (file, action, content)
        pass

class SearchReplaceFormat(EditFormat):
    def parse(self, response):
        # Parse search/replace markers
        pass

class EditBlockFormat(EditFormat):
    def parse(self, response):
        # Parse <<<...>>> markers
        pass

# Factory
FORMAT_REGISTRY = {
    'search_replace': SearchReplaceFormat(),
    'editblock': EditBlockFormat(),
    ...
}
```

**Test Needs:**
- `test_search_replace_format.py`
- `test_editblock_format.py`
- `test_format_fallback.py`

---

### 8. Chat History & Summarization
**Impact:** MEDIUM | Complexity: MEDIUM | Time: 6-8 hours

**Why:** Long conversations hit token limits. Smart summarization helps.

**Implementation:**
```python
class ChatSummarizer:
    def summarize(self, messages, max_tokens=1000):
        # Use LLM to compress conversation
        summary_prompt = f"Summarize this conversation in {max_tokens} tokens"
        return llm.generate(summary_prompt + format(messages))

class ChatHistory:
    def __init__(self, max_tokens=2000):
        self.messages = []
        self.summarizer = ChatSummarizer()
    
    def add(self, role, content):
        self.messages.append({'role': role, 'content': content})
        if self.get_token_count() > self.max_tokens:
            self.compress()
    
    def compress(self):
        # Summarize old messages
        old_msgs = self.messages[:-10]  # Keep recent
        summary = self.summarizer.summarize(old_msgs)
        self.messages = [SYSTEM_SUMMARY, summary] + self.messages[-10:]
```

**Integration:**
- Automatic in long-running graphs
- Optional per user preference
- Test with model switching

**Test Needs:**
- `test_chat_summarization.py`
- `test_history_compression.py`

---

### 9. Environment Validation Layer
**Impact:** MEDIUM | Complexity: LOW | Time: 2-3 hours

**Why:** Catch configuration issues early, better error messages.

**Implementation:**
```python
class EnvironmentValidator:
    def validate(self, model):
        missing = []
        for env_var in model.required_env_vars:
            if not os.getenv(env_var):
                missing.append(env_var)
        
        if missing:
            raise MissingEnvironmentError(
                f"Missing: {', '.join(missing)}"
            )
    
    def fast_validate(self, model):
        # Quick check (just env vars)
        pass
    
    def full_validate(self, model):
        # Comprehensive (try API call, etc.)
        pass
```

**Integration:**
- Run on graph initialization
- Called before first node execution
- Optional full validation mode

**Test Needs:**
- `test_env_validation.py`
- `test_missing_api_keys.py`

---

### 10. Integrated Linting
**Impact:** MEDIUM | Complexity: MEDIUM | Time: 4-6 hours

**Why:** Code quality feedback integrated into workflow.

**Implementation:**
```python
class LinterNode(Node):
    def __init__(self, lang='python', cmd='ruff check'):
        self.lang = lang
        self.cmd = cmd
    
    def exec(self, prep_res):
        # Run linter on file
        result = run_cmd(f"{self.cmd} {prep_res['file']}")
        return self.parse_linter_output(result)
    
    def post(self, shared, prep_res, exec_res):
        shared['lint_results'] = exec_res
        return 'pass' if exec_res['errors'] == 0 else 'fix'
```

**Integration:**
- Optional node in code generation pipeline
- Parse output to actionable feedback
- Support multiple linters

**Test Needs:**
- `test_linter_node.py`
- `test_linter_parsing.py`

---

## TIER 3: Advanced Features (Nice-to-Have)

### 11. File Watching
**Impact:** LOW | Complexity: MEDIUM | Time: 4-6 hours

**Implementation:**
```python
class FileWatcher:
    def watch(self, paths, callback):
        # Detect external changes
        # Alert on modifications
        pass
```

---

### 12. Voice Input Support
**Impact:** LOW | Complexity: MEDIUM | Time: 6-8 hours

**Implementation:**
```python
class VoiceInput:
    def listen(self, language='en'):
        # Record and transcribe
        # Return text
        pass
```

---

### 13. Caching Layer
**Impact:** MEDIUM | Complexity: MEDIUM | Time: 6-8 hours

**Implementation:**
```python
class ResponseCache:
    def __init__(self, storage='diskcache'):
        self.cache = DiskCache('cache')
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value, ttl=None):
        self.cache.set(key, value, expire=ttl)
```

---

### 14. Metrics & Analytics
**Impact:** LOW | Complexity: MEDIUM | Time: 4-6 hours

**Implementation:**
```python
class Metrics:
    def record_node_execution(self, node_name, duration, tokens_used):
        # Store metrics
        pass
    
    def get_stats(self):
        # Return aggregated stats
        pass
```

---

## Implementation Roadmap

### Phase 1 (Weeks 1-2): Core Features
1. Reasoning tag support (2-3 hours)
2. Node-level prompts (2-3 hours)
3. Multi-model management (4-6 hours)

**Subtotal:** 8-12 hours | **Effort:** 1-2 days

### Phase 2 (Weeks 3-4): Integration
4. Git tracking (5-8 hours)
5. Environment validation (2-3 hours)
6. Basic streaming (4-6 hours)

**Subtotal:** 11-17 hours | **Effort:** 2-3 days

### Phase 3 (Weeks 5-6): Advanced
7. Chat history (6-8 hours)
8. RepoMap integration (12-16 hours)
9. Multiple edit formats (10-14 hours)
10. Linting (4-6 hours)

**Subtotal:** 32-44 hours | **Effort:** 5-7 days

### Phase 4 (Week 7+): Polish
11. File watching (4-6 hours)
12. Voice input (6-8 hours)
13. Caching (6-8 hours)
14. Metrics (4-6 hours)

**Subtotal:** 20-28 hours | **Effort:** 3-5 days

---

## Total Effort Estimate

**All 14 Features:** ~72-101 hours (10-14 days for 1 developer)

**MVP (Features 1-5):** ~12-20 hours (2-3 days)

**Production-Ready (Features 1-10):** ~43-62 hours (6-8 days)

---

## Testing Strategy

### For Each Feature:
1. **Unit Tests** - Component behavior
2. **Integration Tests** - With Graph/Node
3. **End-to-End Tests** - Full workflow

### Test File Naming:
```
tests/features/
├── test_reasoning_tags.py
├── test_multi_model.py
├── test_git_integration.py
├── test_node_prompts.py
├── test_streaming.py
├── test_repomap.py
├── test_edit_formats.py
├── test_chat_history.py
├── test_env_validation.py
├── test_linting.py
├── test_file_watching.py
├── test_voice_input.py
├── test_caching.py
└── test_metrics.py
```

---

## Dependencies to Add

### For All Features:
```
GitPython>=3.1.0          # Git operations
```

### For Specific Features:
- **RepoMap**: `tree-sitter`, `grep-ast`
- **Linting**: `ruff` (or custom integration)
- **Voice**: `pyaudio`, `speech_recognition`
- **Caching**: `diskcache`
- **Streaming**: Already supported by `anthropic` library

---

## Success Criteria

After implementing Tier 1:
- Users can see Claude's reasoning process
- Can switch between models mid-conversation
- Changes are tracked in git

After Tier 2:
- Large codebases work efficiently
- Real-time streaming feedback
- Automatic history compression

After Tier 3:
- Voice-based input
- Persistent caching
- Detailed metrics/reporting

---

## References

See `AIDER_ANALYSIS.md` for detailed implementation examples from Aider codebase.

Key files to study:
- `/aider/coders/base_coder.py` - Streaming, model management
- `/aider/models.py` - Multi-model pattern
- `/aider/repo.py` - Git integration
- `/aider/repomap.py` - Context selection
- `/aider/linter.py` - Linting integration
- `/aider/reasoning_tags.py` - Reasoning extraction
