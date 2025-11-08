# Playground Setup Guide: Workflow Builder Instance

**Date**: 2025-11-01
**Purpose**: Set up a dedicated Playground instance for the Declarative Visual Workflow Builder

---

## Overview

This guide explains how to create a fresh Playground instance for implementing Phase 2 (Backend API) and Phase 3 (Frontend UI) of the Workflow Builder project.

**Why a New Instance?**
- Clean separation from the existing `/media/tmos-bumblebe/dev_dev/year25/oct25/Kaygraph-Playground`
- Dedicated database and configuration for workflow builder
- Can be version controlled separately
- Easy to deploy independently

---

## Directory Structure Plan

```
/media/tmos-bumblebe/dev_dev/year25/oct25/
├── KayGraph/                          (core package - don't modify for Phase 2/3)
├── Kaygraph-Playground/               (existing - don't modify)
└── KayGraph-Workflow-Builder/        (NEW - our dedicated instance)
    ├── backend/
    │   ├── app/
    │   │   ├── api/
    │   │   │   └── routes/
    │   │   │       └── workflows.py    (NEW - our endpoints)
    │   │   ├── models/
    │   │   │   └── workflow.py         (NEW - our models)
    │   │   ├── schemas/
    │   │   │   └── workflow.py         (NEW - our schemas)
    │   │   ├── services/
    │   │   │   └── workflow_runner.py  (NEW - execution service)
    │   │   └── core/
    │   │       ├── config.py
    │   │       └── database.py
    │   ├── pyproject.toml
    │   └── ...
    ├── frontend/
    │   ├── src/
    │   │   ├── components/
    │   │   │   └── WorkflowBuilder/    (NEW - our components)
    │   │   ├── hooks/
    │   │   │   └── useWorkflowBuilder.ts  (NEW)
    │   │   └── routes/
    │   │       └── _layout/
    │   │           └── workflows/       (NEW - our routes)
    │   ├── package.json
    │   └── ...
    ├── .env
    ├── docker-compose.yml
    ├── CLAUDE.md
    └── README.md
```

---

## Setup Steps

### Step 1: Identify Template Source

We'll use the existing Playground as a template, but create a minimal copy with only what we need.

**Key Directories to Copy**:
```bash
Kaygraph-Playground/
├── backend/              (Copy structure, not all files)
├── frontend/             (Copy structure, not all files)
├── docker-compose.yml    (Copy and customize)
├── .env-templates/       (Copy)
├── scripts/              (Copy development scripts)
└── docs/                 (Reference, don't copy)
```

### Step 2: Create New Instance

```bash
# Navigate to parent directory
cd /media/tmos-bumblebe/dev_dev/year25/oct25/

# Create new directory
mkdir -p KayGraph-Workflow-Builder
cd KayGraph-Workflow-Builder

# Initialize git
git init
```

### Step 3: Copy Backend Structure

```bash
# Copy backend directory structure
mkdir -p backend/app/{api/routes,models,schemas,services,core,db/migrations}

# Copy essential backend files
cp ../Kaygraph-Playground/backend/pyproject.toml backend/
cp ../Kaygraph-Playground/backend/app/core/config.py backend/app/core/
cp ../Kaygraph-Playground/backend/app/core/database.py backend/app/core/
cp ../Kaygraph-Playground/backend/app/main.py backend/app/

# Copy migration setup
cp -r ../Kaygraph-Playground/backend/app/db/migrations backend/app/db/
```

**Edit `backend/pyproject.toml`** to add our dependencies:

```toml
[project]
name = "kaygraph-workflow-builder-backend"
version = "0.1.0"
description = "Backend API for KayGraph Workflow Builder"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.110.0",
    "uvicorn[standard]>=0.27.1",
    "tortoise-orm[asyncpg]>=0.20.0",
    "aerich>=0.7.2",
    "pydantic>=2.6.1",
    "pydantic-settings>=2.1.0",
    "casbin>=1.36.0",
    "pycasbin-async-sqlalchemy-adapter>=0.4.4",
    "python-multipart>=0.0.9",
    "python-jose[cryptography]>=3.3.0",
    "passlib[bcrypt]>=1.7.4",
    "pyyaml>=6.0",          # For YAML workflows
    "kaygraph>=0.1.0",      # Our core package with declarative module
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.5",
    "httpx>=0.26.0",
]
```

### Step 4: Copy Frontend Structure

```bash
# Copy frontend directory structure
mkdir -p frontend/src/{components,hooks,routes,lib}

# Copy essential frontend files
cp ../Kaygraph-Playground/frontend/package.json frontend/
cp ../Kaygraph-Playground/frontend/vite.config.ts frontend/
cp ../Kaygraph-Playground/frontend/tsconfig.json frontend/
cp ../Kaygraph-Playground/frontend/index.html frontend/

# Copy Chakra UI setup
cp ../Kaygraph-Playground/frontend/src/main.tsx frontend/src/
cp ../Kaygraph-Playground/frontend/src/theme.ts frontend/src/
```

**Edit `frontend/package.json`** - verify these are already included:

```json
{
  "name": "kaygraph-workflow-builder-frontend",
  "version": "0.1.0",
  "dependencies": {
    "@chakra-ui/react": "^3.8.0",
    "@xyflow/react": "^12.8.6",
    "@tanstack/react-query": "^5.28.14",
    "@tanstack/react-router": "1.19.1",
    "js-yaml": "^4.1.0",
    "@monaco-editor/react": "^4.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/js-yaml": "^4.0.9",
    "typescript": "^5.3.3",
    "vite": "^5.0.0",
    "@vitejs/plugin-react": "^4.2.0"
  }
}
```

### Step 5: Docker Setup

Copy and customize docker-compose.yml:

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: workflow_builder
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5433:5432"  # Different port to avoid conflicts
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8001:8000"  # Different port to avoid conflicts
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/workflow_builder
      ENVIRONMENT: development
    volumes:
      - ./backend:/app
    depends_on:
      - postgres
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5174:5173"  # Different port to avoid conflicts
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      VITE_API_URL: http://localhost:8001
    command: npm run dev

volumes:
  postgres_data:
```

### Step 6: Environment Configuration

Create `.env` file:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5433/workflow_builder

# API
API_V1_STR=/api/v1
PROJECT_NAME="KayGraph Workflow Builder"
BACKEND_CORS_ORIGINS=["http://localhost:5174"]

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENVIRONMENT=development
```

### Step 7: Create Project README

```markdown
# KayGraph Workflow Builder

Declarative visual workflow builder for KayGraph.

## Features

- Visual workflow editor with ReactFlow
- Declarative YAML workflow definitions
- Mock and real execution modes
- Export to portable `.kg.yaml` format
- Multi-tenant with organization isolation

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose

### Setup

1. **Clone and setup**:
   ```bash
   cd backend
   pip install -e .

   cd ../frontend
   npm install
   ```

2. **Start services**:
   ```bash
   docker-compose up -d postgres
   ```

3. **Run migrations**:
   ```bash
   cd backend
   aerich init -t app.core.database.TORTOISE_ORM
   aerich init-db
   ```

4. **Start development servers**:

   Terminal 1 (Backend):
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8001
   ```

   Terminal 2 (Frontend):
   ```bash
   cd frontend
   npm run dev
   ```

5. **Access**:
   - Frontend: http://localhost:5174
   - Backend API: http://localhost:8001
   - API Docs: http://localhost:8001/docs

## Project Structure

See [plan.md](./tasks/declarative-visual-workflow-builder/plan.md) for comprehensive implementation plan.

## Development

### Backend

- FastAPI + Tortoise ORM
- PostgreSQL database
- CASBIN RBAC
- Workflow execution service

### Frontend

- React + TypeScript
- Chakra UI components
- ReactFlow for visual editor
- TanStack Router + Query

## Documentation

- [Implementation Plan](./tasks/declarative-visual-workflow-builder/plan.md)
- [Phase 1 Summary](./tasks/declarative-visual-workflow-builder/PHASE1_COMPLETE.md)
- [Publishing Guide](./tasks/declarative-visual-workflow-builder/PUBLISHING_GUIDE.md)

## License

MIT
```

### Step 8: Create CLAUDE.md

```markdown
# CLAUDE.md

Project-specific instructions for Claude Code when working on the Workflow Builder.

## Project Overview

This is a dedicated instance of Kaygraph-Playground for building the Declarative Visual Workflow Builder.

**DO NOT** modify files in:
- `/media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph/` (core package)
- `/media/tmos-bumblebe/dev_dev/year25/oct25/Kaygraph-Playground/` (original playground)

**Work in**: `/media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph-Workflow-Builder/`

## Implementation Plan

Follow the comprehensive plan at:
`./tasks/declarative-visual-workflow-builder/plan.md`

## Current Phase

**Phase 2: Backend API** (8-10 hours estimated)

Tasks:
1. Create database models (WorkflowDefinition, WorkflowExecution)
2. Build CRUD API endpoints
3. Implement workflow runner service
4. Add RBAC integration
5. Write tests

## Key Dependencies

- Core package: `kaygraph>=0.1.0` (with declarative module)
- Serialization already available via `from kaygraph.declarative import WorkflowSerializer`
- Use existing `Domain` class from core for workflow loading

## Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Architecture

See research.md and plan.md in tasks/ directory for:
- Existing patterns analysis
- Complete implementation specifications
- Database schemas
- API endpoint designs
- React component structure
```

---

## Verification Checklist

After setup, verify:

- [ ] New directory created: `KayGraph-Workflow-Builder/`
- [ ] Git initialized
- [ ] Backend structure copied
- [ ] Frontend structure copied
- [ ] `docker-compose.yml` customized (different ports)
- [ ] `.env` file created
- [ ] README.md created
- [ ] CLAUDE.md created
- [ ] Dependencies installable (`pip install -e .` in backend)
- [ ] Dependencies installable (`npm install` in frontend)
- [ ] PostgreSQL starts on port 5433
- [ ] No conflicts with existing Playground

---

## Alternative: Use Copier Template

If the Kaygraph-Playground has copier.yml, you could use it:

```bash
# Install copier
pip install copier

# Create from template
copier copy /media/tmos-bumblebe/dev_dev/year25/oct25/Kaygraph-Playground KayGraph-Workflow-Builder

# Answer prompts:
# - Project name: kaygraph-workflow-builder
# - Database name: workflow_builder
# - Ports: Backend 8001, Frontend 5174, Postgres 5433
```

However, **manual copy is recommended** for this project because:
1. We need specific customizations
2. We want minimal bloat
3. We're familiar with the structure already

---

## Next Steps After Setup

1. **Copy Task Directory**:
   ```bash
   cp -r ../KayGraph/workbooks/kaygraph-declarative-workflows/tasks KayGraph-Workflow-Builder/
   ```

2. **Install Core Package** (with declarative support):
   ```bash
   cd backend
   pip install kaygraph>=0.1.0
   ```

3. **Start Phase 2 Implementation**:
   - Follow `tasks/declarative-visual-workflow-builder/plan.md`
   - Begin with database models

4. **Create Development Branch**:
   ```bash
   git checkout -b phase2-backend-api
   ```

---

## Maintenance

### Updating from Playground Template

If the original Playground gets updates you want:

```bash
# Cherry-pick specific improvements
cp ../Kaygraph-Playground/backend/app/core/some_new_file.py backend/app/core/

# Or merge if both are git repos:
git remote add template ../Kaygraph-Playground
git fetch template
git cherry-pick <commit-hash>
```

### Syncing Core Package Changes

When KayGraph core updates:

```bash
cd backend
pip install --upgrade kaygraph
```

---

## Troubleshooting

### Port Conflicts

If ports are already in use:

```bash
# Check what's using the port
lsof -i :5433  # Postgres
lsof -i :8001  # Backend
lsof -i :5174  # Frontend

# Kill or change ports in docker-compose.yml
```

### Database Connection Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres

# Re-run migrations
cd backend
aerich upgrade
```

### Import Errors

```bash
# Verify kaygraph installed
pip list | grep kaygraph

# Reinstall
pip install --force-reinstall kaygraph>=0.1.0
```

---

## Resources

- Original Playground: `/media/tmos-bumblebe/dev_dev/year25/oct25/Kaygraph-Playground`
- Core Package: `/media/tmos-bumblebe/dev_dev/year25/oct25/KayGraph`
- Implementation Plan: `./tasks/declarative-visual-workflow-builder/plan.md`
- Playground CLAUDE.md: For reference on existing patterns
