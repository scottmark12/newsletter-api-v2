#!/usr/bin/env python3
"""
Force crawl script that works around deployment issues
"""

import requests
import time
import json

API_BASE = "https://newsletter-api-v2.onrender.com"

def test_api():
    """Test if API is responding"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"✅ API Health: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Health failed: {e}")
        return False

def try_clear_db():
    """Try to clear the database"""
    try:
        response = requests.post(f"{API_BASE}/admin/clear-db", timeout=30)
        if response.status_code == 200:
            print(f"✅ Clear DB: {response.json()}")
            return True
        else:
            print(f"⚠️ Clear DB: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Clear DB failed: {e}")
        return False

def try_small_crawl():
    """Try a very small crawl to initialize database"""
    try:
        print("🔄 Attempting small crawl to initialize database...")
        response = requests.post(f"{API_BASE}/ingest/run?limit=1", timeout=60)
        if response.status_code == 200:
            print(f"✅ Small crawl: {response.json()}")
            return True
        else:
            print(f"⚠️ Small crawl: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Small crawl failed: {e}")
        return False

def check_articles():
    """Check if articles exist"""
    try:
        response = requests.get(f"{API_BASE}/api/articles?limit=5", timeout=30)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"📊 Found {count} articles")
            return count > 0
        else:
            print(f"⚠️ Articles check: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Articles check failed: {e}")
        return False

def run_full_crawl():
    """Run a full crawl"""
    try:
        print("🔄 Running full crawl...")
        response = requests.post(f"{API_BASE}/ingest/run?limit=50", timeout=300)
        if response.status_code == 200:
            print(f"✅ Full crawl: {response.json()}")
            return True
        else:
            print(f"⚠️ Full crawl: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Full crawl failed: {e}")
        return False

def main():
    print("🚀 Starting force crawl process...")
    
    # Test API
    if not test_api():
        print("❌ API not responding, exiting")
        return
    
    # Try to clear database
    clear_success = try_clear_db()
    
    # Try small crawl to initialize
    if not clear_success:
        print("🔄 Trying small crawl to initialize database...")
        try_small_crawl()
        time.sleep(5)
    
    # Check if we have articles
    has_articles = check_articles()
    
    # Run full crawl if needed
    if not has_articles:
        print("🔄 No articles found, running full crawl...")
        run_full_crawl()
        time.sleep(10)
        has_articles = check_articles()
    
    if has_articles:
        print("✅ Success! Database is populated with articles")
        
        # Show some sample articles
        try:
            response = requests.get(f"{API_BASE}/api/articles?limit=3", timeout=30)
            if response.status_code == 200:
                data = response.json()
                articles = data.get('items', [])
                print("\n📰 Sample articles:")
                for i, article in enumerate(articles, 1):
                    print(f"{i}. {article.get('title', 'No title')} (Score: {article.get('composite_score', 'N/A')})")
        except Exception as e:
            print(f"⚠️ Could not fetch sample articles: {e}")
    else:
        print("❌ Still no articles found after crawl attempts")
        print("💡 The deployment might still be updating or there's a database issue")

if __name__ == "__main__":
    main()
