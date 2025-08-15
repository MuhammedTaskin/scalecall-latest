#!/bin/bash

echo "=========================================="
echo "TEKNOFEST 2025 - COMPLETE SYSTEM LAUNCHER"
echo "=========================================="

# Check if Colab URL is provided
if [ -z "$1" ]; then
    echo "⚠️  No Colab URL provided - Running without AI model"
    echo ""
    echo "To connect your trained model:"
    echo "1. Run SERVE_MODEL_FROM_DRIVE.ipynb in Colab"
    echo "2. Copy the ngrok URL"
    echo "3. Run: ./RUN_COMPLETE_SYSTEM.sh https://your-ngrok-url.ngrok.io"
    echo ""
    echo "Starting in standalone mode..."
    python3 ENTERPRISE_TELCO_PLATFORM.py
else
    echo "✅ Connecting to Colab model at: $1"
    echo ""
    echo "Starting with AI model integration..."
    python3 ENTERPRISE_TELCO_PLATFORM.py "$1"
fi