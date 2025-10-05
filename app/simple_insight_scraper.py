#!/usr/bin/env python3
"""
Simple Insight Scraper - Web scraping for insight pages without Selenium
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import time
import re

class SimpleInsightScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def extract_articles_from_page(self, soup: BeautifulSoup, base_url: str, source_name: str, quality_score: int) -> List[Dict[str, Any]]:
        """Extract articles from a parsed HTML page"""
        articles = []
        
        # Comprehensive selectors for different page layouts
        article_selectors = [
            # Common article containers
            'article',
            '.article',
            '.post',
            '.insight',
            '.research',
            '.publication',
            '.report',
            '.blog-post',
            '.news-item',
            '.content-item',
            '.card',
            '.entry',
            
            # Specific to insight/research pages
            '.insight-item',
            '.research-item',
            '.publication-item',
            '.report-item',
            '.analysis-item',
            '.market-insight',
            '.industry-insight',
            
            # Generic content containers
            '.item',
            '.listing-item',
            '.feed-item',
            '.content-block',
            
            # List items that might contain articles
            'li',
            '.list-item'
        ]
        
        found_articles = []
        for selector in article_selectors:
            elements = soup.select(selector)
            for elem in elements:
                # Skip if element is too small or doesn't contain text
                text_content = elem.get_text(strip=True)
                if len(text_content) < 50:  # Skip very short content
                    continue
                
                # Look for links within the element
                links = elem.find_all('a')
                if links:
                    found_articles.append(elem)
        
        # Remove duplicates and limit results
        seen_urls = set()
        for article_elem in found_articles[:50]:  # Limit to avoid too many results
            try:
                # Find the main link in this article element
                link_elem = article_elem.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                link = urljoin(base_url, link_elem['href'])
                if link in seen_urls:
                    continue
                seen_urls.add(link)
                
                # Extract title
                title = ""
                title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                if title_elem:
                    title = title_elem.get_text(strip=True)
                elif link_elem:
                    title = link_elem.get_text(strip=True)
                
                if len(title) < 10:  # Skip very short titles
                    continue
                
                # Extract summary
                summary = ""
                summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt', '.abstract'])
                if summary_elem:
                    summary = summary_elem.get_text(strip=True)
                
                # Extract date
                date_text = ""
                for elem in article_elem.find_all(text=True):
                    if re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}/\d{1,2}/\d{4}', elem):
                        date_text = elem.strip()
                        break
                
                articles.append({
                    'title': title,
                    'url': link,
                    'summary': summary[:500] if summary else "",  # Limit summary length
                    'source': source_name,
                    'published_at': date_text or datetime.now(timezone.utc).isoformat(),
                    'fetched_at': datetime.now(timezone.utc).isoformat(),
                    'content_type': 'insight',
                    'quality_score': quality_score
                })
                
            except Exception as e:
                print(f"   ⚠️  Error processing article: {e}")
                continue
        
        return articles
    
    def scrape_insight_page(self, url: str, source_name: str, quality_score: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape a single insight page"""
        print(f"🔍 Scraping {source_name}...")
        articles = []
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.extract_articles_from_page(soup, url, source_name, quality_score)
            
            print(f"   ✅ Found {len(articles)} articles from {source_name}")
            
        except Exception as e:
            print(f"   ❌ Error scraping {source_name}: {e}")
        
        return articles[:limit]
    
    def scrape_multiple_sources(self, sources: List[Dict[str, Any]], limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape multiple insight sources"""
        print("🚀 Starting insight scraping from multiple sources...")
        
        all_articles = []
        sources_per_site = limit // len(sources) if sources else 20
        
        for source in sources:
            try:
                articles = self.scrape_insight_page(
                    source['url'], 
                    source['name'], 
                    source['quality_score'], 
                    sources_per_site
                )
                all_articles.extend(articles)
                time.sleep(2)  # Be respectful to servers
                
            except Exception as e:
                print(f"❌ Error with source {source['name']}: {e}")
                continue
        
        print(f"🎉 Total insights scraped: {len(all_articles)}")
        return all_articles

def load_insight_sources():
    """Load insight sources from comprehensive_insights.json"""
    try:
        with open('app/comprehensive_insights.json', 'r') as f:
            data = json.load(f)
        
        sources = []
        for category, category_data in data.items():
            if 'sources' in category_data:
                sources.extend(category_data['sources'])
        
        return sources
    except FileNotFoundError:
        print("⚠️  Comprehensive insights file not found")
        return []

def main():
    """Test the simple insight scraper"""
    scraper = SimpleInsightScraper()
    
    # Load sources from JSON file
    sources = load_insight_sources()
    
    # Test with a few high-quality sources
    test_sources = [
        {
            'url': 'https://commercialobserver.com/',
            'name': 'Commercial Observer',
            'quality_score': 92
        },
        {
            'url': 'https://creinsightjournal.com/',
            'name': 'CRE Insight Journal', 
            'quality_score': 88
        }
    ]
    
    articles = scraper.scrape_multiple_sources(test_sources, limit=20)
    
    print(f"\n📊 Scraping Results:")
    print(f"Total articles: {len(articles)}")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Quality Score: {article['quality_score']}")
        print(f"   URL: {article['url']}")

if __name__ == "__main__":
    main()
