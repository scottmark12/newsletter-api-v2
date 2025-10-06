"""
Working Corporate Insights Scraper
Focuses on sites that are confirmed to work
"""

import asyncio
import aiohttp
from typing import List, Dict, Optional
from datetime import datetime, timezone, timedelta
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from dataclasses import dataclass
import re
import time

from .config import get_config
from .data_collectors import ArticleData


@dataclass
class WorkingCorporateSource:
    """Corporate source configuration for working sites"""
    name: str
    base_url: str
    insights_url: str
    article_selectors: Dict[str, str]
    content_selectors: List[str]
    delay: float = 2.0


class WorkingCorporateScraper:
    """Scrapes insights from confirmed working corporate sites"""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
        
        # Only include sites that we confirmed work
        self.working_sources = [
            WorkingCorporateSource(
                name="JLL",
                base_url="https://www.jll.com",
                insights_url="https://www.jll.com/insights",
                article_selectors={
                    "container": ".insight-card, .research-card, .article-item, .post, .article",
                    "title": "h3, h2, h1, .card-title, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, time, .post-date",
                    "summary": ".excerpt, .summary, .description, p"
                },
                content_selectors=[
                    ".article-content", ".post-content", ".insight-detail",
                    ".research-detail", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            WorkingCorporateSource(
                name="Marcus & Millichap",
                base_url="https://www.marcusmillichap.com",
                insights_url="https://www.marcusmillichap.com/research",
                article_selectors={
                    "container": ".research-item, .insight-card, .post, .article",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            WorkingCorporateSource(
                name="Goldman Sachs",
                base_url="https://www.goldmansachs.com",
                insights_url="https://www.goldmansachs.com/insights",
                article_selectors={
                    "container": ".insight-item, .research-card, .post, .article",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            WorkingCorporateSource(
                name="Morgan Stanley",
                base_url="https://www.morganstanley.com",
                insights_url="https://www.morganstanley.com/ideas",
                article_selectors={
                    "container": ".insight-card, .research-item, .post, .article",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            WorkingCorporateSource(
                name="Apollo",
                base_url="https://www.apollo.com",
                insights_url="https://www.apollo.com/insights",
                article_selectors={
                    "container": ".insight-card, .research-item, .post, .article",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            # Add some additional accessible sites
            WorkingCorporateSource(
                name="Brookings",
                base_url="https://www.brookings.edu",
                insights_url="https://www.brookings.edu/topics/housing/",
                article_selectors={
                    "container": ".post, .article, .research-item",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            ),
            
            WorkingCorporateSource(
                name="Urban Institute",
                base_url="https://www.urban.org",
                insights_url="https://www.urban.org/research",
                article_selectors={
                    "container": ".post, .article, .research-item",
                    "title": "h3, h2, h1, .title, .post-title",
                    "link": "a",
                    "date": ".date, .published, .post-date",
                    "summary": ".excerpt, .summary, .description"
                },
                content_selectors=[
                    ".article-content", ".post-content", "main", "article", ".content"
                ],
                delay=2.0
            )
        ]
    
    async def __aenter__(self):
        # Enhanced headers to bypass bot detection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',  # Removed brotli to avoid issues
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Create connector
        connector = aiohttp.TCPConnector(
            ssl=False,
            limit=10,
            limit_per_host=2
        )
        
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers=headers,
            connector=connector
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_working_source(self, source: WorkingCorporateSource) -> List[ArticleData]:
        """Scrape articles from a working corporate source"""
        articles = []
        
        try:
            print(f"Scraping {source.name}: {source.insights_url}")
            
            async with self.session.get(source.insights_url) as response:
                if response.status != 200:
                    print(f"❌ {source.name}: HTTP {response.status}")
                    return articles
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Find article containers
                containers = soup.select(source.article_selectors["container"])
                
                if not containers:
                    print(f"⚠️  {source.name}: No article containers found")
                    # Try alternative selectors
                    containers = soup.find_all(['article', 'div'], class_=re.compile(r'(post|article|insight|research)'))
                
                if not containers:
                    print(f"⚠️  {source.name}: No articles found with any selector")
                    return articles
                
                print(f"📄 {source.name}: Found {len(containers)} potential articles")
                
                for container in containers[:15]:  # Limit to 15 articles per source
                    try:
                        article_data = await self._extract_article_from_container(
                            container, source
                        )
                        if article_data:
                            articles.append(article_data)
                    except Exception as e:
                        print(f"   Error extracting article: {e}")
                        continue
                
                print(f"✅ {source.name}: Extracted {len(articles)} articles")
                
        except Exception as e:
            print(f"❌ {source.name}: Error scraping - {e}")
        
        # Rate limiting
        await asyncio.sleep(source.delay)
        return articles
    
    async def _extract_article_from_container(self, container, source: WorkingCorporateSource) -> Optional[ArticleData]:
        """Extract article data from a container element"""
        
        # Extract title
        title_elem = container.select_one(source.article_selectors["title"])
        if not title_elem:
            return None
        
        title = title_elem.get_text().strip()
        if len(title) < 10:  # Skip very short titles
            return None
        
        # Extract link
        link_elem = container.select_one(source.article_selectors["link"])
        if not link_elem:
            return None
        
        href = link_elem.get('href')
        if not href:
            return None
        
        # Make absolute URL
        url = urljoin(source.base_url, href)
        
        # Extract summary
        summary = ""
        summary_elem = container.select_one(source.article_selectors["summary"])
        if summary_elem:
            summary = summary_elem.get_text().strip()
        
        # Extract date
        published_at = None
        date_elem = container.select_one(source.article_selectors["date"])
        if date_elem:
            date_text = date_elem.get_text().strip()
            published_at = self._parse_date(date_text)
        
        # If no date found, assume recent
        if not published_at:
            published_at = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Create article data
        return ArticleData(
            title=title,
            url=url,
            source=source.name,
            summary=summary,
            published_at=published_at,
            content=None  # Will be scraped separately
        )
    
    async def scrape_article_content(self, article_data: ArticleData) -> ArticleData:
        """Scrape full content of an article"""
        try:
            async with self.session.get(article_data.url) as response:
                if response.status != 200:
                    return article_data
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Try different content selectors
                content = ""
                for selector in [
                    ".article-content", ".post-content", ".insight-content",
                    ".research-content", "main", "article", ".content"
                ]:
                    content_elem = soup.select_one(selector)
                    if content_elem:
                        content = content_elem.get_text().strip()
                        break
                
                if not content:
                    # Fallback: get all paragraph text
                    paragraphs = soup.find_all('p')
                    content = ' '.join([p.get_text().strip() for p in paragraphs])
                
                # Clean up content
                content = self._clean_content(content)
                
                # Update article with content
                article_data.content = content
                article_data.summary = content[:500] + "..." if len(content) > 500 else content
                
        except Exception as e:
            print(f"   Error scraping content for {article_data.title}: {e}")
        
        return article_data
    
    def _parse_date(self, date_text: str) -> Optional[datetime]:
        """Parse various date formats"""
        if not date_text:
            return None
        
        # Common date patterns
        date_patterns = [
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  # MM/DD/YYYY
            r'(\d{4})-(\d{1,2})-(\d{1,2})',  # YYYY-MM-DD
            r'(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{4})',  # DD Mon YYYY
            r'(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+(\d{1,2}),?\s+(\d{4})',  # Mon DD, YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, date_text, re.IGNORECASE)
            if match:
                try:
                    if '/' in date_text:
                        month, day, year = match.groups()
                        return datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
                    elif '-' in date_text:
                        year, month, day = match.groups()
                        return datetime(int(year), int(month), int(day), tzinfo=timezone.utc)
                    else:
                        # Handle text months
                        month_names = {
                            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
                            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
                        }
                        if len(match.groups()) == 3:
                            if match.group(1).lower() in month_names:
                                month, day, year = match.groups()
                                return datetime(int(year), month_names[month.lower()], int(day), tzinfo=timezone.utc)
                            else:
                                day, month, year = match.groups()
                                return datetime(int(year), month_names[month.lower()], int(day), tzinfo=timezone.utc)
                except:
                    continue
        
        return None
    
    def _clean_content(self, content: str) -> str:
        """Clean and normalize article content"""
        if not content:
            return ""
        
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common navigation/footer text
        unwanted_patterns = [
            r'Subscribe.*?newsletter',
            r'Follow us on.*?social media',
            r'©.*?All rights reserved',
            r'Privacy Policy.*?Terms of Service',
            r'Cookie Policy.*?GDPR',
        ]
        
        for pattern in unwanted_patterns:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        return content.strip()
    
    async def scrape_all_working_sources(self) -> List[ArticleData]:
        """Scrape articles from all working corporate sources"""
        all_articles = []
        
        print(f"🔍 Starting working corporate insights scraping...")
        print(f"📊 Scraping {len(self.working_sources)} confirmed working sources")
        print("=" * 60)
        
        for source in self.working_sources:
            try:
                articles = await self.scrape_working_source(source)
                
                # Scrape full content for each article
                for article in articles:
                    article = await self.scrape_article_content(article)
                    all_articles.append(article)
                
            except Exception as e:
                print(f"❌ Error scraping {source.name}: {e}")
                continue
        
        print("=" * 60)
        print(f"✅ Working corporate scraping complete: {len(all_articles)} articles collected")
        
        return all_articles


# Convenience function
async def scrape_working_corporate_insights() -> List[ArticleData]:
    """Scrape corporate insights from confirmed working sites"""
    async with WorkingCorporateScraper() as scraper:
        return await scraper.scrape_all_working_sources()
