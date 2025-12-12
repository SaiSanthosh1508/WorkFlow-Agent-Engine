#!/bin/bash
# Simple startup script for the Workflow Agent Engine API

echo "Starting Workflow Agent Engine..."
echo "API will be available at: http://localhost:8000"
echo "API documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python api.py
