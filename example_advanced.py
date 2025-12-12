"""
Advanced example: Content moderation workflow
Demonstrates a realistic use case with conditional routing, state management, and error handling.
"""
from workflow_engine import Workflow, Node, Edge


def create_content_moderation_workflow():
    """
    Create a content moderation workflow that:
    1. Receives content for review
    2. Checks content length
    3. Routes to appropriate moderation path
    4. Applies different rules based on content type
    5. Returns moderation decision
    """
    workflow = Workflow(name="content_moderation")
    
    # Node 1: Initialize and validate input
    def validate_input(state):
        content = state.get("content", "")
        state["content_length"] = len(content)
        state["has_content"] = len(content) > 0
        return state
    
    # Node 2: Short content quick review
    def quick_review(state):
        content = state.get("content", "").lower()
        # Simple keyword check for short content
        bad_words = ["spam", "abuse", "hate"]
        state["flagged"] = any(word in content for word in bad_words)
        state["review_type"] = "quick"
        return state
    
    # Node 3: Long content detailed review
    def detailed_review(state):
        content = state.get("content", "").lower()
        # More thorough check for long content
        bad_words = ["spam", "abuse", "hate", "violence", "illegal"]
        flag_count = sum(1 for word in bad_words if word in content)
        state["flagged"] = flag_count > 0
        state["flag_count"] = flag_count
        state["review_type"] = "detailed"
        return state
    
    # Node 4: Approve content
    def approve_content(state):
        state["decision"] = "approved"
        state["message"] = f"Content approved ({state.get('review_type', 'unknown')} review)"
        return state
    
    # Node 5: Reject content
    def reject_content(state):
        state["decision"] = "rejected"
        reason = f"{state.get('flag_count', 1)} violations found" if state.get("flag_count") else "policy violation"
        state["message"] = f"Content rejected: {reason}"
        return state
    
    # Node 6: Handle empty content
    def handle_empty(state):
        state["decision"] = "rejected"
        state["message"] = "No content provided"
        return state
    
    # Add nodes
    workflow.add_node(Node("validate", validate_input, "Validate Input"))
    workflow.add_node(Node("quick_review", quick_review, "Quick Review"))
    workflow.add_node(Node("detailed_review", detailed_review, "Detailed Review"))
    workflow.add_node(Node("approve", approve_content, "Approve Content"))
    workflow.add_node(Node("reject", reject_content, "Reject Content"))
    workflow.add_node(Node("empty", handle_empty, "Handle Empty"))
    
    # Add conditional edges
    # From validate: check if content exists
    def has_content(state):
        return state.get("has_content", False)
    
    def no_content(state):
        return not state.get("has_content", True)
    
    workflow.add_edge(Edge("validate", "quick_review", lambda s: has_content(s) and s.get("content_length", 0) <= 100))
    workflow.add_edge(Edge("validate", "detailed_review", lambda s: has_content(s) and s.get("content_length", 0) > 100))
    workflow.add_edge(Edge("validate", "empty", no_content))
    
    # From review nodes: approve or reject
    def not_flagged(state):
        return not state.get("flagged", True)
    
    def is_flagged(state):
        return state.get("flagged", False)
    
    workflow.add_edge(Edge("quick_review", "approve", not_flagged))
    workflow.add_edge(Edge("quick_review", "reject", is_flagged))
    workflow.add_edge(Edge("detailed_review", "approve", not_flagged))
    workflow.add_edge(Edge("detailed_review", "reject", is_flagged))
    
    # Set entry and end points
    workflow.set_entry_point("validate")
    workflow.add_end_node("approve")
    workflow.add_end_node("reject")
    workflow.add_end_node("empty")
    
    return workflow


def run_moderation_tests():
    """Run various test cases for content moderation."""
    print("=" * 70)
    print("CONTENT MODERATION WORKFLOW - ADVANCED EXAMPLE")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Short clean content",
            "content": "This is a nice message about puppies"
        },
        {
            "name": "Short flagged content",
            "content": "This is spam content"
        },
        {
            "name": "Long clean content",
            "content": "This is a longer message that talks about many different topics including technology, science, and nature. " * 3
        },
        {
            "name": "Long flagged content",
            "content": "This is a longer message that contains spam and abuse and other violations. " * 3
        },
        {
            "name": "Empty content",
            "content": ""
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print("-" * 70)
        
        workflow = create_content_moderation_workflow()
        result = workflow.execute({"content": test["content"]})
        
        print(f"Content Length: {result.get('content_length', 0)}")
        print(f"Review Type: {result.get('review_type', 'N/A')}")
        print(f"Decision: {result.get('decision', 'unknown')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        print("\nExecution Path:")
        for entry in workflow.execution_history:
            print(f"  → {entry['node_name']}")
    
    print("\n" + "=" * 70)
    print("All moderation tests completed!")
    print("=" * 70)


if __name__ == "__main__":
    run_moderation_tests()
