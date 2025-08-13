#!/bin/bash

# Telco Agent Local Development Script

set -e

echo "🚀 Starting Telco Agent..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install/update dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Create necessary directories
mkdir -p backend/audio_cache
mkdir -p reports

# Start backend server in background
echo "Starting FastAPI backend..."
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 3

# Start frontend development server
echo "Starting React frontend..."
cd frontend
npm install
npm run dev &
FRONTEND_PID=$!

echo ""
echo "✅ Telco Agent is running!"
echo ""
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend:  http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Function to cleanup processes
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    wait 2>/dev/null || true
    echo "✅ All services stopped"
    exit 0
}

# Setup signal handlers
trap cleanup INT TERM

# Wait for processes
wait
