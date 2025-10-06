"""
Google News RSS Feed Generator for Newsletter API v4
Converts targeted queries into RSS feeds using Google News RSS
"""

from typing import List, Dict
import urllib.parse
import asyncio
import aiohttp
import feedparser
from datetime import datetime, timezone
from dataclasses import dataclass

@dataclass
class QueryCategory:
    """Category for organizing queries"""
    name: str
    description: str
    queries: List[str]

class GoogleNewsRSSGenerator:
    """Generates RSS feeds from Google News queries"""
    
    def __init__(self):
        self.base_url = "https://news.google.com/rss/search?q="
        
        # Define all query categories
        self.query_categories = [
            QueryCategory(
                name="Opportunities",
                description="Market opportunities, investments, and success stories",
                queries=[
                    "real estate development case study OR success story",
                    "multifamily investment ROI OR returns",
                    "Airbnb investment success OR portfolio",
                    "adaptive reuse commercial real estate",
                    "small developer growth OR scaled up"
                ]
            ),
            
            QueryCategory(
                name="Practices",
                description="Building methods, techniques, and productivity",
                queries=[
                    "modular construction OR prefab construction",
                    "timber construction OR mass timber",
                    "construction productivity study OR research",
                    "building practices innovation OR efficiency",
                    "architecture design biophilic OR wellness productivity"
                ]
            ),
            
            QueryCategory(
                name="Systems_Codes",
                description="Policies, regulations, and building codes",
                queries=[
                    "zoning reform real estate",
                    "building code timber OR update OR reform",
                    "incentives development OR opportunity zone",
                    "construction regulation update OR change",
                    "sustainable building code OR green building policy"
                ]
            ),
            
            QueryCategory(
                name="Vision",
                description="Smart cities, future development, and long-term insights",
                queries=[
                    "smart city development OR infrastructure",
                    "future of real estate OR future of cities",
                    "urban planning insights OR innovation",
                    "placemaking community impact",
                    "architecture of the future OR visionary design"
                ]
            ),
            
            QueryCategory(
                name="Big_Firm_Insights",
                description="Direct research from major CRE and financial firms",
                queries=[
                    "CBRE insights site:cbre.com",
                    "JLL research site:jll.com",
                    "Colliers site:colliers.com research OR insights",
                    "Brookfield site:brookfield.com insights",
                    "Prologis site:prologis.com insights",
                    "market insights site:nar.realtor"
                ]
            )
        ]
    
    def generate_rss_url(self, query: str) -> str:
        """Generate RSS URL for a Google News query"""
        # URL encode the query
        encoded_query = urllib.parse.quote_plus(query)
        return f"{self.base_url}{encoded_query}"
    
    def get_all_rss_feeds(self) -> Dict[str, List[str]]:
        """Get all RSS feeds organized by category"""
        all_feeds = {}
        
        for category in self.query_categories:
            feeds = []
            for query in category.queries:
                rss_url = self.generate_rss_url(query)
                feeds.append(rss_url)
            
            all_feeds[category.name] = feeds
        
        return all_feeds
    
    def get_flat_rss_list(self) -> List[str]:
        """Get a flat list of all RSS feeds"""
        all_feeds = []
        for category in self.query_categories:
            for query in category.queries:
                rss_url = self.generate_rss_url(query)
                all_feeds.append(rss_url)
        return all_feeds
    
    async def test_rss_feed(self, rss_url: str, query: str) -> Dict:
        """Test if an RSS feed is working and return stats"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(rss_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status != 200:
                        return {
                            'query': query,
                            'url': rss_url,
                            'status': 'error',
                            'error': f'HTTP {response.status}',
                            'articles': 0
                        }
                    
                    content = await response.text()
                    feed = feedparser.parse(content)
                    
                    if not feed.entries:
                        return {
                            'query': query,
                            'url': rss_url,
                            'status': 'empty',
                            'error': 'No entries found',
                            'articles': 0
                        }
                    
                    # Analyze recent articles
                    recent_articles = 0
                    for entry in feed.entries:
                        # Check if article is recent (within 7 days)
                        if hasattr(entry, 'published_parsed') and entry.published_parsed:
                            published_date = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                            days_old = (datetime.now(timezone.utc) - published_date).days
                            if days_old <= 7:
                                recent_articles += 1
                        else:
                            # If no date, assume recent
                            recent_articles += 1
                    
                    return {
                        'query': query,
                        'url': rss_url,
                        'status': 'working',
                        'total_articles': len(feed.entries),
                        'recent_articles': recent_articles,
                        'feed_title': getattr(feed.feed, 'title', 'Unknown')
                    }
                    
        except Exception as e:
            return {
                'query': query,
                'url': rss_url,
                'status': 'error',
                'error': str(e),
                'articles': 0
            }
    
    async def test_all_feeds(self) -> Dict:
        """Test all RSS feeds and return results"""
        results = {}
        
        print("Testing Google News RSS feeds...")
        print("=" * 80)
        
        for category in self.query_categories:
            print(f"\n📂 {category.name} ({category.description})")
            category_results = []
            
            for query in category.queries:
                rss_url = self.generate_rss_url(query)
                result = await self.test_rss_feed(rss_url, query)
                category_results.append(result)
                
                # Print result
                if result['status'] == 'working':
                    print(f"  ✅ {query[:50]}... - {result['recent_articles']} recent articles")
                elif result['status'] == 'empty':
                    print(f"  📭 {query[:50]}... - No articles found")
                else:
                    print(f"  ❌ {query[:50]}... - {result.get('error', 'Unknown error')}")
                
                # Rate limiting
                await asyncio.sleep(0.5)
            
            results[category.name] = category_results
        
        return results

# Convenience functions
def get_google_news_rss_feeds() -> List[str]:
    """Get all Google News RSS feeds as a flat list"""
    generator = GoogleNewsRSSGenerator()
    return generator.get_flat_rss_list()

def get_google_news_feeds_by_category() -> Dict[str, List[str]]:
    """Get Google News RSS feeds organized by category"""
    generator = GoogleNewsRSSGenerator()
    return generator.get_all_rss_feeds()

async def test_google_news_feeds():
    """Test all Google News RSS feeds"""
    generator = GoogleNewsRSSGenerator()
    return await generator.test_all_feeds()

# Example usage
if __name__ == "__main__":
    generator = GoogleNewsRSSGenerator()
    
    print("Google News RSS Feed Generator")
    print("=" * 50)
    print(f"Total queries: {sum(len(cat.queries) for cat in generator.query_categories)}")
    print(f"Total RSS feeds: {len(generator.get_flat_rss_list())}")
    
    print("\nCategories and Query Count:")
    for category in generator.query_categories:
        print(f"  {category.name}: {len(category.queries)} queries")
    
    print("\nSample RSS URLs:")
    sample_feeds = generator.get_flat_rss_list()[:5]
    for i, feed in enumerate(sample_feeds, 1):
        print(f"  {i}. {feed}")
    
    print(f"\nRun 'asyncio.run(test_google_news_feeds())' to test all feeds")
