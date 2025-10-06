#!/usr/bin/env python3
"""
Diagnostic script to identify deployment and database issues
"""

import requests
import json
from datetime import datetime

def test_api_endpoints():
    """Test all available API endpoints"""
    base_url = "https://newsletter-api-v2.onrender.com"
    
    endpoints = [
        "/health",
        "/",
        "/docs",
        "/openapi.json",
        "/api/articles",
        "/ingest/run",
        "/score/run"
    ]
    
    print("🔍 Testing API Endpoints")
    print("=" * 50)
    
    for endpoint in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            if endpoint == "/ingest/run":
                response = requests.post(url, timeout=10)
            else:
                response = requests.get(url, timeout=10)
            
            print(f"✅ {endpoint}: {response.status_code}")
            if endpoint == "/health":
                try:
                    data = response.json()
                    print(f"   Version: {data.get('version', 'N/A')}")
                    print(f"   Timestamp: {data.get('timestamp', 'N/A')}")
                except:
                    pass
                    
        except requests.exceptions.Timeout:
            print(f"⏰ {endpoint}: TIMEOUT")
        except requests.exceptions.RequestException as e:
            print(f"❌ {endpoint}: {str(e)[:50]}...")
        except Exception as e:
            print(f"❌ {endpoint}: {str(e)[:50]}...")

def check_database_url():
    """Check if database URL is accessible"""
    print("\n🗄️ Database URL Analysis")
    print("=" * 50)
    
    db_url = "postgresql://newsletter_db_v3_user:VHpHOSx5hObdEa6nKTG0iv03i54QIjTm@dpg-d3h9c2juibrs73aome20-a/newsletter_db_v3"
    
    # Parse the URL
    parts = db_url.split('@')
    if len(parts) == 2:
        credentials = parts[0].split('//')[1]
        host_port_db = parts[1]
        
        print(f"Host: {host_port_db.split('/')[0]}")
        print(f"Database: {host_port_db.split('/')[1]}")
        print(f"User: {credentials.split(':')[0]}")
        print(f"Password: {'*' * len(credentials.split(':')[1])}")
        
        # Test hostname resolution
        import socket
        hostname = host_port_db.split('/')[0].split(':')[0]
        try:
            ip = socket.gethostbyname(hostname)
            print(f"✅ Hostname resolves to: {ip}")
        except socket.gaierror:
            print(f"❌ Hostname cannot be resolved: {hostname}")

def provide_solutions():
    """Provide specific solutions"""
    print("\n🛠️ Recommended Solutions")
    print("=" * 50)
    
    print("1. **Database Issue**: The hostname 'dpg-d3h9c2juibrs73aome20-a' cannot be resolved")
    print("   - Check if the database service is running in Render")
    print("   - Verify the database URL in Render dashboard")
    print("   - The database might be paused or deleted")
    
    print("\n2. **Deployment Issue**: API is stuck on old version")
    print("   - Go to Render Dashboard → Your Service → Settings")
    print("   - Check 'Auto-Deploy' is enabled")
    print("   - Try 'Manual Deploy' from latest commit")
    print("   - Or restart the service completely")
    
    print("\n3. **Immediate Fix**: Create new database")
    print("   - Go to Render Dashboard → Create → PostgreSQL")
    print("   - Use the new database URL")
    print("   - Update environment variables")
    
    print("\n4. **Alternative**: Use Render's database tools")
    print("   - Go to Render Dashboard → Your Database → Connect")
    print("   - Use the web-based SQL editor to create tables")

if __name__ == "__main__":
    print("🎯 Newsletter API Diagnostic Tool")
    print("=" * 50)
    
    test_api_endpoints()
    check_database_url()
    provide_solutions()
    
    print(f"\n⏰ Diagnostic completed at: {datetime.now().isoformat()}")
