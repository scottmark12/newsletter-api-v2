"""
Newsletter API v4 - Simplified Version for Render
Minimal version to ensure successful deployment
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter API v4",
    description="Intelligent construction and real estate platform",
    version="4.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Newsletter API v4",
        "description": "Intelligent construction and real estate platform",
        "version": "4.0.0",
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "database": "connected" if os.getenv("DATABASE_URL") else "not_configured"
    }

@app.get("/api/v4/home")
async def get_homepage_data():
    """Get homepage data"""
    return {
        "ok": True,
        "endpoint": "homepage",
        "message": "v4 API is running! Full functionality will be available after database setup.",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "themes": {
            "opportunities": {"name": "Opportunities", "count": 0},
            "practices": {"name": "Practices", "count": 0},
            "systems_codes": {"name": "Systems & Codes", "count": 0},
            "vision": {"name": "Vision", "count": 0}
        }
    }

@app.get("/api/v4/top-stories")
async def get_top_stories():
    """Get top stories"""
    return {
        "ok": True,
        "endpoint": "top_stories",
        "message": "v4 API is running! Articles will appear after data collection.",
        "count": 0,
        "articles": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/opportunities")
async def get_opportunities():
    """Get opportunities articles"""
    return {
        "ok": True,
        "theme": "opportunities",
        "message": "v4 API is running! Articles will appear after data collection.",
        "count": 0,
        "articles": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/practices")
async def get_practices():
    """Get practices articles"""
    return {
        "ok": True,
        "theme": "practices",
        "message": "v4 API is running! Articles will appear after data collection.",
        "count": 0,
        "articles": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/systems-codes")
async def get_systems_codes():
    """Get systems & codes articles"""
    return {
        "ok": True,
        "theme": "systems_codes",
        "message": "v4 API is running! Articles will appear after data collection.",
        "count": 0,
        "articles": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/vision")
async def get_vision():
    """Get vision articles"""
    return {
        "ok": True,
        "theme": "vision",
        "message": "v4 API is running! Articles will appear after data collection.",
        "count": 0,
        "articles": [],
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.post("/api/v4/admin/collect")
async def collect_data():
    """Trigger data collection"""
    return {
        "ok": True,
        "message": "Data collection endpoint ready. Full functionality will be available after database setup.",
        "status": "ready"
    }

@app.post("/api/v4/admin/score")
async def run_scoring():
    """Run scoring"""
    return {
        "ok": True,
        "message": "Scoring endpoint ready. Full functionality will be available after database setup.",
        "status": "ready"
    }
