#!/usr/bin/env python3
"""
Advanced Insight Scraper - Comprehensive web scraping for high-quality insight sources
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from datetime import datetime, timezone
from typing import List, Dict, Any
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

class AdvancedInsightScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.selenium_driver = None
    
    def setup_selenium(self):
        """Setup Selenium WebDriver for JavaScript-heavy sites"""
        if self.selenium_driver is None:
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--window-size=1920,1080')
            
            try:
                self.selenium_driver = webdriver.Chrome(options=chrome_options)
            except Exception as e:
                print(f"   ⚠️  Selenium setup failed: {e}")
                return False
        return True
    
    def close_selenium(self):
        """Close Selenium WebDriver"""
        if self.selenium_driver:
            self.selenium_driver.quit()
            self.selenium_driver = None
    
    def scrape_with_selenium(self, url: str, wait_time: int = 10) -> BeautifulSoup:
        """Scrape JavaScript-heavy pages with Selenium"""
        if not self.setup_selenium():
            return None
        
        try:
            self.selenium_driver.get(url)
            WebDriverWait(self.selenium_driver, wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Wait for content to load
            time.sleep(3)
            
            html = self.selenium_driver.page_source
            return BeautifulSoup(html, 'html.parser')
            
        except Exception as e:
            print(f"   ⚠️  Selenium scraping failed: {e}")
            return None
    
    def extract_articles_generic(self, soup: BeautifulSoup, base_url: str, source_name: str, quality_score: int) -> List[Dict[str, Any]]:
        """Generic article extraction for insight pages"""
        articles = []
        
        # Common selectors for article containers
        article_selectors = [
            '.insight-item',
            '.article-item',
            '.post-item',
            '.research-item',
            '.blog-post',
            '.news-item',
            '.content-item',
            '.publication-item',
            '.report-item',
            'article',
            '.card',
            '.entry',
            '[data-testid*="insight"]',
            '[data-testid*="article"]',
            '[class*="insight"]',
            '[class*="article"]',
            '[class*="post"]',
            '[class*="research"]'
        ]
        
        found_articles = []
        for selector in article_selectors:
            found_articles.extend(soup.select(selector))
            if len(found_articles) > 5:  # Stop if we find enough articles
                break
        
        for article_elem in found_articles:
            try:
                # Extract title
                title_elem = article_elem.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'])
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if len(title) < 10:  # Skip very short titles
                    continue
                
                # Extract link
                link_elem = article_elem.find('a')
                if not link_elem or not link_elem.get('href'):
                    continue
                
                link = urljoin(base_url, link_elem['href'])
                
                # Extract summary/description
                summary_elem = article_elem.find(['p', '.summary', '.description', '.excerpt', '.abstract'])
                summary = summary_elem.get_text(strip=True) if summary_elem else ""
                
                # Extract date
                date_text = ""
                for elem in article_elem.find_all(text=True):
                    if re.search(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}|\d{1,2}/\d{1,2}/\d{4}', elem):
                        date_text = elem.strip()
                        break
                
                articles.append({
                    'title': title,
                    'url': link,
                    'summary': summary,
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
    
    def scrape_cbre_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CBRE Research & Insights"""
        print("🔍 Scraping CBRE Insights...")
        articles = []
        
        try:
            url = "https://www.cbre.com/insights"
            soup = self.scrape_with_selenium(url)
            if not soup:
                return articles
            
            articles = self.extract_articles_generic(soup, url, "CBRE Research", 95)
            print(f"   ✅ Found {len(articles)} CBRE articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CBRE: {e}")
        
        return articles[:limit]
    
    def scrape_jll_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape JLL Research & Insights"""
        print("🔍 Scraping JLL Insights...")
        articles = []
        
        try:
            url = "https://www.jll.com/en/insights"
            soup = self.scrape_with_selenium(url)
            if not soup:
                return articles
            
            articles = self.extract_articles_generic(soup, url, "JLL Research", 95)
            print(f"   ✅ Found {len(articles)} JLL articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping JLL: {e}")
        
        return articles[:limit]
    
    def scrape_blackstone_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Blackstone Insights"""
        print("🔍 Scraping Blackstone Insights...")
        articles = []
        
        try:
            url = "https://www.blackstone.com/insights/"
            soup = self.scrape_with_selenium(url)
            if not soup:
                return articles
            
            articles = self.extract_articles_generic(soup, url, "Blackstone Insights", 95)
            print(f"   ✅ Found {len(articles)} Blackstone articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping Blackstone: {e}")
        
        return articles[:limit]
    
    def scrape_cre_analyst_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CRE Analyst insights"""
        print("🔍 Scraping CRE Analyst...")
        articles = []
        
        try:
            url = "https://www.creanalyst.com/insights/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.extract_articles_generic(soup, url, "CRE Analyst", 90)
            print(f"   ✅ Found {len(articles)} CRE Analyst articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CRE Analyst: {e}")
        
        return articles[:limit]
    
    def scrape_cre_insight_journal(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape CRE Insight Journal"""
        print("🔍 Scraping CRE Insight Journal...")
        articles = []
        
        try:
            url = "https://creinsightjournal.com/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.extract_articles_generic(soup, url, "CRE Insight Journal", 88)
            print(f"   ✅ Found {len(articles)} CRE Insight Journal articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping CRE Insight Journal: {e}")
        
        return articles[:limit]
    
    def scrape_nar_cre_insights(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape NAR Commercial Real Estate Insights"""
        print("🔍 Scraping NAR CRE Insights...")
        articles = []
        
        try:
            url = "https://www.nar.realtor/commercial-real-estate-market-insights"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.extract_articles_generic(soup, url, "NAR Commercial Real Estate", 92)
            print(f"   ✅ Found {len(articles)} NAR articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping NAR CRE insights: {e}")
        
        return articles[:limit]
    
    def scrape_commercial_observer(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Scrape Commercial Observer"""
        print("🔍 Scraping Commercial Observer...")
        articles = []
        
        try:
            url = "https://commercialobserver.com/"
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = self.extract_articles_generic(soup, url, "Commercial Observer", 92)
            print(f"   ✅ Found {len(articles)} Commercial Observer articles")
            
        except Exception as e:
            print(f"   ❌ Error scraping Commercial Observer: {e}")
        
        return articles[:limit]
    
    def scrape_all_insights(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Scrape all insight sources"""
        print("🚀 Starting comprehensive insight scraping...")
        
        all_articles = []
        
        # Define scraping functions
        scrapers = [
            (self.scrape_cbre_insights, limit // 7),
            (self.scrape_jll_insights, limit // 7),
            (self.scrape_blackstone_insights, limit // 7),
            (self.scrape_cre_analyst_insights, limit // 7),
            (self.scrape_cre_insight_journal, limit // 7),
            (self.scrape_nar_cre_insights, limit // 7),
            (self.scrape_commercial_observer, limit // 7)
        ]
        
        for scraper_func, scraper_limit in scrapers:
            try:
                articles = scraper_func(scraper_limit)
                all_articles.extend(articles)
                time.sleep(3)  # Be respectful to servers
            except Exception as e:
                print(f"❌ Error with scraper: {e}")
                continue
        
        # Close Selenium driver
        self.close_selenium()
        
        print(f"🎉 Total insights scraped: {len(all_articles)}")
        return all_articles

def main():
    """Test the advanced insight scraper"""
    scraper = AdvancedInsightScraper()
    articles = scraper.scrape_all_insights(limit=50)
    
    print(f"\n📊 Scraping Results:")
    print(f"Total articles: {len(articles)}")
    
    for i, article in enumerate(articles[:10]):
        print(f"\n{i+1}. {article['title'][:60]}...")
        print(f"   Source: {article['source']}")
        print(f"   Quality Score: {article['quality_score']}")
        print(f"   URL: {article['url']}")

if __name__ == "__main__":
    main()
