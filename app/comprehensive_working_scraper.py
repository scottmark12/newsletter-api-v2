#!/usr/bin/env python3
"""
Comprehensive Working Sources Scraper - All 30 verified working sources
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import time
import re

class ComprehensiveWorkingScraper:
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
            '.insight-item',
            '.research-item',
            '.publication-item',
            '.report-item',
            '.analysis-item',
            '.market-insight',
            '.industry-insight',
            'li',
            '.list-item'
        ]
        
        found_articles = []
        for selector in article_selectors:
            elements = soup.select(selector)
            for elem in elements:
                text_content = elem.get_text(strip=True)
                if len(text_content) < 50:
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
                
                if len(title) < 10:
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
    
    def scrape_source(self, url: str, source_name: str, quality_score: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape a single source"""
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
    
    def scrape_all_working_sources(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape all 30 verified working sources"""
        print("🚀 Starting comprehensive scraping of all working sources...")
        
        # All 30 verified working sources
        working_sources = [
            # HIGH QUALITY (95+)
            {"url": "https://www.jll.com/en/insights", "name": "JLL Research & Insights", "quality": 95},
            {"url": "https://www.blackstone.com/insights/", "name": "Blackstone Insights", "quality": 95},
            {"url": "https://am.jpmorgan.com/us/en/asset-management/adv/insights/", "name": "J.P. Morgan Asset Management", "quality": 95},
            {"url": "https://www.goldmansachs.com/insights/", "name": "Goldman Sachs Insights", "quality": 95},
            {"url": "https://www.brookings.edu/", "name": "Brookings Institution", "quality": 95},
            {"url": "https://www.federalreserve.gov/", "name": "Federal Reserve", "quality": 95},
            
            # GOOD QUALITY (90-94)
            {"url": "https://www.cushmanwakefield.com/en/insights", "name": "Cushman & Wakefield Insights", "quality": 92},
            {"url": "https://www.morganstanley.com/insights", "name": "Morgan Stanley Insights", "quality": 92},
            {"url": "https://www.constructiondive.com/", "name": "Construction Dive", "quality": 90},
            {"url": "https://commercialobserver.com/", "name": "Commercial Observer", "quality": 92},
            {"url": "https://therealdeal.com/", "name": "The Real Deal", "quality": 90},
            {"url": "https://www.creanalyst.com/insights/", "name": "CRE Analyst", "quality": 90},
            {"url": "https://www.nar.realtor/commercial-real-estate-market-insights", "name": "NAR Commercial Real Estate", "quality": 92},
            {"url": "https://www.reit.com/news-resources", "name": "NAREIT News & Resources", "quality": 90},
            {"url": "https://www.huduser.gov/portal/home.html", "name": "HUD User", "quality": 90},
            {"url": "https://www.census.gov/", "name": "U.S. Census Bureau", "quality": 90},
            
            # MEDIUM QUALITY (<90)
            {"url": "https://www.savills.com/insight-and-opinion/", "name": "Savills Insight & Opinion", "quality": 88},
            {"url": "https://www.knightfrank.com/research", "name": "Knight Frank Research", "quality": 88},
            {"url": "https://www.americancentury.com/insights", "name": "American Century Insights", "quality": 88},
            {"url": "https://www.bdcnetwork.com/", "name": "Building Design+Construction", "quality": 88},
            {"url": "https://www.constructionexec.com/", "name": "Construction Executive", "quality": 85},
            {"url": "https://www.asce.org/news/", "name": "ASCE News", "quality": 88},
            {"url": "https://www.bisnow.com/", "name": "Bisnow", "quality": 88},
            {"url": "https://www.globest.com/", "name": "GlobeSt", "quality": 85},
            {"url": "https://urbanland.uli.org/", "name": "Urban Land Institute", "quality": 88},
            {"url": "https://creinsightjournal.com/", "name": "CRE Insight Journal", "quality": 88},
            {"url": "https://www.realestateinvesting.com/", "name": "Real Estate Investing", "quality": 85},
            {"url": "https://www.constructiontech.com/", "name": "Construction Technology", "quality": 88},
            {"url": "https://www.procore.com/blog/", "name": "Procore Blog", "quality": 80},
            {"url": "https://www.fhfa.gov/", "name": "Federal Housing Finance Agency", "quality": 88}
        ]
        
        all_articles = []
        sources_per_site = max(1, limit // len(working_sources))
        
        for source in working_sources:
            try:
                articles = self.scrape_source(
                    source['url'], 
                    source['name'], 
                    source['quality'], 
                    sources_per_site
                )
                all_articles.extend(articles)
                time.sleep(2)  # Be respectful to servers
                
            except Exception as e:
                print(f"❌ Error with source {source['name']}: {e}")
                continue
        
        print(f"🎉 Total articles scraped from all working sources: {len(all_articles)}")
        return all_articles

def main():
    """Test the comprehensive working scraper"""
    scraper = ComprehensiveWorkingScraper()
    articles = scraper.scrape_all_working_sources(limit=60)
    
    print(f"\n📊 Scraping Results:")
    print(f"Total articles: {len(articles)}")
    
    # Group by source
    by_source = {}
    for article in articles:
        source = article['source']
        if source not in by_source:
            by_source[source] = []
        by_source[source].append(article)
    
    print(f"\n📈 Articles by source:")
    for source, source_articles in sorted(by_source.items(), key=lambda x: len(x[1]), reverse=True):
        print(f"   {source}: {len(source_articles)} articles")
    
    print(f"\n🏆 Top articles by quality:")
    high_quality_articles = [a for a in articles if a['quality_score'] >= 95]
    for i, article in enumerate(high_quality_articles[:5]):
        print(f"{i+1}. {article['title'][:60]}...")
        print(f"   Source: {article['source']} (Quality: {article['quality_score']})")

if __name__ == "__main__":
    main()
