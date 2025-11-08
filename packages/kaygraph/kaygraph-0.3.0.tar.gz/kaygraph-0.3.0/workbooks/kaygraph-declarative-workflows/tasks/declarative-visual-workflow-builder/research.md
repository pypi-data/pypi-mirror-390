# Research: Declarative Visual Workflow Builder

**Date**: 2025-11-01
**Status**: Complete

---

## Executive Summary

We have **excellent foundations** for building the visual workflow builder:

1. ✅ **Declarative system complete** - All 8 patterns implemented and tested
2. ✅ **ReactFlow already installed** - Both `reactflow` and `@xyflow/react` available
3. ✅ **Existing visualization code** - 2,150 lines of node schema extraction
4. ✅ **Playground infrastructure** - Multi-tenant FastAPI + React stack ready
5. ✅ **Serialization patterns** - `to_dict()` methods in concepts module

**Gap Analysis**: Need bidirectional serialization (Domain/Graph → YAML) and visual converter (ReactFlow ↔ YAML).

---

## 1. Existing KayGraph Declarative Patterns

### 1.1 Current Implementation Status

**Location**: `/workbooks/kaygraph-declarative-workflows/`

**Files and Line Counts**:
```
nodes.py                    1,025 lines  - All node types, including new ones
workflow_loader.py            290 lines  - YAML → Graph conversion
cli.py                        170 lines  - kgraph validate/run/list
domain.py                     270 lines  - Multi-workflow support
utils/concepts.py             690 lines  - Concept validation
utils/config_loader.py        380 lines  - YAML/TOML loading
utils/multiplicity.py         290 lines  - Type system

Total: ~3,115 lines (already implemented)
```

**8 Patterns Already Working**:
1. ✅ Named Intermediate Results (`result:`, `inputs:`)
2. ✅ Inline Schema Definitions (YAML concepts)
3. ✅ CLI + Validation (`kgraph` command)
4. ✅ Expression-Based Routing (safe conditionals)
5. ✅ Batch-in-Sequence (`batch_over:` syntax)
6. ✅ Domain Organization (.kg.yaml files)
7. ✅ Auto-Discovery (CLI list command)
8. ✅ Parallel Operations (`parallels:` task parallelism)

**Node Types Available**:
- `ConfigNode` - Base for all declarative nodes
- `ConceptNode` - Type-safe validation
- `MapperNode` - Data transformation
- `ConditionalNode` - Routing/branching
- `BatchConfigNode` - Batch processing
- `ParallelConfigNode` - Parallel execution

---

### 1.2 YAML Format Analysis

**Complete Example**:
```yaml
# Domain metadata
domain:
  name: invoice_processor
  version: 1.0
  description: "Invoice processing workflow"
  main_workflow: process_invoice

# Concepts (inline schemas)
concepts:
  Invoice:
    description: "Commercial invoice"
    structure:
      invoice_number:
        type: text
        required: true
        pattern: "^INV-\\d{6}$"
      total_amount:
        type: number
        required: true
        min_value: 0.0

# Workflows
workflows:
  process_invoice:
    steps:
      - node: extract_data
        type: llm
        prompt: "Extract invoice data..."
        output_concept: Invoice
        result: invoice_data

      - node: validate
        type: condition
        inputs: [invoice_data]
        expression: "total_amount > 0"
        result: is_valid

      - node: process_batch
        type: llm
        batch_over: items
        batch_as: item
        prompt: "Process {{item}}"
        result: processed_items

      - node: parallel_ops
        type: parallel
        parallels:
          - node: task_a
            type: llm
            result: result_a
          - node: task_b
            type: llm
            result: result_b
```

**Key Observations**:
- Clean, hierarchical structure
- Supports all node types
- Named results for data flow
- Inline concept definitions
- Multiple workflows per file

---

### 1.3 Existing Serialization

**Found in `utils/concepts.py:422`**:
```python
def to_dict(self) -> Dict[str, Any]:
    """Convert concept definition to dictionary."""
    return {
        "description": self.description,
        "structure": self.structure_def
    }
```

**ConceptRegistry** (lines 430-520):
- Manages concept registration
- `load_from_yaml()` method exists
- Can retrieve concepts by name

**What's Missing**:
- ❌ No `Domain.to_dict()` method
- ❌ No `ConfigNode.to_step_dict()` method
- ❌ No `Graph.to_workflow_dict()` method
- ❌ No YAML export functionality

**Implication**: We can load workflows but not serialize them back. Need to add bidirectional support.

---

## 2. Existing Visualization Infrastructure

### 2.1 KayGraph Visualization Workbook

**Location**: `/workbooks/kaygraph-visualization/`

**Files**:
```
node_schema.py         612 lines  - Node introspection, schema extraction
api_server.py          470 lines  - FastAPI endpoints for visualization
visualize.py           510 lines  - Graphviz/Matplotlib rendering
trace_execution.py     499 lines  - Execution tracing
main.py                 59 lines  - CLI entry point

Total: 2,150 lines
```

**Key Classes** (`node_schema.py`):
```python
@dataclass
class ConfigParameter:
    """Node configuration parameter"""
    name: str
    type: str
    default: Any
    required: bool
    options: Optional[List[Any]]

@dataclass
class SharedStateField:
    """Field in shared state"""
    name: str
    type: str
    required: bool

@dataclass
class NodeSchema:
    """Complete schema for a node"""
    node_type: str
    module_path: str
    category: str  # "input", "processing", "output", "decision", "loop"
    display_name: str
    description: str
    icon: str
    config_params: List[ConfigParameter]
    inputs: List[SharedStateField]
    outputs: List[SharedStateField]
    actions: List[str]
    ui_color: str
    ui_width: int
    ui_height: int
```

**Functionality**:
- Introspects Python nodes
- Extracts configuration schemas
- Maps shared state to input/output ports
- Generates UI metadata (colors, sizes, icons)

**Relevance to Our Project**:
- ✅ Good reference for node metadata
- ⚠️ Designed for Python node classes, not YAML configs
- ⚠️ No ReactFlow integration (uses Graphviz)
- 🤔 Could adapt for our declarative nodes

---

### 2.2 API Server Patterns

**`api_server.py`** provides:
```python
@app.get("/nodes/schema")
async def get_node_schemas():
    """Get schemas for all available node types"""

@app.post("/graph/validate")
async def validate_graph(graph_def: dict):
    """Validate graph definition"""

@app.post("/graph/visualize")
async def visualize_graph(graph_def: dict):
    """Generate visualization"""
```

**Key Insights**:
- REST API for node metadata
- Validation endpoints
- Visualization generation
- **But**: Not integrated with declarative workflows yet

---

## 3. ReactFlow Ecosystem

### 3.1 Current Installation

**Playground `frontend/package.json`**:
```json
"dependencies": {
  "@xyflow/react": "^12.8.6",    // ← Latest ReactFlow
  "reactflow": "^11.11.4",       // ← Legacy version (still works)
  "@chakra-ui/react": "^3.8.0",  // ← UI framework
  "@tanstack/react-query": "^5.28.14",
  "@tanstack/react-router": "1.19.1",
  ...
}
```

**Observations**:
- ✅ **@xyflow/react** is the modern package (use this)
- ✅ **reactflow** (v11) is legacy but still functional
- ✅ Chakra UI v3 for consistent styling
- ✅ TanStack Query for data fetching
- ✅ TanStack Router for navigation

---

### 3.2 ReactFlow Capabilities

**Core Features** (from @xyflow/react v12):
- Drag-and-drop nodes
- Custom node components
- Edge connections
- Handles (input/output ports)
- Zoom and pan
- Mini-map
- Controls (zoom buttons)
- Background patterns

**Custom Node Support**:
```typescript
const nodeTypes = {
  llm: LLMNode,
  transform: TransformNode,
  condition: ConditionNode,
  // ... custom components for each node type
}

<ReactFlow nodes={nodes} edges={edges} nodeTypes={nodeTypes} />
```

**Data Flow**:
```typescript
// Node structure
const node = {
  id: '1',
  type: 'llm',
  position: { x: 100, y: 200 },
  data: {
    label: 'Analyze Document',
    prompt: '...',
    result: 'analysis'
  }
}

// Edge structure
const edge = {
  id: 'e1-2',
  source: '1',
  target: '2',
  type: 'default'
}
```

---

### 3.3 ReactFlow → YAML Mapping

**How to Convert**:

**ReactFlow Format**:
```json
{
  "nodes": [
    {
      "id": "node-1",
      "type": "llm",
      "position": {"x": 100, "y": 200},
      "data": {
        "label": "Extract",
        "prompt": "...",
        "result": "raw_data"
      }
    },
    {
      "id": "node-2",
      "type": "transform",
      "position": {"x": 350, "y": 200},
      "data": {
        "label": "Clean",
        "inputs": ["raw_data"],
        "mapping": {...}
      }
    }
  ],
  "edges": [
    {
      "id": "e1-2",
      "source": "node-1",
      "target": "node-2"
    }
  ]
}
```

**YAML Format** (Target):
```yaml
workflows:
  main:
    steps:
      - node: extract        # from node-1
        type: llm
        prompt: "..."
        result: raw_data

      - node: clean          # from node-2
        type: transform
        inputs: [raw_data]
        mapping: {...}

canvas:  # Store visual layout
  nodes:
    - id: extract
      position: {x: 100, y: 200}
    - id: clean
      position: {x: 350, y: 200}
```

**Conversion Logic Needed**:
1. ReactFlow `nodes` → YAML `steps`
2. ReactFlow `edges` → Determine step order + inputs
3. ReactFlow `position` → YAML `canvas.nodes`
4. Node `data` → Step configuration

---

## 4. Playground Infrastructure

### 4.1 Backend (FastAPI)

**Stack**:
- FastAPI (async-first)
- Tortoise ORM (async database)
- PostgreSQL (dual database architecture)
- Aerich (migrations)
- JWT authentication
- CASBIN (RBAC permissions)
- Multi-tenancy (organization-based)

**Existing Patterns**:
```python
# Example: Items CRUD
class Item(TenantModel):
    id = fields.UUIDField(pk=True)
    organization_id = fields.UUIDField(index=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)

@router.get("/items/")
async def list_items(user: CurrentUser, org: CurrentOrg):
    return await Item.filter(organization_id=org.id).all()
```

**What We Need to Add**:
```python
class WorkflowDefinition(TenantModel):
    """Store workflow as YAML"""
    organization_id = fields.UUIDField(index=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    yaml_content = fields.TextField()  # The .kg.yaml file
    visual_layout = fields.JSONField(null=True)  # ReactFlow state
    is_deployed = fields.BooleanField(default=False)

class WorkflowExecution(TenantModel):
    """Execution logs"""
    workflow_id = fields.ForeignKeyField("models.WorkflowDefinition")
    organization_id = fields.UUIDField(index=True)
    input_data = fields.JSONField()
    output_data = fields.JSONField(null=True)
    status = fields.CharField(max_length=50)
    error_message = fields.TextField(null=True)
    started_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
```

---

### 4.2 Frontend (React + TypeScript)

**Stack**:
- React 18
- TypeScript (strict mode)
- Vite (build tool)
- Chakra UI v3
- TanStack Router (file-based routing)
- TanStack Query (data fetching)
- ReactFlow (already installed!)

**Existing Component Patterns**:
```
src/components/
├── Common/
│   ├── ActionsMenu.tsx
│   ├── DeleteAlert.tsx
│   ├── EditModal.tsx
│   └── Navbar.tsx
├── Items/
│   ├── AddItem.tsx
│   ├── EditItem.tsx
│   └── ItemsTable.tsx
└── ui/
    ├── button.tsx
    ├── input.tsx
    └── ... (Chakra UI primitives)
```

**What We Need to Add**:
```
src/components/WorkflowBuilder/
├── WorkflowCanvas.tsx        # Main ReactFlow canvas
├── NodePalette.tsx           # Drag-drop node library
├── NodeEditor.tsx            # Edit node properties
├── ConceptEditor.tsx         # Define concepts
├── EdgeConfig.tsx            # Configure edges (actions)
├── WorkflowToolbar.tsx       # Zoom, save, test controls
└── TestConsole.tsx           # Execute and view results

src/routes/_layout/workflows/
├── index.tsx                 # List workflows
├── new.tsx                   # Create new workflow
├── $id.tsx                   # Edit workflow
└── $id.execute.tsx           # Test/run workflow
```

---

### 4.3 LLM Integration Patterns

**Existing Service** (`backend/app/services/llm_service.py`):
```python
from litellm import completion

async def call_llm(
    messages: List[Dict],
    model: str = "gpt-4",
    temperature: float = 0.7
) -> str:
    response = await completion(
        model=model,
        messages=messages,
        temperature=temperature
    )
    return response.choices[0].message.content
```

**For Workflow Generation**:
```python
async def generate_workflow_from_description(
    description: str,
    examples: Optional[List[Dict]] = None
) -> str:
    """
    Generate .kg.yaml from natural language description.

    Args:
        description: User's workflow description
        examples: Optional example workflows for context

    Returns:
        Complete .kg.yaml content
    """
    prompt = f"""
    Generate a KayGraph workflow in YAML format.

    Description: {description}

    Format:
    domain:
      name: workflow_name
    concepts:
      ConceptName:
        structure: {{...}}
    workflows:
      main:
        steps: [...]

    Return only valid YAML.
    """

    yaml_content = await call_llm([
        {"role": "system", "content": "You are a workflow generator."},
        {"role": "user", "content": prompt}
    ])

    return yaml_content
```

---

## 5. Technology Stack Recommendations

### 5.1 Frontend Libraries

**Core**:
- ✅ `@xyflow/react` v12 (already installed) - Visual canvas
- ✅ `@chakra-ui/react` v3 (already installed) - UI components
- ✅ `@tanstack/react-query` (already installed) - Data fetching
- ✅ `react-hook-form` (already installed) - Form management

**Need to Add**:
- `js-yaml` - YAML parsing/serialization
- `monaco-editor` or `@uiw/react-codemirror` - Code editor for YAML
- `react-syntax-highlighter` - Syntax highlighting for readonly views

**Installation**:
```bash
cd frontend
npm install js-yaml @types/js-yaml
npm install @monaco-editor/react
# or
npm install @uiw/react-codemirror
```

---

### 5.2 Backend Libraries

**Core** (already have):
- ✅ `tortoise-orm` - Database ORM
- ✅ `fastapi` - Web framework
- ✅ `pydantic` - Validation
- ✅ `litellm` - LLM calls

**Need to Add to KayGraph Core**:
- `pyyaml` - YAML serialization (add to `[declarative]` extra)

**KayGraph Core `setup.py`**:
```python
[project.optional-dependencies]
declarative = [
    "pyyaml>=6.0",
]
```

---

## 6. Similar Projects Analysis

### 6.1 n8n (Workflow Automation)
- **Visual Builder**: Node-based drag-drop
- **Storage**: PostgreSQL with JSON
- **Export**: JSON format
- **Lessons**:
  - Visual is primary, code is secondary
  - Need good undo/redo
  - Templates are valuable

### 6.2 Langflow (LLM Workflows)
- **Visual Builder**: ReactFlow-based
- **Storage**: JSON in SQLite/PostgreSQL
- **Export**: JSON + Python code generation
- **Lessons**:
  - Chat interface for workflow generation
  - Component marketplace
  - Live testing crucial

### 6.3 Flowise (LLM Chains)
- **Visual Builder**: ReactFlow
- **Storage**: TypeORM (JSON)
- **Export**: JSON format
- **Lessons**:
  - Simple, focused UI
  - Quick testing is key
  - Good documentation templates

**Key Takeaway**: All use JSON as primary storage format and generate code/config as export. We're doing the opposite (YAML primary, visual secondary) which is better for portability!

---

## 7. Technical Decisions

### 7.1 Data Flow Architecture

**Choice: YAML as Source of Truth**

```
User Interaction
    ↓
Visual Canvas (ReactFlow)
    ↓
Convert to YAML
    ↓
Store in Database (yaml_content field)
    ↓
Load from YAML
    ↓
Execute via KayGraph
```

**Alternative Considered**:
- Store ReactFlow JSON, generate YAML on export
- ❌ Rejected: YAML must be portable, not an afterthought

**Implications**:
- Bidirectional sync: Visual ↔ YAML
- YAML is editable directly
- Visual is a "view" of YAML
- Changes in either side sync to both

---

### 7.2 Serialization Strategy

**Approach: Two-Layer System**

**Layer 1: Core Serialization** (in `kaygraph/declarative/`)
```python
# serializer.py
class WorkflowSerializer:
    def domain_to_dict(self, domain: Domain) -> Dict
    def domain_to_yaml(self, domain: Domain) -> str
    def graph_to_workflow_dict(self, graph: Graph) -> Dict
    def node_to_step_dict(self, node: ConfigNode) -> Dict
```

**Layer 2: Visual Converter** (in `kaygraph/declarative/`)
```python
# visual_converter.py
class VisualConverter:
    def reactflow_to_domain_dict(self, reactflow_data: Dict) -> Dict
    def domain_dict_to_reactflow(self, domain_dict: Dict) -> Dict
```

**Why Two Layers**:
- Core serialization: KayGraph → YAML (library responsibility)
- Visual conversion: ReactFlow ↔ YAML (UI-specific)
- Separation of concerns
- Core package doesn't depend on ReactFlow

---

### 7.3 Testing Strategy

**Mock Mode**:
```python
# Mock LLM responses for fast iteration
MOCK_RESPONSES = {
    "analyze_invoice": {"invoice_number": "INV-123", "total": 1000.00},
    "validate_data": {"is_valid": True},
}

def execute_workflow_mock(workflow: Domain, inputs: Dict) -> Dict:
    """Execute with mock responses (fast)"""
    # Simulate execution, return mocked results
```

**Real Mode**:
```python
async def execute_workflow_real(workflow: Domain, inputs: Dict) -> Dict:
    """Execute with real LLM calls (accurate)"""
    domain = load_domain_from_string(workflow.yaml_content)
    graph = create_graph_from_domain(domain)
    shared = inputs.copy()
    graph.run(shared)
    return shared
```

**UI Toggle**:
```typescript
const [executionMode, setExecutionMode] = useState<'mock' | 'real'>('mock')

<Toggle value={executionMode} onChange={setExecutionMode}>
  <Option value="mock">Mock (Fast)</Option>
  <Option value="real">Real (Accurate)</Option>
</Toggle>
```

---

## 8. Implementation Complexity Estimates

### 8.1 Core Package Changes

**Files to Add**: 2 new files
- `kaygraph/declarative/serializer.py` - 300 lines
- `kaygraph/declarative/visual_converter.py` - 250 lines

**Files to Modify**: 2 existing files
- `kaygraph/declarative/domain.py` - Add `to_dict()` methods - 50 lines
- `kaygraph/declarative/cli.py` - Add export commands - 100 lines

**Total Addition**: ~700 lines to core package

**Complexity**: **Medium** (5/10)
- Clear patterns to follow
- Reverse of existing loaders
- Good test coverage possible

---

### 8.2 Backend Changes

**Files to Add**: 6 new files
- `backend/app/models.py` - Add 2 models - 100 lines
- `backend/migrations/*.py` - Migration file - auto-generated
- `backend/app/api/routes/workflows.py` - CRUD endpoints - 250 lines
- `backend/app/api/routes/executions.py` - Execution endpoints - 150 lines
- `backend/app/services/workflow_runner.py` - Execution service - 200 lines
- `backend/tests/test_workflows.py` - Tests - 300 lines

**Total Addition**: ~1,000 lines

**Complexity**: **Low** (3/10)
- Follows existing CRUD patterns
- Standard Tortoise ORM usage
- Existing test patterns to copy

---

### 8.3 Frontend Changes

**Files to Add**: 12 new files
- `frontend/src/components/WorkflowBuilder/*.tsx` - 7 components - 1,200 lines
- `frontend/src/hooks/useWorkflowBuilder.ts` - State management - 150 lines
- `frontend/src/hooks/useYAMLSync.ts` - Bidirectional sync - 200 lines
- `frontend/src/routes/_layout/workflows/*.tsx` - 4 routes - 800 lines
- `frontend/src/types/workflow.ts` - TypeScript types - 100 lines

**Total Addition**: ~2,450 lines

**Complexity**: **High** (8/10)
- ReactFlow learning curve
- Bidirectional sync is complex
- State management across components
- Need good UX/UI design

---

## 9. Key Findings Summary

### 9.1 Strengths

✅ **Excellent Foundation**:
- Declarative system 100% complete
- ReactFlow already installed
- Playground infrastructure mature
- Multi-tenancy ready
- LLM integration exists

✅ **Clear Patterns**:
- CRUD follows existing Items pattern
- Component structure is established
- Routing is file-based and clear

✅ **Good Documentation**:
- Extensive LLM guides in Playground
- CLAUDE.md for both repos
- Implementation notes for declarative

---

### 9.2 Gaps to Fill

❌ **Missing Bidirectional Serialization**:
- Can load YAML → Graph ✅
- Cannot save Graph → YAML ❌
- Need to add `to_dict()` methods

❌ **No Visual Builder Yet**:
- ReactFlow installed but not used
- Need complete component set
- Need bidirectional sync logic

❌ **No Workflow CRUD**:
- No database models
- No API endpoints
- No frontend routes

---

### 9.3 Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| ReactFlow complexity | Medium | Start simple, iterate |
| Bidirectional sync bugs | High | Comprehensive tests, YAML is source of truth |
| Core package size | Low | Strict line limits, focused scope |
| UI/UX design | Medium | Copy patterns from n8n/Langflow |
| Performance with large workflows | Low | React memo, virtualization if needed |

---

## 10. Recommendations

### 10.1 Implementation Order (Reaffirmed)

1. **Core Package** (Week 1) - Foundation
   - Add serialization (Domain/Graph → YAML)
   - Add visual converter (ReactFlow ↔ YAML)
   - Add export CLI commands
   - Test thoroughly

2. **Backend API** (Week 2) - Data Layer
   - Add Tortoise models
   - Create migrations
   - Build CRUD endpoints
   - Build execution endpoint
   - Add permissions

3. **Frontend UI** (Week 3) - User Interface
   - ReactFlow canvas
   - Node palette
   - Bidirectional sync
   - Test console
   - Polish UX

---

### 10.2 Quick Wins

**Week 1 Quick Wins**:
- ✅ Serialization proves bidirectionality
- ✅ CLI export validates portability
- ✅ Tests give confidence

**Week 2 Quick Wins**:
- ✅ Can store workflows in database
- ✅ Can execute workflows via API
- ✅ Can test with Swagger UI

**Week 3 Quick Wins**:
- ✅ Visual builder working
- ✅ Can create simple workflows
- ✅ Export/import working

---

## 11. Next Steps

✅ Research Complete

→ **Create Comprehensive Plan** (`plan.md`)

Plan should include:
1. Complete DSL specification
2. Database schema (SQL)
3. API endpoints (OpenAPI spec)
4. Component tree (React)
5. File-by-file implementation checklist
6. Test strategy
7. Example workflows

---

## Appendix A: Code Samples

### A.1 Existing Workflow Loading

```python
# From workflow_loader.py
def load_workflow(workflow_path: str) -> Graph:
    config = load_config(workflow_path)

    # Load concepts
    concepts_dict = config.get("concepts", {})
    if concepts_dict:
        registry = get_concept_registry()
        registry.load_from_yaml(concepts_dict)

    # Build graph from steps
    steps = config["workflow"]["steps"]
    nodes = [create_config_node_from_step(step) for step in steps]

    graph = Graph(start=nodes[0])
    for i in range(len(nodes) - 1):
        nodes[i] >> nodes[i + 1]

    return graph
```

### A.2 Existing Concept Serialization

```python
# From utils/concepts.py
class Concept:
    def to_dict(self) -> Dict[str, Any]:
        return {
            "description": self.description,
            "structure": self.structure_def
        }
```

### A.3 Existing CRUD Pattern

```python
# From backend/app/api/routes/items.py
@router.post("/", response_model=ItemPublic)
async def create_item(
    item_in: ItemCreate,
    user: CurrentUser,
    org: CurrentOrg
):
    item = await Item.create(
        **item_in.dict(),
        organization_id=org.id,
        owner_id=user.id
    )
    return item
```

---

## Appendix B: Technology Stack

**Core Package**:
- Python 3.10+
- pyyaml (new dependency)
- Zero other dependencies

**Backend**:
- FastAPI
- Tortoise ORM
- PostgreSQL
- LiteLLM
- CASBIN

**Frontend**:
- React 18
- TypeScript
- @xyflow/react v12
- Chakra UI v3
- TanStack Query/Router
- js-yaml (new)
- Monaco Editor (new)

---

**Research Complete**. Ready for planning phase.
