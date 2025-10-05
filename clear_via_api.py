#!/usr/bin/env python3
"""
Clear database via API by running crawler with limit 0
"""
import requests
import time

def clear_database():
    """Clear database by running crawler with limit 0"""
    base_url = "https://newsletter-api-v2.onrender.com"
    
    print("🔄 Attempting to clear database via API...")
    
    # First, check current articles
    try:
        response = requests.get(f"{base_url}/api/articles?limit=10")
        data = response.json()
        print(f"📊 Current articles: {data['count']}")
        
        if data['count'] == 0:
            print("✅ Database is already empty!")
            return True
            
    except Exception as e:
        print(f"❌ Error checking articles: {e}")
        return False
    
    # Try to run crawler with limit 0 (might clear old articles)
    try:
        print("🚀 Running crawler with limit 0...")
        response = requests.post(f"{base_url}/ingest/run?limit=0")
        print(f"Crawler response: {response.json()}")
        
        # Wait a moment
        time.sleep(5)
        
        # Check articles again
        response = requests.get(f"{base_url}/api/articles?limit=10")
        data = response.json()
        print(f"📊 Articles after crawler: {data['count']}")
        
        if data['count'] == 0:
            print("✅ Database cleared successfully!")
            return True
        else:
            print("⚠️  Articles still exist, trying scoring to filter them...")
            
            # Run scoring to filter out bad articles
            response = requests.post(f"{base_url}/score/run")
            result = response.json()
            print(f"Scoring result: {result}")
            
            # Check articles again
            time.sleep(3)
            response = requests.get(f"{base_url}/api/articles?limit=10")
            data = response.json()
            print(f"📊 Articles after scoring: {data['count']}")
            
            if data['count'] == 0:
                print("✅ Database cleared via scoring filters!")
                return True
            else:
                print(f"⚠️  Still {data['count']} articles remaining")
                return False
                
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        return False

if __name__ == "__main__":
    clear_database()
