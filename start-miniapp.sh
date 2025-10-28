#!/bin/bash

echo "🚀 Starting Mini App..."

# Start API server in background
echo "📡 Starting API server on port 8000..."
cd /home/runner/workspace
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
API_PID=$!

# Wait a bit for API to start
sleep 3

# Start frontend dev server
echo "🎨 Starting frontend dev server on port 5000..."
cd /home/runner/workspace/webapp
npm run dev

# Cleanup on exit
trap "kill $API_PID" EXIT
