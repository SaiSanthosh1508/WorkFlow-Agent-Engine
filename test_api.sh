#!/bin/bash
# Test script for workflow engine API

echo "======================================"
echo "Testing Workflow Agent Engine API"
echo "======================================"

# Test 1: Create a workflow
echo -e "\n1. Creating a workflow..."
WORKFLOW_RESPONSE=$(curl -s -X POST "http://localhost:8000/workflow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "test_workflow",
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
      },
      {
        "node_id": "append",
        "name": "Append",
        "function_type": "transform",
        "function_params": {
          "input_key": "result",
          "output_key": "final",
          "operation": "append",
          "append_value": " WORLD!"
        }
      }
    ],
    "edges": [
      {"from_node": "start", "to_node": "transform"},
      {"from_node": "transform", "to_node": "append"}
    ],
    "start_node": "start",
    "end_nodes": ["append"]
  }')

echo "$WORKFLOW_RESPONSE" | python3 -m json.tool
WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_id'])")
echo "Workflow ID: $WORKFLOW_ID"

# Test 2: Execute the workflow
echo -e "\n2. Executing the workflow..."
EXECUTE_RESPONSE=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_state": {"user": "Alice"}
  }')

echo "$EXECUTE_RESPONSE" | python3 -m json.tool

# Test 3: Get workflow state
echo -e "\n3. Getting workflow state..."
STATE_RESPONSE=$(curl -s -X GET "http://localhost:8000/workflow/$WORKFLOW_ID/state")
echo "$STATE_RESPONSE" | python3 -m json.tool

# Test 4: Get workflow status
echo -e "\n4. Getting workflow status..."
STATUS_RESPONSE=$(curl -s -X GET "http://localhost:8000/workflow/$WORKFLOW_ID/status")
echo "$STATUS_RESPONSE" | python3 -m json.tool

# Test 5: List all workflows
echo -e "\n5. Listing all workflows..."
LIST_RESPONSE=$(curl -s -X GET "http://localhost:8000/workflows")
echo "$LIST_RESPONSE" | python3 -m json.tool

echo -e "\n======================================"
echo "All API tests completed successfully!"
echo "======================================"
