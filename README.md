# WorkFlow Agent Engine

A simplified workflow engine similar to LangGraph that allows you to define, connect, and execute sequences of steps (nodes) with shared state management.

## Features

- **Node-based Architecture**: Define individual steps as nodes with custom functions
- **Conditional Edges**: Connect nodes with optional conditions for dynamic flow control
- **Shared State Management**: Maintain state across all nodes in the workflow
- **REST API**: Full API support for creating and executing workflows
- **Execution History**: Track execution flow and node status
- **Built-in Functions**: Pre-defined node functions for common operations

## Architecture

The engine consists of three main components:

1. **Node**: Represents a single step with an executable function
2. **Edge**: Connects nodes with optional conditional logic
3. **Workflow**: Manages the graph of nodes and orchestrates execution

## Installation

```bash
# Clone the repository
git clone https://github.com/SaiSanthosh1508/WorkFlow-Agent-Engine.git
cd WorkFlow-Agent-Engine

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Running Examples

```bash
# Run example workflows
python examples.py
```

### Starting the API Server

```bash
# Start the FastAPI server
python api.py

# Or using uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`. Visit `http://localhost:8000/docs` for interactive API documentation.

## Usage

### Programmatic Usage

```python
from workflow_engine import Workflow, Node, Edge

# Create a workflow
workflow = Workflow(name="my_workflow")

# Define node functions
def step1(state):
    state["counter"] = 0
    return state

def step2(state):
    state["counter"] += 10
    return state

# Add nodes
workflow.add_node(Node("start", step1, "Initialize"))
workflow.add_node(Node("process", step2, "Process"))

# Connect nodes
workflow.add_edge(Edge("start", "process"))

# Set entry point and end nodes
workflow.set_entry_point("start")
workflow.add_end_node("process")

# Execute workflow
final_state = workflow.execute({"initial_value": 100})
print(final_state)
```

### API Usage

#### 1. Create a Workflow

```bash
curl -X POST "http://localhost:8000/workflow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "example_workflow",
    "nodes": [
      {
        "node_id": "start",
        "name": "Initialize",
        "function_type": "set_value",
        "function_params": {"key": "message", "value": "Hello"}
      },
      {
        "node_id": "transform",
        "name": "Transform",
        "function_type": "transform",
        "function_params": {
          "input_key": "message",
          "output_key": "result",
          "operation": "uppercase"
        }
      }
    ],
    "edges": [
      {"from_node": "start", "to_node": "transform"}
    ],
    "start_node": "start",
    "end_nodes": ["transform"]
  }'
```

#### 2. Execute a Workflow

```bash
curl -X POST "http://localhost:8000/workflow/{workflow_id}/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_state": {"user": "Alice"}
  }'
```

#### 3. Get Workflow State

```bash
curl -X GET "http://localhost:8000/workflow/{workflow_id}/state"
```

#### 4. Get Workflow Status

```bash
curl -X GET "http://localhost:8000/workflow/{workflow_id}/status"
```

#### 5. List All Workflows

```bash
curl -X GET "http://localhost:8000/workflows"
```

## Built-in Function Types

### set_value
Sets a static value in the state.
```json
{
  "function_type": "set_value",
  "function_params": {
    "key": "name",
    "value": "John"
  }
}
```

### transform
Transforms a value using an operation.
```json
{
  "function_type": "transform",
  "function_params": {
    "input_key": "text",
    "output_key": "result",
    "operation": "uppercase"
  }
}
```

Supported operations: `uppercase`, `lowercase`, `double`, `increment`, `append`

### aggregate
Aggregates multiple values.
```json
{
  "function_type": "aggregate",
  "function_params": {
    "input_keys": ["value1", "value2", "value3"],
    "output_key": "total",
    "operation": "sum"
  }
}
```

Supported operations: `sum`, `product`, `concat`, `list`

### custom
Custom pass-through function.
```json
{
  "function_type": "custom",
  "function_params": {
    "message": "Custom logic executed"
  }
}
```

## Conditional Edges

### key_equals
Edge is followed if a key equals a specific value.
```json
{
  "condition_type": "key_equals",
  "condition_params": {
    "key": "status",
    "value": "approved"
  }
}
```

### key_exists
Edge is followed if a key exists in state.
```json
{
  "condition_type": "key_exists",
  "condition_params": {
    "key": "user_id"
  }
}
```

### key_greater_than
Edge is followed if a key's value is greater than a threshold.
```json
{
  "condition_type": "key_greater_than",
  "condition_params": {
    "key": "score",
    "threshold": 80
  }
}
```

## Examples

### Simple Linear Workflow
```python
workflow = example_simple_workflow()
result = workflow.execute()
# Output: {'counter': 10, 'message': 'HELLO', 'result': 'HELLO - Counter: 10'}
```

### Conditional Branching
```python
workflow = example_conditional_workflow()
result = workflow.execute({"input_score": 95})
# Output: {'score': 95, 'result': 'HIGH: You passed with flying colors!', 'grade': 'A'}
```

### Data Processing Pipeline
```python
workflow = example_data_processing_workflow()
result = workflow.execute({"input_data": [10, 20, 30, 40, 50]})
# Output: {'raw_data': [10, 20, 30, 40, 50], 'valid': True, 
#          'transformed_data': [20, 40, 60, 80, 100], 
#          'sum': 300, 'count': 5, 'average': 60.0}
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API information |
| POST | `/workflow/create` | Create a new workflow |
| POST | `/workflow/{id}/execute` | Execute a workflow |
| GET | `/workflow/{id}/state` | Get current state |
| GET | `/workflow/{id}/status` | Get execution status |
| GET | `/workflows` | List all workflows |
| DELETE | `/workflow/{id}` | Delete a workflow |

## Project Structure

```
WorkFlow-Agent-Engine/
├── workflow_engine.py  # Core workflow engine (Node, Edge, Workflow)
├── api.py             # FastAPI REST API
├── examples.py        # Example workflows
├── requirements.txt   # Python dependencies
├── .gitignore        # Git ignore rules
└── README.md         # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.