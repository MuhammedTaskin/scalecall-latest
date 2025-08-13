#!/bin/bash

echo "🚀 Setting up Scalecall Telco Agent..."
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3.11+ is required"
    exit 1
fi

python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $python_version found"

# Check Node.js version
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 18+ is required"
    exit 1
fi

node_version=$(node -v)
echo "✅ Node.js $node_version found"

# Setup backend
echo ""
echo "🔧 Setting up backend..."
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Initializing database..."
python -c "from backend.db import init_db; init_db()"

# Setup frontend
echo ""
echo "🎨 Setting up frontend..."
cd frontend
echo "Installing Node.js dependencies..."
npm install
cd ..

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the application:"
echo "1. Backend: cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload"
echo "2. Frontend: cd frontend && npm run dev"
echo "3. Open: http://localhost:5173"
echo ""
echo "📖 See README.md for full documentation and demo script"
