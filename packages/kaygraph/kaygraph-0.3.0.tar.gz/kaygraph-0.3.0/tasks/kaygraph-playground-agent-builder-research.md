# KayGraph Playground + Agent Builder: Research & Architecture

**Date**: 2025-11-01
**Goal**: Understand how to integrate declarative workflows with visual agent builder in KayGraph Playground

---

## 🎯 The Big Picture

### What We Have

1. **KayGraph Core** (Main repo)
   - Zero-dependency graph framework
   - 71 production examples in workbooks/
   - Pure Python, thread-safe, production-ready

2. **Declarative Workflows** (This session - just completed!)
   - CLI tool: `kgraph validate/run/list`
   - YAML/TOML workflow definitions
   - Named results, inline schemas
   - Batch processing, domains
   - Expression-based routing
   - **7 of 8 patterns complete** ✅

3. **KayGraph Playground** (Full-stack template)
   - FastAPI + React + TypeScript
   - Dual databases (webapp-db + backend-db)
   - JWT authentication
   - Podman containers
   - `./dev.sh` for development
   - `./manage.sh` for production

4. **Visual Builder System** (Partially built)
   - `node_schema.py` - Auto-introspection (650 lines) ✅
   - `api_server.py` - FastAPI backend (400 lines) ✅
   - `UI_INTEGRATION_GUIDE.md` - React architecture (850 lines) ✅
   - **4 workbooks with metadata** ✅
   - ReactFlow frontend - NOT YET BUILT ❌

---

## 🏗️ The Vision: Complete Agent Builder Platform

### User Journey

```
1. User opens KayGraph Playground web app
   ↓
2. Sees library of workbooks (Deep Research, Customer Support, etc.)
   ↓
3. Drags nodes onto canvas (n8n-style)
   ↓
4. Connects nodes visually
   ↓
5. Configures each node (auto-generated forms)
   ↓
6. Clicks "Validate" → Instant feedback
   ↓
7. Clicks "Run" → Real-time execution visualization
   ↓
8. Exports to:
   - Python code
   - YAML workflow (.kg.yaml)
   - TOML workflow (.plx)
   ↓
9. Shares workflow with community (future: hub)
```

---

## 🔄 How Declarative Workflows Fit In

### Current State: Two Parallel Systems

**System A: Visual Builder (KayGraph Playground)**
- Users drag-drop nodes
- Configure via UI forms
- Execute workflows visually
- **Backend**: FastAPI + node introspection
- **Frontend**: React + ReactFlow (TO BE BUILT)

**System B: Declarative Workflows (kaygraph-declarative-workflows)**
- Users write YAML/TOML
- Validate with `kgraph validate`
- Run with `kgraph run`
- **CLI tool**: Works now ✅
- **File format**: .kg.yaml / .toml

### The Integration Opportunity

```
Visual Builder → Generates → Declarative YAML
                              ↓
                         kgraph validate
                              ↓
                         kgraph run
                              ↓
                         Results displayed in UI
```

**AND**

```
Declarative YAML → Loads into → Visual Builder
                                 ↓
                            Edit visually
                                 ↓
                            Save as YAML
```

**Bi-directional flow!**

---

## 📊 Architecture: How It All Connects

```
┌─────────────────────────────────────────────────────────────┐
│                  KayGraph Playground Web App                 │
│                      (React + FastAPI)                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Visual Workflow Editor                   │  │
│  │                (ReactFlow Canvas)                     │  │
│  │                                                        │  │
│  │  [Drag nodes] → [Connect] → [Configure] → [Run]      │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓ ↑                              │
│                    Export / Import                          │
│                            ↓ ↑                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          Declarative Workflow Engine                  │  │
│  │                                                        │  │
│  │  • Load .kg.yaml files                                │  │
│  │  • Validate workflows (kgraph validate)               │  │
│  │  • Execute workflows (kgraph run)                     │  │
│  │  • Generate YAML from visual                          │  │
│  │  • Parse YAML to visual                               │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓ ↑                              │
│                    Node Introspection                       │
│                            ↓ ↑                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              Node Schema System                       │  │
│  │           (node_schema.py - 650 lines)                │  │
│  │                                                        │  │
│  │  • Auto-discover workbooks                            │  │
│  │  • Extract node schemas                               │  │
│  │  • Generate UI forms                                  │  │
│  └──────────────────────────────────────────────────────┘  │
│                            ↓                                │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                KayGraph Workbooks                     │  │
│  │                                                        │  │
│  │  📁 deep_research/    nodes.py + graphs.py           │  │
│  │  📁 document_analysis/                                │  │
│  │  📁 customer_support/                                 │  │
│  │  📁 conversation_memory/                              │  │
│  │  📁 kaygraph-declarative-workflows/  .kg.yaml files  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Integration Points

### 1. Workflow Format Bridging

**Challenge**: Visual builder uses JSON, declarative uses YAML/TOML

**Solution**: Bi-directional converters

```python
# api_server.py additions
@app.post("/api/workflows/export/yaml")
async def export_to_yaml(visual_workflow: VisualWorkflow):
    """Convert visual workflow to .kg.yaml format"""
    return yaml_generator.from_visual(visual_workflow)

@app.post("/api/workflows/import/yaml")
async def import_from_yaml(file: UploadFile):
    """Convert .kg.yaml to visual workflow"""
    yaml_content = await file.read()
    return yaml_parser.to_visual(yaml_content)
```

### 2. Node Schema Unification

**Challenge**: Visual nodes vs declarative nodes

**Current**:
- Visual: Introspected from Python classes
- Declarative: Defined in YAML with `type: llm/extract/transform/condition`

**Solution**: ConfigNode acts as universal adapter

```python
# In node_schema.py
def extract_config_node_schemas():
    """Extract schemas for ConfigNode types"""
    return {
        "llm": {
            "config_params": ["model", "prompt", "system_prompt"],
            "inputs": ["dynamic based on prompt {{variables}}"],
            "outputs": ["based on output_concept"],
        },
        "extract": {
            "config_params": ["field", "extractor_type"],
            ...
        },
        "transform": ...,
        "condition": ...,
        "parallel": ...,  # NEW!
    }
```

### 3. Validation Integration

**Challenge**: Keep validation logic in one place

**Solution**: Visual builder calls `kgraph validate` via API

```python
# api_server.py
@app.post("/api/workflows/validate")
async def validate_workflow(workflow: Dict[str, Any]):
    # Save to temp .kg.yaml file
    temp_path = save_temp_yaml(workflow)

    # Call kgraph validate
    result = await run_kgraph_cli("validate", temp_path)

    return {
        "valid": result.returncode == 0,
        "errors": parse_validation_errors(result.stderr)
    }
```

### 4. Execution Streaming

**Challenge**: Real-time execution updates in UI

**Already Built!**:
```python
# api_server.py (line 380-398)
@app.websocket("/ws/execute/{workflow_id}")
async def websocket_execute(websocket: WebSocket, workflow_id: str):
    await websocket.accept()

    # Stream execution events
    async for event in execute_workflow_stream(workflow_id):
        await websocket.send_json({
            "node_id": event.node_id,
            "status": event.status,  # pending/running/complete/error
            "shared_state": event.shared_state,
            "result": event.result
        })
```

---

## 🎨 User Experience Flow

### Scenario 1: Visual → Declarative

**User wants to**: Build workflow visually, then use in production via CLI

1. **Build in UI**: Drag IntentClarification → LeadResearcher → SubAgent
2. **Configure**: Set prompts, models, parameters
3. **Export**: Click "Export YAML"
4. **Receives**: `my_research.kg.yaml`
5. **Production use**:
   ```bash
   kgraph validate my_research.kg.yaml
   kgraph run my_research.kg.yaml --input query="quantum computing"
   ```

### Scenario 2: Declarative → Visual

**User wants to**: Edit existing YAML workflow visually

1. **Has**: `invoice_processing_domain.kg.yaml`
2. **Upload**: In UI, clicks "Import YAML"
3. **Visualizes**: Workflow appears on canvas
4. **Edit**: Add new node, change connections
5. **Export**: Updated YAML with changes

### Scenario 3: AI Builder (Future)

**User wants to**: Generate workflow from natural language

1. **Describe**: "Process support tickets by urgency, route to teams, generate responses"
2. **AI Generates**: Complete .kg.yaml with domain, concepts, workflows
3. **Load**: Into visual builder
4. **Refine**: User tweaks visually
5. **Deploy**: Export and run

---

## 📋 Implementation Checklist

### Phase 1: Connect Existing Pieces (2-3 weeks)

**Frontend** (React + ReactFlow)
- [ ] Set up ReactFlow canvas
- [ ] Implement node palette (from discovered workbooks)
- [ ] Drag-drop node placement
- [ ] Visual connections
- [ ] Config panel (auto-generated from schemas)
- [ ] Real-time execution visualization
- [ ] WebSocket integration

**Backend Integration**
- [ ] YAML export endpoint (visual → .kg.yaml)
- [ ] YAML import endpoint (.kg.yaml → visual)
- [ ] Validation API (calls `kgraph validate`)
- [ ] Execution API (calls workflow_loader.load_workflow())
- [ ] Domain support (multi-workflow files)

**Testing**
- [ ] Convert existing .kg.yaml examples to visual
- [ ] Export visual workflows to YAML
- [ ] Validate round-trip (YAML → Visual → YAML)

### Phase 2: Parallel Execution (1 week)

**Add to Declarative System**
- [ ] Implement ParallelConfigNode
- [ ] Add parallel: syntax to workflow_loader
- [ ] Example: parallel_extraction_example.kg.yaml
- [ ] Update schema system

**Add to Visual Builder**
- [ ] Parallel node type in palette
- [ ] Visual representation (parallel branches)
- [ ] Config panel for parallel operations

### Phase 3: AI Builder Integration (3-4 weeks)

**Backend**
- [ ] LLM integration for workflow generation
- [ ] Prompt engineering for high-quality workflows
- [ ] Concept inference from task description
- [ ] Validation of generated workflows

**Frontend**
- [ ] Natural language input
- [ ] Generation progress UI
- [ ] Preview generated workflow
- [ ] Edit/refine interface

### Phase 4: Polish & Features (2-3 weeks)

- [ ] Workflow templates library
- [ ] Version control integration
- [ ] Collaboration features
- [ ] Workflow marketplace (hub)
- [ ] Documentation generator
- [ ] Testing framework

---

## 🔧 Technical Decisions

### 1. Where Does Code Live?

**Decision**: Keep separation of concerns

```
KayGraph/                          # Main repo (framework)
├── kaygraph/                      # Core framework (zero deps)
├── workbooks/                     # Examples
│   └── kaygraph-declarative-workflows/  # CLI tool + patterns
│
Kaygraph-Playground/               # Separate repo (full-stack app)
├── backend/
│   ├── app/
│   │   ├── api/                   # REST + WebSocket APIs
│   │   ├── workflow_engine/       # Integration with kaygraph
│   │   └── schemas/               # Pydantic models
│   └── kaygraph/                  # Vendored or git submodule
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── WorkflowCanvas/    # ReactFlow
│   │   │   ├── NodePalette/       # Draggable nodes
│   │   │   └── ConfigPanel/       # Auto-generated forms
│   │   └── api/                   # Generated API client
```

**Why Separate?**:
- KayGraph = Framework (lightweight, zero deps, PyPI package)
- Playground = Application (full stack, batteries included)
- Users can use KayGraph without Playground
- Playground showcases what's possible

### 2. How to Share Code?

**Options**:
1. Git submodule (symlink-like)
2. Copy files (manual sync)
3. PyPI package (publish releases)

**Recommendation**: Start with #2 (copy), migrate to #3 (PyPI) when stable

### 3. File Formats

**Decision**: Support multiple formats

- `.kg.yaml` - KayGraph declarative workflows
- `.plx` - Pipelex-compatible (for ecosystem)
- `.json` - Visual builder internal format
- `.py` - Export to Python code

### 4. Validation Strategy

**Decision**: Single source of truth

```python
# All validation goes through workflow_loader.py
from kaygraph_declarative_workflows import validate_workflow

# Visual builder, CLI, and API all use same validator
```

---

## 🚀 Quick Win: Minimal Viable Builder

### What Can Be Built in 1 Week?

**Goal**: Prove the concept works

**Scope**:
1. Load one workbook (deep_research)
2. Display nodes in palette
3. Drag nodes to canvas
4. Connect 2-3 nodes
5. Export to YAML
6. Import YAML back
7. Validate workflow

**Result**: Demo video showing round-trip

---

## 💡 Key Insights from Research

### 1. Pipelex Parallel Execution

**What we learned**: Parallel operations are valuable and well-designed

**How to add to KayGraph**:
```yaml
steps:
  - node: parallel_extract
    type: parallel
    parallels:
      - node: extract_cv
        type: llm
        result: cv_text
      - node: extract_job
        type: llm
        result: job_text
```

**Value**: Performance boost for independent operations

### 2. Visual → Declarative is Natural

**Observation**: Visual builders make sense for exploration, YAML for production

**Pattern**:
- Rapid prototyping in UI
- Export to YAML for version control
- Run in production via CLI
- Edit YAML directly for fine-tuning

### 3. Schema System is Key

**Current**: node_schema.py already does most of the work

**Gap**: Need ConfigNode type schemas

**Solution**: Document the ConfigNode types as schemas

### 4. Bi-directional is Critical

**Must have**: Round-trip YAML ↔ Visual

**Why**: Users want flexibility to switch between modes

---

## 📊 Success Metrics

### MVP Success (1 week)

- [ ] Load 1 workbook into UI
- [ ] Drag 3 nodes to canvas
- [ ] Connect nodes
- [ ] Export to valid .kg.yaml
- [ ] Import same YAML back
- [ ] Visual matches original

### Beta Success (1 month)

- [ ] All 4 workbooks available
- [ ] All ConfigNode types supported
- [ ] Validation working
- [ ] Execution with real-time updates
- [ ] 5 users successfully build workflows

### Production Success (3 months)

- [ ] AI builder generating workflows
- [ ] Parallel execution implemented
- [ ] 50+ community workflows
- [ ] Documentation complete
- [ ] Deployed at kaygraph.com

---

## 🎯 Next Steps

### Immediate (This Session)

1. ✅ Complete declarative workflow patterns (DONE!)
2. ✅ Research Pipelex for additional patterns (DONE!)
3. ✅ Understand KayGraph Playground architecture (DONE!)
4. ✅ Create integration research doc (THIS!)

### Next Session

1. **Plan Parallel Execution** (Pattern 8 of 8)
   - ParallelConfigNode implementation
   - YAML syntax design
   - Example workflows
   - Update visual builder schemas

2. **Plan Visual Builder MVP**
   - Frontend tech stack confirmation
   - Backend API additions
   - YAML converter design
   - 1-week sprint plan

### Future Sessions

1. **Implement Parallel Execution** (~2 hours)
2. **Build Visual Builder MVP** (~1 week)
3. **AI Builder Integration** (~3-4 weeks)

---

## 🔗 Related Documents

**In This Repo**:
- `tasks/remaining-six-patterns/COMPLETED.md` - What we just built
- `tasks/pipelex-additional-analysis.md` - Pipelex feature comparison
- `workbooks/kaygraph-visualization/UI_INTEGRATION_GUIDE.md` - Visual builder design
- `workbooks/kaygraph-visualization/node_schema.py` - Auto-introspection system
- `workbooks/kaygraph-visualization/api_server.py` - Backend API

**In Playground Repo**:
- `/media/tmos-bumblebe/dev_dev/year25/oct25/Kaygraph-Playground/README.md`

---

## 💭 Open Questions for Discussion

1. **Should we add parallel execution now or after visual builder?**
   - Pro (now): Completes pattern set, easier to visualize later
   - Pro (later): Focus on visual builder, add parallel when needed

2. **Where should AI builder live?**
   - Option A: Integrated in Playground web app
   - Option B: Separate `kaygraph-ai` CLI tool
   - Option C: Both (CLI generates, web edits)

3. **How to handle workbook discovery?**
   - Current: Scan directories for workbook.json
   - Future: Database of registered workbooks?
   - Marketplace: Community-contributed workbooks?

4. **File format priority?**
   - Focus on .kg.yaml? (our format)
   - Also support .plx? (Pipelex compatibility)
   - Support both from day 1?

---

## ✅ Summary

**What We Have**:
- ✅ Declarative workflow system (7 of 8 patterns)
- ✅ Visual builder backend (node_schema.py, api_server.py)
- ✅ Full-stack template (KayGraph Playground)
- ✅ Clear architecture vision

**What We Need**:
- ❌ React frontend for visual builder
- ❌ YAML ↔ Visual converters
- ❌ Parallel execution (Pattern 8)
- ❌ AI builder integration

**The Path Forward**:
1. Add parallel execution → 100% pattern completion
2. Build visual builder MVP → Prove integration works
3. Add AI builder → Transform user experience
4. Launch marketplace → Community growth

**We're incredibly close to a transformative platform!** 🚀
