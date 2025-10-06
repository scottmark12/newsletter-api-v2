"""
Newsletter API v4 - Main Application Entry Point
Use: python app.py
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the current directory to the path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

# Import the v4 API
from newsletter_v4.api import app
from newsletter_v4.config import get_config

def main():
    """Main entry point for the Newsletter API v4"""
    config = get_config()
    
    print("🚀 Starting Newsletter API v4...")
    print(f"📊 API Title: {config.api.title}")
    print(f"🔧 Version: {config.api.version}")
    print(f"🗄️ Database: {config.database.url}")
    print(f"🌐 Debug Mode: {config.api.debug}")
    print(f"📡 RSS Feeds: {len(config.data_sources.rss_feeds)} configured")
    print("\n📍 Available endpoints:")
    print("   🌐 Main Website: http://localhost:8000/website")
    print("   📊 Admin Dashboard: http://localhost:8000/dashboard")
    print("   📚 API Docs: http://localhost:8000/docs")
    print("   ❤️ Health Check: http://localhost:8000/health")
    
    # Start the server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=config.api.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()