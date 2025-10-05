#!/usr/bin/env python3
"""
Blocked Sources Scraper - Scrape content from sources that blocked RSS access
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import time
import re

class BlockedSourcesScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
    
    def scrape_cbre_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CBRE insights page directly"""
        print("🔍 Scraping CBRE insights...")
        articles = []
        
        try:
            # Try multiple CBRE insight pages
            urls = [
                "https://www.cbre.com/insights",
                "https://www.cbre.com/insights/research",
                "https://www.cbre.com/insights/market-reports",
                "https://www.cbre.com/insights/thought-leadership"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "CBRE Research", 95))
                        time.sleep(2)  # Be respectful
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} CBRE articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CBRE: {e}")
        
        return articles[:limit]
    
    def scrape_jll_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape JLL insights page directly"""
        print("🔍 Scraping JLL insights...")
        articles = []
        
        try:
            urls = [
                "https://www.jll.com/en/insights",
                "https://www.jll.com/en/insights/research",
                "https://www.jll.com/en/insights/market-reports"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "JLL Research", 95))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} JLL articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping JLL: {e}")
        
        return articles[:limit]
    
    def scrape_cushman_wakefield(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Cushman & Wakefield insights"""
        print("🔍 Scraping Cushman & Wakefield...")
        articles = []
        
        try:
            urls = [
                "https://www.cushmanwakefield.com/en/insights",
                "https://www.cushmanwakefield.com/en/insights/research",
                "https://www.cushmanwakefield.com/en/insights/market-reports"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "Cushman & Wakefield", 92))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} C&W articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping C&W: {e}")
        
        return articles[:limit]
    
    def scrape_blackstone_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Blackstone insights"""
        print("🔍 Scraping Blackstone insights...")
        articles = []
        
        try:
            urls = [
                "https://www.blackstone.com/insights/",
                "https://www.blackstone.com/insights/real-estate/",
                "https://www.blackstone.com/insights/private-equity/"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "Blackstone Insights", 95))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} Blackstone articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping Blackstone: {e}")
        
        return articles[:limit]
    
    def scrape_bisnow_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Bisnow news page"""
        print("🔍 Scraping Bisnow...")
        articles = []
        
        try:
            urls = [
                "https://www.bisnow.com/",
                "https://www.bisnow.com/news",
                "https://www.bisnow.com/national/news"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "Bisnow", 88))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} Bisnow articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping Bisnow: {e}")
        
        return articles[:limit]
    
    def scrape_enr_articles(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape ENR articles page"""
        print("🔍 Scraping ENR articles...")
        articles = []
        
        try:
            urls = [
                "https://www.enr.com/articles",
                "https://www.enr.com/articles/latest",
                "https://www.enr.com/articles/construction"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "Engineering News-Record", 95))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} ENR articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping ENR: {e}")
        
        return articles[:limit]
    
    def scrape_bdc_network(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape BDC Network articles"""
        print("🔍 Scraping BDC Network...")
        articles = []
        
        try:
            urls = [
                "https://www.bdcnetwork.com/",
                "https://www.bdcnetwork.com/articles",
                "https://www.bdcnetwork.com/news"
            ]
            
            for url in urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        articles.extend(self._extract_articles_from_page(soup, url, "Building Design+Construction", 88))
                        time.sleep(2)
                except Exception as e:
                    print(f"   ⚠️  Error with {url}: {e}")
                    continue
                
                if len(articles) >= limit:
                    break
            
            print(f"   ✅ Found {len(articles)} BDC articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping BDC: {e}")
        
        return articles[:limit]
    
    def _extract_articles_from_page(self, soup: BeautifulSoup, base_url: str, source_name: str, quality_score: int) -> List[Dict[str, Any]]:
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
            '.listing-item',
            '.feed-item',
            '.content-block',
            
            # Specific to insight/research pages
            '.insight-item',
            '.research-item',
            '.publication-item',
            '.report-item',
            '.analysis-item',
            '.market-insight',
            '.industry-insight',
            
            # List items that might contain articles
            'li',
            '.list-item'
        ]
        
        found_articles = []
        for selector in article_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text_content = elem.get_text(strip=True)
                if len(text_content) < 50:  # Skip very short content
                    continue
                
                links = elem.find_all('a')
                if links:
                    found_articles.append(elem)
        
        # Remove duplicates and limit results
        seen_urls = set()
        for article_elem in found_articles[:50]:
            try:
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
                    'summary': summary[:500] if summary else "",
                    'source': source_name,
                    'published_at': date_text or datetime.now(timezone.utc).isoformat(),
                    'fetched_at': datetime.now(timezone.utc).isoformat(),
                    'content_type': 'insight',
                    'quality_score': quality_score
                })
                
            except Exception as e:
                continue
        
        return articles
    
    def scrape_all_blocked_sources(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape all blocked sources"""
        print("🚀 Starting blocked sources scraping...")
        
        all_articles = []
        
        # Define scraping functions for blocked sources
        scrapers = [
            (self.scrape_cbre_insights, limit // 6),
            (self.scrape_jll_insights, limit // 6),
            (self.scrape_cushman_wakefield, limit // 6),
            (self.scrape_blackstone_insights, limit // 6),
            (self.scrape_bisnow_news, limit // 6),
            (self.scrape_enr_articles, limit // 6)
        ]
        
        for scraper_func, scraper_limit in scrapers:
            try:
                articles = scraper_func(scraper_limit)
                all_articles.extend(articles)
                time.sleep(3)  # Be respectful to servers
            except Exception as e:
                print(f"❌ Error with scraper: {e}")
                continue
        
        print(f"🎉 Total blocked sources scraped: {len(all_articles)}")
        return all_articles

def main():
    """Test the blocked sources scraper"""
    scraper = BlockedSourcesScraper()
    articles = scraper.scrape_all_blocked_sources(limit=30)
    
    print(f"\n📊 Scraping Results:")
    print(f"Total articles: {len(articles)}")
    
    for i, article in enumerate(articles[:10]):
        print(f"\n{i+1}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Quality Score: {article['quality_score']}")
        print(f"   URL: {article['url']}")

if __name__ == "__main__":
    main()
