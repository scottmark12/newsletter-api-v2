#!/usr/bin/env python3
"""
Enhanced Crawler - Combines RSS feeds with web scraping for high-quality sources
"""

import json
import os
from typing import List, Dict, Any
from .crawler import ingest_run as rss_ingest_run
from .insight_scraper import InsightScraper
from .db import SessionLocal
from sqlalchemy import text
import uuid
from datetime import datetime, timezone

def load_professional_seeds():
    """Load professional RSS feeds and scraper sources"""
    try:
        with open('app/professional_seeds.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("⚠️  Professional seeds file not found, using default seeds")
        return None

def save_scraped_articles(articles: List[Dict[str, Any]]):
    """Save scraped articles to database"""
    if not articles:
        return 0
    
    saved_count = 0
    db = SessionLocal()
    
    try:
        for article in articles:
            try:
                # Check if article already exists
                existing = db.execute(
                    text("SELECT id FROM articles WHERE url = :url"),
                    {"url": article['url']}
                ).fetchone()
                
                if existing:
                    continue
                
                # Insert new article
                article_id = str(uuid.uuid4())
                
                db.execute(text("""
                    INSERT INTO articles (
                        id, title, url, summary_raw, content, published_at, 
                        fetched_at, lang, source, status
                    ) VALUES (
                        :id, :title, :url, :summary, :content, :published_at,
                        :fetched_at, :lang, :source, 'new'
                    )
                """), {
                    "id": article_id,
                    "title": article['title'],
                    "url": article['url'],
                    "summary": article['summary'],
                    "content": article['summary'],  # Use summary as content for now
                    "published_at": article['published_at'],
                    "fetched_at": article['fetched_at'],
                    "lang": "en",
                    "source": article['source']
                })
                
                saved_count += 1
                print(f"   ✅ Saved: {article['title'][:50]}...")
                
            except Exception as e:
                print(f"   ⚠️  Error saving article: {e}")
                continue
        
        db.commit()
        print(f"🎉 Saved {saved_count} new articles from scraping")
        
    except Exception as e:
        print(f"❌ Error saving articles: {e}")
        db.rollback()
    finally:
        db.close()
    
    return saved_count

def enhanced_ingest_run(limit: int = 100):
    """Enhanced ingestion combining RSS feeds and web scraping"""
    print("🚀 Starting Enhanced Ingest Run...")
    print(f"📊 Target: {limit} articles")
    
    total_ingested = 0
    
    # Load professional sources
    seeds = load_professional_seeds()
    
    # Phase 1: Scrape high-quality insight sources
    print("\n📡 Phase 1: Scraping High-Quality Insight Sources")
    scraper = InsightScraper()
    
    try:
        scraped_articles = scraper.scrape_all_insights(limit=limit // 2)
        scraped_count = save_scraped_articles(scraped_articles)
        total_ingested += scraped_count
        print(f"✅ Scraped {scraped_count} articles from insight sources")
    except Exception as e:
        print(f"❌ Error in scraping phase: {e}")
    
    # Phase 2: Use professional RSS feeds
    print("\n📡 Phase 2: Professional RSS Feeds")
    
    if seeds and 'professional_sources' in seeds:
        # Update the seeds.json with professional sources
        professional_feeds = []
        for category, data in seeds['professional_sources'].items():
            for feed in data['feeds']:
                professional_feeds.append({
                    "url": feed['url'],
                    "name": feed['name'],
                    "category": category,
                    "quality_score": feed.get('quality_score', 80)
                })
        
        # Save professional feeds to seeds.json temporarily
        try:
            with open('app/seeds.json', 'r') as f:
                original_seeds = json.load(f)
            
            # Add professional feeds to existing seeds
            for feed in professional_feeds:
                original_seeds['feeds'].append(feed)
            
            with open('app/seeds.json', 'w') as f:
                json.dump(original_seeds, f, indent=2)
            
            print(f"✅ Added {len(professional_feeds)} professional RSS feeds")
            
        except Exception as e:
            print(f"⚠️  Error updating seeds: {e}")
    
    # Run RSS crawler
    try:
        print("🔄 Running RSS crawler...")
        rss_result = rss_ingest_run(limit=limit // 2)
        if isinstance(rss_result, dict) and 'ingested' in rss_result:
            rss_count = rss_result['ingested']
        else:
            rss_count = 0
        
        total_ingested += rss_count
        print(f"✅ RSS crawler ingested {rss_count} articles")
        
    except Exception as e:
        print(f"❌ Error in RSS phase: {e}")
    
    # Phase 3: Google Search for high-opportunity content
    print("\n📡 Phase 3: Google Search for High-Opportunity Content")
    
    if seeds and 'google_search_queries' in seeds:
        try:
            from .crawler import crawl_google_searches
            
            # Create a temporary database session for Google searches
            db = SessionLocal()
            
            # Mock the parameters needed for Google search
            inserted_counter = [0]
            attempts_counter = [0]
            domain_counts = {}
            cap = 1000
            now_utc = datetime.now(timezone.utc)
            
            google_count = crawl_google_searches(
                limit=limit // 4,  # Use 1/4 of limit for Google searches
                db=db,
                inserted_counter=inserted_counter,
                attempts_counter=attempts_counter,
                domain_counts=domain_counts,
                cap=cap,
                now_utc=now_utc
            )
            
            total_ingested += google_count
            print(f"✅ Google searches found {google_count} articles")
            
            db.close()
            
        except Exception as e:
            print(f"❌ Error in Google search phase: {e}")
    
    print(f"\n🎉 Enhanced Ingest Complete!")
    print(f"📊 Total articles ingested: {total_ingested}")
    
    return {
        "ok": True,
        "total_ingested": total_ingested,
        "phases": {
            "scraping": scraped_count if 'scraped_count' in locals() else 0,
            "rss": rss_count if 'rss_count' in locals() else 0,
            "google": google_count if 'google_count' in locals() else 0
        }
    }

def main():
    """Test the enhanced crawler"""
    result = enhanced_ingest_run(limit=50)
    print(f"\nResult: {result}")

if __name__ == "__main__":
    main()
