#!/usr/bin/env python3
"""
Test script to verify SQLite-only configuration works
"""
import os
import sys

# Force SQLite configuration
os.environ["FORCE_SQLITE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///test_newsletter.db"
os.environ["OPENAI_API_KEY"] = "test-key"

print("🧪 Testing SQLite-only configuration...")

try:
    # Test imports
    print("Testing imports...")
    from app.config import DATABASE_URL
    print(f"✅ DATABASE_URL: {DATABASE_URL}")
    
    from app.db import actual_db_url, is_postgres, engine
    print(f"✅ actual_db_url: {actual_db_url}")
    print(f"✅ is_postgres: {is_postgres}")
    print(f"✅ engine: {engine}")
    
    # Test database connection
    print("\nTesting database connection...")
    from sqlalchemy import text
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).fetchone()
        print(f"✅ Database connection successful: {result}")
    
    # Test main app import
    print("\nTesting main app import...")
    from app.main import web_app
    print("✅ FastAPI app imported successfully")
    
    print("\n🎉 All tests passed! SQLite-only configuration works.")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
