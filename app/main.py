"""
Newsletter API v4 - V3-Inspired Thematic Intelligence
Advanced narrative-based scoring with opportunity detection
"""

import os
from typing import Dict, Any, List
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

# Create FastAPI app
app = FastAPI(
    title="Newsletter API v4",
    version="4.0.0",
    description="Advanced narrative-based scoring with opportunity detection",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_database_engine():
    """Get database engine with proper driver selection"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    # Ensure we use the correct PostgreSQL driver
    if database_url.startswith("postgresql://"):
        try:
            import psycopg
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
        except ImportError:
            try:
                import psycopg2
                database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
            except ImportError:
                pass  # Use default driver
    
    return create_engine(database_url)

# Health endpoints
@app.get("/health")
@app.get("/healthz")
def health():
    return {"ok": True, "version": "v4.0.0", "timestamp": datetime.now().isoformat(), "build": "latest"}

@app.get("/")
def root():
    return {
        "status": "ok", 
        "version": "v4.0.0",
        "docs": "/docs", 
        "health": "/health",
        "endpoints": {
            "main_page": "/api/v4/main",
            "themes": "/api/v4/themes",
            "opportunities": "/api/v4/opportunities",
            "practices": "/api/v4/practices",
            "systems": "/api/v4/systems",
            "vision": "/api/v4/vision"
        }
    }

# V3 Theme-based endpoints
@app.get("/api/v4/themes")
def get_themes():
    """Get available themes"""
    return {
        "themes": [
            {
                "id": "opportunities",
                "name": "Opportunities",
                "description": "Stories of transformation, investments, deals, and wealth-building examples"
            },
            {
                "id": "practices", 
                "name": "Practices",
                "description": "Building methods, design principles, process improvements, and lessons learned"
            },
            {
                "id": "systems",
                "name": "Systems & Codes", 
                "description": "Policy updates, building code changes, zoning reforms, and regulatory unlocks"
            },
            {
                "id": "vision",
                "name": "Vision",
                "description": "Smart cities, future-of-living models, community impact, and biophilic design"
            }
        ]
    }

@app.get("/api/v4/opportunities")
def get_opportunities(limit: int = 10):
    """Get opportunity-themed articles"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Query for opportunity-themed articles (big_returns, market_transformations)
            result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary,
                       s.composite_score, s.topics, s.why1
                FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                  AND (s.topics @> '{"big_returns"}' OR s.topics @> '{"market_transformations"}')
                ORDER BY COALESCE(s.composite_score, 0) DESC, a.published_at DESC
                LIMIT :limit
            """), {"limit": limit})
            
            articles = []
            for row in result:
                articles.append({
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "composite_score": float(row.composite_score) if row.composite_score else 0.0,
                    "topics": row.topics,
                    "why": row.why1
                })
            
            return {
                "theme": "opportunities",
                "count": len(articles),
                "articles": articles
            }
    except Exception as e:
        return {"theme": "opportunities", "count": 0, "articles": [], "error": str(e)}

@app.get("/api/v4/practices")
def get_practices(limit: int = 10):
    """Get practice-themed articles"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary,
                       s.overall_score, s.practices_score
                FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                ORDER BY COALESCE(s.overall_score, 0) DESC, a.published_at DESC
                LIMIT :limit
            """), {"limit": limit})
            
            articles = []
            for row in result:
                articles.append({
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "overall_score": float(row.overall_score) if row.overall_score else 0.0,
                    "practices_score": float(row.practices_score) if row.practices_score else 0.0
                })
            
            return {
                "theme": "practices",
                "count": len(articles),
                "articles": articles
            }
    except Exception as e:
        return {"theme": "practices", "count": 0, "articles": [], "error": str(e)}

@app.get("/api/v4/systems")
def get_systems(limit: int = 10):
    """Get systems & codes themed articles"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary,
                       s.overall_score, s.systems_score
                  FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                ORDER BY COALESCE(s.overall_score, 0) DESC, a.published_at DESC
                    LIMIT :limit
            """), {"limit": limit})
            
            articles = []
            for row in result:
                articles.append({
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "overall_score": float(row.overall_score) if row.overall_score else 0.0,
                    "systems_score": float(row.systems_score) if row.systems_score else 0.0
                })
            
            return {
                "theme": "systems",
                "count": len(articles),
                "articles": articles
            }
    except Exception as e:
        return {"theme": "systems", "count": 0, "articles": [], "error": str(e)}

@app.get("/api/v4/vision")
def get_vision(limit: int = 10):
    """Get vision-themed articles"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary,
                       s.overall_score, s.vision_score
                FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                ORDER BY COALESCE(s.overall_score, 0) DESC, a.published_at DESC
                LIMIT :limit
            """), {"limit": limit})
            
            articles = []
            for row in result:
                articles.append({
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "overall_score": float(row.overall_score) if row.overall_score else 0.0,
                    "vision_score": float(row.vision_score) if row.vision_score else 0.0
                })
            
            return {
                "theme": "vision",
                "count": len(articles),
                "articles": articles
            }
    except Exception as e:
        return {"theme": "vision", "count": 0, "articles": [], "error": str(e)}

# Main page endpoint with top story and quick hits
@app.get("/api/v4/main")
def get_main_page(limit: int = 10):
    """Get main page with top story and quick hits"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Get top story (highest composite score)
            top_story_result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary, a.body,
                       s.composite_score, s.topics, s.why1
                  FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                ORDER BY COALESCE(s.composite_score, 0) DESC, a.published_at DESC
                LIMIT 1
            """))
            
            top_story = None
            for row in top_story_result:
                top_story = {
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "body": row.body,
                    "composite_score": float(row.composite_score) if row.composite_score else 0.0,
                    "topics": row.topics,
                    "why": row.why1
                }
                break
            
            # Get quick hits (top 5 excluding the top story)
            quick_hits_result = conn.execute(text("""
                SELECT a.id, a.title, a.url, a.published_at, a.summary,
                       s.composite_score, s.topics, s.why1
                FROM articles a
                LEFT JOIN article_scores s ON a.id = s.article_id
                WHERE a.published_at >= NOW() - INTERVAL '7 days'
                  AND (:top_story_id IS NULL OR a.id != :top_story_id)
                ORDER BY COALESCE(s.composite_score, 0) DESC, a.published_at DESC
                LIMIT 5
            """), {
                "top_story_id": top_story["id"] if top_story else None
            })
            
            quick_hits = []
            for row in quick_hits_result:
                quick_hits.append({
                    "id": str(row.id),
                    "title": row.title,
                    "url": row.url,
                    "published_at": row.published_at.isoformat() if row.published_at else None,
                    "summary": row.summary,
                    "composite_score": float(row.composite_score) if row.composite_score else 0.0,
                    "topics": row.topics,
                    "why": row.why1
                })
            
            return {
                "top_story": top_story,
                "quick_hits": quick_hits,
                "metadata": {
                    "generated_at": datetime.now().isoformat(),
                    "version": "v3-clean"
                }
            }
    except Exception as e:
        return {
            "top_story": None,
            "quick_hits": [],
            "error": str(e),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "version": "v3-clean"
            }
        }

# Database management endpoints
@app.post("/api/v4/admin/clear-db")
def clear_database():
    """Clear all articles and scores from the database"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Clear article scores first (foreign key constraint)
            conn.execute(text("DELETE FROM article_scores"))
            conn.execute(text("DELETE FROM articles"))
            conn.commit()
            
            return {
                "status": "success",
                "message": "Database cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

@app.get("/api/v4/admin/db-status")
def database_status():
    """Check database status and article count"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Count articles
            article_count = conn.execute(text("SELECT COUNT(*) FROM articles")).scalar()
            score_count = conn.execute(text("SELECT COUNT(*) FROM article_scores")).scalar()
            
            return {
                "status": "connected",
                "articles": article_count,
                "scores": score_count,
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Test endpoint
@app.get("/api/v4/test")
def test_endpoint():
    """Test endpoint to verify V4 is working"""
    return {
        "status": "ok",
        "version": "v4.0.0",
        "message": "V4 endpoints are working!",
        "timestamp": datetime.now().isoformat()
    }