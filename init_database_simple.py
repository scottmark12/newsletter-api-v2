#!/usr/bin/env python3
"""
Simple database initialization script
This will initialize the database tables directly
"""

import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_engine():
    """Get database engine with proper error handling"""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        print("Please set it to: postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3")
        sys.exit(1)
    
    try:
        import psycopg
        engine = create_engine(database_url)
        print("✅ Using psycopg driver")
    except ImportError:
        try:
            import psycopg2
            engine = create_engine(database_url)
            print("✅ Using psycopg2 driver")
        except ImportError:
            print("❌ Neither psycopg nor psycopg2 is available")
            print("Please install: pip install 'psycopg[binary]'")
            sys.exit(1)
    
    return engine

def initialize_database_tables():
    """Initialize database tables"""
    print("🚀 Initializing database tables...")
    
    try:
        engine = get_database_engine()
        
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
            print("✅ Database tables initialized successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def test_database():
    """Test database connection and tables"""
    print("🧪 Testing database...")
    
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            # Test articles table
            result = conn.execute(text("SELECT COUNT(*) FROM articles"))
            article_count = result.fetchone()[0]
            
            # Test scores table
            result = conn.execute(text("SELECT COUNT(*) FROM article_scores"))
            scores_count = result.fetchone()[0]
            
            print(f"✅ Database test successful!")
            print(f"   Articles: {article_count}")
            print(f"   Scores: {scores_count}")
            return True
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Newsletter API Database Initializer")
    print("=" * 50)
    
    # Set the database URL
    os.environ["DATABASE_URL"] = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a.virginia-postgres.render.com/newsletter_db_v3"
    
    # Initialize database
    if initialize_database_tables():
        # Test database
        if test_database():
            print("\n🎉 Database is ready!")
            print("You can now run crawls and the API will work properly.")
        else:
            print("\n⚠️ Database initialized but test failed")
    else:
        print("\n❌ Database initialization failed")
        sys.exit(1)
