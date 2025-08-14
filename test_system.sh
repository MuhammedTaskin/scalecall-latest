#!/bin/bash

echo "🚀 COMPLETE SYSTEM TEST"
echo "======================"
echo ""

echo "1️⃣  TESTING API ENDPOINTS"
echo "-------------------------"

# Test health endpoint
echo "🧪 Testing Health Check..."
curl -s http://localhost:8000/health
echo ""
echo ""

# Test OpenAPI
echo "🧪 Testing API Documentation..."
curl -s http://localhost:8000/openapi.json | head -c 200
echo "..."
echo ""

# Test auth-protected endpoint (should return 401)
echo "🧪 Testing LLM Chat (should require auth)..."
curl -s -X POST -H "Content-Type: application/json" http://localhost:8000/api/llm/chat
echo ""
echo ""

echo "2️⃣  CHECKING CONFIGURATION" 
echo "--------------------------"

# Check API key status
if grep -q "AIzaSyATHQOhKjQT0RweOQ-PF3lqT0uzlGKx0nc" .env; then
    echo "⚠️  Gemini API Key: Using placeholder - needs real key"
    echo "   🔧 Get key from: https://makersuite.google.com/"
    echo "   🔧 Update with: ./update_api_key.sh YOUR_KEY"
else
    echo "✅ Gemini API Key: Configured"
fi

echo ""
echo "📋 Current LLM Provider: $(grep LLM_PROVIDER .env)"
echo ""

echo "3️⃣  STARTING FRONTEND"
echo "--------------------"

# Start frontend
cd frontend
echo "🚀 Starting frontend on http://localhost:5173..."
npm run dev &
cd ..

echo ""
echo "⏳ Waiting for frontend to start..."
sleep 5

if curl -s http://localhost:5173 > /dev/null; then
    echo "✅ Frontend: Running successfully"
else
    echo "⏳ Frontend: Still starting up..."
fi

echo ""
echo "🎉 ACCESS POINTS:"
echo "   • Frontend:    http://localhost:5173"
echo "   • Backend:     http://localhost:8000"
echo "   • API Docs:    http://localhost:8000/docs"
echo "   • Supabase UI: http://127.0.0.1:54323"
