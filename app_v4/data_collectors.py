"""
Newsletter API v4 Data Collectors
RSS, Google queries, web scraping, and YouTube data collection
"""

import asyncio
import aiohttp
import feedparser
import requests
from bs4 import BeautifulSoup
import trafilatura
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
import logging
import time
from urllib.parse import urljoin, urlparse
import json
import re

from .config import get_config
from .models import Article, ContentSource, VideoContent, get_session

logger = logging.getLogger(__name__)

class RSSCollector:
    """RSS feed collector"""
    
    def __init__(self):
        self.config = get_config().data_collection
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def collect_from_feeds(self, feeds: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Collect articles from RSS feeds"""
        if feeds is None:
            feeds = self.config.rss_feeds
        
        articles = []
        
        for feed_url in feeds:
            try:
                logger.info(f"Collecting from RSS feed: {feed_url}")
                feed_articles = await self._collect_from_feed(feed_url)
                articles.extend(feed_articles)
                
                # Rate limiting
                await asyncio.sleep(self.config.crawler_delay)
                
            except Exception as e:
                logger.error(f"Error collecting from feed {feed_url}: {str(e)}")
                continue
        
        logger.info(f"Collected {len(articles)} articles from RSS feeds")
        return articles
    
    async def _collect_from_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Collect articles from a single RSS feed"""
        articles = []
        
        try:
            # Parse RSS feed
            feed = feedparser.parse(feed_url)
            
            if feed.bozo:
                logger.warning(f"RSS feed has parsing issues: {feed_url}")
            
            for entry in feed.entries[:self.config.max_articles_per_source]:
                try:
                    article = {
                        'url': entry.get('link', ''),
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', '') or entry.get('description', ''),
                        'source': self._extract_source_from_url(entry.get('link', '')),
                        'published_at': self._parse_published_date(entry.get('published', '')),
                        'lang': 'en',
                        'status': 'fetched',
                        'media_type': 'article'
                    }
                    
                    # Validate article
                    if self._validate_article(article):
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error processing RSS entry: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error parsing RSS feed {feed_url}: {str(e)}")
        
        return articles
    
    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        if not url:
            return 'unknown'
        
        try:
            domain = urlparse(url).netloc
            # Remove www. prefix
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'unknown'
    
    def _parse_published_date(self, date_str: str) -> Optional[datetime]:
        """Parse published date from various formats"""
        if not date_str:
            return None
        
        try:
            # Try common date formats
            formats = [
                '%a, %d %b %Y %H:%M:%S %z',
                '%a, %d %b %Y %H:%M:%S %Z',
                '%Y-%m-%dT%H:%M:%S%z',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # Fallback to feedparser's parsing
            parsed = feedparser._parse_date(date_str)
            if parsed:
                return datetime.fromtimestamp(time.mktime(parsed), tz=timezone.utc)
                
        except Exception as e:
            logger.error(f"Error parsing date {date_str}: {str(e)}")
        
        return datetime.now(timezone.utc)
    
    def _validate_article(self, article: Dict[str, Any]) -> bool:
        """Validate article data"""
        required_fields = ['url', 'title']
        return all(article.get(field) for field in required_fields)

class GoogleSearchCollector:
    """Google Custom Search collector"""
    
    def __init__(self):
        self.config = get_config().data_collection
        self.api_key = self.config.google_api_key
        self.cse_id = self.config.google_cse_id
        
        if not self.api_key or not self.cse_id:
            logger.warning("Google API key or CSE ID not configured")
    
    async def collect_from_queries(self, queries: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Collect articles using Google Custom Search"""
        if not self.api_key or not self.cse_id:
            logger.warning("Google search not configured, skipping")
            return []
        
        if queries is None:
            queries = self.config.google_queries
        
        articles = []
        
        for query in queries:
            try:
                logger.info(f"Searching Google for: {query}")
                search_results = await self._search_google(query)
                articles.extend(search_results)
                
                # Rate limiting
                await asyncio.sleep(self.config.crawler_delay * 2)  # Slower for Google API
                
            except Exception as e:
                logger.error(f"Error searching Google for '{query}': {str(e)}")
                continue
        
        logger.info(f"Collected {len(articles)} articles from Google search")
        return articles
    
    async def _search_google(self, query: str, num_results: int = 10) -> List[Dict[str, Any]]:
        """Search Google Custom Search API"""
        articles = []
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            'key': self.api_key,
            'cx': self.cse_id,
            'q': query,
            'num': num_results,
            'dateRestrict': 'd7',  # Last 7 days
            'sort': 'date'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            article = {
                                'url': item.get('link', ''),
                                'title': item.get('title', ''),
                                'summary': item.get('snippet', ''),
                                'source': self._extract_source_from_url(item.get('link', '')),
                                'published_at': datetime.now(timezone.utc),  # Google doesn't always provide exact dates
                                'lang': 'en',
                                'status': 'fetched',
                                'media_type': 'article'
                            }
                            
                            if self._validate_article(article):
                                articles.append(article)
                    else:
                        logger.error(f"Google API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error calling Google API: {str(e)}")
        
        return articles
    
    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        if not url:
            return 'unknown'
        
        try:
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'unknown'
    
    def _validate_article(self, article: Dict[str, Any]) -> bool:
        """Validate article data"""
        required_fields = ['url', 'title']
        return all(article.get(field) for field in required_fields)

class WebScrapingCollector:
    """Web scraping collector using trafilatura"""
    
    def __init__(self):
        self.config = get_config().data_collection
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    async def collect_from_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Collect articles from specific URLs"""
        articles = []
        
        for url in urls:
            try:
                logger.info(f"Scraping URL: {url}")
                article = await self._scrape_url(url)
                
                if article and self._validate_article(article):
                    articles.append(article)
                
                # Rate limiting
                await asyncio.sleep(self.config.crawler_delay)
                
            except Exception as e:
                logger.error(f"Error scraping {url}: {str(e)}")
                continue
        
        logger.info(f"Scraped {len(articles)} articles from URLs")
        return articles
    
    async def _scrape_url(self, url: str) -> Optional[Dict[str, Any]]:
        """Scrape a single URL for article content"""
        try:
            response = self.session.get(url, timeout=self.config.crawler_timeout)
            response.raise_for_status()
            
            # Extract content using trafilatura
            content = trafilatura.extract(response.text)
            
            if not content:
                logger.warning(f"No content extracted from {url}")
                return None
            
            # Extract metadata
            metadata = trafilatura.extract_metadata(response.text)
            
            # Parse HTML for additional metadata
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract title
            title = None
            if metadata and metadata.title:
                title = metadata.title
            else:
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text().strip()
            
            # Extract published date
            published_at = None
            if metadata and metadata.date:
                published_at = metadata.date
            else:
                # Look for common date patterns
                date_patterns = [
                    r'<meta[^>]*property="article:published_time"[^>]*content="([^"]*)"',
                    r'<meta[^>]*name="date"[^>]*content="([^"]*)"',
                    r'<time[^>]*datetime="([^"]*)"'
                ]
                
                for pattern in date_patterns:
                    match = re.search(pattern, response.text, re.IGNORECASE)
                    if match:
                        try:
                            published_at = datetime.fromisoformat(match.group(1).replace('Z', '+00:00'))
                            break
                        except:
                            continue
            
            if not published_at:
                published_at = datetime.now(timezone.utc)
            
            article = {
                'url': url,
                'title': title or 'Untitled',
                'content': content,
                'summary': content[:500] + '...' if len(content) > 500 else content,
                'source': self._extract_source_from_url(url),
                'published_at': published_at,
                'lang': metadata.language if metadata else 'en',
                'status': 'fetched',
                'media_type': 'article'
            }
            
            return article
            
        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}")
            return None
    
    def _extract_source_from_url(self, url: str) -> str:
        """Extract source name from URL"""
        if not url:
            return 'unknown'
        
        try:
            domain = urlparse(url).netloc
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return 'unknown'
    
    def _validate_article(self, article: Dict[str, Any]) -> bool:
        """Validate article data"""
        required_fields = ['url', 'title', 'content']
        return all(article.get(field) for field in required_fields)

class YouTubeCollector:
    """YouTube video collector"""
    
    def __init__(self):
        self.config = get_config().data_collection
        self.api_key = self.config.youtube_api_key
        
        if not self.api_key:
            logger.warning("YouTube API key not configured")
    
    async def collect_from_channels(self, channels: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Collect videos from YouTube channels"""
        if not self.api_key:
            logger.warning("YouTube collection not configured, skipping")
            return []
        
        if channels is None:
            channels = self.config.youtube_channels or []
        
        if not channels:
            logger.warning("No YouTube channels configured")
            return []
        
        videos = []
        
        for channel_id in channels:
            try:
                logger.info(f"Collecting videos from YouTube channel: {channel_id}")
                channel_videos = await self._collect_from_channel(channel_id)
                videos.extend(channel_videos)
                
                # Rate limiting
                await asyncio.sleep(self.config.crawler_delay)
                
            except Exception as e:
                logger.error(f"Error collecting from YouTube channel {channel_id}: {str(e)}")
                continue
        
        logger.info(f"Collected {len(videos)} videos from YouTube")
        return videos
    
    async def _collect_from_channel(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Collect videos from a YouTube channel"""
        videos = []
        
        url = "https://www.googleapis.com/youtube/v3/search"
        params = {
            'key': self.api_key,
            'channelId': channel_id,
            'part': 'snippet',
            'order': 'date',
            'maxResults': max_results,
            'type': 'video',
            'publishedAfter': (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        for item in data.get('items', []):
                            snippet = item.get('snippet', {})
                            video_id = item.get('id', {}).get('videoId', '')
                            
                            if not video_id:
                                continue
                            
                            # Get additional video details
                            video_details = await self._get_video_details(video_id)
                            
                            video = {
                                'video_id': video_id,
                                'title': snippet.get('title', ''),
                                'description': snippet.get('description', ''),
                                'channel_id': channel_id,
                                'channel_name': snippet.get('channelTitle', ''),
                                'published_at': self._parse_youtube_date(snippet.get('publishedAt', '')),
                                'thumbnail_url': snippet.get('thumbnails', {}).get('high', {}).get('url', ''),
                                'video_url': f"https://www.youtube.com/watch?v={video_id}",
                                'media_type': 'video',
                                'status': 'fetched'
                            }
                            
                            # Add video details
                            if video_details:
                                video.update(video_details)
                            
                            videos.append(video)
                    else:
                        logger.error(f"YouTube API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error calling YouTube API: {str(e)}")
        
        return videos
    
    async def _get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get additional details for a video"""
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'key': self.api_key,
            'id': video_id,
            'part': 'contentDetails,statistics'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if data.get('items'):
                            item = data['items'][0]
                            content_details = item.get('contentDetails', {})
                            statistics = item.get('statistics', {})
                            
                            # Parse duration
                            duration = content_details.get('duration', '')
                            duration_seconds = self._parse_duration(duration)
                            
                            return {
                                'duration': duration_seconds,
                                'view_count': int(statistics.get('viewCount', 0)),
                                'like_count': int(statistics.get('likeCount', 0))
                            }
                            
        except Exception as e:
            logger.error(f"Error getting video details for {video_id}: {str(e)}")
        
        return None
    
    def _parse_duration(self, duration: str) -> Optional[int]:
        """Parse YouTube duration (PT4M13S) to seconds"""
        if not duration:
            return None
        
        try:
            # Remove PT prefix
            duration = duration[2:]
            
            total_seconds = 0
            
            # Parse hours
            if 'H' in duration:
                hours = int(duration.split('H')[0])
                total_seconds += hours * 3600
                duration = duration.split('H')[1]
            
            # Parse minutes
            if 'M' in duration:
                minutes = int(duration.split('M')[0])
                total_seconds += minutes * 60
                duration = duration.split('M')[1]
            
            # Parse seconds
            if 'S' in duration:
                seconds = int(duration.split('S')[0])
                total_seconds += seconds
            
            return total_seconds
            
        except Exception as e:
            logger.error(f"Error parsing duration {duration}: {str(e)}")
            return None
    
    def _parse_youtube_date(self, date_str: str) -> Optional[datetime]:
        """Parse YouTube date format"""
        if not date_str:
            return None
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except Exception as e:
            logger.error(f"Error parsing YouTube date {date_str}: {str(e)}")
            return datetime.now(timezone.utc)

class DataCollectionOrchestrator:
    """Orchestrates all data collection activities"""
    
    def __init__(self):
        self.rss_collector = RSSCollector()
        self.google_collector = GoogleSearchCollector()
        self.web_scraper = WebScrapingCollector()
        self.youtube_collector = YouTubeCollector()
        
        self.config = get_config()
    
    async def collect_all_data(self) -> Dict[str, Any]:
        """Collect data from all sources"""
        logger.info("Starting comprehensive data collection")
        
        results = {
            'rss_articles': [],
            'google_articles': [],
            'scraped_articles': [],
            'youtube_videos': [],
            'total_collected': 0,
            'errors': []
        }
        
        try:
            # Collect from RSS feeds
            try:
                rss_articles = await self.rss_collector.collect_from_feeds()
                results['rss_articles'] = rss_articles
            except Exception as e:
                logger.error(f"RSS collection error: {str(e)}")
                results['errors'].append(f"RSS: {str(e)}")
            
            # Collect from Google search
            try:
                google_articles = await self.google_collector.collect_from_queries()
                results['google_articles'] = google_articles
            except Exception as e:
                logger.error(f"Google collection error: {str(e)}")
                results['errors'].append(f"Google: {str(e)}")
            
            # Collect from YouTube
            try:
                youtube_videos = await self.youtube_collector.collect_from_channels()
                results['youtube_videos'] = youtube_videos
            except Exception as e:
                logger.error(f"YouTube collection error: {str(e)}")
                results['errors'].append(f"YouTube: {str(e)}")
            
            # Calculate totals
            results['total_collected'] = (
                len(results['rss_articles']) + 
                len(results['google_articles']) + 
                len(results['scraped_articles']) + 
                len(results['youtube_videos'])
            )
            
            logger.info(f"Data collection completed. Total items: {results['total_collected']}")
            
        except Exception as e:
            logger.error(f"Data collection orchestration error: {str(e)}")
            results['errors'].append(f"Orchestration: {str(e)}")
        
        return results
    
    async def save_collected_data(self, results: Dict[str, Any]) -> Dict[str, int]:
        """Save collected data to database"""
        session = get_session(self.config.database.url)
        saved_counts = {
            'articles': 0,
            'videos': 0,
            'errors': 0
        }
        
        try:
            # Save articles
            all_articles = (
                results.get('rss_articles', []) + 
                results.get('google_articles', []) + 
                results.get('scraped_articles', [])
            )
            
            for article_data in all_articles:
                try:
                    # Check if article already exists
                    existing = session.query(Article).filter(Article.url == article_data['url']).first()
                    if existing:
                        continue
                    
                    # Create new article
                    article = Article(
                        url=article_data['url'],
                        title=article_data['title'],
                        content=article_data.get('content'),
                        summary=article_data.get('summary'),
                        source=article_data.get('source'),
                        published_at=article_data.get('published_at'),
                        lang=article_data.get('lang', 'en'),
                        status=article_data.get('status', 'fetched'),
                        media_type=article_data.get('media_type', 'article')
                    )
                    
                    session.add(article)
                    saved_counts['articles'] += 1
                    
                except Exception as e:
                    logger.error(f"Error saving article {article_data.get('url', 'unknown')}: {str(e)}")
                    saved_counts['errors'] += 1
            
            # Save videos
            for video_data in results.get('youtube_videos', []):
                try:
                    # Check if video already exists
                    existing = session.query(VideoContent).filter(VideoContent.video_id == video_data['video_id']).first()
                    if existing:
                        continue
                    
                    # Create new video
                    video = VideoContent(
                        video_id=video_data['video_id'],
                        title=video_data['title'],
                        description=video_data.get('description'),
                        channel_id=video_data.get('channel_id'),
                        channel_name=video_data.get('channel_name'),
                        published_at=video_data.get('published_at'),
                        view_count=video_data.get('view_count'),
                        like_count=video_data.get('like_count'),
                        thumbnail_url=video_data.get('thumbnail_url'),
                        duration=video_data.get('duration'),
                        processed=False
                    )
                    
                    session.add(video)
                    saved_counts['videos'] += 1
                    
                except Exception as e:
                    logger.error(f"Error saving video {video_data.get('video_id', 'unknown')}: {str(e)}")
                    saved_counts['errors'] += 1
            
            session.commit()
            logger.info(f"Saved {saved_counts['articles']} articles and {saved_counts['videos']} videos")
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error saving collected data: {str(e)}")
            saved_counts['errors'] += 1
        finally:
            session.close()
        
        return saved_counts
