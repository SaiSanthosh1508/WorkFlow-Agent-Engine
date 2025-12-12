#!/bin/bash
# Advanced test demonstrating conditional workflow via API

echo "======================================"
echo "Testing Conditional Workflow"
echo "======================================"

# Create a conditional workflow (score grading system)
echo -e "\n1. Creating conditional workflow..."
WORKFLOW_RESPONSE=$(curl -s -X POST "http://localhost:8000/workflow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "score_grading_workflow",
    "nodes": [
      {
        "node_id": "init",
        "name": "Initialize",
        "function_type": "custom",
        "function_params": {"message": "Starting grading"}
      },
      {
        "node_id": "high_grade",
        "name": "High Grade",
        "function_type": "aggregate",
        "function_params": {
          "input_keys": ["score"],
          "output_key": "result",
          "operation": "concat"
        }
      },
      {
        "node_id": "high_grade_msg",
        "name": "Set High Message",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "A - Excellent!", "force": true}
      },
      {
        "node_id": "medium_grade",
        "name": "Medium Grade",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "C - Acceptable", "force": true}
      },
      {
        "node_id": "low_grade",
        "name": "Low Grade",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "F - Failed", "force": true}
      }
    ],
    "edges": [
      {
        "from_node": "init",
        "to_node": "high_grade",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 79}
      },
      {
        "from_node": "high_grade",
        "to_node": "high_grade_msg"
      },
      {
        "from_node": "init",
        "to_node": "medium_grade",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 49}
      },
      {
        "from_node": "init",
        "to_node": "low_grade",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": -1}
      }
    ],
    "start_node": "init",
    "end_nodes": ["high_grade_msg", "medium_grade", "low_grade"]
  }')

echo "$WORKFLOW_RESPONSE" | python3 -m json.tool
WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_id'])")

# Test with high score
echo -e "\n2. Testing with high score (95)..."
RESULT_HIGH=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 95}}')
echo "$RESULT_HIGH" | python3 -m json.tool

# Test with medium score
echo -e "\n3. Testing with medium score (65)..."
RESULT_MED=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 65}}')
echo "$RESULT_MED" | python3 -m json.tool

# Test with low score
echo -e "\n4. Testing with low score (30)..."
RESULT_LOW=$(curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 30}}')
echo "$RESULT_LOW" | python3 -m json.tool

echo -e "\n======================================"
echo "Conditional workflow test completed!"
echo "======================================"
