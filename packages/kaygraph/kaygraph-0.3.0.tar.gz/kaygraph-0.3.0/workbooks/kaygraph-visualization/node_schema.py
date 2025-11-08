"""
Node Schema System for UI Integration

This module provides automatic schema extraction from KayGraph nodes,
enabling dynamic UI generation for workflow builders.

**FOR AI AGENTS:** Study this to understand how to:
- Introspect Python nodes for configuration
- Generate JSON schemas for UI forms
- Map shared state to input/output ports
- Validate node connections
"""

import inspect
import ast
from typing import Dict, Any, List, Optional, Type, get_type_hints
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import importlib
import json

from kaygraph import BaseNode, Node, AsyncNode, BatchNode, ParallelBatchNode


# =============================================================================
# Schema Data Structures
# =============================================================================

@dataclass
class ConfigParameter:
    """Represents a configuration parameter for a node."""
    name: str
    type: str  # "string", "number", "boolean", "enum"
    default: Any = None
    required: bool = False
    options: Optional[List[Any]] = None  # For enum types
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class SharedStateField:
    """Represents a field read from or written to shared state."""
    name: str
    type: str
    required: bool = False
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class NodeSchema:
    """Complete schema for a KayGraph node."""

    # Basic info
    node_type: str  # Class name
    module_path: str  # Import path
    category: str  # "input", "processing", "output", "decision", "loop"
    display_name: str
    description: str
    icon: str = "📦"  # Emoji or icon identifier

    # Configuration (from __init__)
    config_params: List[ConfigParameter] = field(default_factory=list)

    # Data flow (from prep/post and shared state)
    inputs: List[SharedStateField] = field(default_factory=list)  # From prep()
    outputs: List[SharedStateField] = field(default_factory=list)  # From post()

    # Routing (from post() return values)
    actions: List[str] = field(default_factory=list)  # Possible routing actions

    # Metadata
    is_async: bool = False
    is_batch: bool = False
    is_parallel: bool = False
    base_class: str = "Node"

    # UI hints
    ui_color: str = "#E3F2FD"  # Default color
    ui_width: int = 200
    ui_height: int = 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict for API."""
        return {
            "node_type": self.node_type,
            "module_path": self.module_path,
            "category": self.category,
            "display_name": self.display_name,
            "description": self.description,
            "icon": self.icon,
            "config_params": [p.to_dict() for p in self.config_params],
            "inputs": [i.to_dict() for i in self.inputs],
            "outputs": [o.to_dict() for o in self.outputs],
            "actions": self.actions,
            "is_async": self.is_async,
            "is_batch": self.is_batch,
            "is_parallel": self.is_parallel,
            "base_class": self.base_class,
            "ui_color": self.ui_color,
            "ui_width": self.ui_width,
            "ui_height": self.ui_height
        }


# =============================================================================
# Schema Extractor
# =============================================================================

class NodeSchemaExtractor:
    """Extract schema information from KayGraph node classes."""

    def __init__(self):
        self.type_map = {
            'str': 'string',
            'int': 'number',
            'float': 'number',
            'bool': 'boolean',
            'list': 'array',
            'dict': 'object',
            'List': 'array',
            'Dict': 'object',
            'Optional': 'optional'
        }

    def extract_schema(self, NodeClass: Type[BaseNode]) -> NodeSchema:
        """
        Extract complete schema from a node class.

        Uses introspection to analyze:
        - __init__ parameters → config_params
        - prep() method → inputs
        - post() method → outputs and actions
        - Docstrings → descriptions
        """
        schema = NodeSchema(
            node_type=NodeClass.__name__,
            module_path=f"{NodeClass.__module__}.{NodeClass.__name__}",
            category=self._infer_category(NodeClass),
            display_name=self._humanize_name(NodeClass.__name__),
            description=self._extract_description(NodeClass),
            icon=self._infer_icon(NodeClass),
            is_async=issubclass(NodeClass, AsyncNode),
            is_batch=issubclass(NodeClass, (BatchNode, ParallelBatchNode)),
            is_parallel=issubclass(NodeClass, ParallelBatchNode),
            base_class=NodeClass.__bases__[0].__name__
        )

        # Extract config parameters from __init__
        schema.config_params = self._extract_config_params(NodeClass)

        # Extract inputs from prep()
        schema.inputs = self._extract_inputs(NodeClass)

        # Extract outputs and actions from post()
        schema.outputs, schema.actions = self._extract_outputs_and_actions(NodeClass)

        # Set UI color based on category
        schema.ui_color = self._get_category_color(schema.category)

        return schema

    def _extract_config_params(self, NodeClass: Type[BaseNode]) -> List[ConfigParameter]:
        """Extract configuration parameters from __init__ signature."""
        params = []

        try:
            sig = inspect.signature(NodeClass.__init__)

            # Get type hints if available
            try:
                type_hints = get_type_hints(NodeClass.__init__)
            except:
                type_hints = {}

            for param_name, param in sig.parameters.items():
                if param_name in ('self', 'node_id'):
                    continue

                # Get type
                param_type = "string"  # Default
                if param_name in type_hints:
                    type_hint = str(type_hints[param_name])
                    param_type = self._map_python_type(type_hint)

                # Get default value
                default = None
                required = True
                if param.default != inspect.Parameter.empty:
                    default = param.default
                    required = False

                # Extract description from docstring
                description = self._extract_param_description(NodeClass, param_name)

                config_param = ConfigParameter(
                    name=param_name,
                    type=param_type,
                    default=default,
                    required=required,
                    description=description
                )

                params.append(config_param)

        except Exception as e:
            print(f"Warning: Could not extract config for {NodeClass.__name__}: {e}")

        return params

    def _extract_inputs(self, NodeClass: Type[BaseNode]) -> List[SharedStateField]:
        """
        Extract inputs by analyzing prep() method.

        Looks for shared.get("key") calls to identify inputs.
        """
        inputs = []

        if not hasattr(NodeClass, 'prep'):
            return inputs

        try:
            source = inspect.getsource(NodeClass.prep)

            # Parse source to find shared.get() calls
            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Look for shared.get("key")
                    if (isinstance(node.func, ast.Attribute) and
                        node.func.attr == 'get' and
                        isinstance(node.func.value, ast.Name) and
                        node.func.value.id == 'shared' and
                        node.args):

                        if isinstance(node.args[0], ast.Constant):
                            key = node.args[0].value

                            # Check if required (no default provided)
                            required = len(node.args) == 1

                            inputs.append(SharedStateField(
                                name=key,
                                type="any",  # Would need type inference
                                required=required,
                                description=f"Read from shared state: {key}"
                            ))

        except Exception as e:
            print(f"Warning: Could not extract inputs for {NodeClass.__name__}: {e}")

        return inputs

    def _extract_outputs_and_actions(
        self,
        NodeClass: Type[BaseNode]
    ) -> tuple[List[SharedStateField], List[str]]:
        """
        Extract outputs and routing actions from post() method.

        - Outputs: shared["key"] = value assignments
        - Actions: return statements (routing)
        """
        outputs = []
        actions = []

        if not hasattr(NodeClass, 'post'):
            return outputs, ["default"]

        try:
            source = inspect.getsource(NodeClass.post)
            tree = ast.parse(source)

            for node in ast.walk(tree):
                # Find shared["key"] = value assignments
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if (isinstance(target, ast.Subscript) and
                            isinstance(target.value, ast.Name) and
                            target.value.id == 'shared' and
                            isinstance(target.slice, ast.Constant)):

                            key = target.slice.value
                            outputs.append(SharedStateField(
                                name=key,
                                type="any",
                                description=f"Written to shared state: {key}"
                            ))

                # Find return statements for actions
                if isinstance(node, ast.Return) and node.value:
                    if isinstance(node.value, ast.Constant):
                        actions.append(node.value.value)

        except Exception as e:
            print(f"Warning: Could not extract outputs for {NodeClass.__name__}: {e}")

        if not actions:
            actions = ["default"]

        return outputs, actions

    def _extract_description(self, NodeClass: Type[BaseNode]) -> str:
        """Extract description from class docstring."""
        doc = NodeClass.__doc__
        if doc:
            # Get first line/paragraph
            lines = doc.strip().split('\n')
            return lines[0].strip()
        return f"{NodeClass.__name__} node"

    def _extract_param_description(self, NodeClass: Type[BaseNode], param_name: str) -> Optional[str]:
        """Extract parameter description from docstring."""
        doc = NodeClass.__init__.__doc__
        if not doc:
            return None

        # Look for "param_name: description" pattern
        lines = doc.split('\n')
        for i, line in enumerate(lines):
            if param_name in line and ':' in line:
                # Extract description after colon
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()

        return None

    def _map_python_type(self, type_hint: str) -> str:
        """Map Python type hints to schema types."""
        type_hint = type_hint.lower()

        for py_type, schema_type in self.type_map.items():
            if py_type.lower() in type_hint:
                return schema_type

        return "string"

    def _infer_category(self, NodeClass: Type[BaseNode]) -> str:
        """Infer category from class name and base class."""
        name = NodeClass.__name__.lower()

        if 'input' in name or 'clarif' in name or 'extract' in name:
            return "input"
        elif 'decision' in name or 'select' in name or 'route' in name:
            return "decision"
        elif 'synthesis' in name or 'result' in name or 'output' in name:
            return "output"
        elif 'lead' in name or 'orchestr' in name:
            return "orchestrator"
        elif 'agent' in name or 'worker' in name:
            return "worker"
        else:
            return "processing"

    def _infer_icon(self, NodeClass: Type[BaseNode]) -> str:
        """Infer emoji icon from node type."""
        name = NodeClass.__name__.lower()

        icon_map = {
            'intent': '🎯',
            'clarif': '❓',
            'lead': '👔',
            'agent': '🤖',
            'search': '🔍',
            'synthesis': '⚡',
            'result': '📊',
            'citation': '📚',
            'quality': '✅',
            'aspect': '🔹',
            'entity': '🏷️',
            'comparison': '⚖️',
            'memory': '🧠',
            'workflow': '🔀'
        }

        for keyword, icon in icon_map.items():
            if keyword in name:
                return icon

        return "📦"

    def _humanize_name(self, class_name: str) -> str:
        """Convert ClassName to Human Readable."""
        # Remove 'Node' suffix
        name = class_name.replace('Node', '')

        # Add spaces before capitals
        import re
        name = re.sub(r'([A-Z])', r' \1', name).strip()

        return name

    def _get_category_color(self, category: str) -> str:
        """Get UI color based on category."""
        colors = {
            "input": "#E8F5E9",      # Light green
            "processing": "#E3F2FD",  # Light blue
            "output": "#FFF3E0",      # Light orange
            "decision": "#F3E5F5",    # Light purple
            "orchestrator": "#E0F2F1", # Light teal
            "worker": "#F1F8E9"       # Light lime
        }
        return colors.get(category, "#F5F5F5")


# =============================================================================
# Workbook Discovery
# =============================================================================

@dataclass
class WorkbookMetadata:
    """Metadata about a KayGraph workbook."""
    name: str
    path: str
    version: str
    description: str
    node_modules: List[str]  # Module names containing nodes
    workflow_functions: List[str]  # Graph creation functions
    categories: List[str]
    icon: str = "📁"


class WorkbookDiscovery:
    """Discover and load KayGraph workbooks."""

    def __init__(self, workbooks_root: Path):
        self.workbooks_root = Path(workbooks_root)
        self.extractor = NodeSchemaExtractor()

    def discover_workbooks(self) -> List[WorkbookMetadata]:
        """
        Scan for workbooks with metadata files.

        Looks for:
        - workbook.json (explicit metadata)
        - README.md (parse for metadata)
        - __init__.py (detect modules)
        """
        workbooks = []

        for workbook_dir in self.workbooks_root.iterdir():
            if not workbook_dir.is_dir():
                continue

            # Look for workbook.json
            metadata_file = workbook_dir / "workbook.json"
            if metadata_file.exists():
                with open(metadata_file) as f:
                    data = json.load(f)
                    workbooks.append(WorkbookMetadata(**data, path=str(workbook_dir)))
            else:
                # Auto-detect
                metadata = self._auto_detect_workbook(workbook_dir)
                if metadata:
                    workbooks.append(metadata)

        return workbooks

    def _auto_detect_workbook(self, workbook_dir: Path) -> Optional[WorkbookMetadata]:
        """Auto-detect workbook metadata from directory structure."""

        # Check for common files
        has_nodes = (workbook_dir / "nodes.py").exists()
        has_graphs = (workbook_dir / "graphs.py").exists()

        if not (has_nodes or has_graphs):
            return None

        node_modules = []
        if has_nodes:
            node_modules.append("nodes")
        if (workbook_dir / "specialized_nodes.py").exists():
            node_modules.append("specialized_nodes")

        # Extract name from directory
        name = workbook_dir.name.replace('_', ' ').title()

        # Try to extract description from README
        description = name
        readme = workbook_dir / "README.md"
        if readme.exists():
            with open(readme) as f:
                lines = f.readlines()
                if len(lines) > 1:
                    description = lines[1].strip()

        return WorkbookMetadata(
            name=name,
            path=str(workbook_dir),
            version="1.0.0",
            description=description,
            node_modules=node_modules,
            workflow_functions=["create_workflow"] if has_graphs else [],
            categories=["general"]
        )

    def load_workbook_nodes(self, workbook: WorkbookMetadata) -> List[NodeSchema]:
        """Load all nodes from a workbook and extract their schemas."""
        schemas = []

        # Import workbook modules
        workbook_path = Path(workbook.path)
        parent_module = workbook_path.parent.name
        workbook_module = workbook_path.name

        for module_name in workbook.node_modules:
            try:
                # Import module
                full_module_path = f"{parent_module}.{workbook_module}.{module_name}"
                module = importlib.import_module(full_module_path)

                # Find all Node subclasses
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)

                    if (inspect.isclass(attr) and
                        issubclass(attr, BaseNode) and
                        attr not in (BaseNode, Node, AsyncNode, BatchNode, ParallelBatchNode)):

                        # Extract schema
                        schema = self.extractor.extract_schema(attr)
                        schemas.append(schema)

            except Exception as e:
                print(f"Warning: Could not load {module_name} from {workbook.name}: {e}")

        return schemas


# =============================================================================
# API for UI
# =============================================================================

class NodeSchemaAPI:
    """API for serving node schemas to the UI."""

    def __init__(self, workbooks_root: Path):
        self.discovery = WorkbookDiscovery(workbooks_root)

    def get_all_workbooks(self) -> List[Dict[str, Any]]:
        """Get list of all available workbooks."""
        workbooks = self.discovery.discover_workbooks()
        return [asdict(wb) for wb in workbooks]

    def get_workbook_nodes(self, workbook_name: str) -> List[Dict[str, Any]]:
        """Get all node schemas for a specific workbook."""
        workbooks = self.discovery.discover_workbooks()

        for wb in workbooks:
            if wb.name == workbook_name or wb.path.endswith(workbook_name):
                schemas = self.discovery.load_workbook_nodes(wb)
                return [schema.to_dict() for schema in schemas]

        return []

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Get all node schemas from all workbooks."""
        all_schemas = []
        workbooks = self.discovery.discover_workbooks()

        for wb in workbooks:
            schemas = self.discovery.load_workbook_nodes(wb)
            all_schemas.extend([schema.to_dict() for schema in schemas])

        return all_schemas


if __name__ == "__main__":
    # Example usage
    import sys
    from pathlib import Path

    # Point to claude_integration directory
    workbooks_root = Path(__file__).parent.parent.parent / "claude_integration"

    api = NodeSchemaAPI(workbooks_root)

    print("="*70)
    print("KAYGRAPH NODE SCHEMA EXTRACTION")
    print("="*70)

    # List all workbooks
    print("\n📁 Available Workbooks:")
    workbooks = api.get_all_workbooks()
    for wb in workbooks:
        print(f"  - {wb['name']} ({len(wb['node_modules'])} modules)")

    # Show deep_research nodes as example
    print("\n🔍 Deep Research Nodes:")
    nodes = api.get_workbook_nodes("deep_research")
    for node in nodes[:3]:  # Show first 3
        print(f"\n  {node['icon']} {node['display_name']}")
        print(f"     Category: {node['category']}")
        print(f"     Config: {len(node['config_params'])} parameters")
        print(f"     Inputs: {len(node['inputs'])} fields")
        print(f"     Outputs: {len(node['outputs'])} fields")
        print(f"     Actions: {', '.join(node['actions'])}")

    print(f"\n  ... and {len(nodes) - 3} more nodes")

    print("\n✅ Schema extraction complete!")
