#!/bin/bash
# Quick start script for Mac

set -e  # Exit on any error

echo "🚀 Starting Newsletter API v2 on Mac..."

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

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating template..."
    cat > .env << EOF
# Core Database (required)
DATABASE_URL=postgresql://localhost:5432/newsletter_db

# OpenAI for scoring (required)
OPENAI_API_KEY=your_openai_api_key_here

# Email (optional)
RESEND_API_KEY=
SENDER_EMAIL=newsletter@yourdomain.com
SENDER_NAME=Building the Future

# Google CSE (optional)
GOOGLE_CSE_API_KEY=
GOOGLE_CSE_CX_ID=

# FRED API for macro data (optional)
FRED_API_KEY=

# App Config
SITE_BASE_URL=http://localhost:10000
USER_AGENT=BuildingTheFutureBot/2.0
MAX_ARTICLES_PER_RUN=1000
EOF
    echo "📝 Please edit .env file with your API keys before running"
    echo "💡 Minimum required: DATABASE_URL and OPENAI_API_KEY"
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ PostgreSQL is not running. Please start it:"
    echo "   brew services start postgresql"
    echo "   createdb newsletter_db"
    exit 1
fi

# Start the API server
echo "🌐 Starting FastAPI server on http://localhost:10000"
echo "📚 API docs will be available at http://localhost:10000/docs"
echo "🔍 Health check: http://localhost:10000/health"
echo ""
echo "Press Ctrl+C to stop the server"

uvicorn app.main:web_app --reload --port 10000

