#!/usr/bin/env python3
"""
Clear database script
"""
import os
import sys
from sqlalchemy import create_engine, text

def clear_database():
    """Clear all articles and scores from the database"""
    try:
        # Get database URL from environment
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL environment variable not set")
            return False
        
        # Create engine
        engine = create_engine(database_url)
        
        with engine.connect() as conn:
            # Clear article scores first (foreign key constraint)
            result = conn.execute(text("DELETE FROM article_scores"))
            print(f"✅ Cleared {result.rowcount} article scores")
            
            result = conn.execute(text("DELETE FROM articles"))
            print(f"✅ Cleared {result.rowcount} articles")
            
            conn.commit()
            
            print("✅ Database cleared successfully")
            return True
            
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    clear_database()
