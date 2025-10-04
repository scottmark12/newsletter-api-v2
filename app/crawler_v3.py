# app/crawler_v3.py
# Enhanced v3 Crawler - Prioritizes High-Quality Sources

from typing import List, Dict, Any, Optional
import requests
import feedparser
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import uuid

from .db import SessionLocal
from .schema_v3 import ArticleV3, ContentSource

# -------- V3 SOURCE PRIORITIZATION --------
V3_SOURCE_CONFIG = {
    "tier_1_research": {
        "sources": [
            "https://www.jll.com/en/trends-and-insights",
            "https://www.cbre.com/insights",
            "https://www.cushmanwakefield.com/en/insights",
            "https://www.colliers.com/en/insights",
            "https://www.marcusmillichap.com/research"
        ],
        "priority": 10,
        "source_type": "research",
        "institutional_level": "top_tier",
        "expected_themes": ["opportunities", "practices", "systems_codes"]
    },
    "tier_1_news": {
        "sources": [
            "https://www.bisnow.com/rss",
            "https://commercialobserver.com/feed/",
            "https://www.rejournals.com/feed/",
            "https://www.globest.com/rss/"
        ],
        "priority": 9,
        "source_type": "news",
        "institutional_level": "high",
        "expected_themes": ["opportunities", "market_news"]
    },
    "tier_2_industry": {
        "sources": [
            "https://www.constructiondive.com/feeds/",
            "https://www.smartcitiesdive.com/feeds/",
            "https://www.engineeringnewsrecord.com/rss",
            "https://www.architecturalrecord.com/rss"
        ],
        "priority": 7,
        "source_type": "industry_news",
        "institutional_level": "medium",
        "expected_themes": ["practices", "vision", "systems_codes"]
    },
    "tier_3_specialized": {
        "sources": [
            "https://www.bdcnetwork.com/rss",
            "https://www.buildinggreen.com/rss",
            "https://www.greenbuildingadvisor.com/rss",
            "https://www.metropolismag.com/rss"
        ],
        "priority": 5,
        "source_type": "specialized",
        "institutional_level": "medium",
        "expected_themes": ["practices", "vision"]
    }
}

# -------- ENHANCED URL FILTERING --------
V3_SKIP_HOSTS = {
    "facebook.com", "twitter.com", "linkedin.com", "instagram.com", "youtube.com",
    "amazon.com", "ebay.com", "shopify.com", "etsy.com", "pinterest.com",
    "reddit.com", "quora.com", "medium.com", "substack.com"
}

V3_SKIP_SUBSTRINGS = {
    "/search", "/category/", "/tag/", "/author/", "/page/", "/wp-admin/",
    "/feed/", "/rss", "/atom", "/sitemap", "/robots.txt", "/privacy",
    "/terms", "/contact", "/about", "/careers", "/jobs", "/hiring"
}

V3_STOP_TAILS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip",
    ".jpg", ".jpeg", ".png", ".gif", ".mp4", ".avi", ".mov", ".mp3"
}

def _likely_article_v3(url: str) -> bool:
    """Enhanced article detection for v3"""
    try:
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path.lower()
        
        # Skip known non-article hosts
        if any(skip_host in host for skip_host in V3_SKIP_HOSTS):
            return False
        
        # Skip obvious non-articles
        if any(skip_sub in url.lower() for skip_sub in V3_SKIP_SUBSTRINGS):
            return False
        
        # Skip file downloads
        if any(path.endswith(tail) for tail in V3_STOP_TAILS):
            return False
        
        # Skip generic pages
        generic_patterns = [
            "/home", "/about", "/contact", "/privacy", "/terms", "/search",
            "/category/", "/categories/", "/tag/", "/tags/", "/archive/",
            "/author/", "/authors/", "/staff/", "/team/", "/leadership/",
            "/careers", "/jobs", "/hiring", "/newsletter", "/subscribe",
            "/login", "/register", "/account", "/profile", "/settings",
            "/shop", "/store", "/products", "/services", "/pricing",
            "/blog/", "/blogs/", "/articles/"
        ]
        
        if any(pattern in path for pattern in generic_patterns):
            return False
        
        # Special handling for /news/ - allow specific articles
        if "/news/" in path:
            path_segments = [s for s in path.strip("/").split("/") if s]
            if len(path_segments) <= 2:  # /news/ or /news/category/ - skip
                return False
        
        # Must have meaningful path structure
        segments = [s for s in path.strip("/").split("/") if s]
        if not segments:
            return False
        
        if len(segments) < 2:
            return False
        
        # Skip category/listing pages
        if any(seg in ["category", "categories", "tag", "tags", "archive", "author", "authors"] for seg in segments):
            return False
        
        # Must have indication it's a specific article
        last_segment = segments[-1]
        if any(char.isdigit() for char in last_segment):  # Contains date/year
            return True
        if len(last_segment) > 20:  # Long slug-like name
            return True
        if "-" in last_segment or "_" in last_segment:  # Slug format
            return True
        
        # Check for article-like patterns
        article_patterns = [
            r"\d{4}/\d{2}/\d{2}",  # Date pattern
            r"\d{4}-\d{2}-\d{2}",  # Date pattern
            r"article-\d+",        # Article ID
            r"news-\d+",           # News ID
            r"post-\d+",           # Post ID
        ]
        
        for pattern in article_patterns:
            if re.search(pattern, url):
                return True
        
        return True
        
    except Exception:
        return False

def _extract_article_content_v3(url: str, source_domain: str) -> Dict[str, Any]:
    """Enhanced content extraction for v3"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Extract title
        title = ""
        title_selectors = [
            'h1.article-title', 'h1.post-title', 'h1.entry-title',
            'h1.headline', 'h1.title', 'h1', '.article-title', '.post-title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem:
                title = title_elem.get_text().strip()
                break
        
        # Extract content
        content = ""
        content_selectors = [
            '.article-content', '.post-content', '.entry-content',
            '.article-body', '.post-body', '.content', 'article',
            '.story-body', '.article-text', '.post-text'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                content = content_elem.get_text().strip()
                break
        
        # If no specific content found, try to get main content
        if not content:
            main_selectors = ['main', '.main-content', '#main', '.container']
            for selector in main_selectors:
                main_elem = soup.select_one(selector)
                if main_elem:
                    content = main_elem.get_text().strip()
                    break
        
        # Extract summary/description
        summary = ""
        summary_selectors = [
            'meta[name="description"]', 'meta[property="og:description"]',
            '.article-summary', '.post-summary', '.excerpt'
        ]
        
        for selector in summary_selectors:
            if selector.startswith('meta'):
                meta_elem = soup.select_one(selector)
                if meta_elem:
                    summary = meta_elem.get('content', '').strip()
                    break
            else:
                summary_elem = soup.select_one(selector)
                if summary_elem:
                    summary = summary_elem.get_text().strip()
                    break
        
        # Determine media type
        media_type = "article"
        if any(ext in url.lower() for ext in ['.pdf']):
            media_type = "pdf"
        elif 'youtube.com' in url or 'youtu.be' in url:
            media_type = "video"
        elif any(keyword in url.lower() for keyword in ['podcast', 'audio']):
            media_type = "podcast"
        
        return {
            "title": title,
            "content": content,
            "summary": summary,
            "media_type": media_type,
            "success": True
        }
        
    except Exception as e:
        return {
            "title": "",
            "content": "",
            "summary": "",
            "media_type": "article",
            "success": False,
            "error": str(e)
        }

def _update_source_metrics_v3(source_domain: str, article_count: int, high_scoring: bool):
    """Update source performance metrics"""
    try:
        db = SessionLocal()
        
        # Update or create source record
        db.execute(text("""
            INSERT INTO content_sources (domain, articles_scraped, high_scoring_articles, last_scraped)
            VALUES (:domain, :articles_scraped, :high_scoring_articles, :last_scraped)
            ON CONFLICT (domain) 
            DO UPDATE SET 
                articles_scraped = content_sources.articles_scraped + :articles_scraped,
                high_scoring_articles = content_sources.high_scoring_articles + :high_scoring_articles,
                last_scraped = :last_scraped
        """), {
            "domain": source_domain,
            "articles_scraped": article_count,
            "high_scoring_articles": 1 if high_scoring else 0,
            "last_scraped": datetime.now(timezone.utc).isoformat()
        })
        
        db.commit()
        db.close()
        
    except Exception as e:
        print(f"Error updating source metrics for {source_domain}: {str(e)}")

def crawl_rss_feed_v3(feed_url: str, source_config: Dict[str, Any], limit: int = 50) -> List[Dict[str, Any]]:
    """Crawl RSS feed with v3 enhancements"""
    articles = []
    
    try:
        print(f"🔍 Crawling RSS feed: {feed_url}")
        
        feed = feedparser.parse(feed_url)
        
        if feed.bozo:
            print(f"⚠️  Feed parsing warning for {feed_url}")
        
        for entry in feed.entries[:limit]:
            try:
                # Get article URL
                article_url = entry.get('link', '')
                if not article_url or not _likely_article_v3(article_url):
                    continue
                
                # Extract basic info
                title = entry.get('title', '').strip()
                summary = entry.get('summary', '').strip()
                published = entry.get('published_parsed')
                
                # Parse published date
                published_at = None
                if published:
                    try:
                        published_at = datetime(*published[:6], tzinfo=timezone.utc)
                    except:
                        published_at = datetime.now(timezone.utc)
                
                # Extract content
                content_result = _extract_article_content_v3(article_url, source_config['source_type'])
                
                if not content_result['success']:
                    continue
                
                # Use extracted content or fall back to summary
                content = content_result['content'] or summary
                
                if len(content) < 200:  # Skip short articles
                    continue
                
                # Determine source domain
                parsed_url = urlparse(article_url)
                source_domain = parsed_url.netloc
                
                article = {
                    "id": str(uuid.uuid4()),
                    "url": article_url,
                    "title": title,
                    "content": content,
                    "summary_raw": summary,
                    "source": source_domain,
                    "published_at": published_at.isoformat() if published_at else datetime.now(timezone.utc).isoformat(),
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "lang": "en",
                    "status": "fetched",
                    "media_type": content_result['media_type'],
                    "project_stage": "unknown",
                    "needs_fact_check": False
                }
                
                articles.append(article)
                
                # Small delay to be respectful
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error processing entry: {str(e)}")
                continue
        
        print(f"✅ Crawled {len(articles)} articles from {feed_url}")
        return articles
        
    except Exception as e:
        print(f"❌ Error crawling RSS feed {feed_url}: {str(e)}")
        return []

def save_articles_v3(articles: List[Dict[str, Any]]) -> int:
    """Save articles to v3 database"""
    if not articles:
        return 0
    
    try:
        db = SessionLocal()
        
        saved_count = 0
        for article in articles:
            try:
                # Check if article already exists
                existing = db.execute(text("""
                    SELECT id FROM articles_v3 WHERE url = :url
                """), {"url": article['url']}).fetchone()
                
                if existing:
                    continue
                
                # Insert article
                db.execute(text("""
                    INSERT INTO articles_v3 (
                        id, url, title, content, summary_raw, source, published_at,
                        fetched_at, lang, status, media_type, project_stage, needs_fact_check
                    ) VALUES (
                        :id, :url, :title, :content, :summary_raw, :source, :published_at,
                        :fetched_at, :lang, :status, :media_type, :project_stage, :needs_fact_check
                    )
                """), article)
                
                saved_count += 1
                
            except Exception as e:
                print(f"Error saving article {article.get('url', 'unknown')}: {str(e)}")
                continue
        
        db.commit()
        db.close()
        
        print(f"✅ Saved {saved_count} new articles to v3 database")
        return saved_count
        
    except Exception as e:
        print(f"❌ Error saving articles: {str(e)}")
        return 0

def run_crawler_v3(limit_per_source: int = 20) -> Dict[str, Any]:
    """Run the v3 crawler across all configured sources"""
    print("🚀 Starting Newsletter API v3 Crawler")
    print(f"📊 Limit per source: {limit_per_source}")
    
    total_articles = 0
    source_results = {}
    
    for tier_name, config in V3_SOURCE_CONFIG.items():
        print(f"\n📂 Processing {tier_name} sources...")
        
        tier_articles = 0
        for source_url in config['sources']:
            try:
                articles = crawl_rss_feed_v3(source_url, config, limit_per_source)
                saved_count = save_articles_v3(articles)
                
                tier_articles += saved_count
                total_articles += saved_count
                
                source_results[source_url] = {
                    "crawled": len(articles),
                    "saved": saved_count,
                    "priority": config['priority']
                }
                
                # Update source metrics
                parsed_url = urlparse(source_url)
                source_domain = parsed_url.netloc
                _update_source_metrics_v3(source_domain, saved_count, False)
                
            except Exception as e:
                print(f"❌ Error processing source {source_url}: {str(e)}")
                source_results[source_url] = {
                    "error": str(e),
                    "priority": config['priority']
                }
        
        print(f"✅ {tier_name}: {tier_articles} articles saved")
    
    print(f"\n🎉 Crawler completed: {total_articles} total articles saved")
    
    return {
        "status": "success",
        "total_articles_saved": total_articles,
        "source_results": source_results,
        "crawl_timestamp": datetime.now(timezone.utc).isoformat()
    }

def crawl_specific_sources_v3(source_urls: List[str], limit_per_source: int = 20) -> Dict[str, Any]:
    """Crawl specific sources only"""
    print(f"🎯 Crawling specific sources: {source_urls}")
    
    total_articles = 0
    source_results = {}
    
    for source_url in source_urls:
        try:
            # Find config for this source
            config = None
            for tier_name, tier_config in V3_SOURCE_CONFIG.items():
                if source_url in tier_config['sources']:
                    config = tier_config
                    break
            
            if not config:
                config = {
                    "source_type": "custom",
                    "institutional_level": "medium",
                    "priority": 5
                }
            
            articles = crawl_rss_feed_v3(source_url, config, limit_per_source)
            saved_count = save_articles_v3(articles)
            
            total_articles += saved_count
            source_results[source_url] = {
                "crawled": len(articles),
                "saved": saved_count,
                "config": config
            }
            
        except Exception as e:
            print(f"❌ Error processing source {source_url}: {str(e)}")
            source_results[source_url] = {"error": str(e)}
    
    return {
        "status": "success",
        "total_articles_saved": total_articles,
        "source_results": source_results,
        "crawl_timestamp": datetime.now(timezone.utc).isoformat()
    }
