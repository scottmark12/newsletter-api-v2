"""
Newsletter API v4 - Main Entry Point
Clean, modern newsletter platform with intelligent scoring and comprehensive data collection
"""

import uvicorn
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the app directory
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

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
    
    # Start the server
    uvicorn.run(
        "newsletter_v4.api:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=config.api.debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()
