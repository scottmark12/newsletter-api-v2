#!/usr/bin/env python3
"""
Debug script to test worker imports and identify the 'your_application' error
"""
import os
import sys

print("=== Worker Debug Script ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Set up environment
os.environ.setdefault("DATABASE_URL", "sqlite:///newsletter.db")
os.environ.setdefault("FORCE_SQLITE", "true")

print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
print(f"FORCE_SQLITE: {os.environ.get('FORCE_SQLITE')}")

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
print(f"Added to path: {current_dir}")

print("\n=== Testing imports ===")

try:
    print("Testing: import os")
    import os
    print("✅ os imported successfully")
except Exception as e:
    print(f"❌ os import failed: {e}")

try:
    print("Testing: import sys")
    import sys
    print("✅ sys imported successfully")
except Exception as e:
    print(f"❌ sys import failed: {e}")

try:
    print("Testing: import schedule")
    import schedule
    print("✅ schedule imported successfully")
except Exception as e:
    print(f"❌ schedule import failed: {e}")

try:
    print("Testing: from sqlalchemy import text")
    from sqlalchemy import text
    print("✅ sqlalchemy imported successfully")
except Exception as e:
    print(f"❌ sqlalchemy import failed: {e}")

try:
    print("Testing: from app.db import get_db")
    from app.db import get_db
    print("✅ app.db imported successfully")
except Exception as e:
    print(f"❌ app.db import failed: {e}")

try:
    print("Testing: from app.config import TIMEZONE")
    from app.config import TIMEZONE
    print("✅ app.config imported successfully")
except Exception as e:
    print(f"❌ app.config import failed: {e}")

print("\n=== Testing worker class ===")
try:
    from worker import NewsletterWorker
    worker = NewsletterWorker()
    print("✅ NewsletterWorker created successfully")
except Exception as e:
    print(f"❌ NewsletterWorker failed: {e}")

print("\n=== Debug complete ===")
