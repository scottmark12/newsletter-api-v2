#!/usr/bin/env python3
"""
Insight Scraper - Convert high-quality non-RSS sources into feed data
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import time
import re

class InsightScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def scrape_jpmorgan_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape J.P. Morgan Asset Management Insights"""
        print("🔍 Scraping J.P. Morgan Insights...")
        articles = []
        
        try:
            # Main insights page
            url = "https://am.jpmorgan.com/us/en/asset-management/adv/insights/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article containers
            article_selectors = [
                '.insight-item',
                '.article-item', 
                '.post-item',
                '[data-testid*="insight"]',
                '.card',
                'article'
            ]
            
            found_articles = []
            for selector in article_selectors:
                found_articles.extend(soup.select(selector))
                if found_articles:
                    break
            
            for article_elem in found_articles[:limit]:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if not title_elem:
                        title_elem = article_elem.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                    
                    # Extract link
                    link_elem = article_elem.find('a')
                    if link_elem and link_elem.get('href'):
                        link = urljoin(url, link_elem['href'])
                    else:
                        continue
                    
                    # Extract summary/description
                    summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt'])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extract date (look for various date patterns)
                    date_text = ""
                    for elem in article_elem.find_all(text=True):
                        if re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}/\d{1,2}/\d{4}', elem):
                            date_text = elem.strip()
                            break
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'source': 'J.P. Morgan Asset Management',
                        'published_at': date_text,
                        'fetched_at': datetime.now(timezone.utc).isoformat(),
                        'content_type': 'insight',
                        'quality_score': 95  # High quality source
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing JPM article: {e}")
                    continue
            
            print(f"   ✅ Found {len(articles)} JPM articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping JPM insights: {e}")
        
        return articles
    
    def scrape_cre_analyst(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CRE Analyst insights"""
        print("🔍 Scraping CRE Analyst...")
        articles = []
        
        try:
            # Main insights page
            url = "https://www.creanalyst.com/insights/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article containers
            article_selectors = [
                '.post',
                '.article',
                '.insight-item',
                '.blog-post',
                'article',
                '.entry'
            ]
            
            found_articles = []
            for selector in article_selectors:
                found_articles.extend(soup.select(selector))
                if found_articles:
                    break
            
            for article_elem in found_articles[:limit]:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if not title_elem:
                        title_elem = article_elem.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                    
                    # Extract link
                    link_elem = article_elem.find('a')
                    if link_elem and link_elem.get('href'):
                        link = urljoin(url, link_elem['href'])
                    else:
                        continue
                    
                    # Extract summary
                    summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt'])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'source': 'CRE Analyst',
                        'published_at': datetime.now(timezone.utc).isoformat(),
                        'fetched_at': datetime.now(timezone.utc).isoformat(),
                        'content_type': 'insight',
                        'quality_score': 90
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing CRE Analyst article: {e}")
                    continue
            
            print(f"   ✅ Found {len(articles)} CRE Analyst articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CRE Analyst: {e}")
        
        return articles
    
    def scrape_cre_insight_journal(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CRE Insight Journal"""
        print("🔍 Scraping CRE Insight Journal...")
        articles = []
        
        try:
            url = "https://creinsightjournal.com/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article containers
            article_selectors = [
                '.post',
                '.article',
                '.journal-entry',
                'article',
                '.content-item'
            ]
            
            found_articles = []
            for selector in article_selectors:
                found_articles.extend(soup.select(selector))
                if found_articles:
                    break
            
            for article_elem in found_articles[:limit]:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if not title_elem:
                        title_elem = article_elem.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                    
                    # Extract link
                    link_elem = article_elem.find('a')
                    if link_elem and link_elem.get('href'):
                        link = urljoin(url, link_elem['href'])
                    else:
                        continue
                    
                    # Extract summary
                    summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt'])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'source': 'CRE Insight Journal',
                        'published_at': datetime.now(timezone.utc).isoformat(),
                        'fetched_at': datetime.now(timezone.utc).isoformat(),
                        'content_type': 'insight',
                        'quality_score': 88
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing CRE Insight Journal article: {e}")
                    continue
            
            print(f"   ✅ Found {len(articles)} CRE Insight Journal articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CRE Insight Journal: {e}")
        
        return articles
    
    def scrape_nar_cre_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape NAR Commercial Real Estate Insights"""
        print("🔍 Scraping NAR CRE Insights...")
        articles = []
        
        try:
            url = "https://www.nar.realtor/commercial-real-estate-market-insights"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for article containers
            article_selectors = [
                '.article',
                '.post',
                '.insight-item',
                '.market-insight',
                'article',
                '.content-item'
            ]
            
            found_articles = []
            for selector in article_selectors:
                found_articles.extend(soup.select(selector))
                if found_articles:
                    break
            
            for article_elem in found_articles[:limit]:
                try:
                    # Extract title
                    title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
                    if not title_elem:
                        title_elem = article_elem.find('a')
                    title = title_elem.get_text(strip=True) if title_elem else "Untitled"
                    
                    # Extract link
                    link_elem = article_elem.find('a')
                    if link_elem and link_elem.get('href'):
                        link = urljoin(url, link_elem['href'])
                    else:
                        continue
                    
                    # Extract summary
                    summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt'])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    articles.append({
                        'title': title,
                        'url': link,
                        'summary': summary,
                        'source': 'NAR Commercial Real Estate',
                        'published_at': datetime.now(timezone.utc).isoformat(),
                        'fetched_at': datetime.now(timezone.utc).isoformat(),
                        'content_type': 'market_insight',
                        'quality_score': 92
                    })
                    
                except Exception as e:
                    print(f"   ⚠️  Error processing NAR article: {e}")
                    continue
            
            print(f"   ✅ Found {len(articles)} NAR articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping NAR CRE insights: {e}")
        
        return articles
    
    def scrape_all_insights(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Scrape all insight sources"""
        print("🚀 Starting insight scraping from high-quality sources...")
        
        all_articles = []
        
        # Add delays between requests to be respectful
        sources = [
            self.scrape_jpmorgan_insights,
            self.scrape_cre_analyst,
            self.scrape_cre_insight_journal,
            self.scrape_nar_cre_insights
        ]
        
        for source_func in sources:
            try:
                articles = source_func(limit // len(sources))
                all_articles.extend(articles)
                time.sleep(2)  # Be respectful to servers
            except Exception as e:
                print(f"❌ Error with source: {e}")
                continue
        
        print(f"🎉 Total insights scraped: {len(all_articles)}")
        return all_articles

def main():
    """Test the insight scraper"""
    scraper = InsightScraper()
    articles = scraper.scrape_all_insights(limit=20)
    
    print(f"\n📊 Scraping Results:")
    print(f"Total articles: {len(articles)}")
    
    for i, article in enumerate(articles[:5]):
        print(f"\n{i+1}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Quality Score: {article['quality_score']}")
        print(f"   URL: {article['url']}")

if __name__ == "__main__":
    main()
