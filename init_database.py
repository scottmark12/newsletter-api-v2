#!/usr/bin/env python3
"""
Database initialization script for the new empty database
"""

import os
import sys
from sqlalchemy import create_engine, text

# Database URL from the user
DATABASE_URL = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3"

def init_database():
    """Initialize the database with required tables"""
    print("🔧 Initializing database...")
    
    try:
        engine = create_engine(DATABASE_URL)
        
        with engine.connect() as conn:
            # Create articles table
            print("📄 Creating articles table...")
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
            print("📊 Creating article_scores table...")
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
            print("🔍 Creating indexes...")
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_article_id ON article_scores(article_id)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_composite_score ON article_scores(composite_score)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_article_scores_topics ON article_scores USING GIN(topics)"))
            
            conn.commit()
            
            print("✅ Database initialized successfully!")
            
            # Test the tables
            result = conn.execute(text("SELECT COUNT(*) FROM articles"))
            article_count = result.fetchone()[0]
            print(f"📊 Articles table ready: {article_count} articles")
            
            result = conn.execute(text("SELECT COUNT(*) FROM article_scores"))
            scores_count = result.fetchone()[0]
            print(f"📊 Scores table ready: {scores_count} scores")
            
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)
