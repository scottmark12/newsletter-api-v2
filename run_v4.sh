#!/bin/bash

# Newsletter API v4 Startup Script
# This script sets up and runs the complete v4 platform

echo "🚀 Starting Newsletter API v4 Platform"
echo "======================================"

# Check if we're in the right directory
if [ ! -f "app_v4/api.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Set environment variables for development
export DATABASE_URL="sqlite:///./newsletter_v4.db"
export ENVIRONMENT="development"
export ENABLE_VIDEO_SUPPORT="true"
export ENABLE_AI_SYNTHESIS="true"
export ENABLE_REAL_TIME_SCORING="true"
export MIN_COMPOSITE_SCORE="50.0"
export MIN_ACTIONABILITY_SCORE="60.0"
export CRAWLER_DELAY="0.1"
export CRAWLER_TIMEOUT="10"
export MAX_ARTICLES_PER_SOURCE="50"
export REQUESTS_PER_MINUTE="60"
export RATE_LIMIT_PER_MINUTE="100"
export CORS_ORIGINS="*"

echo "📦 Installing dependencies..."
pip install -r requirements_v4.txt

echo "🗄️ Initializing database..."
python -m app_v4.init_db

echo "🌐 Starting API server on port 8000..."
python -m uvicorn app_v4.api:app --reload --host 0.0.0.0 --port 8000 &

echo "⚙️ Starting background worker..."
python -m app_v4.worker &

echo "🎥 Starting video worker..."
python -m app_v4.video_worker &

echo "🌍 Starting website server on port 8082..."
cd website_v4
python server.py &

echo ""
echo "✅ Newsletter API v4 Platform is now running!"
echo ""
echo "📍 Access Points:"
echo "   • API Documentation: http://localhost:8000/docs"
echo "   • API Base: http://localhost:8000"
echo "   • Website: http://localhost:8082"
echo ""
echo "🎯 Main Endpoints:"
echo "   • Homepage: http://localhost:8000/api/v4/home"
echo "   • Top Stories: http://localhost:8000/api/v4/top-stories"
echo "   • Opportunities: http://localhost:8000/api/v4/opportunities"
echo "   • Practices: http://localhost:8000/api/v4/practices"
echo "   • Systems & Codes: http://localhost:8000/api/v4/systems-codes"
echo "   • Vision: http://localhost:8000/api/v4/vision"
echo ""
echo "🛠️ Admin Endpoints:"
echo "   • Collect Data: POST http://localhost:8000/api/v4/admin/collect"
echo "   • Run Scoring: POST http://localhost:8000/api/v4/admin/score"
echo "   • Process Videos: POST http://localhost:8000/api/v4/admin/process-videos"
echo "   • Health Check: http://localhost:8000/api/v4/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo ""; echo "🛑 Shutting down services..."; kill $(jobs -p); exit 0' INT
wait
