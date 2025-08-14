#!/bin/bash

echo "🔑 Gemini API Key Setup Script"
echo ""

# Check if API key is provided as argument
if [ "$1" != "" ]; then
    API_KEY="$1"
    echo "✅ Using provided API key: ${API_KEY:0:10}..."
    
    # Update the .env file
    sed -i.bak "s/GEMINI_API_KEY=AIzaSyATHQOhKjQT0RweOQ-PF3lqT0uzlGKx0nc/GEMINI_API_KEY=$API_KEY/" .env
    
    echo "✅ Updated .env file with your Gemini API key"
    echo ""
    
    # Verify the update
    echo "📝 Updated configuration:"
    grep "GEMINI_API_KEY" .env
    echo ""
    
    echo "🔄 Restarting backend to use new API key..."
    pkill -f uvicorn
    sleep 2
    
    cd backend && source ../.env && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload &
    cd ..
    
    echo "⏳ Waiting for backend to restart..."
    sleep 5
    
    # Test the backend
    echo "🧪 Testing backend with new API key..."
    curl -s http://localhost:8000/health
    echo ""
    
else
    echo "❌ Please provide your Gemini API key as an argument"
    echo ""
    echo "Usage: ./update_api_key.sh YOUR_GEMINI_API_KEY"
    echo ""
    echo "To get your API key:"
    echo "1. Go to: https://makersuite.google.com/"
    echo "2. Sign in with Google"
    echo "3. Create an API key"
    echo "4. Run: ./update_api_key.sh YOUR_KEY_HERE"
    echo ""
    exit 1
fi

echo "✅ Setup complete! Your backend is now using Gemini 2.5 Flash"
