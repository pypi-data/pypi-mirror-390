from __future__ import annotations
"""
SubGraphNode - Enables graph composition.

Features:
- Encapsulate entire graph as single node
- Isolated execution context
- Input/output mapping
- Reusable workflow components
"""

from typing import Dict, Any, List, Optional
from kaygraph import BaseNode, Graph


class SubGraphNode(BaseNode):
    """
    Node that encapsulates a graph as a reusable component.

    This enables composition of complex workflows from smaller, tested components.
    The subgraph runs with its own isolated context, with configurable input/output mapping.

    Example:
        >>> # Create a reusable workflow
        >>> validation_workflow = create_validation_workflow()
        >>> validation_node = SubGraphNode(validation_workflow)

        >>> # Use in larger workflow
        >>> main_workflow = input_node >> validation_node >> process_node

        >>> # With input/output mapping
        >>> sub = SubGraphNode(
        >>>     graph=validation_workflow,
        >>>     input_keys=["data", "rules"],  # Only pass these keys
        >>>     output_keys=["is_valid", "errors"]  # Only return these
        >>> )
    """

    def __init__(
        self,
        graph: Graph,
        node_id: str = None,
        input_keys: Optional[List[str]] = None,
        output_keys: Optional[List[str]] = None
    ):
        """
        Initialize SubGraphNode.

        Args:
            graph: Graph to encapsulate
            node_id: Node identifier (default: auto-generated)
            input_keys: Keys to copy from parent shared to subgraph.
                       If None, copies all keys.
            output_keys: Keys to copy from subgraph result to parent shared.
                        If None, returns all keys.
        """
        super().__init__(node_id or f"subgraph_{id(graph)}")
        self.subgraph = graph
        self.input_keys = input_keys
        self.output_keys = output_keys

    def prep(self, shared: Dict) -> Dict:
        """
        Prepare input for subgraph from parent shared state.

        Args:
            shared: Parent workflow's shared state

        Returns:
            Dictionary to pass to subgraph
        """
        if self.input_keys:
            # Copy only specified keys
            subgraph_input = {}
            for key in self.input_keys:
                if key in shared:
                    subgraph_input[key] = shared[key]
                else:
                    self.logger.warning(f"Input key '{key}' not found in shared state")
            return subgraph_input
        else:
            # Copy all shared data (deep copy to isolate)
            import copy
            return copy.deepcopy(shared)

    def exec(self, prep_res: Dict) -> Dict:
        """
        Execute subgraph with isolated context.

        Args:
            prep_res: Prepared input for subgraph

        Returns:
            Subgraph execution results
        """
        self.logger.info(f"Executing subgraph {self.node_id}")

        # Run subgraph with prepared input
        # The subgraph modifies prep_res in-place
        last_action = self.subgraph.run(prep_res)

        # Log completion
        self.logger.info(f"Subgraph {self.node_id} completed with action: {last_action}")

        # Extract output
        if self.output_keys:
            # Return only specified keys
            output = {}
            for key in self.output_keys:
                if key in prep_res:
                    output[key] = prep_res[key]
                else:
                    self.logger.warning(f"Output key '{key}' not found in subgraph result")
            return output
        else:
            # Return all results
            return prep_res

    def post(self, shared: Dict, prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """
        Merge subgraph results into parent shared state.

        Args:
            shared: Parent workflow's shared state
            prep_res: Input that was sent to subgraph
            exec_res: Output from subgraph

        Returns:
            Action string for routing (default: None)
        """
        # Update parent shared with subgraph results
        shared.update(exec_res)

        # Could implement conditional routing based on subgraph results
        # For example:
        # if exec_res.get("status") == "error":
        #     return "handle_error"

        return None


def compose_graphs(*graphs: Graph, node_id: str = None) -> SubGraphNode:
    """
    Compose multiple graphs into a single node.

    This is a convenience function for creating composite workflows.

    Args:
        *graphs: Graphs to compose
        node_id: Identifier for the composed node

    Returns:
        SubGraphNode containing the composed workflow

    Example:
        >>> validation = create_validation_workflow()
        >>> processing = create_processing_workflow()
        >>> composed = compose_graphs(validation, processing)
    """
    if len(graphs) == 0:
        raise ValueError("At least one graph must be provided")

    if len(graphs) == 1:
        # Single graph - just wrap it
        return SubGraphNode(graphs[0], node_id=node_id)

    # For multiple graphs, we need to chain them
    # This is a simplified implementation - full version would create
    # a new Graph that chains the subgraphs
    from kaygraph import Graph, BaseNode

    class ChainedGraphsNode(BaseNode):
        """Internal node for chaining multiple graphs."""

        def __init__(self, graphs_list):
            super().__init__("chained_graphs")
            self.graphs = graphs_list

        def exec(self, prep_res):
            """Execute graphs in sequence."""
            current_data = prep_res.copy()

            for i, graph in enumerate(self.graphs):
                self.logger.info(f"Executing graph {i + 1} of {len(self.graphs)}")
                # Each graph modifies current_data in place
                graph.run(current_data)

            return current_data

        def post(self, shared, prep_res, exec_res):
            shared.update(exec_res)
            return None

    # Create a graph with the chained node
    chain_node = ChainedGraphsNode(graphs)
    wrapper_graph = Graph(chain_node)

    return SubGraphNode(wrapper_graph, node_id=node_id or "composed_workflow")


class ConditionalSubGraphNode(SubGraphNode):
    """
    SubGraphNode that conditionally executes based on shared state.

    Example:
        >>> expensive_workflow = create_expensive_workflow()
        >>> conditional = ConditionalSubGraphNode(
        >>>     graph=expensive_workflow,
        >>>     condition_key="needs_processing",
        >>>     condition_value=True
        >>> )
    """

    def __init__(
        self,
        graph: Graph,
        condition_key: str,
        condition_value: Any = True,
        node_id: str = None,
        input_keys: Optional[List[str]] = None,
        output_keys: Optional[List[str]] = None
    ):
        """
        Initialize ConditionalSubGraphNode.

        Args:
            graph: Graph to conditionally execute
            condition_key: Key in shared to check
            condition_value: Value that triggers execution
            node_id: Node identifier
            input_keys: Keys to pass to subgraph
            output_keys: Keys to return from subgraph
        """
        super().__init__(graph, node_id, input_keys, output_keys)
        self.condition_key = condition_key
        self.condition_value = condition_value

    def prep(self, shared: Dict) -> Dict:
        """Check condition and prepare input if needed."""
        # Check condition
        should_execute = shared.get(self.condition_key) == self.condition_value

        if not should_execute:
            self.logger.info(f"Skipping subgraph {self.node_id} - condition not met")
            return {"_skip": True}

        # Condition met - prepare input normally
        return super().prep(shared)

    def exec(self, prep_res: Dict) -> Dict:
        """Execute subgraph only if condition was met."""
        if prep_res.get("_skip"):
            return {}  # Return empty result if skipped

        return super().exec(prep_res)


class ParallelSubGraphNode(BaseNode):
    """
    Node that runs multiple subgraphs in parallel.

    Note: This is a conceptual implementation. True parallelism would
    require AsyncGraph or threading support.

    Example:
        >>> validation = create_validation_workflow()
        >>> analysis = create_analysis_workflow()
        >>> parallel = ParallelSubGraphNode([validation, analysis])
    """

    def __init__(
        self,
        graphs: List[Graph],
        node_id: str = None,
        merge_results: bool = True
    ):
        """
        Initialize ParallelSubGraphNode.

        Args:
            graphs: List of graphs to run in parallel
            node_id: Node identifier
            merge_results: Whether to merge all results into shared
        """
        super().__init__(node_id or "parallel_subgraphs")
        self.graphs = graphs
        self.merge_results = merge_results

    def prep(self, shared: Dict) -> Dict:
        """Prepare input for parallel execution."""
        # Return a copy of shared state
        import copy
        return copy.deepcopy(shared) if shared else {}

    def exec(self, prep_res: Dict) -> Dict:
        """
        Execute all subgraphs (conceptually in parallel).

        In this implementation, they run sequentially but with
        isolated contexts to simulate parallel execution.
        """
        import copy
        results = {}

        for i, graph in enumerate(self.graphs):
            # Each graph gets its own copy of input
            graph_input = copy.deepcopy(prep_res)

            self.logger.info(f"Executing parallel graph {i + 1} of {len(self.graphs)}")
            graph.run(graph_input)

            # Store result with graph index
            results[f"graph_{i}"] = graph_input

        return results

    def post(self, shared: Dict, prep_res: Dict, exec_res: Dict) -> Optional[str]:
        """Merge results from parallel execution."""
        if self.merge_results:
            # Merge all results into shared
            for graph_key, graph_result in exec_res.items():
                # Could implement conflict resolution here
                shared.update(graph_result)
        else:
            # Store results separately
            shared["parallel_results"] = exec_res

        return None