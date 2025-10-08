#!/usr/bin/env python3
"""
Quick Newsletter Workflow Script
Fast workflow to ingest, score, enhance, and refresh
"""

import requests
import time
from datetime import datetime, timezone

# Configuration
API_BASE = "https://newsletter-api-v2.onrender.com"

def run_quick_workflow():
    """Run the quick workflow"""
    print("🚀 Starting Quick Newsletter Workflow...")
    print(f"API: {API_BASE}")
    print(f"Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("-" * 50)
    
    # Step 1: Ingest articles
    print("📥 Step 1: Ingesting articles...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/collect", timeout=300)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Ingested {data.get('collected', 0)} articles")
        else:
            print(f"❌ Ingestion failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Ingestion error: {e}")
    
    time.sleep(5)
    
    # Step 2: Clear old scores
    print("🧹 Step 2: Clearing old scores...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/clear-scores", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cleared {data.get('deleted_count', 0)} old scores")
        else:
            print(f"❌ Clear scores failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Clear scores error: {e}")
    
    time.sleep(5)
    
    # Step 3: Score articles
    print("🎯 Step 3: Scoring articles with BUILT grader...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/score", timeout=600)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Scored {data.get('scored', 0)} articles, rejected {data.get('rejected', 0)}")
        else:
            print(f"❌ Scoring failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Scoring error: {e}")
    
    time.sleep(5)
    
    # Step 4: Create summaries and 'why it matters'
    print("📝 Step 4: Creating summaries and 'why it matters'...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/generate-content", timeout=600)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Created {data.get('enhanced', 0)} summaries")
        else:
            print(f"❌ Summary creation failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Summary creation error: {e}")
    
    time.sleep(5)
    
    # Step 5: Pull photos
    print("🖼️  Step 5: Extracting photos...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/extract-images", timeout=600)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Extracted {data.get('images_extracted', 0)} photos")
        else:
            print(f"❌ Photo extraction failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Photo extraction error: {e}")
    
    time.sleep(5)
    
    # Step 6: Clean up old articles (older than a week)
    print("🧹 Step 6: Cleaning up articles older than a week...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/cleanup-old-articles", timeout=60)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Cleaned up {data.get('cleaned_count', 0)} old articles")
        else:
            print(f"❌ Cleanup failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Cleanup error: {e}")
    
    # Step 7: Get final stats
    print("📊 Step 7: Getting final stats...")
    try:
        response = requests.get(f"{API_BASE}/api/v4/admin/stats", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Final stats:")
            print(f"   Total articles: {data.get('total_articles', 0)}")
            print(f"   Scored articles: {data.get('scored_articles', 0)}")
            print(f"   Unscored articles: {data.get('unscored_articles', 0)}")
        else:
            print(f"❌ Stats failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Stats error: {e}")
    
    print("-" * 50)
    print("🎉 Quick workflow complete!")
    print(f"🌐 View your newsletter with new rankings: {API_BASE}/website")

if __name__ == "__main__":
    run_quick_workflow()
