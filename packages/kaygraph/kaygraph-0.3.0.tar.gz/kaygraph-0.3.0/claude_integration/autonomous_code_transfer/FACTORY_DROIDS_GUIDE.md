# Factory AI Droid Patterns - Implementation Guide

> **Based on research of Factory AI's production Droid architecture**

## Overview

Factory AI offers specialized "Droids" - task-specific AI agents that handle different aspects of software development. This guide shows you how to implement similar patterns in your autonomous code transfer system.

## Factory AI's Four Main Droids

### 1. **Code Droid** - Main Engineering Agent
- **Purpose**: Feature development, refactoring, bug fixes, implementation
- **Tools**: Full access (Read, Write, Edit, Bash)
- **Use Cases**:
  - Writing new features from specs
  - Refactoring legacy code
  - Implementing API endpoints
  - Bug fixes with tests

### 2. **Reliability Droid** - Production Issues
- **Purpose**: Incident response, root cause analysis, hotfix generation
- **Tools**: Read, Bash, Grep, monitoring tools
- **Use Cases**:
  - Analyzing production logs
  - Identifying error patterns
  - Creating hotfix PRs
  - Reducing MTTR (Mean Time To Resolution)

### 3. **Knowledge Droid** - Research & Documentation
- **Purpose**: Codebase research, documentation generation, architectural analysis
- **Tools**: Read, Grep, Glob, WebSearch
- **Use Cases**:
  - Understanding legacy systems
  - Generating API documentation
  - Creating ADRs (Architectural Decision Records)
  - Answering "how does X work?" questions

### 4. **Tutorial Droid** - Developer Education
- **Purpose**: Onboarding, creating learning materials, explaining patterns
- **Tools**: Read, WebSearch, documentation generation
- **Use Cases**:
  - Creating interactive tutorials
  - Onboarding new team members
  - Explaining complex code patterns
  - Generating learning paths

## Custom Droid Architecture

### File Format

Custom droids are **Markdown files with YAML frontmatter**:

```markdown
---
name: code-reviewer
description: Senior reviewer that checks diffs for correctness risks
model: inherit  # or specify: sonnet-4.5, opus, haiku
tools: ["Read", "Grep", "Glob"]  # Restricted tool access
---

# System Prompt

You are the team's senior code reviewer. Your role is to...

## Operating Rules
1. Always read the full diff before commenting
2. Focus on correctness, not style
3. Flag security risks immediately

## Input Parsing
You will receive:
- **goal**: What changes to review
- **context.pr_number**: PR identifier
- **context.files**: List of changed files

## Process
1. Read changed files using Read tool
2. Analyze for issues
3. Create review report
4. Return summary + file path

## Output Contract
Return JSON:
{
  "summary": "Brief assessment",
  "issues_found": 5,
  "report_path": "reviews/pr-123-review.md"
}
```

### Storage Locations

- **Project droids**: `.factory/droids/` (version controlled, team-shared)
- **Personal droids**: `~/.factory/droids/` (individual preferences)

## The Worker Pattern

### Core Principles

1. **Structured Input**: Receive clear objectives from orchestrator
2. **Tool-First Investigation**: Gather facts before reasoning
3. **Artifact Files**: Write large outputs to files
4. **Small Returns**: Return metadata only (not full content)
5. **No Chaining**: Don't invoke other droids (orchestrator decides flow)

### Example Flow

```
Orchestrator (Main Agent)
    ↓ delegates with structured input
Code Reviewer Droid
    ↓ uses tools: Read, Grep
    ↓ creates artifact: review.md
    ↓ returns: {summary: "...", path: "review.md"}
Orchestrator
    ↓ reads review, decides next step
    ↓ delegates to next droid or completes
```

## Tool Categories & Permissions

| Category | Tools | Risk Level | Use Cases |
|----------|-------|------------|-----------|
| **Read-Only** | Read, Grep, Glob, LS | 🟢 Low | Analysis, research, review |
| **Web** | WebSearch, FetchUrl | 🟢 Low | Documentation, research |
| **Edit** | Edit, MultiEdit | 🟡 Medium | Code changes, refactoring |
| **Create** | Write, Create | 🟡 Medium | New files, generation |
| **Execute** | Bash, Execute | 🔴 High | Testing, building, deployment |

**Best Practice**: Grant minimum necessary tools for each droid's task.

## Specialized Droid Examples

### 1. Code Reviewer Droid

```yaml
---
name: code-reviewer
model: inherit
tools: ["Read", "Grep", "Glob"]
---

## Your Role
Senior code reviewer checking for:
- Correctness issues
- Missing tests
- Security vulnerabilities
- Breaking changes
- Migration risks

## Output Format
Markdown report with:
- ✅ What looks good
- ⚠️ Concerns
- ❌ Must fix before merge
- 📝 Suggested improvements
```

**Usage in Our System**:
```python
class CodeReviewerDroid(AsyncNode):
    """Factory AI-style code reviewer."""

    async def exec(self, prep_res):
        # Review changed files
        # Create review report
        # Return summary + path
```

### 2. Security Checker Droid

```yaml
---
name: security-checker
model: inherit
tools: ["Read", "Grep", "WebSearch"]
---

## Your Role
Security specialist scanning for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Exposed secrets/API keys
- Insecure dependencies
- Authentication bypasses

## Process
1. Grep for dangerous patterns
2. Read suspicious files
3. WebSearch for known CVEs
4. Generate security report

## Output
{
  "critical_issues": [],
  "warnings": [],
  "report_path": "security-scan.md"
}
```

### 3. Migration Specialist Droid

```yaml
---
name: migration-specialist
model: sonnet-4.5  # Use more powerful model
tools: ["Read", "Edit", "Grep", "Glob"]
---

## Your Role
Expert in code migrations and modernization:
- Framework upgrades (React 17→18, Python 2→3)
- API migrations (REST→GraphQL)
- Dependency updates
- Pattern modernization

## Strategy
1. Analyze current codebase patterns
2. Identify all migration points
3. Create migration plan
4. Execute changes with tests
5. Validate no regressions

## Metrics to Track
- Files migrated
- Tests passing
- Breaking changes avoided
- Performance impact
```

### 4. Test Generator Droid

```yaml
---
name: test-generator
model: inherit
tools: ["Read", "Write", "Bash"]
---

## Your Role
Testing specialist that:
- Analyzes code coverage gaps
- Generates unit tests
- Creates integration tests
- Ensures test quality

## Test Patterns
- Arrange-Act-Assert
- Given-When-Then
- Mock external dependencies
- Test edge cases

## Output
- Generated test files
- Coverage report
- Missing test scenarios
```

## Multi-Agent Orchestration Patterns

### Pattern 1: Sequential Pipeline

```
Research Droid → Planning Droid → Code Droid → Review Droid → Test Droid
```

Each droid completes its phase before the next starts.

### Pattern 2: Parallel Investigation

```
                    ↙ Security Droid
Orchestrator → → → → Code Review Droid
                    ↘ Test Coverage Droid

Then aggregate results
```

Multiple specialists analyze simultaneously.

### Pattern 3: Iterative Refinement

```
Code Droid → Review Droid → Code Droid (fixes) → Review Droid (validate) → Done
```

Loop until quality standards met.

### Pattern 4: Competitive Solutions

```
Orchestrator → → → Code Droid A (approach 1)
              → → → Code Droid B (approach 2)

Compare results, pick best
```

Race different approaches, select winner.

## Implementing Factory Patterns in KayGraph

### Step 1: Create Specialized Nodes

```python
from kaygraph import AsyncNode

class CodeReviewerDroid(AsyncNode):
    """Factory AI-style code review droid."""

    def __init__(self):
        super().__init__(node_id="code_reviewer")
        self.allowed_tools = ["Read", "Grep", "Glob"]  # Read-only

    async def exec(self, prep_res):
        # Claude Code headless with restricted tools
        claude = ClaudeHeadless()
        result = claude.execute(
            prompt=self._build_review_prompt(prep_res),
            allowed_tools=self.allowed_tools,
            output_format=OutputFormat.JSON
        )
        return result
```

### Step 2: Create Orchestration Workflow

```python
from graphs import create_multi_droid_workflow

# Build workflow with specialized droids
workflow = create_multi_droid_workflow([
    ResearchDroid(),      # Knowledge Droid pattern
    PlanningDroid(),      # Code Droid pattern
    ImplementationDroid(), # Code Droid pattern
    ReviewerDroid(),      # Custom review pattern
    TestGeneratorDroid(), # Reliability pattern
    SecurityCheckerDroid() # Security pattern
])
```

### Step 3: Add Droid Coordination

```python
# Parallel review by multiple specialists
code_droid >> ("complete", [
    security_droid,
    review_droid,
    test_coverage_droid
])

# Aggregate results
all_droids >> aggregator >> final_validation
```

## Performance Metrics (Factory AI Benchmarks)

- **Terminal-Bench Score**: 58.75% (SOTA as of 2025)
- **Migration Speed**: 96% faster than manual
- **Code Review**: Finds 85% of issues humans catch
- **Test Generation**: 92% valid test coverage
- **Documentation**: Reduces doc time by 80%

## Best Practices from Factory AI

### 1. Model Selection Strategy
- **Small/Fast** (Haiku): Analysis, summaries, simple tasks
- **Medium** (Sonnet): Most coding tasks, reviews
- **Large** (Opus): Complex reasoning, migrations

### 2. Tool Restriction Philosophy
- Grant **minimum necessary** permissions
- Read-only for analysis droids
- Execute only for testing droids
- Full access only for implementation droids

### 3. Output Artifact Pattern
- Large outputs (>3000 tokens) → Write to file
- Return small metadata only (~200 tokens)
- Prevents truncation and context overflow

### 4. Graceful Degradation
- Multiple fallbacks for file discovery
- Don't fail on optional files
- Adapt to different project structures

### 5. Progress Visibility
- Use TodoWrite for long operations
- Stream status updates
- Enable user monitoring

## Integration with Our Autonomous Transfer System

### Add Factory Droids to Transfer Workflow

```python
# Enhanced workflow with Factory patterns
workflow = create_enhanced_transfer_workflow([
    # Phase 1: Research (Knowledge Droid pattern)
    ResearchDroid(tools=["Read", "Grep", "Glob", "WebSearch"]),

    # Phase 2: Planning (Code Droid pattern)
    PlanningDroid(tools=["Read"]),

    # Phase 3: Implementation (Code Droid pattern)
    ImplementationDroid(tools=["Read", "Write", "Edit", "Bash"]),

    # Phase 4: Multi-Specialist Review (Factory pattern)
    ParallelReview([
        CodeReviewerDroid(tools=["Read", "Grep"]),
        SecurityCheckerDroid(tools=["Read", "Grep", "WebSearch"]),
        TestCoverageDroid(tools=["Read", "Bash"])
    ]),

    # Phase 5: Final Validation
    ValidationDroid(tools=["Read", "Bash"])
])
```

## Example: Complete Code Review Droid

See `droids/code_reviewer.py` for full implementation with:
- Correctness checking
- Security scanning
- Test coverage analysis
- Migration risk detection
- Performance implications

## Resources

- **Factory AI Docs**: https://docs.factory.ai
- **Terminal-Bench**: Performance benchmark for coding agents
- **Custom Droids Reference**: https://docs.factory.ai/cli/configuration/custom-droids
- **Worker Pattern Guide**: https://droidtrees.com/factory-ai-instructions/custom-droids-the-worker-pattern

---

**Next**: See `droids/` directory for ready-to-use implementations of Code Reviewer, Security Checker, Test Generator, and Migration Specialist droids!
