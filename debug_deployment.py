#!/usr/bin/env python3
"""
Debug deployment script
"""

import requests
import time
import json

API_BASE = "https://newsletter-api-v2.onrender.com"

def test_all_endpoints():
    """Test all possible endpoints"""
    endpoints = [
        "/",
        "/health", 
        "/healthz",
        "/docs",
        "/test-database",
        "/initialize-database",
        "/api/articles",
        "/api/crawl",
        "/test-db",
        "/init-db",
        "/clear-db",
        "/admin/clear-db",
        "/admin/test-db",
        "/ingest/run",
        "/score/run"
    ]
    
    print("🔍 Testing all endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE}{endpoint}", timeout=10)
            print(f"✅ {endpoint}: {response.status_code}")
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict) and 'version' in data:
                        print(f"   Version: {data.get('version')}")
                except:
                    pass
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:50]}")

def check_deployment_status():
    """Check deployment status"""
    print("🚀 Checking deployment status...")
    
    # Test health endpoint multiple times to see if it changes
    for i in range(3):
        try:
            response = requests.get(f"{API_BASE}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Health check {i+1}: {data}")
            else:
                print(f"Health check {i+1}: {response.status_code}")
        except Exception as e:
            print(f"Health check {i+1}: {e}")
        
        if i < 2:
            time.sleep(5)

def main():
    """Main function"""
    print("🔧 Deployment Debug Tool")
    print("=" * 50)
    
    check_deployment_status()
    print("\n" + "=" * 50)
    test_all_endpoints()
    
    print("\n💡 Analysis:")
    print("- If all endpoints return 404, the deployment is completely stuck")
    print("- If only new endpoints return 404, the old version is still running")
    print("- If health shows old timestamp, the deployment hasn't updated")

if __name__ == "__main__":
    main()
