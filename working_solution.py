#!/usr/bin/env python3
"""
Working solution that bypasses the stuck deployment
"""

import requests
import time
import json
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Database URL from user
DATABASE_URL = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3"

def initialize_database_directly():
    """Initialize database directly"""
    print("🔧 Initializing database directly...")
    
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

def create_simple_api_server():
    """Create a simple API server that works locally"""
    print("🚀 Creating simple API server...")
    
    server_code = '''
from fastapi import FastAPI, Query
from datetime import datetime, timezone, timedelta
import os
from sqlalchemy import create_engine, text

app = FastAPI(title="Newsletter API - Local Working Version")

DATABASE_URL = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3"

def get_engine():
    try:
        import psycopg
        return create_engine(DATABASE_URL)
    except ImportError:
        import psycopg2
        return create_engine(DATABASE_URL)

@app.get("/health")
def health():
    return {"ok": True, "version": "local-working", "timestamp": datetime.now().isoformat()}

@app.get("/api/articles")
def get_articles(limit: int = Query(20, ge=1, le=100)):
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
            
            return {"ok": True, "count": len(rows), "items": [dict(r) for r in rows]}
    except Exception as e:
        return {"ok": False, "error": str(e), "count": 0, "items": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083)
'''
    
    with open("local_api_server.py", "w") as f:
        f.write(server_code)
    
    print("✅ Local API server created: local_api_server.py")
    print("🚀 Run: python3 local_api_server.py")
    print("📱 Access at: http://localhost:8083")

def main():
    """Main function"""
    print("🔧 WORKING SOLUTION - Bypass Stuck Deployment")
    print("=" * 60)
    
    # Step 1: Initialize database directly
    if initialize_database_directly():
        print("\n✅ Database is ready!")
        
        # Step 2: Create local API server
        create_simple_api_server()
        
        print("\n🎉 SOLUTION READY!")
        print("=" * 60)
        print("✅ Database initialized with tables")
        print("✅ Local API server created")
        print("✅ Ready to work around stuck deployment")
        print("\n🚀 Next steps:")
        print("1. Run: python3 local_api_server.py")
        print("2. Access: http://localhost:8083")
        print("3. Use the local API while we fix the deployment")
        
    else:
        print("\n❌ Database initialization failed")
        print("💡 The database URL might not be accessible from this location")

if __name__ == "__main__":
    main()
