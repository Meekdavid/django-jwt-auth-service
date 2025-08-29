#!/bin/bash

# Rate Limiting Test Runner
# This script starts the Django server and runs the rate limiting tests

echo "🧪 AUTH SERVICE RATE LIMITING TEST RUNNER"
echo "=========================================="

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "⚠️ Virtual environment not activated. Activating..."
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate 2>/dev/null
fi

# Start Django development server in background
echo "🚀 Starting Django development server..."
python manage.py runserver 127.0.0.1:8000 &
SERVER_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
sleep 5

# Check if server is running
if ! curl -s http://127.0.0.1:8000/swagger/ > /dev/null; then
    echo "❌ Server failed to start"
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "✅ Server is running, starting tests..."

# Run the rate limiting tests
python scripts/test_rate_limiting.py

# Cleanup: Kill the server
echo "🧹 Cleaning up..."
kill $SERVER_PID 2>/dev/null
wait $SERVER_PID 2>/dev/null

echo "✅ Tests completed!"
