from typing import Dict, List, Callable, Any, Optional
from .models import State, Node, Edge

class Engine:
    def __init__(self, nodes: List[Node], edges: List[Edge], tool_registry: Dict[str, Callable]):
        self.node_map = {n.name: n for n in nodes}
        self.edges = edges
        self.registry = tool_registry
        self.current_state = State()

    def _get_next_node_name(self, current_node: str, state: State):
        candidates = [e for e in self.edges if e.from_node == current_node]

        for edge in candidates:
            
            if not edge.condition:
                return edge.to_node
            
            
            try:
                if eval(edge.condition, {}, {"state": state}):
                    return edge.to_node
            except Exception as e:
                print(f"Error evaluating condition '{edge.condition}': {e}")
                continue

        return None
    
    def run_node(self, node_name: str):
        node = self.node_map.get(node_name)
        if not node:
            raise ValueError(f"Node {node_name} not found")

        tool_function = self.registry.get(node.tool_name)
        if not tool_function:
            raise ValueError(f"Tool {node.tool_name} not found")

        self.current_state.logs.append(
            f"Running node {node_name} with tool {node.tool_name}"
        )

        updates = tool_function(self.current_state)

        if updates:
            state_data = self.current_state.model_dump()
            state_data.update(updates)
            self.current_state = State(**state_data)
        
    def execute(self, start_node_name: str, initial_input: Dict[str, Any]):
        # Initialize
        self.current_state = State(**initial_input)
        current_node_name = start_node_name

        steps = 0
        MAX_STEPS = 10

        while current_node_name and steps < MAX_STEPS:
            self.run_node(current_node_name)

            next_node = self._get_next_node_name(current_node_name, self.current_state)

            current_node_name = next_node
            steps += 1

        if steps >= MAX_STEPS:
            self.current_state.logs.append("Maximum steps reached. Workflow terminated.")
        else:
            self.current_state.logs.append("Workflow completed successfully.")
        
        return self.current_state.model_dump()