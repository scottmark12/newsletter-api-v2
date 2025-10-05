#!/usr/bin/env python3
"""
Fix the system by working around the deployment issue
"""

import requests
import time
import json

API_BASE = "https://newsletter-api-v2.onrender.com"

def make_request(method, endpoint, **kwargs):
    """Make a request with error handling"""
    try:
        url = f"{API_BASE}{endpoint}"
        response = requests.request(method, url, timeout=30, **kwargs)
        return response
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return None

def check_health():
    """Check API health"""
    print("🔍 Checking API health...")
    response = make_request("GET", "/health")
    if response and response.status_code == 200:
        data = response.json()
        print(f"✅ Health: {data}")
        return True
    else:
        print(f"❌ Health check failed: {response.status_code if response else 'No response'}")
        return False

def try_database_init():
    """Try to initialize database through API"""
    print("🔧 Attempting database initialization...")
    
    # Try different endpoints that might initialize the database
    endpoints = [
        ("POST", "/init-db"),
        ("POST", "/admin/init-db"),
        ("POST", "/api/init-db"),
        ("GET", "/test-db"),
        ("GET", "/admin/test-db"),
        ("GET", "/api/test-db"),
    ]
    
    for method, endpoint in endpoints:
        print(f"🔄 Trying {method} {endpoint}...")
        response = make_request(method, endpoint)
        if response:
            print(f"📊 Response: {response.status_code} - {response.text[:200]}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data.get('ok'):
                        print(f"✅ Success with {endpoint}")
                        return True
                except:
                    pass
    
    return False

def try_small_crawl():
    """Try a very small crawl"""
    print("🔄 Attempting small crawl...")
    response = make_request("POST", "/ingest/run?limit=1")
    if response and response.status_code == 200:
        data = response.json()
        print(f"✅ Small crawl: {data}")
        return True
    else:
        print(f"❌ Small crawl failed: {response.status_code if response else 'No response'}")
        return False

def check_articles():
    """Check if articles exist"""
    print("📰 Checking articles...")
    response = make_request("GET", "/api/articles?limit=1")
    if response and response.status_code == 200:
        try:
            data = response.json()
            count = data.get('count', 0)
            print(f"📊 Found {count} articles")
            return count > 0
        except:
            pass
    elif response:
        print(f"📊 Articles check: {response.status_code} - {response.text[:200]}")
    
    return False

def run_comprehensive_fix():
    """Run comprehensive fix process"""
    print("🚀 Starting comprehensive system fix...")
    
    # Step 1: Check health
    if not check_health():
        print("❌ API not responding, cannot proceed")
        return False
    
    # Step 2: Try database initialization
    db_init_success = try_database_init()
    
    # Step 3: Try small crawl
    if not db_init_success:
        print("🔄 Database init failed, trying small crawl...")
        crawl_success = try_small_crawl()
        if crawl_success:
            time.sleep(5)
    
    # Step 4: Check articles
    has_articles = check_articles()
    
    if has_articles:
        print("🎉 SUCCESS! System is working with articles")
        return True
    else:
        print("⚠️ System is responding but no articles found")
        print("💡 This might mean:")
        print("   - Database tables don't exist yet")
        print("   - Crawl failed to find articles")
        print("   - Articles were filtered out")
        return False

def main():
    """Main function"""
    print("🔧 Newsletter API System Fix Tool")
    print("=" * 50)
    
    success = run_comprehensive_fix()
    
    if success:
        print("\n✅ SYSTEM FIXED!")
        print("🔧 The API is now working properly")
        print("📰 You can now use the system to get articles")
    else:
        print("\n❌ SYSTEM STILL NEEDS WORK")
        print("🔧 The deployment might be stuck on an old version")
        print("💡 Try manually checking the Render dashboard")
        print("🔄 Or wait for the deployment to complete")

if __name__ == "__main__":
    main()
