#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "🚀 Starting Automated Test Suite..."

# --- Backend Tests ---
echo "
🧪 Running Django Backend Tests..."
echo "========================================="

# Navigate to the backend directory
cd "$(dirname "$0")/blackend"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "Activating Python virtual environment..."
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run Django tests
# The --failfast option stops the test run on the first error.
python manage.py test --failfast

echo "✅ Backend tests completed successfully."

# --- Frontend Tests ---
echo "
🧪 Running React Frontend Tests..."
echo "========================================="

# Navigate to the frontend directory
cd "$(dirname "$0")/frontend"

# Run frontend tests using npm
# The -- --watch=false argument ensures Vitest runs once and exits.
npm test -- --watch=false

echo "✅ Frontend tests completed successfully."


echo "
🎉 All tests passed!"
