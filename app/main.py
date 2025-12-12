import uuid
import nltk
from fastapi import FastAPI, HTTPException, BackgroundTasks
from typing import Dict, Any, List
from .models import (
    Graph, WorkflowCreateRequest, WorkflowRunRequest, 
    Node, Edge, State
)
from .engine import Engine
from .tools import TOOL_REGISTRY

app = FastAPI(title="Backend Agent Engine")

GRAPHS: Dict[str, Graph] = {}
RUNS: Dict[str, Dict[str, Any]] = {}

def _run_workflow_task(run_id: str, graph: Graph, initial_state: dict):
    """
    Runs the engine in a background thread.
    """
    try:
        engine = Engine(
            nodes=graph.nodes,
            edges=graph.edges,
            tool_registry=TOOL_REGISTRY
        )
        
        final_state = engine.execute(graph.start_node, initial_state)
        
        RUNS[run_id]["status"] = "COMPLETED"
        RUNS[run_id]["state"] = final_state
        
    except Exception as e:
        print(f"Workflow Failed: {e}")
        RUNS[run_id]["status"] = "FAILED"
        RUNS[run_id]["error"] = str(e)

@app.on_event("startup")
def startup_event():

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')

    graph_id = "summary-agent"
    
    nodes = [
        Node(name="node_split", tool_name="split"),
        Node(name="node_chunk_sum", tool_name="summarize_chunks"),
        Node(name="node_merge", tool_name="merge"),
        Node(name="node_refine", tool_name="refine"),
    ]
    
    edges = [
        
        Edge(from_node="node_split", to_node="node_chunk_sum"),
        
        Edge(from_node="node_chunk_sum", to_node="node_merge"),
        
        Edge(from_node="node_merge", to_node="node_refine"),
        
        Edge(
            from_node="node_refine", 
            to_node="node_refine", 
            condition="state.iteration_count > 1"
        )
    ]
    
    GRAPHS[graph_id] = Graph(nodes=nodes, edges=edges, start_node="node_split")
    print(f"✅ Seeded Graph ID: {graph_id}")

@app.post("/graph/create")
def create_graph(request: WorkflowCreateRequest):
    graph_id = str(uuid.uuid4())
    new_graph = Graph(
        nodes=request.nodes,
        edges=request.edges,
        start_node=request.start_node
    )
    GRAPHS[graph_id] = new_graph
    return {"graph_id": graph_id, "message": "Graph created."}

@app.post("/graph/run")
def run_workflow(request: WorkflowRunRequest, background_tasks: BackgroundTasks):
    if request.graph_id not in GRAPHS:
        raise HTTPException(status_code=404, detail="Graph ID not found")
    
    run_id = str(uuid.uuid4())
    graph = GRAPHS[request.graph_id]
    
    RUNS[run_id] = {"status": "RUNNING", "state": None}
    
    background_tasks.add_task(_run_workflow_task, run_id, graph, request.initial_state)
    
    return {"run_id": run_id, "status": "QUEUED"}

@app.get("/graph/run/{run_id}")
def get_run_status(run_id: str):
    if run_id not in RUNS:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return RUNS[run_id]