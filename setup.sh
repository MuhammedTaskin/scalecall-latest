#!/bin/bash

# TEKNOFEST 2025 - Simple Setup Script
# Works on ANY computer with Python 3

echo "======================================"
echo "TEKNOFEST 2025 - Telco AI System Setup"
echo "======================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python 3 found"

# Install minimal dependencies
echo "📦 Installing dependencies..."
pip3 install numpy aiohttp --quiet

echo "✅ Dependencies installed"

# Run the system
echo "🚀 Starting Telco AI System..."
echo "======================================"
python3 SIMPLE_STANDALONE_SYSTEM.py