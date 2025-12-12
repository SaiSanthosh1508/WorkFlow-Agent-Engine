#!/bin/bash
# Comprehensive test suite for the Workflow Agent Engine

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║        WORKFLOW AGENT ENGINE - COMPREHENSIVE TEST SUITE            ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    
    echo -e "${BLUE}[TEST]${NC} $test_name"
    
    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC} $test_name"
        ((TESTS_PASSED++))
        return 0
    else
        echo -e "${RED}[FAIL]${NC} $test_name"
        ((TESTS_FAILED++))
        return 1
    fi
}

echo "═══════════════════════════════════════════════════════════════════"
echo "1. Testing Core Workflow Engine (Programmatic)"
echo "═══════════════════════════════════════════════════════════════════"

run_test "Basic examples execution" "python examples.py"
run_test "Advanced content moderation example" "python example_advanced.py"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "2. Testing API Server"
echo "═══════════════════════════════════════════════════════════════════"

# Check if API server is running
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo -e "${RED}[ERROR]${NC} API server is not running on port 8000"
    echo "Please start the server with: ./start_server.sh"
    exit 1
fi

run_test "API root endpoint" "curl -s http://localhost:8000/ | grep -q 'Workflow Agent Engine'"
run_test "API workflow creation" "curl -s -X POST 'http://localhost:8000/workflow/create' -H 'Content-Type: application/json' -d '{\"name\":\"test\",\"nodes\":[{\"node_id\":\"n1\",\"function_type\":\"custom\",\"function_params\":{}}],\"edges\":[],\"start_node\":\"n1\",\"end_nodes\":[\"n1\"]}' | grep -q 'workflow_id'"
run_test "API workflows listing" "curl -s http://localhost:8000/workflows | grep -q 'workflows'"

echo ""
echo "═══════════════════════════════════════════════════════════════════"
echo "3. Integration Tests"
echo "═══════════════════════════════════════════════════════════════════"

run_test "Conditional workflow test" "./test_conditional.sh > /dev/null 2>&1"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║                          TEST SUMMARY                              ║"
echo "╠════════════════════════════════════════════════════════════════════╣"
echo -e "║ ${GREEN}Tests Passed:${NC} $TESTS_PASSED                                                 "
echo -e "║ ${RED}Tests Failed:${NC} $TESTS_FAILED                                                 "
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed successfully!${NC}"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the output above.${NC}"
    exit 1
fi
