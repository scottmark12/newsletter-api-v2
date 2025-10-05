#!/usr/bin/env python3
"""
Script to clear all articles and scores from the database
"""

import os
import sys
from sqlalchemy import create_engine, text

# Set up database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    print("Please set it with: export DATABASE_URL='your_database_url'")
    sys.exit(1)

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as conn:
        print("🔍 Checking current database state...")
        
        # Check current article count
        result = conn.execute(text("SELECT COUNT(*) FROM articles"))
        article_count = result.fetchone()[0]
        print(f"📊 Current articles: {article_count}")
        
        # Check current scores count
        result = conn.execute(text("SELECT COUNT(*) FROM article_scores"))
        scores_count = result.fetchone()[0]
        print(f"📊 Current scores: {scores_count}")
        
        if article_count == 0 and scores_count == 0:
            print("✅ Database is already empty!")
            sys.exit(0)
        
        # Confirm deletion
        print(f"\n⚠️  About to delete:")
        print(f"   • {article_count} articles")
        print(f"   • {scores_count} scores")
        
        confirm = input("\n❓ Are you sure you want to clear the database? (yes/no): ")
        
        if confirm.lower() in ['yes', 'y']:
            print("\n🗑️  Clearing database...")
            
            # Delete scores first (foreign key constraint)
            if scores_count > 0:
                result = conn.execute(text("DELETE FROM article_scores"))
                print(f"✅ Deleted {result.rowcount} scores")
            
            # Delete articles
            if article_count > 0:
                result = conn.execute(text("DELETE FROM articles"))
                print(f"✅ Deleted {result.rowcount} articles")
            
            # Commit changes
            conn.commit()
            print("\n🎉 Database cleared successfully!")
            
            # Verify
            result = conn.execute(text("SELECT COUNT(*) FROM articles"))
            final_articles = result.fetchone()[0]
            result = conn.execute(text("SELECT COUNT(*) FROM article_scores"))
            final_scores = result.fetchone()[0]
            
            print(f"\n📊 Final state:")
            print(f"   • Articles: {final_articles}")
            print(f"   • Scores: {final_scores}")
            
        else:
            print("❌ Operation cancelled")
            
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
