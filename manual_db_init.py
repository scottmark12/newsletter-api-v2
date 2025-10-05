#!/usr/bin/env python3
"""
Manual database initialization using direct connection
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database URL from user
DATABASE_URL = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3"

def init_database():
    """Initialize database tables"""
    print("🔧 Connecting to database...")
    
    try:
        # Parse the database URL
        import urllib.parse as urlparse
        url = urlparse.urlparse(DATABASE_URL)
        
        # Connect to database
        conn = psycopg2.connect(
            host=url.hostname,
            port=url.port,
            database=url.path[1:],  # Remove leading slash
            user=url.username,
            password=url.password,
            sslmode='require'
        )
        
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("✅ Connected to database")
        
        # Create articles table
        print("📄 Creating articles table...")
        cursor.execute("""
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
        """)
        
        # Create article_scores table
        print("📊 Creating article_scores table...")
        cursor.execute("""
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
        """)
        
        # Create indexes
        print("🔍 Creating indexes...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_url ON articles(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_scores_article_id ON article_scores(article_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_scores_composite_score ON article_scores(composite_score)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_article_scores_topics ON article_scores USING GIN(topics)")
        
        # Test the tables
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM article_scores")
        scores_count = cursor.fetchone()[0]
        
        print(f"✅ Database initialized successfully!")
        print(f"📊 Articles table: {article_count} articles")
        print(f"📊 Scores table: {scores_count} scores")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    success = init_database()
    if success:
        print("\n🎉 SUCCESS! Database is ready for use!")
        print("🔧 Now you can run crawls to populate it with articles")
    else:
        print("\n❌ FAILED! Database initialization failed")
