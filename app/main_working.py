"""
Minimal working API for newsletter database initialization
"""

from fastapi import FastAPI, Query
from datetime import datetime, timezone, timedelta
import os
from sqlalchemy import create_engine, text

# Create FastAPI app
app = FastAPI(
    title="Newsletter API - Working Version",
    version="1.0.0",
    description="Minimal working API for database initialization"
)

def get_engine():
    """Get database engine"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Try psycopg first, then psycopg2
    try:
        import psycopg
        engine = create_engine(database_url)
    except ImportError:
        import psycopg2
        engine = create_engine(database_url)
    
    return engine

def init_database():
    """Initialize database tables"""
    try:
        engine = get_engine()
        
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

@app.on_event("startup")
def startup():
    """Initialize database on startup"""
    print("🚀 Starting Newsletter API - Working Version")
    if init_database():
        print("✅ Database initialized successfully")
    else:
        print("⚠️ Database initialization failed")

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "ok": True,
        "version": "1.0.0-working",
        "timestamp": datetime.now().isoformat(),
        "database": "initialized"
    }

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "status": "ok",
        "version": "1.0.0-working",
        "docs": "/docs",
        "health": "/health",
        "endpoints": ["/health", "/test-db", "/clear-db"]
    }

@app.get("/test-db")
def test_database():
    """Test database connection and tables"""
    try:
        engine = get_engine()
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
                "database": "working"
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "database": "failed"
        }

@app.post("/clear-db")
def clear_database():
    """Clear all articles and scores"""
    try:
        engine = get_engine()
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
            "message": "Failed to clear database"
        }

@app.get("/api/articles")
def get_articles(limit: int = Query(20, ge=1, le=100)):
    """Get articles from database"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                       a.published_at, a.fetched_at, a.lang,
                       s.composite_score, s.topics, s.geography, s.macro_flag,
                       s.summary2, s.why1, s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                LEFT JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                ORDER BY COALESCE(s.composite_score, 0) DESC, COALESCE(a.published_at, a.fetched_at) DESC
                LIMIT :limit
            """), {"limit": limit}).mappings().all()
            
            return {
                "ok": True,
                "count": len(rows),
                "items": [dict(r) for r in rows]
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "count": 0,
            "items": []
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
