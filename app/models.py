from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
import uuid

class State(BaseModel):
    original_text: str = ""      
    chunks: List[str] = []
    summaries: List[str] = []
    current_summary: str = ""
    iteration_count: int = 0
    logs: List[str] = []

    class Config:
        extra = "allow" 

class Node(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str  
    tool_name: str 

class Edge(BaseModel):
    from_node: str
    to_node: str
    condition: Optional[str] = None 

class Graph(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str
class WorkflowCreateRequest(BaseModel):
    nodes: List[Node]
    edges: List[Edge]
    start_node: str

class WorkflowRunRequest(BaseModel):
    graph_id: str
    initial_state: Dict[str, Any]

class WorkflowStatusResponse(BaseModel):
    run_id: str
    status: str
    state: Optional[Dict[str, Any]]