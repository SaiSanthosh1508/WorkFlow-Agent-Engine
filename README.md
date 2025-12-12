# WorkFlow-Agent-Engine

A clean, backend-only graph execution engine built with **Python** and **FastAPI**.

This project implements a directed graph workflow system that manages state, transitions, and conditional loops. It demonstrates a working **"Summarization & Refinement"** agent (Option B) that splits text, summarizes chunks, merges them, and iteratively refines the output until it meets length constraints.

## 📂 Project Structure

```text
/app
    ├── main.py           # API Entrypoint & Graph Definitions
    ├── engine.py         # The Graph Execution Engine (The "Brain")
    ├── models.py         # Pydantic Models for State & API
    └── tools.py          # Business Logic (Split, Summarize, Refine)
requirements.txt          # Project Dependencies
README.md                 # Documentation
```

## 🚀 Setup & Installation

1. Clone the repository
```bash
git clone [https://github.com/SaiSanthosh1508/WorkFlow-Agent-Engine.git](https://github.com/SaiSanthosh1508/WorkFlow-Agent-Engine.git)
cd WorkFlow-Agent-Engine
```

2. Install Dependencies
```bash
pip install -r requirements.txt
```

3. Run the server
```bash
uvicorn app.main:app --reload
```

## 🧪 How to Test (The Summarization Agent)

The engine comes pre-seeded with the `summary-agent` workflow.

The Workflow Logic:

Split: Divides text into chunks.

Summarize: Generates summaries for each chunk.

Merge: Combines chunk summaries.

Refine (Loop): Iteratively shortens the summary until it meets the specific length/sentence count criteria.

Step 1: Trigger the Workflow
Run this command to send a long text to the agent:
```bash
curl -X POST "[http://127.0.0.1:8000/graph/run](http://127.0.0.1:8000/graph/run)" \
-H "Content-Type: application/json" \
-d '{
  "graph_id": "summary-agent",
  "initial_state": {
    "original_text": "Artificial intelligence is intelligence demonstrated by machines, as opposed to the natural intelligence displayed by humans or animals. Leading AI textbooks define the field as the study of intelligent agents: any system that perceives its environment and takes actions that maximize its chance of achieving its goals. Some popular accounts use the term artificial intelligence to describe machines that mimic cognitive functions that humans associate with the human mind, such as learning and problem solving, however, this definition is rejected by major AI researchers."
  }
}'
```

Response:
```json
{
    "run_id": "70325a50-57b9...",
    "status": "QUEUED"
}
```
Step 2: Check Results
Use the run_id received above to check the status. The agent runs in the background.

```bash
curl "[http://127.0.0.1:8000/graph/run/](http://127.0.0.1:8000/graph/run/){YOUR_RUN_ID}"
```

### ⚡ Advanced: Create Custom Graph via JSON
The engine is dynamic. You can define new workflows without changing code by sending a JSON blueprint to /graph/create.

Example: A Simple Split-Merge Pipeline (No Loop)

```bash
curl -X POST "[http://127.0.0.1:8000/graph/create](http://127.0.0.1:8000/graph/create)" \
-H "Content-Type: application/json" \
-d '{
  "nodes": [
    {"name": "step1", "tool_name": "split"},
    {"name": "step2", "tool_name": "merge"}
  ],
  "edges": [
    {"from_node": "step1", "to_node": "step2"}
  ],
  "start_node": "step1"
}'
```

This returns a graph_id that you can use immediately in the /graph/run endpoint.
