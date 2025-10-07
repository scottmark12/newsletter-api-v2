#!/usr/bin/env python3
"""
Script to generate unique content for articles using OpenAI
Run this after articles are scored to add unique "Why it matters" and takeaways
"""

import os
import sys
import asyncio
import httpx
from datetime import datetime

async def generate_content_for_articles(limit=50, hours=168):
    """Generate content for articles using the API endpoint"""
    
    # API endpoint
    url = "https://newsletter-api-v2.onrender.com/api/v4/admin/generate-content"
    
    params = {
        "limit": limit,
        "hours": hours
    }
    
    print(f"🚀 Generating unique content for articles...")
    print(f"   Limit: {limit} articles")
    print(f"   Timeframe: Last {hours} hours")
    print(f"   API: {url}")
    print()
    
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(url, params=params)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("ok"):
                    print("✅ Success!")
                    print(f"   Processed: {result.get('processed', 0)} articles")
                    print(f"   Errors: {result.get('errors', 0)} articles")
                    print(f"   Message: {result.get('message', '')}")
                else:
                    print("❌ Error:")
                    print(f"   {result.get('error', 'Unknown error')}")
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                print(f"   Response: {response.text}")
                
    except Exception as e:
        print(f"❌ Exception: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("🤖 OpenAI Content Generator for Newsletter API v4")
    print("=" * 60)
    print()
    
    # Check if OpenAI API key is configured
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("   Content generation will use fallback methods")
        print("   To use OpenAI, set: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # Default parameters
    limit = 50
    hours = 168  # Last week
    
    # Allow override via command line
    if len(sys.argv) > 1:
        try:
            limit = int(sys.argv[1])
        except ValueError:
            print(f"Invalid limit: {sys.argv[1]}")
            return
    
    if len(sys.argv) > 2:
        try:
            hours = int(sys.argv[2])
        except ValueError:
            print(f"Invalid hours: {sys.argv[2]}")
            return
    
    # Run the content generation
    asyncio.run(generate_content_for_articles(limit, hours))
    
    print()
    print("=" * 60)
    print(f"✨ Content generation completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
