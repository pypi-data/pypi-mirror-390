# KayGraph UI Integration Guide

**Complete guide to building n8n/Zapier-style visual workflow builders for KayGraph**

---

## 🎯 Overview

This system enables **dynamic discovery, configuration, and visual editing** of KayGraph workflows using ReactFlow/XYFlow. It automatically:

1. **Discovers** workbooks and their nodes
2. **Extracts** configuration schemas via introspection
3. **Generates** UI forms for node configuration
4. **Validates** workflow connections
5. **Executes** workflows with real-time updates
6. **Exports** workflows as Python code

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    React Frontend (Port 3000)                │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  ReactFlow Canvas                                       │ │
│  │  - Drag-drop nodes from palette                        │ │
│  │  - Connect nodes visually                              │ │
│  │  - Configure nodes via panels                          │ │
│  │  - Watch real-time execution                           │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/WebSocket
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              FastAPI Backend (Port 8000)                     │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  api_server.py                                          │ │
│  │  - GET /api/workbooks → List workbooks                 │ │
│  │  - GET /api/nodes → Get node schemas                   │ │
│  │  - POST /api/workflows/validate → Validate workflow    │ │
│  │  - POST /api/workflows/execute → Execute workflow      │ │
│  │  - WS /ws/execute/:id → Stream execution events        │ │
│  └────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  node_schema.py                                         │ │
│  │  - NodeSchemaExtractor: Introspect nodes               │ │
│  │  - WorkbookDiscovery: Find workbooks                   │ │
│  │  - NodeSchemaAPI: Serve schemas to UI                  │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                    KayGraph Workbooks                        │
│  ┌──────────────┬──────────────┬──────────────┬──────────┐ │
│  │ deep_research│ document_    │ customer_    │ conver-  │ │
│  │              │ analysis     │ support      │ sation_  │ │
│  │              │              │              │ memory   │ │
│  │ nodes.py     │ nodes.py     │ nodes.py     │ nodes.py │ │
│  │ specialized_ │              │              │          │ │
│  │ nodes.py     │              │              │          │ │
│  │ graphs.py    │ graphs.py    │ graphs.py    │ graphs.py│ │
│  │ workbook.json│ workbook.json│ workbook.json│ workbook.│ │
│  │              │              │              │ json     │ │
│  └──────────────┴──────────────┴──────────────┴──────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Key Components

### 1. **Node Schema System** (`node_schema.py`)

**Purpose:** Automatically extract metadata from Python nodes for UI generation

#### Schema Structure

```python
NodeSchema {
    # Identity
    node_type: "IntentClarificationNode"
    module_path: "claude_integration.deep_research.nodes.IntentClarificationNode"
    category: "input"  # input, processing, output, decision, orchestrator, worker
    display_name: "Intent Clarification"
    description: "Analyzes research query and clarifies intent"
    icon: "🎯"

    # Configuration (from __init__ parameters)
    config_params: [
        {
            name: "enable_clarifying_questions"
            type: "boolean"
            default: true
            required: false
            description: "Whether to ask clarifying questions"
        },
        {
            name: "interface"
            type: "enum"
            options: ["cli", "async"]
            default: "cli"
        }
    ]

    # Data Flow (from prep/post methods)
    inputs: [
        {
            name: "query"
            type: "string"
            required: true
            description: "Read from shared state: query"
        }
    ]

    outputs: [
        {
            name: "research_task"
            type: "ResearchTask"
            description: "Written to shared state: research_task"
        },
        {
            name: "key_questions"
            type: "List[str]"
        }
    ]

    # Routing (from post() return values)
    actions: ["clarifying_questions", "lead_researcher"]

    # UI Hints
    ui_color: "#E8F5E9"
    ui_width: 200
    ui_height: 100
}
```

#### How It Works

**Introspection Process:**

1. **`__init__` Analysis:**
   ```python
   def __init__(self, enable_clarifying_questions: bool = True):
   ```
   ↓ **Extracts**
   ```json
   {
     "name": "enable_clarifying_questions",
     "type": "boolean",
     "default": true,
     "required": false
   }
   ```

2. **`prep()` Analysis:**
   ```python
   def prep(self, shared):
       return {"query": shared.get("query", "")}
   ```
   ↓ **Detects `shared.get()` calls**
   ```json
   {
     "name": "query",
     "required": false  # has default ""
   }
   ```

3. **`post()` Analysis:**
   ```python
   def post(self, shared, prep_res, exec_res):
       shared["research_task"] = task
       return "lead_researcher"
   ```
   ↓ **Detects `shared["key"] = value` and `return "action"`**
   ```json
   {
     "outputs": [{"name": "research_task"}],
     "actions": ["lead_researcher"]
   }
   ```

---

### 2. **Workbook Discovery** (`workbook.json`)

**Purpose:** Metadata files for each workbook

```json
// claude_integration/deep_research/workbook.json
{
  "name": "Deep Research",
  "version": "1.0.0",
  "description": "Multi-agent research system...",
  "icon": "🔬",
  "categories": ["research", "multi-agent"],
  "node_modules": ["nodes", "specialized_nodes"],
  "workflow_functions": [
    "create_research_workflow",
    "create_multi_aspect_research_workflow"
  ],
  "entry_point": "main.py",
  "examples": ["examples/01_basic_research.py"]
}
```

**Auto-Discovery:**
- Scans `claude_integration/` directory
- Looks for `workbook.json` files
- Falls back to auto-detection if no metadata file

---

### 3. **FastAPI Backend** (`api_server.py`)

**Endpoints:**

#### Discovery
```bash
GET /api/workbooks
# Returns: [{name, icon, categories, node_count}, ...]

GET /api/workbooks/{name}/nodes
# Returns: [NodeSchema, ...]

GET /api/nodes/{node_type}/schema
# Returns: NodeSchema (full details)
```

#### Workflow Management
```bash
POST /api/workflows/validate
# Body: WorkflowDefinition
# Returns: {valid: bool, errors: [], warnings: []}

POST /api/workflows/export/python
# Body: WorkflowDefinition
# Returns: {code: "python code", filename: "workflow.py"}
```

#### Execution
```bash
POST /api/workflows/execute
# Body: {workflow, input_data}
# Returns: {execution_id, status, output}

WS /ws/execute/{execution_id}
# Streams: {event_type, node_id, timestamp, data}
```

---

## 🎨 React Frontend Implementation

### Required Libraries

```bash
npm install reactflow zustand
npm install @tanstack/react-query  # API calls
npm install tailwindcss  # Styling
```

### Directory Structure

```
src/
├── components/
│   ├── Canvas/
│   │   ├── KayGraphCanvas.tsx          # Main ReactFlow canvas
│   │   ├── Sidebar.tsx                 # Node palette
│   │   └── Minimap.tsx                 # Overview
│   ├── Nodes/
│   │   ├── BaseNode.tsx                # Base node component
│   │   ├── IntentNode.tsx              # Specific node types...
│   │   └── DynamicNode.tsx             # Generic node from schema
│   ├── Panels/
│   │   ├── NodeConfigPanel.tsx         # Configure selected node
│   │   ├── SharedStateViewer.tsx       # View shared state
│   │   └── ExecutionTracePanel.tsx     # Real-time execution
│   └── Edges/
│       ├── ConditionalEdge.tsx         # Edge with action label
│       └── AnimatedEdge.tsx            # Animated during execution
├── hooks/
│   ├── useWorkbooks.ts                 # Fetch workbooks
│   ├── useNodeSchema.ts                # Fetch node schemas
│   ├── useWorkflowExecution.ts         # Execute workflows
│   └── useWebSocket.ts                 # Real-time events
├── store/
│   └── workflowStore.ts                # Zustand state management
└── utils/
    ├── schemaToForm.ts                 # Generate forms from schema
    └── workflowConverter.ts            # Convert to KayGraph
```

### Core Components

#### 1. Main Canvas

```tsx
// src/components/Canvas/KayGraphCanvas.tsx
import ReactFlow, { Node, Edge, Background, Controls } from 'reactflow';
import { useWorkflowStore } from '@/store/workflowStore';
import { DynamicNode } from '@/components/Nodes/DynamicNode';

export function KayGraphCanvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect } =
    useWorkflowStore();

  // Dynamic node types from schemas
  const nodeTypes = useMemo(() => ({
    dynamicNode: DynamicNode,
    // ... other custom nodes
  }), []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
      nodeTypes={nodeTypes}
      fitView
    >
      <Background />
      <Controls />
    </ReactFlow>
  );
}
```

#### 2. Dynamic Node Component

```tsx
// src/components/Nodes/DynamicNode.tsx
import { Handle, Position } from 'reactflow';
import { NodeSchema } from '@/types/schema';

interface DynamicNodeProps {
  data: {
    schema: NodeSchema;
    config: Record<string, any>;
    status?: 'idle' | 'running' | 'complete' | 'error';
  };
  selected: boolean;
}

export function DynamicNode({ data, selected }: DynamicNodeProps) {
  const { schema, config, status } = data;

  return (
    <div
      className={`node ${selected ? 'selected' : ''} ${status}`}
      style={{ backgroundColor: schema.ui_color }}
    >
      {/* Header */}
      <div className="node-header">
        <span className="node-icon">{schema.icon}</span>
        <span className="node-title">{schema.display_name}</span>
      </div>

      {/* Body - Show config preview */}
      <div className="node-body">
        {schema.config_params.slice(0, 2).map(param => (
          <div key={param.name} className="config-preview">
            <label>{param.name}:</label>
            <span>{config[param.name] ?? param.default}</span>
          </div>
        ))}
      </div>

      {/* Status indicator */}
      {status && (
        <div className={`status-badge status-${status}`}>
          {status === 'running' && '⏳'}
          {status === 'complete' && '✅'}
          {status === 'error' && '❌'}
        </div>
      )}

      {/* Handles */}
      <Handle type="target" position={Position.Top} />
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}
```

#### 3. Node Config Panel

```tsx
// src/components/Panels/NodeConfigPanel.tsx
import { NodeSchema, ConfigParameter } from '@/types/schema';
import { generateFormField } from '@/utils/schemaToForm';

interface NodeConfigPanelProps {
  node: Node;
  schema: NodeSchema;
  onConfigChange: (config: Record<string, any>) => void;
}

export function NodeConfigPanel({ node, schema, onConfigChange }: Props) {
  const [config, setConfig] = useState(node.data.config || {});

  const handleChange = (param: string, value: any) => {
    const updated = { ...config, [param]: value };
    setConfig(updated);
    onConfigChange(updated);
  };

  return (
    <div className="config-panel">
      <h3>{schema.display_name} Configuration</h3>

      {schema.config_params.map(param => (
        <div key={param.name} className="config-field">
          <label>
            {param.name}
            {param.required && <span className="required">*</span>}
          </label>

          {generateFormField(param, config[param.name], handleChange)}

          {param.description && (
            <p className="field-help">{param.description}</p>
          )}
        </div>
      ))}
    </div>
  );
}
```

#### 4. Schema-to-Form Generator

```tsx
// src/utils/schemaToForm.ts
import { ConfigParameter } from '@/types/schema';

export function generateFormField(
  param: ConfigParameter,
  value: any,
  onChange: (name: string, value: any) => void
) {
  switch (param.type) {
    case 'boolean':
      return (
        <input
          type="checkbox"
          checked={value ?? param.default}
          onChange={(e) => onChange(param.name, e.target.checked)}
        />
      );

    case 'number':
      return (
        <input
          type="number"
          value={value ?? param.default}
          min={param.min_value}
          max={param.max_value}
          onChange={(e) => onChange(param.name, Number(e.target.value))}
        />
      );

    case 'enum':
      return (
        <select
          value={value ?? param.default}
          onChange={(e) => onChange(param.name, e.target.value)}
        >
          {param.options?.map(opt => (
            <option key={opt} value={opt}>{opt}</option>
          ))}
        </select>
      );

    case 'string':
    default:
      return (
        <input
          type="text"
          value={value ?? param.default ?? ''}
          onChange={(e) => onChange(param.name, e.target.value)}
        />
      );
  }
}
```

#### 5. Real-Time Execution

```tsx
// src/hooks/useWorkflowExecution.ts
import { useWebSocket } from '@/hooks/useWebSocket';

export function useWorkflowExecution() {
  const [executionId, setExecutionId] = useState<string | null>(null);
  const { messages, sendMessage, isConnected } = useWebSocket(
    executionId ? `ws://localhost:8000/ws/execute/${executionId}` : null
  );

  const executeWorkflow = async (workflow, inputData) => {
    const id = crypto.randomUUID();
    setExecutionId(id);

    // Send workflow via WebSocket
    sendMessage({
      workflow,
      input_data: inputData
    });
  };

  // Process execution events
  useEffect(() => {
    messages.forEach(msg => {
      switch (msg.event_type) {
        case 'node_start':
          // Update node status to 'running'
          updateNodeStatus(msg.node_id, 'running');
          break;

        case 'node_complete':
          // Update node status to 'complete'
          updateNodeStatus(msg.node_id, 'complete');
          break;

        case 'state_update':
          // Update shared state viewer
          updateSharedState(msg.data);
          break;

        case 'workflow_complete':
          // Show results
          setResults(msg.data);
          break;
      }
    });
  }, [messages]);

  return { executeWorkflow, isExecuting: isConnected };
}
```

---

## 🚀 Complete Workflow

### 1. **UI Loads** → Fetch Schemas

```tsx
// On app load
const { data: workbooks } = useQuery({
  queryKey: ['workbooks'],
  queryFn: () => fetch('http://localhost:8000/api/workbooks').then(r => r.json())
});

// When user selects workbook
const { data: nodes } = useQuery({
  queryKey: ['workbook-nodes', workbookName],
  queryFn: () => fetch(`/api/workbooks/${workbookName}/nodes`).then(r => r.json())
});
```

### 2. **User Drags Node** → Create Instance

```tsx
// User drags from sidebar
const onDrop = (event) => {
  const schema = JSON.parse(event.dataTransfer.getData('nodeSchema'));

  const newNode = {
    id: `${schema.node_type}_${Date.now()}`,
    type: 'dynamicNode',
    position: { x: event.clientX, y: event.clientY },
    data: {
      schema,
      config: getDefaultConfig(schema),
      status: 'idle'
    }
  };

  addNode(newNode);
};
```

### 3. **User Connects Nodes** → Create Edge

```tsx
const onConnect = (params) => {
  addEdge({
    ...params,
    label: 'default',  // Can be edited later
    animated: true
  });
};
```

### 4. **User Configures Node** → Update Config

```tsx
// Click node → show config panel
const onNodeClick = (event, node) => {
  setSelectedNode(node);
  setShowConfigPanel(true);
};

// Update config
const onConfigChange = (nodeId, config) => {
  updateNode(nodeId, (node) => ({
    ...node,
    data: { ...node.data, config }
  }));
};
```

### 5. **User Clicks Run** → Execute Workflow

```tsx
const onExecute = async () => {
  // Validate
  const validation = await fetch('/api/workflows/validate', {
    method: 'POST',
    body: JSON.stringify({ nodes, edges, start_node_id })
  }).then(r => r.json());

  if (!validation.valid) {
    showErrors(validation.errors);
    return;
  }

  // Execute with WebSocket streaming
  await executeWorkflow({ nodes, edges, start_node_id }, inputData);
};
```

### 6. **Watch Execution** → Update UI

```tsx
// WebSocket events update node status
useEffect(() => {
  wsMessages.forEach(msg => {
    if (msg.event_type === 'node_start') {
      // Highlight node, show spinner
      updateNodeStatus(msg.node_id, 'running');

      // Animate edge
      animateEdge(getCurrentEdge(msg.node_id));
    }
  });
}, [wsMessages]);
```

---

## 📝 Example: Deep Research in UI

### Workbook Sidebar

```
📁 Workbooks
  └─ 🔬 Deep Research
       ├─ 🎯 Intent Clarification
       ├─ ❓ Clarifying Questions
       ├─ 👔 Lead Researcher
       ├─ 🤖 Sub Agent
       ├─ 🔹 Aspect Prioritization
       ├─ ⚖️ Comparison Matrix
       └─ ⚡ Result Synthesis
```

### Canvas After Building Workflow

```
┌───────────────┐
│ 🎯 Intent     │
│ Clarification │
└───────┬───────┘
        │ "clarifying_questions"
        ├─────────────────┐
        │                 ▼
        │         ┌──────────────┐
        │         │ ❓ Clarifying│
        │         │  Questions   │
        │         └──────┬───────┘
        │                │
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│ 🔹 Aspect    │  │ 👔 Lead      │
│ Prioritizer  │◄─┤ Researcher   │
└──────┬───────┘  └──────────────┘
       │
       ▼
┌──────────────┐
│ 🤖 Sub Agent │ (ParallelBatch)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ ⚡ Synthesis │
└──────────────┘
```

### Config Panel (Intent Clarification Node Selected)

```
┌─────────────────────────────────────┐
│ Configuration: Intent Clarification │
├─────────────────────────────────────┤
│                                     │
│ ☑ Enable Clarifying Questions      │
│   Ask user for clarification when   │
│   query is ambiguous                │
│                                     │
│ Interface: [cli ▼]                  │
│   Options: cli, async               │
│   CLI for terminal, async for API   │
│                                     │
│ [Cancel]              [Apply]       │
└─────────────────────────────────────┘
```

---

## 🎯 Key Decisions Answered

### ✅ **Discovery: How to load workbooks?**
- `workbook.json` metadata files
- Auto-detection as fallback
- `/api/workbooks` endpoint

### ✅ **Schema: How to map inputs/configs?**
- Python introspection via `inspect` module
- AST parsing for shared state analysis
- Type hints → UI field types

### ✅ **Representation: How to generate UI forms?**
- `ConfigParameter` schema → form fields
- Type-based rendering (boolean → checkbox, enum → select)
- Validation rules from schema

### ✅ **Validation: How to ensure valid connections?**
- Check `inputs` match `outputs`
- Validate action routing
- Detect unreachable nodes

---

## 🚀 Next Steps

1. **Implement ReactFlow Frontend** (see structure above)
2. **Add Real Execution** (convert ReactFlow → KayGraph Python)
3. **Enhance Schema Extraction** (better type inference)
4. **Add Templates** (pre-built workflows like n8n)
5. **Add Collaboration** (multi-user editing)

This architecture gives you a **production-ready foundation** for building visual workflow editors for KayGraph! 🎉
