#!/bin/bash
# Demonstrates a proper conditional workflow with mutually exclusive conditions

echo "======================================"
echo "Conditional Workflow - Mutually Exclusive Paths"
echo "======================================"

# Create a workflow with properly designed mutually exclusive conditions
echo -e "\n1. Creating workflow with exclusive conditions..."
WORKFLOW_RESPONSE=$(curl -s -X POST "http://localhost:8000/workflow/create" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "exclusive_grading_workflow",
    "nodes": [
      {
        "node_id": "start",
        "name": "Start",
        "function_type": "custom",
        "function_params": {"message": "Evaluating score"}
      },
      {
        "node_id": "evaluate_high",
        "name": "Check High",
        "function_type": "custom",
        "function_params": {"message": "Checking if high score"}
      },
      {
        "node_id": "evaluate_medium",
        "name": "Check Medium",
        "function_type": "custom",
        "function_params": {"message": "Checking if medium score"}
      },
      {
        "node_id": "grade_a",
        "name": "Grade A",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "A - Excellent!", "force": true}
      },
      {
        "node_id": "grade_c",
        "name": "Grade C",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "C - Acceptable", "force": true}
      },
      {
        "node_id": "grade_f",
        "name": "Grade F",
        "function_type": "set_value",
        "function_params": {"key": "grade", "value": "F - Failed", "force": true}
      }
    ],
    "edges": [
      {
        "from_node": "start",
        "to_node": "evaluate_high",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 79}
      },
      {
        "from_node": "start",
        "to_node": "evaluate_medium",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 0}
      },
      {
        "from_node": "evaluate_high",
        "to_node": "grade_a"
      },
      {
        "from_node": "evaluate_medium",
        "to_node": "grade_c",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 49}
      },
      {
        "from_node": "evaluate_medium",
        "to_node": "grade_f",
        "condition_type": "key_greater_than",
        "condition_params": {"key": "score", "threshold": 0}
      }
    ],
    "start_node": "start",
    "end_nodes": ["grade_a", "grade_c", "grade_f"]
  }')

echo "$WORKFLOW_RESPONSE" | python3 -m json.tool
WORKFLOW_ID=$(echo "$WORKFLOW_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['workflow_id'])")

# Test cases
echo -e "\n2. High Score (score=95):"
curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 95}}' | python3 -m json.tool | grep -E '"score"|"grade"'

echo -e "\n3. Medium Score (score=65):"
curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 65}}' | python3 -m json.tool | grep -E '"score"|"grade"'

echo -e "\n4. Low Score (score=30):"
curl -s -X POST "http://localhost:8000/workflow/$WORKFLOW_ID/execute" \
  -H "Content-Type: application/json" \
  -d '{"initial_state": {"score": 30}}' | python3 -m json.tool | grep -E '"score"|"grade"'

echo -e "\n======================================"
