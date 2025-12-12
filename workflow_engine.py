"""
Core workflow engine components.
"""
from typing import Any, Dict, Callable, Optional, List
from enum import Enum
import uuid
from datetime import datetime


class NodeStatus(Enum):
    """Status of a node execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Node:
    """
    Represents a single step/node in the workflow.
    Each node has a unique ID, a function to execute, and can access/modify shared state.
    """
    
    def __init__(self, node_id: str, function: Callable[[Dict[str, Any]], Dict[str, Any]], 
                 name: Optional[str] = None):
        """
        Initialize a node.
        
        Args:
            node_id: Unique identifier for the node
            function: Function to execute. Takes state dict and returns updated state dict
            name: Optional human-readable name
        """
        self.node_id = node_id
        self.function = function
        self.name = name or node_id
        self.status = NodeStatus.PENDING
        self.error: Optional[str] = None
        
    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the node's function with the given state.
        
        Args:
            state: Current workflow state
            
        Returns:
            Updated state after execution
            
        Raises:
            Exception: If execution fails
        """
        try:
            self.status = NodeStatus.RUNNING
            result = self.function(state)
            self.status = NodeStatus.COMPLETED
            return result
        except Exception as e:
            self.status = NodeStatus.FAILED
            self.error = str(e)
            raise
    
    def reset(self):
        """Reset node status for re-execution."""
        self.status = NodeStatus.PENDING
        self.error = None


class Edge:
    """
    Represents a connection between two nodes.
    Optionally can include a condition function to determine if edge should be followed.
    """
    
    def __init__(self, from_node: str, to_node: str, 
                 condition: Optional[Callable[[Dict[str, Any]], bool]] = None):
        """
        Initialize an edge.
        
        Args:
            from_node: Source node ID
            to_node: Target node ID
            condition: Optional function to determine if edge should be followed
        """
        self.from_node = from_node
        self.to_node = to_node
        self.condition = condition
    
    def should_traverse(self, state: Dict[str, Any]) -> bool:
        """
        Check if this edge should be traversed based on state.
        
        Args:
            state: Current workflow state
            
        Returns:
            True if edge should be traversed, False otherwise
        """
        if self.condition is None:
            return True
        return self.condition(state)


class WorkflowStatus(Enum):
    """Status of workflow execution."""
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class Workflow:
    """
    Main workflow engine that manages nodes, edges, and execution.
    Similar to a simplified LangGraph.
    """
    
    def __init__(self, workflow_id: Optional[str] = None, name: Optional[str] = None):
        """
        Initialize a workflow.
        
        Args:
            workflow_id: Unique identifier for the workflow
            name: Optional human-readable name
        """
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.name = name or f"workflow_{self.workflow_id[:8]}"
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.state: Dict[str, Any] = {}
        self.status = WorkflowStatus.CREATED
        self.start_node: Optional[str] = None
        self.end_nodes: List[str] = []
        self.execution_history: List[Dict[str, Any]] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        
    def add_node(self, node: Node):
        """
        Add a node to the workflow.
        
        Args:
            node: Node to add
        """
        self.nodes[node.node_id] = node
        self.updated_at = datetime.utcnow()
        
    def add_edge(self, edge: Edge):
        """
        Add an edge connecting two nodes.
        
        Args:
            edge: Edge to add
        """
        if edge.from_node not in self.nodes:
            raise ValueError(f"Source node '{edge.from_node}' not found")
        if edge.to_node not in self.nodes:
            raise ValueError(f"Target node '{edge.to_node}' not found")
        self.edges.append(edge)
        self.updated_at = datetime.utcnow()
        
    def set_entry_point(self, node_id: str):
        """
        Set the starting node for workflow execution.
        
        Args:
            node_id: ID of the node to start execution from
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' not found")
        self.start_node = node_id
        self.updated_at = datetime.utcnow()
        
    def add_end_node(self, node_id: str):
        """
        Mark a node as a potential end node.
        
        Args:
            node_id: ID of the node to mark as end
        """
        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_id}' not found")
        if node_id not in self.end_nodes:
            self.end_nodes.append(node_id)
        self.updated_at = datetime.utcnow()
        
    def get_next_nodes(self, current_node_id: str) -> List[str]:
        """
        Get the next nodes to execute based on edges and conditions.
        
        Args:
            current_node_id: Current node ID
            
        Returns:
            List of next node IDs to execute
        """
        next_nodes = []
        for edge in self.edges:
            if edge.from_node == current_node_id:
                if edge.should_traverse(self.state):
                    next_nodes.append(edge.to_node)
        return next_nodes
    
    def execute(self, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the workflow from start to end.
        
        Args:
            initial_state: Initial state to start with
            
        Returns:
            Final state after execution
            
        Raises:
            ValueError: If workflow is not properly configured
            Exception: If execution fails
        """
        if self.start_node is None:
            raise ValueError("No entry point set for workflow")
        
        # Initialize state
        self.state = initial_state or {}
        self.status = WorkflowStatus.RUNNING
        self.execution_history = []
        
        # Reset all nodes
        for node in self.nodes.values():
            node.reset()
        
        try:
            # Execute workflow using BFS
            current_nodes = [self.start_node]
            visited = set()
            
            while current_nodes:
                next_nodes = []
                
                for node_id in current_nodes:
                    if node_id in visited:
                        continue
                    
                    visited.add(node_id)
                    node = self.nodes[node_id]
                    
                    # Log execution
                    execution_entry = {
                        "node_id": node_id,
                        "node_name": node.name,
                        "timestamp": datetime.utcnow().isoformat(),
                        "status": "started"
                    }
                    
                    # Execute node
                    try:
                        self.state = node.execute(self.state)
                        execution_entry["status"] = "completed"
                    except Exception as e:
                        execution_entry["status"] = "failed"
                        execution_entry["error"] = str(e)
                        self.execution_history.append(execution_entry)
                        raise
                    
                    self.execution_history.append(execution_entry)
                    
                    # Check if end node
                    if node_id in self.end_nodes:
                        continue
                    
                    # Get next nodes
                    next_node_ids = self.get_next_nodes(node_id)
                    next_nodes.extend(next_node_ids)
                
                current_nodes = next_nodes
            
            self.status = WorkflowStatus.COMPLETED
            self.updated_at = datetime.utcnow()
            return self.state
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.updated_at = datetime.utcnow()
            raise
    
    def get_state(self) -> Dict[str, Any]:
        """Get current workflow state."""
        return self.state.copy()
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Get detailed status information about the workflow.
        
        Returns:
            Dictionary with workflow status details
        """
        node_statuses = {
            node_id: {
                "status": node.status.value,
                "error": node.error
            }
            for node_id, node in self.nodes.items()
        }
        
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "nodes": node_statuses,
            "execution_history": self.execution_history
        }
