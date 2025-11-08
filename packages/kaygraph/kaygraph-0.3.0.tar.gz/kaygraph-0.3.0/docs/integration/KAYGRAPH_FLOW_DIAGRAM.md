# KayGraph Chat: Visual Flow Diagrams

---

## Full Request-Response Cycle

```
┌─────────────────────────────────────────────────────────────────┐
│                   FRONTEND (React)                              │
│  User types: "Build auth system" + selects "claude-conversational"│
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP POST /api/v1/conversations/:slug/agents/execute
                           │ {
                           │   prompt: "Build auth system",
                           │   agent_type: "claude-conversational",
                           │   context: {...}
                           │ }
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   RAILS API (agents_controller)                │
│  1. Create Message in conversation                              │
│  2. Create AgentState (status: "pending")                       │
│  3. Enqueue KayGraphAgentJob                                    │
│  4. Return 202 Accepted with agent_state_id                     │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ 202 Accepted
                           │ { agent_state_id: 123, status: "pending" }
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         FRONTEND (Polling or ActionCable listening)             │
│  Poll /api/v1/conversations/:slug/agents/123/status every 1s   │
│  OR listen for "agent_response" on WebSocket                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ (Meanwhile, in background queue...)
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│            SIDEKIQ BACKGROUND JOB (KayGraphAgentJob)            │
│  1. Load AgentState(123)                                        │
│  2. Check: external_agent?("claude-conversational") => true     │
│  3. Call ExternalAgentService.new(agent_state).execute          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ Routes based on agent_type
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         EXTERNAL AGENT SERVICE (Rails Service)                 │
│  case "claude-conversational"                                   │
│    execute_claude_conversational()                              │
│    ├─ base_url = "http://localhost:8000"                        │
│    ├─ uri = "#{base_url}/v1/claude/query"                       │
│    └─ HTTP POST with:                                           │
│       {                                                         │
│         message: "Build auth system",                           │
│         conversation_id: "auth-system-conv",                    │
│         workspace: "/tmp",                                      │
│         account_id: 1,                                          │
│         user_id: 42,                                            │
│         agent_type: "conversational"                            │
│       }                                                          │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP POST /v1/claude/query
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         KAYNEXUS (FastAPI, port 8000)                           │
│  /v1/claude/query endpoint:                                     │
│  ├─ Parse request                                              │
│  ├─ Call ClaudeConversationManager.query()                     │
│  │  ├─ Get/create conversation memory for ID                  │
│  │  ├─ Build system prompt (conversational mode)              │
│  │  ├─ Call Claude SDK with conversation history             │
│  │  └─ Return response with metadata                          │
│  └─ Return JSON:                                               │
│     {                                                           │
│       "success": true,                                          │
│       "response": "Here's how to build auth...",                │
│       "metadata": {                                             │
│         "tools_used": ["web_search"],                           │
│         "model": "claude-3-5-sonnet",                           │
│         "cost_usd": 0.15                                        │
│       }                                                          │
│     }                                                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
                           │ HTTP 200 with JSON response
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│         RAILS BACKGROUND JOB (still executing)                 │
│  KayGraphAgentJob:                                              │
│  ├─ Receive response from KayNexus                             │
│  ├─ Parse: execution_result = { success: true, output: "...", }│
│  ├─ Update AgentState:                                          │
│  │  agent_state.update(                                        │
│  │    status: "completed",                                     │
│  │    result: "Here's how to build auth..."                    │
│  │  )                                                           │
│  ├─ Create response Message in Conversation                   │
│  ├─ Broadcast via ActionCable:                                 │
│  │  ActionCable.broadcast(                                     │
│  │    "conversation_#{conversation.id}",                       │
│  │    { type: "agent_response", content: "Here's how..." }    │
│  │  )                                                           │
│  └─ Job complete ✓                                             │
└──────────────────────────┬──────────────────────────────────────┘
                           │
        ┌──────────────────┴──────────────────┐
        │ WebSocket Broadcast               Polling Response
        ▼                                   ▼
┌──────────────────────────┐  ┌──────────────────────────┐
│ Frontend (ActionCable)   │  │ Frontend (Status Check)  │
│ Receives update:         │  │ GET status endpoint      │
│ {                        │  │ status: "completed"      │
│   type: "agent_response" │  │ result: "Here's how..."  │
│   content: "Here's how..." │ └──────────────────────────┘
│ }                        │
│                          │
│ Update messages array    │
│ Re-render chat UI ✓      │
└──────────────────────────┘
```

---

## Agent Type Decision Tree

```
User submits prompt with agent_type

                    ▼
        Is it in SUPPORTED_AGENT_TYPES?
                    │
         ┌──────────┼──────────┐
         │ YES      │ NO       │
         ▼          ▼
    Continue    Return error
                (400 Bad Request)
         │
         ▼
    externalAgent?(agent_type)
         │
    ┌────┴────┐
    │YES      │NO
    ▼         ▼
 External   Coding Session
 Agent      Agent (SSH/
  │         Orchestrator)
  │         │
  ▼         ▼
case:      (different flow)
│
├─ "kaygraph-chat"
│  └─> POST /v1/chat
│
├─ "kaygraph-rag"
│  └─> POST /v1/rag
│
├─ "claude-conversational"
│  └─> POST /v1/claude/query
│      (agent_type: "conversational")
│
├─ "claude-planner"
│  └─> POST /v1/claude/query
│      (agent_type: "planner")
│
├─ "claude-complete-planner"
│  └─> POST /v1/claude/query
│      (agent_type: "complete-planner")
│
├─ "anthropic-chat"
│  └─> Direct Anthropic API (no KayNexus)
│
├─ "openai-chat"
│  └─> Direct OpenAI API (no KayNexus)
│
└─ "custom-api"
   └─> Configurable endpoint
```

---

## File Dependencies

```
Frontend Request
       ↓
agents_controller.rb
       ├─> creates: Message
       ├─> creates: AgentState
       └─> enqueues: KayGraphAgentJob
       ↓
KayGraphAgentJob
       ├─> calls: ExternalAgentService (if external_agent?)
       └─> calls: Orchestrator (if !external_agent?)
       ↓
ExternalAgentService
       ├─> execute_anthropic()
       ├─> execute_openai()
       ├─> execute_kaygraph()
       ├─> execute_kaygraph_rag()
       ├─> execute_claude_conversational()
       ├─> execute_claude_planner()
       ├─> execute_claude_complete_planner()
       └─> execute_custom_api()
       ↓ (HTTP calls)
KayNexus (/v1/*)
       ├─> api_routes.py
       │   ├─> @router.post("/chat")
       │   ├─> @router.post("/chat/stream")
       │   ├─> @router.post("/rag")
       │   ├─> @router.post("/claude/query")
       │   ├─> @router.get("/models")
       │   ├─> @router.get("/tools")
       │   └─> @router.get("/config")
       │
       ├─> agent.py
       │   └─> KayGraphAgent.process_message()
       │
       ├─> llm_manager.py
       │   └─> LLMManager.complete()
       │
       ├─> claude_conversation_manager.py
       │   └─> ClaudeConversationManager.query()
       │
       └─> tools.py
           └─> Tool registry

Response flows back → Rails → ActionCable → Frontend
```

---

## HTTP Request/Response Examples

### Example 1: KayGraph Chat Agent

**Rails → KayNexus HTTP POST**:
```
POST /v1/chat
Content-Type: application/json

{
  "message": "What's the best way to optimize database queries?",
  "conversation_id": "opt-db-conv",
  "provider": "ionet",
  "model": "qwen-coder",
  "context": {
    "account_id": 1,
    "user_id": 42
  }
}
```

**KayNexus Response**:
```json
{
  "response": "Here are the best practices for database optimization...",
  "metadata": {
    "model": "qwen-coder",
    "tokens_used": 512,
    "execution_time_ms": 2140
  }
}
```

---

### Example 2: Claude Conversational Agent

**Rails → KayNexus HTTP POST**:
```
POST /v1/claude/query
Content-Type: application/json

{
  "message": "What's the best way to optimize database queries?",
  "conversation_id": "opt-db-conv",
  "workspace": "/tmp",
  "account_id": 1,
  "user_id": 42,
  "agent_type": "conversational"
}
```

**KayNexus Response**:
```json
{
  "success": true,
  "response": "Here are the best practices... [includes web search results]",
  "metadata": {
    "tools_used": ["web_search", "file_operations"],
    "cost_usd": 0.12,
    "message_count": 3,
    "total_cost_usd": 0.35,
    "conversation_active": true,
    "agent_type": "claude-conversational",
    "model": "claude-3-5-sonnet",
    "api_endpoint": "https://api.anthropic.com/v1/messages"
  }
}
```

---

### Example 3: Claude Planner Agent

**Rails → KayNexus HTTP POST**:
```
POST /v1/claude/query
Content-Type: application/json

{
  "message": "Build a real-time chat application",
  "conversation_id": "chat-app-plan",
  "workspace": "/tmp",
  "account_id": 1,
  "user_id": 42,
  "agent_type": "planner"  # ← Different from conversational
}
```

**KayNexus Response**:
```json
{
  "success": true,
  "response": "Here's a detailed plan for building a real-time chat app:\n\n1. Backend Architecture\n   - Choose WebSocket library (Socket.io, ActionCable)\n   - Design message schema\n   - Plan authentication flow\n\n2. Frontend Implementation\n   - Real-time message updates\n   - User presence indicators\n   - Message history pagination\n\n3. Deployment Strategy...",
  "metadata": {
    "tools_used": ["web_search"],
    "cost_usd": 0.08,
    "message_count": 2,
    "agent_type": "claude-planner"
  }
}
```

---

## State Transitions

```
                 create
Frontend Request ──────────> AgentState
                              (status: "pending")
                                   ↓
                           KayGraphAgentJob
                              enqueued
                                   ↓
                           Sidekiq picks up
                                   ↓
                      ExternalAgentService
                         (or Orchestrator)
                                   ↓
                           ┌────────┴────────┐
                           │                 │
                    SUCCESS │                │ FAILURE
                           ▼                 ▼
                    AgentState            AgentState
                  (status: completed)    (status: failed)
                  (result: response)    (error_message: error)
                           │                 │
                           └────────┬────────┘
                                    ▼
                            ActionCable Broadcast
                            OR Polling Response
                                    │
                                    ▼
                           Frontend Updates UI
```

---

## Adding New Agent: Changes Required

```
1. Rail ExternalAgentService
   ├─ SUPPORTED_AGENT_TYPES (add type name)
   ├─ execute() case statement (add when clause)
   └─ execute_my_agent() (add private method)

2. KayNexus api_routes.py
   ├─ Add Pydantic request model
   ├─ Add @router.post endpoint
   └─ Add handler logic / import helper

3. Frontend (optional)
   └─ Add UI to select agent type

4. Environment (if needed)
   └─ Add API keys to .env
```

---

## Performance Characteristics

| Component | Typical Time | Notes |
|-----------|--------------|-------|
| Agent request → Rails API | <100ms | Synchronous |
| AgentState + Message creation | <50ms | Database writes |
| Job enqueue | <10ms | Redis push |
| Sidekiq pickup latency | 100-500ms | Depends on queue depth |
| HTTP POST to KayNexus | 50-100ms | Network roundtrip |
| Claude API call | 2-10 sec | LLM response time |
| Response parse + DB write | <100ms | Sync operations |
| ActionCable broadcast | <50ms | WebSocket push |
| **Total latency** | **3-15 seconds** | Dominated by LLM |

---

## Debugging Checklist

```
□ Verify Sidekiq is running
  ps aux | grep sidekiq

□ Check Rails logs
  tail -f log/development.log | grep -i agent

□ Verify KayNexus is running
  curl http://localhost:8000/health

□ Check KayNexus logs
  tail -f kaygraph-agent-server/logs/server.log

□ Test agent directly
  curl -X POST http://localhost:8000/v1/chat \
    -H "Content-Type: application/json" \
    -d '{"message": "test"}'

□ Check AgentState in Rails console
  AgentState.last.inspect

□ Verify API keys are set
  echo $ANTHROPIC_API_KEY
  echo $OPENAI_API_KEY

□ Check conversation ID is valid
  Conversation.where(slug: "your-slug").exists?
```

---

**End of Diagrams**
