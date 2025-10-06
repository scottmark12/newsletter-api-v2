"""
Newsletter API v4 - Main Entry Point
Clean, production-ready FastAPI application
"""

import os
import uvicorn
from newsletter_v4.api import app

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "newsletter_v4.api:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Set to True for development
    )
