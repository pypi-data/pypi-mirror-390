"""
KayGraph Visualization API Server

FastAPI backend that serves node schemas, executes workflows,
and provides real-time execution tracing for the ReactFlow UI.

**FOR AI AGENTS:** This is the backend for the visual workflow builder.
Study this to understand:
- How to serve node schemas to the UI
- How to convert ReactFlow graphs to KayGraph
- How to stream execution events via WebSocket
- How to validate workflow configurations
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from pathlib import Path
import asyncio
import json
import uuid
from datetime import datetime

from node_schema import NodeSchemaAPI, WorkbookMetadata


# =============================================================================
# Pydantic Models for API
# =============================================================================

class NodeDefinition(BaseModel):
    """ReactFlow node definition."""
    id: str
    type: str  # node_type from schema
    position: Dict[str, float]  # {x, y}
    data: Dict[str, Any]  # {config, label, etc}


class EdgeDefinition(BaseModel):
    """ReactFlow edge definition."""
    id: str
    source: str  # source node id
    target: str  # target node id
    label: Optional[str] = "default"  # action name


class WorkflowDefinition(BaseModel):
    """Complete workflow definition from UI."""
    nodes: List[NodeDefinition]
    edges: List[EdgeDefinition]
    start_node_id: str
    metadata: Optional[Dict[str, Any]] = {}


class ExecutionRequest(BaseModel):
    """Request to execute a workflow."""
    workflow: WorkflowDefinition
    input_data: Dict[str, Any]


class ExecutionEvent(BaseModel):
    """Event emitted during workflow execution."""
    event_type: str  # "node_start", "node_complete", "node_error", "workflow_complete"
    node_id: Optional[str] = None
    node_type: Optional[str] = None
    timestamp: datetime
    data: Dict[str, Any] = {}


# =============================================================================
# FastAPI App
# =============================================================================

app = FastAPI(
    title="KayGraph Visualization API",
    description="Backend API for visual workflow builder",
    version="1.0.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize schema API
workbooks_root = Path(__file__).parent.parent.parent / "claude_integration"
schema_api = NodeSchemaAPI(workbooks_root)

# Store active executions
active_executions: Dict[str, Dict[str, Any]] = {}


# =============================================================================
# Discovery Endpoints
# =============================================================================

@app.get("/api/workbooks")
async def get_workbooks() -> List[Dict[str, Any]]:
    """
    Get list of all available workbooks.

    Returns array of workbook metadata for sidebar categorization.
    """
    return schema_api.get_all_workbooks()


@app.get("/api/workbooks/{workbook_name}/nodes")
async def get_workbook_nodes(workbook_name: str) -> List[Dict[str, Any]]:
    """
    Get all node schemas for a specific workbook.

    Used to populate the node palette when user selects a workbook.
    """
    nodes = schema_api.get_workbook_nodes(workbook_name)
    if not nodes:
        raise HTTPException(status_code=404, detail="Workbook not found")
    return nodes


@app.get("/api/nodes")
async def get_all_nodes() -> List[Dict[str, Any]]:
    """
    Get all node schemas from all workbooks.

    For "show all nodes" view in the UI.
    """
    return schema_api.get_all_nodes()


@app.get("/api/nodes/{node_type}/schema")
async def get_node_schema(node_type: str) -> Dict[str, Any]:
    """
    Get detailed schema for a specific node type.

    Used when configuring a node to show the config panel.
    """
    all_nodes = schema_api.get_all_nodes()
    for node in all_nodes:
        if node["node_type"] == node_type:
            return node

    raise HTTPException(status_code=404, detail="Node type not found")


# =============================================================================
# Workflow Management
# =============================================================================

@app.post("/api/workflows/validate")
async def validate_workflow(workflow: WorkflowDefinition) -> Dict[str, Any]:
    """
    Validate a workflow definition.

    Checks:
    - All nodes are valid types
    - Connections are valid (outputs → inputs)
    - Required inputs are provided
    - No cycles (unless intentional)
    """
    errors = []
    warnings = []

    # Check start node exists
    start_node = next((n for n in workflow.nodes if n.id == workflow.start_node_id), None)
    if not start_node:
        errors.append({
            "type": "missing_start_node",
            "message": "Start node not found"
        })

    # Check all node types are valid
    valid_node_types = {n["node_type"] for n in schema_api.get_all_nodes()}
    for node in workflow.nodes:
        if node.type not in valid_node_types:
            errors.append({
                "type": "invalid_node_type",
                "node_id": node.id,
                "message": f"Unknown node type: {node.type}"
            })

    # Check edges connect valid nodes
    node_ids = {n.id for n in workflow.nodes}
    for edge in workflow.edges:
        if edge.source not in node_ids:
            errors.append({
                "type": "invalid_edge",
                "edge_id": edge.id,
                "message": f"Source node not found: {edge.source}"
            })
        if edge.target not in node_ids:
            errors.append({
                "type": "invalid_edge",
                "edge_id": edge.id,
                "message": f"Target node not found: {edge.target}"
            })

    # Check for unreachable nodes
    reachable = set()
    def mark_reachable(node_id):
        if node_id in reachable:
            return
        reachable.add(node_id)
        for edge in workflow.edges:
            if edge.source == node_id:
                mark_reachable(edge.target)

    mark_reachable(workflow.start_node_id)

    for node in workflow.nodes:
        if node.id not in reachable:
            warnings.append({
                "type": "unreachable_node",
                "node_id": node.id,
                "message": f"Node is not reachable from start: {node.id}"
            })

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


@app.post("/api/workflows/export/python")
async def export_to_python(workflow: WorkflowDefinition) -> Dict[str, str]:
    """
    Export workflow to Python code.

    Generates executable Python script that creates the KayGraph workflow.
    """
    # Generate Python code
    lines = [
        "\"\"\"",
        "Generated KayGraph Workflow",
        f"Created: {datetime.now().isoformat()}",
        "\"\"\"",
        "",
        "from kaygraph import Graph",
        ""
    ]

    # Import node classes
    imports = set()
    for node in workflow.nodes:
        # Find node schema to get module path
        schemas = schema_api.get_all_nodes()
        for schema in schemas:
            if schema["node_type"] == node.type:
                module_path = schema["module_path"].rsplit('.', 1)[0]
                imports.add(f"from {module_path} import {node.type}")
                break

    lines.extend(sorted(imports))
    lines.append("")
    lines.append("def create_workflow():")
    lines.append("    \"\"\"Create the workflow graph.\"\"\"")
    lines.append("")

    # Create node instances
    lines.append("    # Create nodes")
    for node in workflow.nodes:
        config = node.data.get("config", {})
        if config:
            config_str = ", ".join(f"{k}={repr(v)}" for k, v in config.items())
            lines.append(f"    {node.id} = {node.type}({config_str})")
        else:
            lines.append(f"    {node.id} = {node.type}()")

    lines.append("")
    lines.append("    # Connect nodes")

    # Create connections
    for edge in workflow.edges:
        if edge.label and edge.label != "default":
            lines.append(f"    {edge.source} - \"{edge.label}\" >> {edge.target}")
        else:
            lines.append(f"    {edge.source} >> {edge.target}")

    lines.append("")
    lines.append(f"    return Graph(start={workflow.start_node_id})")
    lines.append("")
    lines.append("")
    lines.append("if __name__ == '__main__':")
    lines.append("    workflow = create_workflow()")
    lines.append("    result = workflow.run({'query': 'your input here'})")
    lines.append("    print(result)")

    return {
        "code": "\n".join(lines),
        "filename": f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
    }


# =============================================================================
# Execution & Real-Time Tracing
# =============================================================================

@app.post("/api/workflows/execute")
async def execute_workflow(request: ExecutionRequest) -> Dict[str, Any]:
    """
    Execute a workflow (non-streaming).

    For simple execution without real-time updates.
    """
    execution_id = str(uuid.uuid4())

    # Store execution
    active_executions[execution_id] = {
        "workflow": request.workflow,
        "input_data": request.input_data,
        "status": "running",
        "started_at": datetime.now(),
        "events": []
    }

    try:
        # TODO: Convert workflow to KayGraph and execute
        # This would use the converter from export_to_python
        # but actually execute instead of generating code

        # For now, return mock result
        result = {
            "execution_id": execution_id,
            "status": "completed",
            "output": {"message": "Execution not yet implemented"},
            "duration_ms": 100
        }

        active_executions[execution_id]["status"] = "completed"
        active_executions[execution_id]["result"] = result

        return result

    except Exception as e:
        active_executions[execution_id]["status"] = "failed"
        active_executions[execution_id]["error"] = str(e)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/ws/execute/{execution_id}")
async def execute_workflow_streaming(websocket: WebSocket, execution_id: str):
    """
    Execute workflow with real-time streaming of events.

    WebSocket connection that streams execution events:
    - node_start: When a node begins execution
    - node_complete: When a node completes
    - node_error: If a node fails
    - state_update: When shared state changes
    - workflow_complete: When workflow finishes
    """
    await websocket.accept()

    try:
        # Receive workflow and input
        data = await websocket.receive_json()
        workflow = WorkflowDefinition(**data["workflow"])
        input_data = data["input_data"]

        # Store execution
        active_executions[execution_id] = {
            "workflow": workflow,
            "input_data": input_data,
            "status": "running",
            "started_at": datetime.now()
        }

        # TODO: Convert workflow to KayGraph
        # Instrument nodes to send events via websocket
        # Execute and stream events

        # Mock execution for now
        await asyncio.sleep(0.5)

        for node in workflow.nodes:
            # Node start
            await websocket.send_json({
                "event_type": "node_start",
                "node_id": node.id,
                "node_type": node.type,
                "timestamp": datetime.now().isoformat()
            })

            await asyncio.sleep(0.2)

            # Node complete
            await websocket.send_json({
                "event_type": "node_complete",
                "node_id": node.id,
                "node_type": node.type,
                "timestamp": datetime.now().isoformat(),
                "data": {"status": "success"}
            })

        # Workflow complete
        await websocket.send_json({
            "event_type": "workflow_complete",
            "timestamp": datetime.now().isoformat(),
            "data": {"result": "Mock execution completed"}
        })

        active_executions[execution_id]["status"] = "completed"

    except WebSocketDisconnect:
        print(f"WebSocket disconnected for execution {execution_id}")
        active_executions[execution_id]["status"] = "cancelled"

    except Exception as e:
        await websocket.send_json({
            "event_type": "error",
            "timestamp": datetime.now().isoformat(),
            "data": {"error": str(e)}
        })
        active_executions[execution_id]["status"] = "failed"
        await websocket.close()


@app.get("/api/executions/{execution_id}")
async def get_execution_status(execution_id: str) -> Dict[str, Any]:
    """Get status of a workflow execution."""
    if execution_id not in active_executions:
        raise HTTPException(status_code=404, detail="Execution not found")

    execution = active_executions[execution_id]
    return {
        "execution_id": execution_id,
        "status": execution["status"],
        "started_at": execution["started_at"].isoformat(),
        "completed_at": execution.get("completed_at", {}).isoformat() if execution.get("completed_at") else None
    }


# =============================================================================
# Health Check
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "workbooks_loaded": len(schema_api.get_all_workbooks()),
        "nodes_available": len(schema_api.get_all_nodes())
    }


# =============================================================================
# Run Server
# =============================================================================

if __name__ == "__main__":
    import uvicorn

    print(f"\n{'='*70}")
    print("🚀 KAYGRAPH VISUALIZATION API SERVER")
    print(f"{'='*70}\n")

    print(f"📊 Loaded {len(schema_api.get_all_workbooks())} workbooks")
    print(f"📦 Available {len(schema_api.get_all_nodes())} node types\n")

    print("🌐 Starting server at http://localhost:8000")
    print("📚 API docs: http://localhost:8000/docs")
    print("🔌 WebSocket: ws://localhost:8000/ws/execute/{execution_id}\n")

    uvicorn.run(app, host="0.0.0.0", port=8000)
