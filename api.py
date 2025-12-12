"""
FastAPI application for the Workflow Agent Engine.
Provides REST APIs to create, manage, and execute workflows.
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime

from workflow_engine import Workflow, Node, Edge, WorkflowStatus


app = FastAPI(
    title="Workflow Agent Engine",
    description="A simplified workflow engine similar to LangGraph",
    version="1.0.0"
)


# In-memory storage for workflows
workflows: Dict[str, Workflow] = {}


# Pydantic models for API
class NodeDefinition(BaseModel):
    """Definition for creating a node."""
    node_id: str = Field(..., description="Unique identifier for the node")
    name: Optional[str] = Field(None, description="Human-readable name for the node")
    function_type: str = Field(..., description="Type of function to execute")
    function_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the function")


class EdgeDefinition(BaseModel):
    """Definition for creating an edge."""
    from_node: str = Field(..., description="Source node ID")
    to_node: str = Field(..., description="Target node ID")
    condition_type: Optional[str] = Field(None, description="Type of condition for traversal")
    condition_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the condition")


class WorkflowCreate(BaseModel):
    """Request model for creating a workflow."""
    name: Optional[str] = Field(None, description="Human-readable name for the workflow")
    nodes: List[NodeDefinition] = Field(..., description="List of nodes in the workflow")
    edges: List[EdgeDefinition] = Field(..., description="List of edges connecting nodes")
    start_node: str = Field(..., description="ID of the starting node")
    end_nodes: List[str] = Field(default_factory=list, description="List of end node IDs")


class WorkflowExecute(BaseModel):
    """Request model for executing a workflow."""
    initial_state: Dict[str, Any] = Field(default_factory=dict, description="Initial state for the workflow")


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    workflow_id: str
    name: str
    status: str
    message: str


class StateResponse(BaseModel):
    """Response model for state queries."""
    workflow_id: str
    state: Dict[str, Any]


class StatusResponse(BaseModel):
    """Response model for status queries."""
    workflow_id: str
    name: str
    status: str
    created_at: str
    updated_at: str
    nodes: Dict[str, Any]
    execution_history: List[Dict[str, Any]]


# Built-in function types
def create_node_function(function_type: str, function_params: Dict[str, Any]):
    """
    Create a node function based on type and parameters.
    
    Args:
        function_type: Type of function to create
        function_params: Parameters for the function
        
    Returns:
        Callable function for the node
    """
    if function_type == "set_value":
        # Set a value in state (only if not already set, or if force=True)
        key = function_params.get("key")
        value = function_params.get("value")
        force = function_params.get("force", False)
        
        def set_value_func(state: Dict[str, Any]) -> Dict[str, Any]:
            if force or key not in state:
                state[key] = value
            return state
        
        return set_value_func
    
    elif function_type == "transform":
        # Transform a value using an operation
        input_key = function_params.get("input_key")
        output_key = function_params.get("output_key")
        operation = function_params.get("operation")
        
        def transform_func(state: Dict[str, Any]) -> Dict[str, Any]:
            if input_key not in state:
                raise ValueError(f"Key '{input_key}' not found in state")
            
            value = state[input_key]
            
            if operation == "uppercase":
                result = str(value).upper()
            elif operation == "lowercase":
                result = str(value).lower()
            elif operation == "double":
                result = value * 2
            elif operation == "increment":
                result = value + 1
            elif operation == "append":
                append_value = function_params.get("append_value", "")
                result = str(value) + str(append_value)
            else:
                result = value
            
            state[output_key] = result
            return state
        
        return transform_func
    
    elif function_type == "aggregate":
        # Aggregate multiple values
        input_keys = function_params.get("input_keys", [])
        output_key = function_params.get("output_key")
        operation = function_params.get("operation", "sum")
        
        def aggregate_func(state: Dict[str, Any]) -> Dict[str, Any]:
            values = [state.get(key, 0) for key in input_keys]
            
            if operation == "sum":
                result = sum(values)
            elif operation == "product":
                result = 1
                for v in values:
                    result *= v
            elif operation == "concat":
                result = "".join(str(v) for v in values)
            elif operation == "list":
                result = values
            else:
                result = values
            
            state[output_key] = result
            return state
        
        return aggregate_func
    
    elif function_type == "custom":
        # Custom function that just passes through
        def custom_func(state: Dict[str, Any]) -> Dict[str, Any]:
            # Allow custom logic to be added later
            message = function_params.get("message", "Custom node executed")
            state["last_message"] = message
            return state
        
        return custom_func
    
    else:
        # Default pass-through function
        def default_func(state: Dict[str, Any]) -> Dict[str, Any]:
            return state
        
        return default_func


def create_condition_function(condition_type: Optional[str], condition_params: Dict[str, Any]):
    """
    Create a condition function for edges.
    
    Args:
        condition_type: Type of condition
        condition_params: Parameters for the condition
        
    Returns:
        Callable condition function or None for unconditional edges
    """
    if condition_type is None:
        return None
    
    if condition_type == "key_equals":
        key = condition_params.get("key")
        value = condition_params.get("value")
        
        def key_equals_func(state: Dict[str, Any]) -> bool:
            return state.get(key) == value
        
        return key_equals_func
    
    elif condition_type == "key_exists":
        key = condition_params.get("key")
        
        def key_exists_func(state: Dict[str, Any]) -> bool:
            return key in state
        
        return key_exists_func
    
    elif condition_type == "key_greater_than":
        key = condition_params.get("key")
        threshold = condition_params.get("threshold", 0)
        
        def key_greater_than_func(state: Dict[str, Any]) -> bool:
            return state.get(key, 0) > threshold
        
        return key_greater_than_func
    
    return None


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Workflow Agent Engine",
        "version": "1.0.0",
        "description": "A simplified workflow engine similar to LangGraph",
        "endpoints": {
            "POST /workflow/create": "Create a new workflow",
            "POST /workflow/{workflow_id}/execute": "Execute a workflow",
            "GET /workflow/{workflow_id}/state": "Get workflow state",
            "GET /workflow/{workflow_id}/status": "Get workflow status",
            "GET /workflows": "List all workflows"
        }
    }


@app.post("/workflow/create", response_model=WorkflowResponse)
async def create_workflow(workflow_def: WorkflowCreate):
    """
    Create a new workflow with nodes and edges.
    
    Args:
        workflow_def: Workflow definition
        
    Returns:
        Created workflow information
    """
    try:
        # Create workflow
        workflow = Workflow(name=workflow_def.name)
        
        # Add nodes
        for node_def in workflow_def.nodes:
            node_func = create_node_function(node_def.function_type, node_def.function_params)
            node = Node(node_def.node_id, node_func, node_def.name)
            workflow.add_node(node)
        
        # Add edges
        for edge_def in workflow_def.edges:
            condition_func = create_condition_function(
                edge_def.condition_type,
                edge_def.condition_params
            )
            edge = Edge(edge_def.from_node, edge_def.to_node, condition_func)
            workflow.add_edge(edge)
        
        # Set entry point
        workflow.set_entry_point(workflow_def.start_node)
        
        # Set end nodes
        for end_node in workflow_def.end_nodes:
            workflow.add_end_node(end_node)
        
        # Store workflow
        workflows[workflow.workflow_id] = workflow
        
        return WorkflowResponse(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            status=workflow.status.value,
            message="Workflow created successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/workflow/{workflow_id}/execute", response_model=StateResponse)
async def execute_workflow(workflow_id: str, execute_req: WorkflowExecute):
    """
    Execute a workflow with initial state.
    
    Args:
        workflow_id: Workflow ID
        execute_req: Execution request with initial state
        
    Returns:
        Final state after execution
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    workflow = workflows[workflow_id]
    
    try:
        final_state = workflow.execute(execute_req.initial_state)
        
        return StateResponse(
            workflow_id=workflow_id,
            state=final_state
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.get("/workflow/{workflow_id}/state", response_model=StateResponse)
async def get_workflow_state(workflow_id: str):
    """
    Get the current state of a workflow.
    
    Args:
        workflow_id: Workflow ID
        
    Returns:
        Current workflow state
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    workflow = workflows[workflow_id]
    
    return StateResponse(
        workflow_id=workflow_id,
        state=workflow.get_state()
    )


@app.get("/workflow/{workflow_id}/status", response_model=StatusResponse)
async def get_workflow_status(workflow_id: str):
    """
    Get the status and execution history of a workflow.
    
    Args:
        workflow_id: Workflow ID
        
    Returns:
        Workflow status information
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    workflow = workflows[workflow_id]
    status_info = workflow.get_status_info()
    
    return StatusResponse(**status_info)


@app.get("/workflows")
async def list_workflows():
    """
    List all workflows.
    
    Returns:
        List of all workflows with basic info
    """
    workflow_list = []
    for workflow_id, workflow in workflows.items():
        workflow_list.append({
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "node_count": len(workflow.nodes),
            "edge_count": len(workflow.edges)
        })
    
    return {"workflows": workflow_list, "count": len(workflow_list)}


@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    """
    Delete a workflow.
    
    Args:
        workflow_id: Workflow ID
        
    Returns:
        Deletion confirmation
    """
    if workflow_id not in workflows:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    
    del workflows[workflow_id]
    
    return {"message": f"Workflow '{workflow_id}' deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
