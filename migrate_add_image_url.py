#!/usr/bin/env python3
"""
Database migration script to add image_url column to articles_v4 table
"""

import os
import sys
from sqlalchemy import create_engine, text

# Add the project root to the Python path
sys.path.append(os.path.dirname(__file__))

from newsletter_v4.config import get_config

def migrate_database():
    """Add image_url column to articles_v4 table"""
    config = get_config()
    
    # Create database engine
    engine = create_engine(config.database.url)
    
    try:
        with engine.connect() as conn:
            # Check if column already exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'articles_v4' 
                AND column_name = 'image_url'
            """))
            
            if result.fetchone():
                print("✅ image_url column already exists")
                return
            
            # Add the image_url column
            print("Adding image_url column to articles_v4 table...")
            conn.execute(text("""
                ALTER TABLE articles_v4 
                ADD COLUMN image_url VARCHAR(1000)
            """))
            
            conn.commit()
            print("✅ Successfully added image_url column to articles_v4 table")
            
    except Exception as e:
        print(f"❌ Error migrating database: {e}")
        raise

if __name__ == "__main__":
    migrate_database()
