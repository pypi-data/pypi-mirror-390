# Task: Declarative Visual Workflow Builder

**Task ID**: `declarative-visual-workflow-builder`
**Created**: 2025-11-01
**Status**: Research Phase

---

## Goal

Build a complete system where users can create KayGraph workflows through multiple interfaces (chat, visual, YAML) and deploy them as portable, executable artifacts across different environments (CLI, FastAPI endpoints, Claude Code agents).

---

## User Requirements

### Primary Objectives

1. **Three Creation Modes**:
   - Chat with LLM to generate workflows
   - Visual canvas (drag-drop nodes)
   - Direct YAML editing

2. **Test in Browser**:
   - Execute workflows in Playground UI
   - See results immediately
   - Iterate quickly

3. **Export/Deploy**:
   - CLI tool: `kgraph run workflow.kg.yaml`
   - FastAPI endpoint: `POST /api/agents/{workflow_name}`
   - Claude Code integration: Documentation + executable workflow

4. **Portability**:
   - Create in Playground → Export → Run anywhere
   - Write locally → Import to Playground
   - Version control workflows as YAML files

### Key Requirements

- **Bidirectional**: Visual ↔ YAML ↔ Execution
- **Universal Format**: One `.kg.yaml` works everywhere
- **Multi-tenant**: Organization-based isolation in Playground
- **Type-safe**: Concept validation, input/output schemas
- **Testable**: Run/debug in UI before deploying
- **Documented**: Auto-generate docs for Claude Code

---

## Architecture Decisions

### Core Package (KayGraph)
- Add `kaygraph.declarative` package with serialization
- CLI tool: `kgraph validate/run/list/export`
- Zero extra dependencies (YAML/JSON only)

### Playground (Full-Stack App)
- Backend: Dynamic workflow executor endpoint
- Frontend: ReactFlow visual builder
- Database: Store workflows as YAML + visual layout
- Multi-tenancy: Organization-scoped workflows

### Deployment Targets
1. **CLI**: Standalone execution via `kgraph`
2. **FastAPI**: Dynamic endpoint `/api/agents/{name}`
3. **Claude Code**: Exported `.kg.yaml` + documentation

---

## Context Files

This task will produce:
- `research.md` - Existing patterns, technologies, decisions
- `plan.md` - Comprehensive implementation plan
- `implementation-log.md` - Progress tracking during build
- `questions.md` - Ambiguities and clarifications needed

---

## Success Criteria

- [ ] User can chat with LLM to generate workflow
- [ ] User can visually build workflow (drag-drop)
- [ ] User can edit YAML directly
- [ ] All three modes stay synchronized
- [ ] User can test workflow in browser
- [ ] User can export as `.kg.yaml` file
- [ ] Exported workflow runs via CLI: `kgraph run workflow.kg.yaml`
- [ ] Workflow can be deployed as FastAPI endpoint
- [ ] Workflow includes Claude Code documentation
- [ ] Core package is clean (<3000 lines added)
- [ ] All tests pass

---

## Next Steps

1. **Research Phase**:
   - Existing declarative workflow patterns (already implemented)
   - ReactFlow integration patterns
   - FastAPI dynamic endpoint patterns
   - Serialization strategies
   - Claude Code integration approaches

2. **Planning Phase**:
   - Complete DSL specification
   - Database schema design
   - API endpoints design
   - Frontend component architecture
   - Export format specifications

3. **Implementation Phase**:
   - Core package: Add serialization
   - Backend: Models, API, executor
   - Frontend: ReactFlow canvas
   - Integration: Test end-to-end
   - Documentation: Guides and examples
