#!/bin/bash

# 🤖 Gemini Weather Agent - Startup Script
# This script starts the Gemini API server with your API key

echo "🤖 Starting Gemini Weather Agent API Server..."
echo ""

# Load environment variables from .env file
if [ -f .env ]; then
    echo "📄 Loading .env file..."
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  Warning: .env file not found"
    echo "Looking for GEMINI_API_KEY in environment..."
fi

# Check if API key is set (from .env or environment)
if [ -z "$GEMINI_API_KEY" ]; then
    echo ""
    echo "❌ ERROR: GEMINI_API_KEY not found!"
    echo ""
    echo "Please either:"
    echo "  1. Edit the .env file and add your API key"
    echo "  2. Export it: export GEMINI_API_KEY='your-key'"
    echo "  3. Pass it as argument: ./start_gemini_server.sh YOUR_API_KEY"
    echo ""
    exit 1
fi

# Allow override via command line argument
if [ ! -z "$1" ]; then
    export GEMINI_API_KEY="$1"
    echo "🔑 Using API key from command line argument"
fi

echo "✅ API Key is set"
echo "🚀 Starting server on http://localhost:8001"
echo "📚 API docs at http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo "================================"
echo ""

# Start the server
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus
/Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/.venv/bin/python gemini_api.py
