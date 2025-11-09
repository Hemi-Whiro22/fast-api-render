#!/bin/bash

# Test runner for Tiwhanawhana FastAPI backend
# Usage: ./run_tests.sh

echo "🧪 Tiwhanawhana API Test Runner"
echo "================================"

# Check if we're in the correct directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this from the backend directory"
    echo "   Expected to find main.py in current directory"
    exit 1
fi

# Check if tests directory exists
if [ ! -d "tests" ]; then
    echo "❌ Error: tests directory not found"
    exit 1
fi

# Load environment variables from .env if it exists
if [ -f ".env" ]; then
    echo "📋 Loading environment variables from .env..."
    set -a
    source .env
    set +a
else
    echo "⚠️  No .env file found - using system environment variables"
fi

# Run the tests
echo "🚀 Running endpoint tests..."
echo ""

python -m tests.test_all_endpoints

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "🎉 All tests completed successfully!"
else
    echo "⚠️  Some tests failed. Check the output above for details."
fi

exit $TEST_EXIT_CODE