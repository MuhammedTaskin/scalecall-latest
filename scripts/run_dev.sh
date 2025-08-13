#!/bin/bash

echo "🚀 Starting Scalecall Telco Agent in Development Mode..."
echo ""

# Function to kill processes on exit
cleanup() {
    echo ""
    echo "🛑 Stopping services..."
    pkill -f "uvicorn"
    pkill -f "vite"
    exit 0
}

# Set up trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
cd backend
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running at http://localhost:8000"
else
    echo "❌ Backend failed to start - check logs/backend.log"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
echo "⏳ Waiting for frontend to start..."
sleep 5

# Check if frontend is running
if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend running at http://localhost:5173"
else
    echo "❌ Frontend failed to start - check logs/frontend.log"
    exit 1
fi

echo ""
echo "🎉 SCALECALL TELCO AGENT IS RUNNING!"
echo ""
echo "📱 Frontend: http://localhost:5173"
echo "🔌 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "🎬 Demo Script:"
echo "1. Merhaba, eSIM almak istiyorum"
echo "2. Adım Ahmet Yılmaz, annemin kızlık soyadı Kaya, numaram 905551234567"
echo "3. IMEI: 123456789012345"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
wait
