#!/usr/bin/env python3
"""
Force the system to work by using existing endpoints creatively
"""

import requests
import time
import json

API_BASE = "https://newsletter-api-v2.onrender.com"

def test_health():
    """Test API health"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=10)
        print(f"✅ Health: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health failed: {e}")
        return False

def try_score_run():
    """Try to run scoring which might initialize database"""
    try:
        print("🔄 Trying scoring run to initialize database...")
        response = requests.post(f"{API_BASE}/score/run", timeout=120)
        if response.status_code == 200:
            print(f"✅ Score run: {response.json()}")
            return True
        else:
            print(f"⚠️ Score run: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Score run failed: {e}")
        return False

def try_small_ingest():
    """Try very small ingest"""
    try:
        print("🔄 Trying small ingest...")
        response = requests.post(f"{API_BASE}/ingest/run?limit=1", timeout=60)
        if response.status_code == 200:
            print(f"✅ Small ingest: {response.json()}")
            return True
        else:
            print(f"⚠️ Small ingest: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Small ingest failed: {e}")
        return False

def check_articles():
    """Check articles"""
    try:
        response = requests.get(f"{API_BASE}/api/articles?limit=1", timeout=30)
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"📊 Articles: {count}")
            return count > 0
        else:
            print(f"⚠️ Articles check: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Articles check failed: {e}")
        return False

def main():
    print("🚀 Forcing system to work...")
    
    # Test health
    if not test_health():
        return
    
    # Try different approaches
    approaches = [
        ("Score run", try_score_run),
        ("Small ingest", try_small_ingest),
    ]
    
    for name, func in approaches:
        print(f"\n🔄 Trying {name}...")
        try:
            success = func()
            if success:
                print(f"✅ {name} succeeded!")
                time.sleep(5)
                if check_articles():
                    print("🎉 SUCCESS! Articles found!")
                    return
        except Exception as e:
            print(f"❌ {name} failed: {e}")
    
    print("\n💡 All approaches failed. The deployment might be stuck.")
    print("🔧 Manual intervention needed - check Render dashboard")

if __name__ == "__main__":
    main()
