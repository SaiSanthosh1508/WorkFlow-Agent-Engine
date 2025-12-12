"""
Example workflows demonstrating the Workflow Agent Engine capabilities.
"""
from workflow_engine import Workflow, Node, Edge


def example_simple_workflow():
    """
    Create a simple linear workflow.
    
    This workflow demonstrates:
    - Sequential node execution
    - State transformation
    - Basic workflow structure
    """
    workflow = Workflow(name="simple_example")
    
    # Node 1: Initialize data
    def init_node(state):
        state["counter"] = 0
        state["message"] = "hello"
        return state
    
    # Node 2: Transform data
    def transform_node(state):
        state["counter"] += 10
        state["message"] = state["message"].upper()
        return state
    
    # Node 3: Final processing
    def final_node(state):
        state["result"] = f"{state['message']} - Counter: {state['counter']}"
        return state
    
    # Add nodes
    workflow.add_node(Node("init", init_node, "Initialize"))
    workflow.add_node(Node("transform", transform_node, "Transform"))
    workflow.add_node(Node("final", final_node, "Finalize"))
    
    # Add edges
    workflow.add_edge(Edge("init", "transform"))
    workflow.add_edge(Edge("transform", "final"))
    
    # Set entry and end points
    workflow.set_entry_point("init")
    workflow.add_end_node("final")
    
    return workflow


def example_conditional_workflow():
    """
    Create a workflow with conditional branching.
    
    This workflow demonstrates:
    - Conditional edges based on state
    - Multiple execution paths
    - Branching logic
    """
    workflow = Workflow(name="conditional_example")
    
    # Node 1: Initialize with a score
    def init_node(state):
        state["score"] = state.get("input_score", 50)
        return state
    
    # Node 2: High score path
    def high_score_node(state):
        state["result"] = "HIGH: You passed with flying colors!"
        state["grade"] = "A"
        return state
    
    # Node 3: Low score path
    def low_score_node(state):
        state["result"] = "LOW: Need improvement"
        state["grade"] = "F"
        return state
    
    # Node 4: Medium score path
    def medium_score_node(state):
        state["result"] = "MEDIUM: Acceptable performance"
        state["grade"] = "C"
        return state
    
    # Add nodes
    workflow.add_node(Node("init", init_node, "Initialize Score"))
    workflow.add_node(Node("high", high_score_node, "High Score"))
    workflow.add_node(Node("medium", medium_score_node, "Medium Score"))
    workflow.add_node(Node("low", low_score_node, "Low Score"))
    
    # Add conditional edges
    def is_high_score(state):
        return state.get("score", 0) >= 80
    
    def is_medium_score(state):
        score = state.get("score", 0)
        return 50 <= score < 80
    
    def is_low_score(state):
        return state.get("score", 0) < 50
    
    workflow.add_edge(Edge("init", "high", is_high_score))
    workflow.add_edge(Edge("init", "medium", is_medium_score))
    workflow.add_edge(Edge("init", "low", is_low_score))
    
    # Set entry point and end nodes
    workflow.set_entry_point("init")
    workflow.add_end_node("high")
    workflow.add_end_node("medium")
    workflow.add_end_node("low")
    
    return workflow


def example_data_processing_workflow():
    """
    Create a workflow for data processing pipeline.
    
    This workflow demonstrates:
    - Data collection
    - Data validation
    - Data transformation
    - Data aggregation
    """
    workflow = Workflow(name="data_processing_example")
    
    # Node 1: Collect data
    def collect_data(state):
        state["raw_data"] = state.get("input_data", [1, 2, 3, 4, 5])
        return state
    
    # Node 2: Validate data
    def validate_data(state):
        data = state.get("raw_data", [])
        state["valid"] = len(data) > 0 and all(isinstance(x, (int, float)) for x in data)
        return state
    
    # Node 3: Transform data
    def transform_data(state):
        if state.get("valid", False):
            data = state.get("raw_data", [])
            state["transformed_data"] = [x * 2 for x in data]
        return state
    
    # Node 4: Aggregate results
    def aggregate_data(state):
        if state.get("valid", False):
            data = state.get("transformed_data", [])
            state["sum"] = sum(data)
            state["count"] = len(data)
            state["average"] = state["sum"] / state["count"] if state["count"] > 0 else 0
        return state
    
    # Node 5: Handle invalid data
    def handle_invalid(state):
        state["error"] = "Invalid data provided"
        return state
    
    # Add nodes
    workflow.add_node(Node("collect", collect_data, "Collect Data"))
    workflow.add_node(Node("validate", validate_data, "Validate Data"))
    workflow.add_node(Node("transform", transform_data, "Transform Data"))
    workflow.add_node(Node("aggregate", aggregate_data, "Aggregate Data"))
    workflow.add_node(Node("error", handle_invalid, "Handle Error"))
    
    # Add edges
    workflow.add_edge(Edge("collect", "validate"))
    
    def is_valid(state):
        return state.get("valid", False)
    
    def is_invalid(state):
        return not state.get("valid", True)
    
    workflow.add_edge(Edge("validate", "transform", is_valid))
    workflow.add_edge(Edge("validate", "error", is_invalid))
    workflow.add_edge(Edge("transform", "aggregate"))
    
    # Set entry point and end nodes
    workflow.set_entry_point("collect")
    workflow.add_end_node("aggregate")
    workflow.add_end_node("error")
    
    return workflow


def run_examples():
    """Run all example workflows."""
    print("=" * 60)
    print("WORKFLOW AGENT ENGINE - EXAMPLES")
    print("=" * 60)
    
    # Example 1: Simple workflow
    print("\n1. Simple Linear Workflow")
    print("-" * 60)
    workflow1 = example_simple_workflow()
    result1 = workflow1.execute()
    print(f"Final State: {result1}")
    print(f"Status: {workflow1.status.value}")
    
    # Example 2: Conditional workflow - High score
    print("\n2. Conditional Workflow - High Score")
    print("-" * 60)
    workflow2a = example_conditional_workflow()
    result2a = workflow2a.execute({"input_score": 95})
    print(f"Final State: {result2a}")
    
    # Example 2b: Conditional workflow - Low score
    print("\n3. Conditional Workflow - Low Score")
    print("-" * 60)
    workflow2b = example_conditional_workflow()
    result2b = workflow2b.execute({"input_score": 30})
    print(f"Final State: {result2b}")
    
    # Example 3: Data processing workflow
    print("\n4. Data Processing Workflow")
    print("-" * 60)
    workflow3 = example_data_processing_workflow()
    result3 = workflow3.execute({"input_data": [10, 20, 30, 40, 50]})
    print(f"Final State: {result3}")
    print(f"Execution History:")
    for entry in workflow3.execution_history:
        print(f"  - {entry['node_name']}: {entry['status']}")
    
    print("\n" + "=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_examples()
