# Next Steps: Workflow Builder Implementation

**Date**: 2025-11-01
**Current Status**: Phase 1 Complete ✅

---

## Quick Summary

We've completed Phase 1 (Core Package) and created two essential guides:

1. **PUBLISHING_GUIDE.md** - How to publish kaygraph v0.1.0 to PyPI
2. **PLAYGROUND_SETUP.md** - How to set up a dedicated Playground instance

---

## Decision Point: Choose Your Path

### Option A: Publish Core Package First (Recommended)

**Pros**:
- Clean separation of core package release
- Backend can install via `pip install kaygraph>=0.1.0`
- Easier to test serialization in isolation
- Professional workflow (package first, then app)

**Cons**:
- Requires PyPI account/tokens
- Extra step before Phase 2

**Steps**:
1. Follow `PUBLISHING_GUIDE.md` to publish v0.1.0
2. Follow `PLAYGROUND_SETUP.md` to create new instance
3. Install published package in backend
4. Start Phase 2 implementation

### Option B: Use Local Package for Development

**Pros**:
- Faster to start Phase 2
- No PyPI setup needed
- Can iterate on core if needed

**Cons**:
- Must use editable install (`pip install -e /path/to/KayGraph`)
- Dependency management is manual
- Eventually need to publish anyway

**Steps**:
1. Follow `PLAYGROUND_SETUP.md` to create new instance
2. Install core with `pip install -e /media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph`
3. Start Phase 2 implementation
4. Publish later when ready

---

## Recommended Workflow

### Step 1: Publish Core Package (30-45 min)

Follow `PUBLISHING_GUIDE.md`:

```bash
cd /media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph

# 1. Update version
# Edit kaygraph/__init__.py: __version__ = "0.1.0"

# 2. Update setup.py (add PyYAML dependency)
# Already documented in guide

# 3. Build
python -m build

# 4. Test locally
python -m venv test_env
source test_env/bin/activate
pip install dist/kaygraph-0.1.0-py3-none-any.whl
python -c "from kaygraph.declarative import WorkflowSerializer; print('✓')"
deactivate
rm -rf test_env

# 5. Upload to TestPyPI (optional)
python -m twine upload --repository testpypi dist/*

# 6. Upload to PyPI
python -m twine upload dist/*

# 7. Tag release
git tag -a v0.1.0 -m "Release v0.1.0: Declarative Workflows Module"
git push origin v0.1.0
```

### Step 2: Set Up New Playground Instance (1-2 hours)

Follow `PLAYGROUND_SETUP.md`:

```bash
cd /media/tmos-bumblebe/dev_dev/year25/oct25/

# Create new directory
mkdir -p KayGraph-Workflow-Builder
cd KayGraph-Workflow-Builder

# Copy backend structure
mkdir -p backend/app/{api/routes,models,schemas,services,core,db/migrations}
cp ../Kaygraph-Playground/backend/pyproject.toml backend/
# ... (follow guide for all copies)

# Copy frontend structure
mkdir -p frontend/src/{components,hooks,routes,lib}
cp ../Kaygraph-Playground/frontend/package.json frontend/
# ... (follow guide)

# Docker setup
cp ../Kaygraph-Playground/docker-compose.yml .
# Edit ports: 5433 (postgres), 8001 (backend), 5174 (frontend)

# Environment
# Create .env file (guide has template)

# Copy task directory
cp -r ../KayGraph/workbooks/kaygraph-declarative-workflows/tasks .

# Create README and CLAUDE.md
# (Templates in guide)

# Initialize git
git init
git add .
git commit -m "Initial setup: Workflow Builder instance"
```

### Step 3: Install Dependencies

```bash
# Backend
cd backend
pip install -e .
pip install kaygraph>=0.1.0  # Published version

# Frontend
cd ../frontend
npm install

# Verify ReactFlow is installed
npm list @xyflow/react
# Should show: @xyflow/react@12.8.6
```

### Step 4: Start Phase 2 Implementation

Follow `plan.md` Phase 2 section:

```bash
cd /media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph-Workflow-Builder

# Create feature branch
git checkout -b phase2-backend-api

# Start with database models
# File: backend/app/models/workflow.py
# Follow plan.md for complete implementation
```

---

## Phase 2 Quick Reference

### Database Models to Create

**File**: `backend/app/models/workflow.py`

```python
from tortoise import fields, models

class WorkflowDefinition(models.Model):
    id = fields.UUIDField(pk=True)
    organization_id = fields.UUIDField()
    name = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    yaml_content = fields.TextField()  # The .kg.yaml file
    visual_layout = fields.JSONField(null=True)  # ReactFlow state
    version = fields.CharField(max_length=50, default="1.0.0")
    is_deployed = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "workflow_definitions"
        unique_together = (("organization_id", "name"),)

class WorkflowExecution(models.Model):
    id = fields.UUIDField(pk=True)
    workflow = fields.ForeignKeyField("models.WorkflowDefinition", related_name="executions")
    input_data = fields.JSONField()
    output_data = fields.JSONField(null=True)
    status = fields.CharField(max_length=50)  # pending, running, success, error
    execution_mode = fields.CharField(max_length=20, default="real")  # mock or real
    started_at = fields.DatetimeField(auto_now_add=True)
    completed_at = fields.DatetimeField(null=True)
    error_message = fields.TextField(null=True)

    class Meta:
        table = "workflow_executions"
```

### API Endpoints to Create

**File**: `backend/app/api/routes/workflows.py`

```python
from fastapi import APIRouter, Depends
from app.schemas.workflow import WorkflowCreate, WorkflowPublic

router = APIRouter()

@router.post("/", response_model=WorkflowPublic)
async def create_workflow(workflow: WorkflowCreate, user: CurrentUser):
    # Implementation in plan.md
    pass

@router.get("/{workflow_id}", response_model=WorkflowPublic)
async def get_workflow(workflow_id: UUID, user: CurrentUser):
    # Implementation in plan.md
    pass

@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: UUID, execution: ExecutionCreate):
    # Implementation in plan.md
    pass

# ... more endpoints in plan.md
```

### Frontend Components to Create

**File**: `frontend/src/components/WorkflowBuilder/WorkflowCanvas.tsx`

```typescript
import { ReactFlow, Background, Controls } from '@xyflow/react'
import { useWorkflowBuilder } from '@/hooks/useWorkflowBuilder'

export function WorkflowCanvas({ initialCanvas, onSave }) {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect } =
    useWorkflowBuilder(initialCanvas)

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onConnect={onConnect}
    >
      <Background />
      <Controls />
    </ReactFlow>
  )
}

// Full implementation in plan.md
```

---

## Task Checklist

### Immediate Tasks (Today)

- [ ] **Decision**: Choose Option A (publish) or Option B (local dev)
- [ ] If Option A: Follow PUBLISHING_GUIDE.md (30-45 min)
- [ ] Follow PLAYGROUND_SETUP.md to create new instance (1-2 hours)
- [ ] Install dependencies in new instance
- [ ] Verify setup (imports work, servers start)

### Phase 2 Tasks (Next 8-10 hours)

- [ ] Create database models (WorkflowDefinition, WorkflowExecution)
- [ ] Generate and run migrations
- [ ] Create Pydantic schemas
- [ ] Build CRUD API endpoints
- [ ] Implement workflow runner service
- [ ] Add RBAC integration
- [ ] Write API tests
- [ ] Test end-to-end: Create → Save → Execute → Export

### Phase 3 Tasks (After Phase 2, 12-15 hours)

- [ ] Install frontend dependencies (js-yaml, monaco-editor)
- [ ] Create WorkflowCanvas component
- [ ] Create NodePalette component
- [ ] Create NodeEditor component
- [ ] Implement useWorkflowBuilder hook
- [ ] Implement useYAMLSync hook
- [ ] Create workflow routes
- [ ] Build test console
- [ ] Integration testing

---

## Key Files Reference

### Documentation

| File | Purpose | Location |
|------|---------|----------|
| PUBLISHING_GUIDE.md | Publish kaygraph v0.1.0 | `tasks/.../PUBLISHING_GUIDE.md` |
| PLAYGROUND_SETUP.md | Setup new instance | `tasks/.../PLAYGROUND_SETUP.md` |
| plan.md | Complete implementation plan | `tasks/.../plan.md` |
| PHASE1_COMPLETE.md | Phase 1 summary | `tasks/.../PHASE1_COMPLETE.md` |
| research.md | Existing patterns analysis | `tasks/.../research.md` |
| decisions.md | Architecture decisions | `tasks/.../decisions.md` |

### Code (Phase 1 - Complete)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| kaygraph/declarative/serializer.py | Domain → YAML | 380 | ✅ |
| kaygraph/declarative/visual_converter.py | ReactFlow ↔ YAML | 446 | ✅ |
| domain.py | Added serialization | +90 | ✅ |
| cli.py | Added export command | +95 | ✅ |
| test_serialization.py | Test suite | 348 | ✅ |

### Code (Phase 2 - To Do)

| File | Purpose | Lines | Status |
|------|---------|-------|--------|
| backend/app/models/workflow.py | Database models | ~150 | ⏳ |
| backend/app/schemas/workflow.py | Pydantic schemas | ~120 | ⏳ |
| backend/app/api/routes/workflows.py | API endpoints | ~300 | ⏳ |
| backend/app/services/workflow_runner.py | Execution service | ~200 | ⏳ |

---

## Success Metrics

### Phase 1 (Complete) ✅
- ✅ 8/8 tests passing
- ✅ Serialization works bidirectionally
- ✅ CLI export functional
- ✅ 1,359 lines of production code

### Phase 2 (Target)
- 🎯 All API endpoints working
- 🎯 Database persisting workflows
- 🎯 Mock + Real execution modes
- 🎯 Multi-tenant isolation
- 🎯 Export generates valid `.kg.yaml`

### Phase 3 (Target)
- 🎯 Visual workflow editor functional
- 🎯 Bidirectional YAML ↔ Visual sync
- 🎯 Test console executes workflows
- 🎯 No data loss in round-trip conversion

---

## Questions to Consider

Before proceeding, consider:

1. **Do you have PyPI credentials?**
   - If yes → Option A (publish first)
   - If no → Option B (local dev) or get credentials

2. **Timeline preference?**
   - Want to ship fast → Option B (skip publishing for now)
   - Want clean release → Option A (publish properly)

3. **Team access?**
   - Solo project → Either option works
   - Team project → Option A (published package) is better

4. **Existing Playground usage?**
   - Still using it → Definitely create new instance
   - Not using it → Could potentially modify existing

---

## Contact Points

If you have questions during implementation:

- **Publishing issues**: Check `PUBLISHING_GUIDE.md` troubleshooting section
- **Setup issues**: Check `PLAYGROUND_SETUP.md` troubleshooting section
- **Implementation questions**: Refer to `plan.md` with code examples
- **Architecture questions**: Check `research.md` and `decisions.md`

---

## Final Recommendation

**Recommended Path for Professional Development**:

1. ✅ **Today**: Follow `PUBLISHING_GUIDE.md` → Publish kaygraph v0.1.0
2. ✅ **Today**: Follow `PLAYGROUND_SETUP.md` → Create clean instance
3. ✅ **Tomorrow**: Start Phase 2 → Database models first
4. ✅ **This Week**: Complete Phase 2 → Full backend API
5. ✅ **Next Week**: Complete Phase 3 → Visual editor

**Total Time Estimate**:
- Publishing: 30-45 min
- Setup: 1-2 hours
- Phase 2: 8-10 hours
- Phase 3: 12-15 hours
- **Total: ~23-28 hours** (achievable in 1-2 weeks)

Good luck! 🚀
