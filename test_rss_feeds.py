"""
Test RSS feeds to check which ones return solid articles
"""
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import json

async def test_rss_feed(session, feed_url, timeout=10):
    """Test a single RSS feed"""
    try:
        async with session.get(feed_url, timeout=aiohttp.ClientTimeout(total=timeout)) as response:
            if response.status != 200:
                return {
                    'url': feed_url,
                    'status': 'error',
                    'error': f'HTTP {response.status}',
                    'articles': 0
                }
            
            content = await response.text()
            feed = feedparser.parse(content)
            
            if not feed.entries:
                return {
                    'url': feed_url,
                    'status': 'empty',
                    'error': 'No entries found',
                    'articles': 0
                }
            
            # Analyze articles
            total_articles = len(feed.entries)
            recent_articles = 0
            stale_articles = 0
            no_date_articles = 0
            
            for entry in feed.entries:
                # Check if article has a published date
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    days_old = (datetime.now(timezone.utc) - published_date).days
                    
                    if days_old <= 30:  # Recent (within 30 days)
                        recent_articles += 1
                    else:
                        stale_articles += 1
                else:
                    no_date_articles += 1
            
            # Determine status
            if recent_articles > 0:
                status = 'active'
            elif stale_articles > 0:
                status = 'stale'  # Still relevant if has articles
            elif no_date_articles > 0:
                status = 'no_dates'  # Has articles but no dates
            else:
                status = 'empty'
            
            return {
                'url': feed_url,
                'status': status,
                'articles': total_articles,
                'recent_articles': recent_articles,
                'stale_articles': stale_articles,
                'no_date_articles': no_date_articles,
                'feed_title': getattr(feed.feed, 'title', 'Unknown'),
                'latest_article': feed.entries[0].title if feed.entries else None
            }
            
    except asyncio.TimeoutError:
        return {
            'url': feed_url,
            'status': 'timeout',
            'error': 'Request timeout',
            'articles': 0
        }
    except Exception as e:
        return {
            'url': feed_url,
            'status': 'error',
            'error': str(e),
            'articles': 0
        }

async def test_all_feeds():
    """Test all RSS feeds from seeds.json"""
    # Load feeds from seeds.json
    with open('app/seeds.json', 'r') as f:
        seeds_data = json.load(f)
    
    # Collect all unique feeds
    all_feeds = []
    for category, feeds in seeds_data.items():
        if isinstance(feeds, list):
            all_feeds.extend(feeds)
    
    # Remove duplicates while preserving order
    unique_feeds = []
    seen = set()
    for feed in all_feeds:
        if feed not in seen and feed.startswith('http'):
            unique_feeds.append(feed)
            seen.add(feed)
    
    print(f"Testing {len(unique_feeds)} RSS feeds...")
    print("=" * 80)
    
    # Test feeds in batches
    async with aiohttp.ClientSession(
        headers={'User-Agent': 'Newsletter API v4 RSS Tester'}
    ) as session:
        
        results = []
        for i, feed_url in enumerate(unique_feeds, 1):
            print(f"[{i:2d}/{len(unique_feeds)}] Testing: {feed_url}")
            
            result = await test_rss_feed(session, feed_url)
            results.append(result)
            
            # Print result
            if result['status'] == 'active':
                print(f"    ✅ ACTIVE - {result['articles']} articles ({result['recent_articles']} recent)")
            elif result['status'] == 'stale':
                print(f"    ⚠️  STALE - {result['articles']} articles ({result['stale_articles']} stale, still relevant)")
            elif result['status'] == 'no_dates':
                print(f"    📅 NO DATES - {result['articles']} articles (no publication dates)")
            elif result['status'] == 'empty':
                print(f"    📭 EMPTY - No articles found")
            elif result['status'] == 'timeout':
                print(f"    ⏱️  TIMEOUT - {result['error']}")
            else:
                print(f"    ❌ ERROR - {result['error']}")
            
            # Small delay between requests
            await asyncio.sleep(0.5)
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    active_feeds = [r for r in results if r['status'] == 'active']
    stale_feeds = [r for r in results if r['status'] == 'stale']
    no_date_feeds = [r for r in results if r['status'] == 'no_dates']
    empty_feeds = [r for r in results if r['status'] == 'empty']
    error_feeds = [r for r in results if r['status'] in ['error', 'timeout']]
    
    print(f"✅ ACTIVE FEEDS: {len(active_feeds)}")
    print(f"⚠️  STALE FEEDS (still relevant): {len(stale_feeds)}")
    print(f"📅 NO DATE FEEDS: {len(no_date_feeds)}")
    print(f"📭 EMPTY FEEDS: {len(empty_feeds)}")
    print(f"❌ ERROR FEEDS: {len(error_feeds)}")
    print(f"📊 TOTAL RELEVANT: {len(active_feeds) + len(stale_feeds) + len(no_date_feeds)}")
    
    # Show problematic feeds
    if empty_feeds or error_feeds:
        print(f"\n🚨 FEEDS TO REMOVE:")
        for result in empty_feeds + error_feeds:
            print(f"   - {result['url']} ({result['status']})")
    
    # Show best performing feeds
    print(f"\n🏆 TOP PERFORMING FEEDS:")
    top_feeds = sorted(
        [r for r in results if r['status'] in ['active', 'stale', 'no_dates']],
        key=lambda x: x['articles'],
        reverse=True
    )[:10]
    
    for i, result in enumerate(top_feeds, 1):
        print(f"   {i:2d}. {result['feed_title']} - {result['articles']} articles")
        print(f"       {result['url']}")
    
    # Save detailed results
    with open('rss_feed_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: rss_feed_test_results.json")

if __name__ == "__main__":
    asyncio.run(test_all_feeds())
