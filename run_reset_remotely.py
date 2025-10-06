#!/usr/bin/env python3
"""
Remote Database Reset Script
Runs the database reset on the live Render service
"""

import requests
import time
import json

def run_remote_reset():
    """Run database reset on the live service"""
    
    base_url = "https://newsletter-api-v2.onrender.com"
    
    print("🔄 Running remote database reset on live service...")
    print("=" * 60)
    
    # Step 1: Try to clear articles (if endpoint exists)
    print("🗑️  Attempting to clear existing articles...")
    try:
        response = requests.delete(f"{base_url}/api/v4/admin/clear-articles", timeout=30)
        if response.status_code == 200:
            print("✅ Successfully cleared existing articles")
        else:
            print(f"⚠️  Clear endpoint not available (status: {response.status_code})")
    except Exception as e:
        print(f"⚠️  Could not clear articles: {e}")
    
    # Step 2: Run fresh data collection
    print("📡 Running fresh data collection with enhanced scoring...")
    try:
        response = requests.post(f"{base_url}/api/v4/admin/collect", timeout=300)  # 5 minute timeout
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Data collection complete!")
            print(f"   Articles collected: {result.get('total_collected', 'Unknown')}")
            print(f"   Articles stored: {result.get('stored', 'Unknown')}")
        else:
            print(f"❌ Data collection failed (status: {response.status_code})")
            print(f"   Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        return
    
    # Step 3: Check results
    print("\n📊 Checking results...")
    time.sleep(5)  # Wait for processing
    
    try:
        # Check stats
        response = requests.get(f"{base_url}/api/v4/admin/stats", timeout=30)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Database stats:")
            print(f"   Total articles: {stats.get('total_articles', 0)}")
            print(f"   Scored articles: {stats.get('scored_articles', 0)}")
            print(f"   Scoring coverage: {stats.get('scoring_coverage', '0%')}")
        
        # Check high-quality opportunities
        response = requests.get(f"{base_url}/api/v4/opportunities?min_score=0.4&limit=3", timeout=30)
        if response.status_code == 200:
            opportunities = response.json()
            print(f"\n🎯 High-quality opportunities found: {opportunities.get('count', 0)}")
            for article in opportunities.get('articles', [])[:3]:
                score = article.get('score', {})
                print(f"   • {article.get('title', 'No title')[:60]}... (Score: {score.get('total', 0):.3f})")
        
        # Check practices
        response = requests.get(f"{base_url}/api/v4/practices?min_score=0.4&limit=3", timeout=30)
        if response.status_code == 200:
            practices = response.json()
            print(f"\n🔧 High-quality practices found: {practices.get('count', 0)}")
            for article in practices.get('articles', [])[:3]:
                score = article.get('score', {})
                print(f"   • {article.get('title', 'No title')[:60]}... (Score: {score.get('total', 0):.3f})")
                
    except Exception as e:
        print(f"⚠️  Could not check results: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Remote reset complete!")
    print("🌐 Check your live service at: https://newsletter-api-v2.onrender.com/website")
    print("📊 View dashboard at: https://newsletter-api-v2.onrender.com/dashboard")
    print("=" * 60)

if __name__ == "__main__":
    run_remote_reset()
