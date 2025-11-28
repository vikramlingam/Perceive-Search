#!/bin/bash

# Function to kill background processes on exit
cleanup() {
    echo "Stopping Perceive..."
    kill $(jobs -p) 2>/dev/null
    exit
}

# Trap Ctrl+C
trap cleanup SIGINT

echo "🚀 Starting Perceive..."

# Start Backend
echo "Starting Backend on port 5001..."
cd backend
python3 -um app --host 0.0.0.0 --port 5001 &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready (simple sleep)
sleep 2

# Start Frontend
echo "Starting Frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ Perceive is running!"
echo "Backend: http://localhost:5001"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop."

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
