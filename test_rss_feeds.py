#!/usr/bin/env python3
"""
Test RSS feeds to see which ones are working
"""

import feedparser
import requests

def test_rss_feed(url):
    """Test if an RSS feed is accessible and has content"""
    try:
        print(f"🔍 Testing: {url}")
        
        # First check if URL is accessible
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"   ❌ HTTP {response.status_code}")
            return False
        
        # Parse RSS feed
        feed = feedparser.parse(url)
        
        if feed.bozo:
            print(f"   ⚠️  RSS parsing error: {feed.bozo_exception}")
            return False
        
        if not feed.entries:
            print(f"   ❌ No entries found")
            return False
        
        print(f"   ✅ {len(feed.entries)} articles found")
        if feed.entries:
            latest = feed.entries[0]
            print(f"   📰 Latest: {latest.get('title', 'No title')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Test key RSS feeds"""
    print("🧪 Testing Professional RSS Feeds...\n")
    
    # Key professional feeds to test
    test_feeds = [
        "https://www.enr.com/rss/all",
        "https://commercialobserver.com/feed/",
        "https://www.constructiondive.com/feeds/news/",
        "https://therealdeal.com/feed/",
        "https://www.bdcnetwork.com/rss.xml",
        "https://www.dezeen.com/feed/",
        "https://www.globest.com/rss/",
        "https://www.reit.com/rss",
        "https://www.penews.com/rss/",
        "https://www.cbre.com/rss"
    ]
    
    working_feeds = []
    broken_feeds = []
    
    for feed_url in test_feeds:
        if test_rss_feed(feed_url):
            working_feeds.append(feed_url)
        else:
            broken_feeds.append(feed_url)
        print()
    
    print("📊 Results:")
    print(f"✅ Working feeds: {len(working_feeds)}")
    print(f"❌ Broken feeds: {len(broken_feeds)}")
    
    if broken_feeds:
        print("\n❌ Broken feeds:")
        for feed in broken_feeds:
            print(f"   - {feed}")
    
    if working_feeds:
        print("\n✅ Working feeds:")
        for feed in working_feeds:
            print(f"   - {feed}")

if __name__ == "__main__":
    main()
