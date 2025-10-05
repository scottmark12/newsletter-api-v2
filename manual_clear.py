#!/usr/bin/env python3
"""
Manual database clearing script for when Render deployments are stuck
"""

import requests
import json

def manual_clear_articles():
    """Manually clear low-quality articles by making API calls"""
    
    api_base = "https://newsletter-api-v2.onrender.com"
    
    print("🔍 Checking current articles...")
    
    # Get current articles
    response = requests.get(f"{api_base}/api/articles")
    if response.status_code != 200:
        print(f"❌ Failed to get articles: {response.status_code}")
        return
    
    data = response.json()
    articles = data.get('items', [])
    
    print(f"📊 Found {len(articles)} articles")
    
    if len(articles) == 0:
        print("✅ Database is already empty!")
        return
    
    # Identify low-quality articles
    low_quality_articles = []
    for article in articles:
        url = article.get('url', '').lower()
        title = article.get('title', '').lower()
        source = article.get('source', '').lower()
        
        # Check for exclusion criteria
        is_low_quality = False
        reason = ""
        
        if '/question/' in url:
            is_low_quality = True
            reason = "Forum question"
        elif 'greenbuildingadvisor' in source and any(word in title for word in ['piano', 'water heater', 'shower', 'basement']):
            is_low_quality = True
            reason = "Personal homeowner question"
        elif any(word in title for word in ['my house', 'my home', 'my basement']):
            is_low_quality = True
            reason = "Personal question"
        
        if is_low_quality:
            low_quality_articles.append({
                'id': article.get('id'),
                'title': article.get('title'),
                'reason': reason
            })
    
    print(f"🚫 Found {len(low_quality_articles)} low-quality articles:")
    for article in low_quality_articles:
        print(f"   • {article['title']} ({article['reason']})")
    
    if len(low_quality_articles) == 0:
        print("✅ No low-quality articles found!")
        return
    
    print(f"\n💡 Since Render deployments are stuck, here are your options:")
    print(f"1. Wait for Render deployment to complete (clear-db endpoint)")
    print(f"2. Run a fresh crawl to get better articles")
    print(f"3. These articles should be filtered out by the scoring system")
    
    # Try to trigger a fresh crawl
    print(f"\n🔄 Attempting to trigger a fresh crawl...")
    try:
        crawl_response = requests.post(f"{api_base}/ingest/run?limit=5", timeout=30)
        if crawl_response.status_code == 200:
            result = crawl_response.json()
            print(f"✅ Crawl triggered: {result}")
        else:
            print(f"❌ Crawl failed: {crawl_response.status_code}")
    except Exception as e:
        print(f"❌ Crawl error: {e}")

if __name__ == "__main__":
    manual_clear_articles()
