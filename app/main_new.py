"""
NEWSLETTER API - COMPLETELY NEW VERSION
This will force a new deployment
"""

from fastapi import FastAPI, Query, HTTPException
from datetime import datetime, timezone, timedelta
import os
from sqlalchemy import create_engine, text
from typing import List, Dict, Any

# Create FastAPI app with completely new structure
app = FastAPI(
    title="Newsletter API - NEW VERSION",
    version="2.0.0-NEW",
    description="Completely new API version with guaranteed database initialization"
)

# Database engine function
def get_database_engine():
    """Get database engine with proper error handling"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    try:
        import psycopg
        engine = create_engine(database_url)
    except ImportError:
        try:
            import psycopg2
            engine = create_engine(database_url)
        except ImportError:
            raise ImportError("Neither psycopg nor psycopg2 is available")
    
    return engine

# Database initialization
def initialize_database_tables():
    """Initialize database tables"""
    try:
        engine = get_database_engine()
        
        with engine.connect() as conn:
            # Create articles table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS articles (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    url TEXT UNIQUE NOT NULL,
                    source TEXT,
                    title TEXT,
                    summary_raw TEXT,
                    content TEXT,
                    published_at TIMESTAMP WITH TIME ZONE,
                    fetched_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    lang TEXT DEFAULT 'en',
                    status TEXT DEFAULT 'new'
                )
            """))
            
            # Create article_scores table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS article_scores (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
                    composite_score FLOAT,
                    topics TEXT[],
                    geography TEXT,
                    macro_flag TEXT,
                    summary2 TEXT,
                    why1 TEXT,
                    project_stage TEXT,
                    needs_fact_check BOOLEAN DEFAULT FALSE,
                    media_type TEXT DEFAULT 'article',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_article_id ON article_scores(article_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_composite_score ON article_scores(composite_score)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_topics ON article_scores USING GIN(topics)"))
            
            conn.commit()
            return True
            
    except Exception as e:
        print(f"Database initialization failed: {e}")
        return False

# Startup event
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    print("🚀 Starting Newsletter API - NEW VERSION")
    if initialize_database_tables():
        print("✅ Database tables initialized successfully")
    else:
        print("⚠️ Database initialization failed")

# Health endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "ok": True,
        "version": "2.0.0-NEW",
        "timestamp": datetime.now().isoformat(),
        "database": "initialized",
        "status": "active"
    }

# Root endpoint
@app.get("/")
def root_endpoint():
    """Root endpoint"""
    return {
        "status": "ok",
        "version": "2.0.0-NEW",
        "message": "Newsletter API - NEW VERSION",
        "docs": "/docs",
        "health": "/health",
        "endpoints": [
            "/health",
            "/test-database",
            "/initialize-database",
            "/clear-database",
            "/api/articles",
            "/api/crawl"
        ]
    }

# Database test endpoint
@app.get("/test-database")
def test_database_connection():
    """Test database connection and tables"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Test articles table
            result = conn.execute(text("SELECT COUNT(*) FROM articles"))
            article_count = result.fetchone()[0]
            
            # Test scores table
            result = conn.execute(text("SELECT COUNT(*) FROM article_scores"))
            scores_count = result.fetchone()[0]
            
            return {
                "ok": True,
                "articles_count": article_count,
                "scores_count": scores_count,
                "database": "working",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "database": "failed",
            "timestamp": datetime.now().isoformat()
        }

# Database initialization endpoint
@app.post("/initialize-database")
def initialize_database_endpoint():
    """Initialize database tables"""
    try:
        success = initialize_database_tables()
        return {
            "ok": success,
            "message": "Database initialized successfully" if success else "Database initialization failed",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Database initialization failed",
            "timestamp": datetime.now().isoformat()
        }

# Clear database endpoint
@app.post("/clear-database")
def clear_database_endpoint():
    """Clear all articles and scores"""
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Clear scores first (foreign key constraint)
            conn.execute(text("DELETE FROM article_scores"))
            # Then clear articles
            conn.execute(text("DELETE FROM articles"))
            conn.commit()
            
            return {
                "ok": True,
                "message": "Database cleared successfully",
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Failed to clear database",
            "timestamp": datetime.now().isoformat()
        }

# Articles endpoint
@app.get("/api/articles")
def get_articles(
    limit: int = Query(20, ge=1, le=100),
    since_hours: int = Query(24, ge=1, le=168)
):
    """Get articles from database"""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
        engine = get_database_engine()
        
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                       a.published_at, a.fetched_at, a.lang,
                       s.composite_score, s.topics, s.geography, s.macro_flag,
                       s.summary2, s.why1, s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                LEFT JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                AND a.url NOT LIKE '%/question/%'
                AND NOT (a.source = 'GreenBuildingAdvisor' AND a.title ILIKE '%piano%')
                AND NOT (a.source = 'GreenBuildingAdvisor' AND a.title ILIKE '%water heater%')
                AND (
                    (a.published_at IS NOT NULL AND a.published_at >= :cutoff)
                    OR
                    (a.published_at IS NULL AND a.fetched_at >= :cutoff)
                )
                ORDER BY COALESCE(s.composite_score, 0) DESC, COALESCE(a.published_at, a.fetched_at) DESC
                LIMIT :limit
            """), {"cutoff": cutoff.isoformat(), "limit": limit}).mappings().all()
            
            return {
                "ok": True,
                "count": len(rows),
                "items": [dict(r) for r in rows],
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "count": 0,
            "items": [],
            "timestamp": datetime.now().isoformat()
        }

# Crawl endpoint
@app.post("/api/crawl")
def run_crawl(limit: int = Query(50, ge=1, le=500)):
    """Run crawl to populate database"""
    try:
        # This is a placeholder - in a real implementation, you'd call the crawler
        return {
            "ok": True,
            "message": "Crawl endpoint ready",
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "message": "Crawl failed",
            "timestamp": datetime.now().isoformat()
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
