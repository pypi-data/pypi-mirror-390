# KayGraph Chat Architecture - Implementation Summary

**Created**: 2025-11-03
**Purpose**: Documentation for adding new agents to the KayGraph chat system
**Status**: Complete with 3 comprehensive guides

---

## What You Now Understand

### The 3-Tier Communication Architecture

```
Tier 1: FRONTEND (React)
  ↓ HTTP POST
Tier 2: RAILS API + SIDEKIQ (KayBridge)
  ↓ HTTP POST
Tier 3: KAYNEXUS HTTP SERVICE (FastAPI)
```

Each tier has a specific responsibility:

1. **Frontend**: User interface, prompts user for query and agent type
2. **Rails**: API gateway, state management, background job orchestration
3. **KayNexus**: LLM execution, tool calling, conversation memory

---

## Document Guide

You've been given 4 comprehensive documents:

### 1. **KAYGRAPH_CHAT_ARCHITECTURE.md** (Primary Reference)

   **Read this first**. Contains:
   - Complete step-by-step flow (all 7 steps)
   - Agent type routing table
   - All 3 agent examples (KayGraph, Claude Conversational, Claude Planner)
   - Environment configuration
   - Key files reference
   - Debugging tips

   **Use when**: Understanding the full flow, troubleshooting issues

### 2. **ADD_NEW_AGENT_GUIDE.md** (Implementation Guide)

   **Read this to implement**. Contains:
   - Worked example: Adding a "Research Agent"
   - Step-by-step code changes (4 concrete steps)
   - Testing procedures (Rails console, curl, frontend)
   - Configuration options
   - Complete checklist
   - Troubleshooting for common errors

   **Use when**: Adding your new agent type

### 3. **KAYGRAPH_FLOW_DIAGRAM.md** (Visual Reference)

   **Read this for understanding**. Contains:
   - ASCII flow diagrams
   - Agent type decision tree
   - File dependency graph
   - HTTP request/response examples
   - State machine diagram
   - Performance characteristics
   - Debugging checklist

   **Use when**: Understanding flow visually, showing teammates

### 4. **KAYGRAPH_IMPLEMENTATION_SUMMARY.md** (This Document)

   Quick index and summary of all documentation.

---

## Quick Start: Adding Your Agent in 3 Steps

### Step 1: Update Rails (5 min)

**File**: `/Users/yadkonrad/dev_dev/year24/dec24/MY_PIXEL_PILOT/app/services/external_agent_service.rb`

```ruby
# Line 19-28: Add your agent type to SUPPORTED_AGENT_TYPES
SUPPORTED_AGENT_TYPES = %w[
  ...existing types...
  your-agent-type    # ← ADD THIS
].freeze

# Line 49-71: Add case statement in execute()
when 'your-agent-type'
  execute_your_agent

# At end (after execute_custom_api): Add handler
def execute_your_agent
  base_url = ENV['KAYGRAPH_API_URL'] || 'http://localhost:8000'
  uri = URI("#{base_url}/v1/your-endpoint")

  # ... HTTP request code ...
  # See ADD_NEW_AGENT_GUIDE.md for full template
end
```

### Step 2: Add Endpoint in KayNexus (5 min)

**File**: `/Users/yadkonrad/dev_dev/year24/dec24/MY_PIXEL_PILOT/kaygraph-agent-server/src/api_routes.py`

```python
# Add request/response models
class YourAgentRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = "default"
    # Add any custom fields

# Add route handler
@router.post("/your-endpoint")
async def your_endpoint(request: YourAgentRequest):
    """Description of what this does."""
    try:
        result = await your_agent_logic(request.message)
        return {
            "success": True,
            "response": result,
            "metadata": {}
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
```

### Step 3: Test & Deploy (5 min)

```bash
# Test via Rails console
cd /Users/yadkonrad/dev_dev/year24/dec24/MY_PIXEL_PILOT
bin/rails console

agent_state = AgentState.create!(
  agent_type: "your-agent-type",
  conversation: Conversation.first,
  message: ...,
  user: User.first,
  status: "pending"
)

KayGraphAgentJob.perform_now(agent_state_id: agent_state.id, ...)
puts agent_state.reload.status  # Should be "completed"
```

---

## File Locations (Quick Reference)

### Rails Backend (KayBridge)

```
/Users/yadkonrad/dev_dev/year24/dec24/MY_PIXEL_PILOT/
├── app/controllers/api/v1/agents_controller.rb      ← API entry point
├── app/jobs/kay_graph_agent_job.rb                  ← Background job router
├── app/services/external_agent_service.rb           ← HTTP gateway (EDIT THIS)
├── app/models/
│   ├── agent_state.rb
│   ├── conversation.rb
│   └── message.rb
└── config/sidekiq.yml                               ← Job queue config
```

### KayNexus Agent Server (FastAPI)

```
kaygraph-agent-server/
├── src/
│   ├── server.py                                    ← App initialization
│   ├── api_routes.py                                ← Route handlers (EDIT THIS)
│   ├── agent.py                                     ← Core agent logic
│   ├── llm_manager.py                               ← LLM provider management
│   ├── claude_conversation_manager.py               ← Claude SDK wrapper
│   ├── claude_planner_prompt.py                     ← Planner system prompt
│   └── tools.py                                     ← Available tools
├── config/
│   └── config.yaml                                  ← LLM configuration
└── venv/                                            ← Python virtualenv
```

### Frontend

```
/Users/yadkonrad/dev_dev/year25/sep25/kayos-ai-frontend/
├── src/components/CodingConversations/
│   └── CodingConversationChat.tsx                   ← Chat UI (calls API)
└── src/client/
    └── railsApi.ts                                  ← API client
```

---

## Key API Endpoints

### Rails API

```
POST   /api/v1/conversations/:slug/agents/execute
       Create new agent execution request
       Returns: { agent_state_id, message_id, status: "pending" }

GET    /api/v1/conversations/:slug/agents/:agent_state_id/status
       Check execution status
       Returns: { status, result, error, updated_at }

POST   /api/v1/conversations/:slug/agents/:agent_state_id/checkpoint
       Save intermediate state (for long-running agents)

POST   /api/v1/conversations/:slug/agents/callback
       Receive callbacks from agents (tool execution, etc.)
```

### KayNexus API

```
POST   /v1/chat
       Generic chat with configurable LLM

POST   /v1/chat/stream
       Streaming response version

POST   /v1/rag
       RAG-based responses

POST   /v1/claude/query
       Claude with conversation memory (agent_type controls behavior)

GET    /v1/models
       List available models

GET    /v1/tools
       List available tools

GET    /health
       Health check

POST   /v1/test
       Test LLM connectivity
```

---

## Agent Type Decision Matrix

| Agent Type | Provider | Backend | Endpoint | Use Case |
|------------|----------|---------|----------|----------|
| `kaygraph-chat` | Configurable | KayNexus | `/v1/chat` | Generic chat |
| `kaygraph-rag` | Configurable | KayNexus | `/v1/rag` | Document search |
| `claude-conversational` | Anthropic | KayNexus | `/v1/claude/query` | Multi-turn conversation |
| `claude-planner` | Anthropic | KayNexus | `/v1/claude/query` | Planning/task breakdown |
| `claude-complete-planner` | Anthropic | KayNexus | `/v1/claude/query` | Full task execution |
| `anthropic-chat` | Anthropic | Direct API | n/a | Direct API (no Rails mediation) |
| `openai-chat` | OpenAI | Direct API | n/a | Direct API (no Rails mediation) |
| `custom-api` | Any | Custom | Configurable | Any custom endpoint |

---

## Data Model: Key Relationships

```
User
  ├── Conversation (many)
  │   ├── Message (many)
  │   │   └── content, role (user/assistant), message_type
  │   └── AgentState (many)
  │       ├── agent_type
  │       ├── status (pending/processing/completed/failed)
  │       ├── context (account_id, user_id, etc.)
  │       ├── result (response text)
  │       └── error_message
  │
  ├── Account (many)
  │   └── SshWorkEnvironment (for SSH-based agents)
  └── CodingSession (many)
      └── Conversation (1)
```

**Key Fields for Agent Execution**:
- `AgentState.agent_type`: Which agent to use
- `AgentState.context`: Metadata (account_id, user_id, etc.)
- `Message.content`: User query
- `Conversation.slug`: Conversation ID (sent to KayNexus for memory)

---

## Environment Variables

### Rails (.env or credentials)

```bash
ORCHESTRATOR_API_URL=http://localhost:8001    # For KaySmith (Claude CLI)
KAYGRAPH_API_URL=http://localhost:8000        # For KayNexus (agents)
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
REDIS_URL=redis://localhost:6379/1
DATABASE_URL=postgresql://localhost/kayos_development
```

### KayNexus (.env)

```bash
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
KAYGRAPH_ENVIRONMENT=development
KAYGRAPH_PORT=8000
KAYGRAPH_HOST=0.0.0.0
```

---

## Common Patterns

### Pattern 1: Simple Chat Agent

Use this when you want basic conversational response:

```ruby
# Rails
def execute_my_agent
  # Simple POST to KayNexus
  # Request: { message: "...", conversation_id: "..." }
  # Response: { success: true, response: "..." }
end
```

### Pattern 2: Agent with State

Use this when agent needs conversation history:

```python
# KayNexus
@router.post("/my-agent")
async def my_agent(request: Request):
    # Get conversation history
    history = agent.get_conversation_history(request.conversation_id)

    # Build context
    context = {
        "history": history,
        "current_message": request.message
    }

    # Call LLM with context
    result = await llm.complete(prompt, context)

    return { "success": True, "response": result }
```

### Pattern 3: Agent with Tools

Use this when agent needs to call external APIs:

```python
# KayNexus
@router.post("/my-agent")
async def my_agent(request: Request):
    # Agent can call tools
    tools = ["web_search", "file_operations", "database_query"]

    result = await agent.process_with_tools(
        message=request.message,
        tools=tools
    )

    return {
        "success": True,
        "response": result["text"],
        "metadata": {
            "tools_used": result["tools_called"],
            "tool_results": result["tool_outputs"]
        }
    }
```

---

## Troubleshooting Flow

```
Agent request fails
    │
    ├─ Check: Is agent_type in SUPPORTED_AGENT_TYPES?
    │   No → Add to external_agent_service.rb
    │
    ├─ Check: Is KayNexus running?
    │   No → Start: python kaygraph-agent-server/src/server.py
    │
    ├─ Check: Is endpoint implemented in KayNexus?
    │   No → Add to api_routes.py
    │
    ├─ Check: Are API keys set?
    │   No → export ANTHROPIC_API_KEY=sk-...
    │
    ├─ Check: Is Sidekiq running?
    │   No → ps aux | grep sidekiq (or redis-server)
    │
    └─ Check: Are there errors in logs?
        Yes → tail -f log/development.log | grep -i agent
```

---

## Performance Expectations

```
Latency Breakdown:

Network roundtrips:
  Rails API ────────────────────────── ~5-10ms
  HTTP to KayNexus ─────────────────── ~50-100ms
  KayNexus to Claude API ──────────── ~1-2 seconds
  Return path ────────────────────── ~100-200ms

Total: ~2-5 seconds (dominated by LLM)

Throughput:
  ~1-2 agents executing simultaneously per core
  Max 10 concurrent with modest hardware (Rails + KayNexus on same machine)

Storage:
  Each conversation message: ~1-5 KB
  AgentState record: ~2-10 KB
  Full conversation history: 1-10 MB
```

---

## Next Steps After Implementation

1. **Add streaming responses**
   - Implement `/v1/my-agent/stream` endpoint
   - Send data chunks as they arrive
   - Update frontend to display streaming text

2. **Add conversation memory**
   - Persist conversation history to database
   - Pass history to KayNexus on each request
   - Enable true multi-turn conversations

3. **Add cost tracking**
   - Log LLM API costs in metadata
   - Track cumulative cost per conversation
   - Display in UI

4. **Add tool calling**
   - Define available tools in agent config
   - Let agent decide which tools to call
   - Execute tools and return results to LLM

5. **Add custom system prompts**
   - Allow users to customize agent behavior
   - Store prompts in database
   - Pass to KayNexus on each request

---

## Support Resources

### File Locations Summary

| Document | Location |
|----------|----------|
| This summary | `KAYGRAPH_IMPLEMENTATION_SUMMARY.md` |
| Full architecture | `KAYGRAPH_CHAT_ARCHITECTURE.md` |
| Implementation guide | `ADD_NEW_AGENT_GUIDE.md` |
| Visual diagrams | `KAYGRAPH_FLOW_DIAGRAM.md` |

### Code References

All documents include line numbers for easy navigation. Format: `filename.rb:123-456`

### Getting Help

1. Read KAYGRAPH_CHAT_ARCHITECTURE.md for "How it works"
2. Read ADD_NEW_AGENT_GUIDE.md for "How to add an agent"
3. Check KAYGRAPH_FLOW_DIAGRAM.md for "Visual understanding"
4. Refer to this document for "Quick lookup"

---

## Summary

You now have a complete understanding of how KayGraph chat works:

✅ **Architecture**: 3-tier system (Frontend → Rails → KayNexus)
✅ **Communication**: HTTP REST with async background jobs
✅ **Extensibility**: Pluggable agent types via ExternalAgentService
✅ **Implementation**: 4-step process to add new agents
✅ **Testing**: Rails console, curl, and frontend testing procedures
✅ **Debugging**: Complete troubleshooting guide included

**You're ready to add your new agent!**

See ADD_NEW_AGENT_GUIDE.md for step-by-step implementation.

---

**Last Updated**: 2025-11-03
**Maintainer**: Claude Code
**Status**: Complete and tested
