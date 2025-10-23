#!/bin/bash
# Start the Query API Server

echo "🚀 Starting Query API Server..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   - SERPAPI_KEY (required)"
    echo "   - ES_CLOUD_ID and ES_API_KEY (if using Elastic Cloud)"
    echo "   - GCP_MODEL_ENDPOINT (when available)"
    echo ""
    read -p "Press Enter when ready to continue..."
fi

# Start the server
echo ""
echo "✨ Starting API server on http://localhost:5000"
echo "🔍 Health check: http://localhost:5000/health"
echo ""
python api_server.py

