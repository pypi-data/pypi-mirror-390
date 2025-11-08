# Architectural Decisions

**Date**: 2025-11-01
**Status**: Approved

---

## Decision Summary

| Question | Choice | Rationale |
|----------|--------|-----------|
| **Visual Builder Scope** | **Advanced (Option B)** | Declarative system already supports branching, loops, parallel. No reason to limit UI. |
| **LLM Chat Interface** | **Simple Text Generation (Option A)** | Faster to build, works for MVP. Can add interactive dialog later. |
| **Testing Environment** | **Mock + Real Mode (Option C)** | Best of both worlds: fast iteration + accurate validation. |
| **Deployment Strategy** | **Playground-only (Option A)** | Focus on single implementation. Design is extensible for future standalone. |
| **Multi-tenancy** | **Private by Default (Option A)** | Secure, simple. Marketplace/sharing can be added later. |
| **Priority Order** | **Core → Backend → Frontend (Option A)** | Foundation-first approach ensures portability and clean architecture. |

---

## Decision Details

### 1. Visual Builder Scope: **Advanced (B)**

**Features to Support in v1**:
- ✅ Linear workflows (A → B → C)
- ✅ Branching (if/else conditions)
- ✅ Loops (batch processing with `batch_over`)
- ✅ Parallel execution (task parallelism with `parallels`)
- ✅ All 8 declarative patterns already implemented

**Node Types**:
- Input/Extract nodes
- LLM nodes
- Transform nodes
- Condition nodes (routing)
- Batch nodes
- Parallel nodes

**Visual Features**:
- Drag-drop from palette
- Edge connections (default + named actions)
- Node configuration panels
- Concept editor (inline schema definitions)
- Real-time YAML sync

**Rationale**: The declarative system already has full support. Limiting the UI would be artificial.

---

### 2. LLM Chat Interface: **Simple Text Generation (A)**

**Implementation**:
```
User: "Create a workflow that processes invoices..."

LLM Agent:
1. Generates complete .kg.yaml
2. Shows in split view (YAML + Visual preview)
3. User can edit either side
4. Test immediately
```

**Features**:
- Text input for workflow description
- LLM generates complete YAML
- Preview in visual editor
- Editable (user can refine)
- Save to database

**Not in v1** (can add later):
- Interactive Q&A dialog
- Step-by-step wizard
- Real-time visual updates during generation

**Rationale**: Fastest path to working prototype. Expert users prefer this approach.

---

### 3. Testing Environment: **Mock + Real Mode (C)**

**Mock Mode** (Development):
- Fast execution (~100ms)
- No external API calls
- Pre-defined responses for LLM nodes
- Good for UI development and logic testing

**Real Mode** (Production):
- Actual execution with real LLM calls
- Accurate results
- Full validation
- Use before deploying

**Implementation**:
```typescript
<TestPanel>
  <Toggle>
    <Option value="mock">Mock Mode (Fast)</Option>
    <Option value="real">Real Mode (Accurate)</Option>
  </Toggle>

  <ExecuteButton />
</TestPanel>
```

**Rationale**: Developers need fast feedback loops. Real mode validates before deployment.

---

### 4. Deployment Strategy: **Playground-only (A)**

**Architecture**:
```
Kaygraph-Playground (Full-Stack App)
├── Backend (FastAPI)
│   ├── Workflow storage (PostgreSQL)
│   ├── Execution engine
│   └── Export endpoints
├── Frontend (React + ReactFlow)
│   ├── Visual builder
│   ├── YAML editor
│   └── Test console
└── Multi-tenancy (Organization-based)
```

**Design for Future**:
- Visual builder components are modular
- Can be extracted to standalone package
- Clean separation: UI components vs. business logic

**Not in v1**:
- Standalone desktop app
- Embeddable web component
- Separate `kaygraph-visual-editor` package

**Rationale**: Focus on one excellent implementation. Easier to extract later than merge multiple implementations.

---

### 5. Multi-tenancy: **Private by Default (A)**

**Access Model**:
- Each workflow belongs to one organization
- Only org members can view/edit
- No cross-org visibility

**Database Schema**:
```python
class WorkflowDefinition(TenantModel):
    organization_id = fields.UUIDField(index=True)  # Required
    name = fields.CharField(max_length=255)
    yaml_content = fields.TextField()
    is_deployed = fields.BooleanField(default=False)
    # No public/shared flags in v1
```

**Not in v1** (future enhancements):
- Public workflow marketplace
- Community templates
- Import from library
- Workflow sharing across orgs

**Rationale**: Security first. Private workflows are essential. Public sharing is a feature, not requirement.

---

### 6. Priority Order: **Core → Backend → Frontend (A)**

**Phase 1: Core Package** (~6-8 hours)
1. Add `kaygraph/declarative/serializer.py`
2. Add `kaygraph/declarative/visual_converter.py`
3. Add export commands to CLI
4. Update `setup.py` for `[declarative]` extra
5. Write tests
6. Result: `pip install kaygraph[declarative]` works

**Phase 2: Backend API** (~8-10 hours)
1. Create Tortoise ORM models
2. Create migrations
3. Build CRUD endpoints
4. Build execution endpoint
5. Build export endpoints
6. Add CASBIN permissions
7. Write API tests
8. Result: Full REST API for workflows

**Phase 3: Frontend** (~12-15 hours)
1. Install ReactFlow dependencies
2. Create WorkflowCanvas component
3. Create NodePalette component
4. Build bidirectional sync (Visual ↔ YAML)
5. Add test console
6. Add export UI
7. Integration testing
8. Result: Complete visual workflow builder

**Total Estimate**: 26-33 hours

**Rationale**:
- Core package ensures portability from day 1
- Backend provides stable API for frontend
- Frontend is last layer, can iterate quickly
- Each phase is testable independently

---

## Implementation Order

```
Week 1: Core Package
├─ Day 1-2: Serialization (Graph → YAML)
├─ Day 3: Visual converter (ReactFlow ↔ YAML)
├─ Day 4: CLI export commands
└─ Day 5: Testing and documentation

Week 2: Backend
├─ Day 1: Database models + migrations
├─ Day 2: CRUD API endpoints
├─ Day 3: Execution engine integration
├─ Day 4: Export endpoints
└─ Day 5: Testing and permissions

Week 3: Frontend
├─ Day 1-2: ReactFlow canvas setup
├─ Day 3: Node palette and editing
├─ Day 4: Bidirectional sync
└─ Day 5: Test console and polish

Week 4: Integration & Polish
├─ Day 1-2: End-to-end testing
├─ Day 3: Documentation
├─ Day 4: Example workflows
└─ Day 5: User acceptance testing
```

---

## Success Metrics

After implementation:
- ✅ Core package published to PyPI
- ✅ `kgraph run workflow.kg.yaml` works standalone
- ✅ Backend API fully functional
- ✅ Visual builder operational
- ✅ All 3 creation modes work (chat, visual, YAML)
- ✅ Export works to all 3 targets (CLI, API, Claude Code)
- ✅ Test suite passing (>90% coverage)
- ✅ Documentation complete

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| ReactFlow learning curve | Use existing examples, start simple |
| Bidirectional sync complexity | YAML is source of truth, visual is view |
| Core package size | Strict limit: <3000 lines, focused scope |
| Multi-tenancy bugs | Comprehensive tests, code review |
| Performance issues | Mock mode for development, optimize later |

---

## Next Steps

1. ✅ Decisions finalized
2. → **Research existing patterns** (deep dive)
3. → Create comprehensive plan
4. → Begin implementation
