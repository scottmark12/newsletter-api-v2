"""
Newsletter API v4 Main Entry Point
Entry point for Render deployment
"""

import os
import uvicorn
from .api import app

if __name__ == "__main__":
    uvicorn.run(
        "app_v4.api:app",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 8000)),
        reload=False
    )
