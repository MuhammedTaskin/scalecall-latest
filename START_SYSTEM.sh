#!/bin/bash

# TEKNOFEST 2025 - System Startup Script  
# Production deployment script for Enterprise Telco AI Platform

echo "╔════════════════════════════════════════════════════════════╗"
echo "║  TEKNOFEST 2025 - ENTERPRISE TELCO AI PLATFORM            ║"
echo "║  Starting Production System...                             ║"
echo "╚════════════════════════════════════════════════════════════╝"

# Check if Colab model URL is provided
COLAB_URL=""
if [ "$1" != "" ]; then
    COLAB_URL="$1"
    echo "🤖 Connecting to Colab model: $COLAB_URL"
else
    echo "🤖 Running in standalone mode (no external model)"
fi

# Check dependencies
echo "📦 Checking dependencies..."
python3 -c "import aiohttp, sqlite3; print(\"✅ All dependencies available\")" 2>/dev/null || {
    echo "❌ Missing dependencies. Installing..."
    pip install -r requirements.txt
}

# Check TTS model
if [ -f "tr_TR-fahrettin-medium.onnx" ]; then
    echo "🔊 Turkish TTS model found"
else
    echo "⚠️  Turkish TTS model not found - audio responses disabled"
fi

# Check database
if [ -f "telco_production.db" ]; then
    echo "💾 Production database found"
else
    echo "💾 Creating production database..."
    python3 -c "from database_config import get_database; get_database()"
fi

# Kill any existing processes
echo "🔄 Stopping existing processes..."
pkill -f "ENTERPRISE_TELCO_PLATFORM.py" 2>/dev/null || true
pkill -f "python.*8000" 2>/dev/null || true

# Start the system
echo "🚀 Starting Enterprise Telco AI Platform..."
if [ "$COLAB_URL" != "" ]; then
    python3 ENTERPRISE_TELCO_PLATFORM.py "$COLAB_URL"
else
    python3 ENTERPRISE_TELCO_PLATFORM.py
fi
