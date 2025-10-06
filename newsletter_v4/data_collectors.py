"""
Data collection system for Newsletter API v4
Clean, modular data collectors for RSS, Google, and web scraping
"""

import asyncio
import aiohttp
import feedparser
import json
from typing import List, Dict, Optional, AsyncGenerator
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
from dataclasses import dataclass

from .config import get_config


@dataclass
class ArticleData:
    """Standardized article data structure"""
    title: str
    url: str
    source: str
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[datetime] = None
    tags: Optional[List[str]] = None


class RSSCollector:
    """Collects articles from RSS feeds"""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Newsletter API v4 Bot'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_rss_feed(self, feed_url: str) -> List[ArticleData]:
        """Fetch articles from a single RSS feed"""
        try:
            async with self.session.get(feed_url) as response:
                if response.status != 200:
                    print(f"RSS feed error: {feed_url} - Status {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries[:self.config.data_sources.max_articles_per_source]:
                    # Extract basic info
                    title = getattr(entry, 'title', 'No Title')
                    url = getattr(entry, 'link', '')
                    
                    if not url:
                        continue
                    
                    # Extract content
                    content = ""
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value
                    elif hasattr(entry, 'summary'):
                        content = entry.summary
                    
                    # Extract metadata
                    author = getattr(entry, 'author', None)
                    published_at = None
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
                    
                    # Extract source from feed
                    source = getattr(feed.feed, 'title', urlparse(feed_url).netloc)
                    
                    articles.append(ArticleData(
                        title=title,
                        url=url,
                        content=content,
                        summary=content[:500] + "..." if len(content) > 500 else content,
                        source=source,
                        author=author,
                        published_at=published_at,
                        tags=getattr(entry, 'tags', [])
                    ))
                
                return articles
                
        except Exception as e:
            print(f"RSS collection error for {feed_url}: {e}")
            return []
    
    async def collect_all_feeds(self) -> List[ArticleData]:
        """Collect from all configured RSS feeds"""
        all_articles = []
        
        for feed_url in self.config.data_sources.rss_feeds:
            print(f"Collecting from RSS feed: {feed_url}")
            articles = await self.fetch_rss_feed(feed_url)
            all_articles.extend(articles)
            
            # Rate limiting
            await asyncio.sleep(self.config.data_sources.request_delay)
        
        return all_articles


class GoogleCollector:
    """Collects articles using Google Custom Search"""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Newsletter API v4 Bot'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def search_google(self, query: str, num_results: int = 10) -> List[ArticleData]:
        """Search Google for articles"""
        if not self.config.data_sources.google_api_key or not self.config.data_sources.google_cse_id:
            print("Google API credentials not configured")
            return []
        
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.config.data_sources.google_api_key,
                'cx': self.config.data_sources.google_cse_id,
                'q': query,
                'num': min(num_results, 10),
                'dateRestrict': 'd7',  # Last 7 days
                'siteSearch': 'constructiondive.com OR enr.com OR bisnow.com OR commercialobserver.com'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"Google search error: Status {response.status}")
                    return []
                
                data = await response.json()
                articles = []
                
                for item in data.get('items', []):
                    title = item.get('title', 'No Title')
                    url = item.get('link', '')
                    snippet = item.get('snippet', '')
                    
                    if not url:
                        continue
                    
                    # Extract source from URL
                    source = urlparse(url).netloc.replace('www.', '')
                    
                    articles.append(ArticleData(
                        title=title,
                        url=url,
                        content=snippet,
                        summary=snippet,
                        source=source,
                        published_at=datetime.now(timezone.utc)
                    ))
                
                return articles
                
        except Exception as e:
            print(f"Google search error: {e}")
            return []
    
    async def collect_construction_news(self) -> List[ArticleData]:
        """Collect construction and real estate news from Google"""
        queries = [
            "construction industry news",
            "real estate development",
            "construction technology innovation",
            "sustainable construction practices",
            "construction market trends"
        ]
        
        all_articles = []
        for query in queries:
            print(f"Google searching: {query}")
            articles = await self.search_google(query, 5)
            all_articles.extend(articles)
            await asyncio.sleep(1)  # Rate limiting
        
        return all_articles


class WebScraper:
    """Scrapes articles from web pages"""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_article(self, url: str) -> Optional[ArticleData]:
        """Scrape a single article"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract title
                title = ""
                title_tag = soup.find('h1') or soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
                
                # Extract content
                content = ""
                content_selectors = [
                    'article', '.article-content', '.post-content', 
                    '.entry-content', '.story-content', 'main'
                ]
                
                for selector in content_selectors:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text().strip()
                        break
                
                if not content:
                    # Fallback: get all paragraph text
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs])
                
                # Extract metadata
                author = ""
                author_tag = soup.find('meta', {'name': 'author'}) or soup.find('.author')
                if author_tag:
                    author = author_tag.get('content') or author_tag.get_text().strip()
                
                # Extract source from URL
                source = urlparse(url).netloc.replace('www.', '')
                
                return ArticleData(
                    title=title,
                    url=url,
                    content=content,
                    summary=content[:500] + "..." if len(content) > 500 else content,
                    source=source,
                    author=author,
                    published_at=datetime.now(timezone.utc)
                )
                
        except Exception as e:
            print(f"Web scraping error for {url}: {e}")
            return None
    
    async def scrape_urls(self, urls: List[str]) -> List[ArticleData]:
        """Scrape multiple URLs"""
        articles = []
        
        for url in urls:
            print(f"Scraping: {url}")
            article = await self.scrape_article(url)
            if article:
                articles.append(article)
            
            await asyncio.sleep(self.config.data_sources.request_delay)
        
        return articles


class DataCollectorManager:
    """Manages all data collection activities"""
    
    def __init__(self):
        self.config = get_config()
    
    async def collect_all_sources(self) -> List[ArticleData]:
        """Collect from all data sources"""
        all_articles = []
        
        print("Starting data collection from all sources...")
        
        # Collect from RSS feeds
        async with RSSCollector() as rss_collector:
            rss_articles = await rss_collector.collect_all_feeds()
            all_articles.extend(rss_articles)
            print(f"Collected {len(rss_articles)} articles from RSS feeds")
        
        # Collect from Google (if configured)
        if self.config.data_sources.google_api_key:
            async with GoogleCollector() as google_collector:
                google_articles = await google_collector.collect_construction_news()
                all_articles.extend(google_articles)
                print(f"Collected {len(google_articles)} articles from Google")
        
        # Remove duplicates based on URL
        unique_articles = {}
        for article in all_articles:
            if article.url not in unique_articles:
                unique_articles[article.url] = article
        
        final_articles = list(unique_articles.values())
        print(f"Total unique articles collected: {len(final_articles)}")
        
        return final_articles


# Convenience functions
async def collect_all_articles() -> List[ArticleData]:
    """Collect articles from all sources"""
    manager = DataCollectorManager()
    return await manager.collect_all_sources()


async def collect_rss_articles() -> List[ArticleData]:
    """Collect articles from RSS feeds only"""
    async with RSSCollector() as collector:
        return await collector.collect_all_feeds()


async def collect_google_articles() -> List[ArticleData]:
    """Collect articles from Google search only"""
    async with GoogleCollector() as collector:
        return await collector.collect_construction_news()
