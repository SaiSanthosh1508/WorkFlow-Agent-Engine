#!/bin/bash
# Demonstrates creating and executing a data processing pipeline via API

echo "======================================"
echo "Data Processing Pipeline Example"
echo "======================================"

# Create a multi-stage data processing workflow
echo -e "\n1. Creating data processing pipeline..."
WORKFLOW_RESPONSE=$(curl -s -X POST "http://localhost:8000/workflow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "data_pipeline",
    "nodes": [
      {
        "node_id": "ingest",
        "name": "Ingest Data",
        "function_type": "custom",
        "function_params": {"message": "Data ingested"}
      },
      {
        "node_id": "validate",
        "name": "Validate Data",
        "function_type": "custom",
        "function_params": {"message": "Data validated"}
      },
      {
        "node_id": "transform",
        "name": "Transform Data",
        "function_type": "transform",
        "function_params": {
          "input_key": "raw_value",
          "output_key": "processed_value",
          "operation": "double"
        }
      },
      {
        "node_id": "aggregate",
        "name": "Aggregate Results",
        "function_type": "aggregate",
        "function_params": {
          "input_keys": ["raw_value", "processed_value"],
          "output_key": "summary",
          "operation": "list"
        }
      },
      {
        "node_id": "error_handler",
        "name": "Error Handler",
        "function_type": "set_value",
        "function_params": {
          "key": "status",
          "value": "error",
          "force": true
        }
      },
      {
        "node_id": "success",
        "name": "Success",
        "function_type": "set_value",
        "function_params": {
          "key": "status",
          "value": "success",
          "force": true
        }
      }
    ],
    "edges": [
      {"from_node": "ingest", "to_node": "validate"},
      {
        "from_node": "validate",
        "to_node": "transform",
        "condition_type": "key_exists",
        "condition_params": {"key": "raw_value"}
      },
      {
        "from_node": "validate",
        "to_node": "error_handler",
        "condition_type": "key_exists",
        "condition_params": {"key": "error"}
      },
      {"from_node": "transform", "to_node": "aggregate"},
      {"from_node": "aggregate", "to_node": "success"}
    ],
    "start_node": "ingest",
    "end_nodes": ["success", "error_handler"]
  }')

echo "$WORKFLOW_RESPONSE" | python3 -m json.tool
WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_id'])")
echo "Pipeline ID: $WORKFLOW_ID"

# Test 1: Successful execution
echo -e "\n2. Processing valid data..."
RESULT_SUCCESS=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"raw_value": 42}}')

echo "$RESULT_SUCCESS" | python3 -m json.tool

# Get execution status
echo -e "\n3. Getting pipeline execution status..."
STATUS=$(curl -s -X GET "http://localhost:8000/workflow/$WORKFLOW_ID/status")
echo "$STATUS" | python3 -c "import sys, json; data = json.load(sys.stdin); print('Status:', data['status']); print('Execution History:'); [print(f\"  {i+1}. {h['node_name']} - {h['status']}\") for i, h in enumerate(data['execution_history'])]"

# Test 2: Error case
echo -e "\n4. Processing invalid data (error case)..."
RESULT_ERROR=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"error": "missing data"}}')

echo "$RESULT_ERROR" | python3 -m json.tool | grep -E '"status"|"error"'

echo -e "\n======================================"
echo "Pipeline demo completed!"
echo "======================================"
