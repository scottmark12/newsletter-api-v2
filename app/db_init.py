"""
Database initialization module
"""

import os
from sqlalchemy import create_engine, text

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
                "scores_count": scores_count
            }
    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }
