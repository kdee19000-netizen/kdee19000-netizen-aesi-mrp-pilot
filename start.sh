#!/bin/bash
# Startup script for AESI-MRP system

echo "=========================================="
echo "AESI-MRP System Startup"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

echo "✓ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

echo "✓ pip3 found"

# Install dependencies if needed
echo ""
echo "Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "=========================================="
echo "Starting Backend API..."
echo "=========================================="
echo ""

# Start the backend API
python3 -m backend.api &
API_PID=$!

echo "Backend API started (PID: $API_PID)"
echo "API available at: http://localhost:8000"

# Wait for API to be ready
echo "Waiting for API to be ready..."
sleep 3

# Check if API is running
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend API is running"
else
    echo "⚠ Warning: Backend API may not be fully started yet"
fi

echo ""
echo "=========================================="
echo "Starting Streamlit Dashboard..."
echo "=========================================="
echo ""

# Start the dashboard
streamlit run frontend/dashboard.py &
DASHBOARD_PID=$!

echo "Dashboard started (PID: $DASHBOARD_PID)"

echo ""
echo "=========================================="
echo "AESI-MRP System is now running!"
echo "=========================================="
echo ""
echo "Backend API:    http://localhost:8000"
echo "API Docs:       http://localhost:8000/docs"
echo "Dashboard:      Will open in browser automatically"
echo ""
echo "To stop the system, press Ctrl+C"
echo ""

# Wait for user to stop
wait
