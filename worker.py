"""
Background worker for scheduled tasks
Handles crawling, scoring, and newsletter generation
"""
import os
import sys
import time
import logging
from datetime import datetime, timedelta
import schedule
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, engine
from app.crawler import crawl_sources
from app.scoring import score_articles
from app.ceo_voice import generate_ceo_voice
from app.macro_data import fetch_macro_data
from app.publish import publish_newsletter
from app.config import TIMEZONE

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsletterWorker:
    """Background worker for newsletter tasks"""
    
    def __init__(self):
        self.logger = logger
        self.running = True
        
    def crawl_and_score(self):
        """Crawl sources and score new articles"""
        try:
            self.logger.info("Starting crawl and score job...")
            
            # Crawl sources
            with next(get_db()) as db:
                crawl_results = crawl_sources(db)
                self.logger.info(f"Crawled {crawl_results.get('articles_added', 0)} new articles")
            
            # Score new articles
            with next(get_db()) as db:
                score_results = score_articles(db)
                self.logger.info(f"Scored {score_results.get('articles_scored', 0)} articles")
                
        except Exception as e:
            self.logger.error(f"Error in crawl_and_score: {e}")
            
    def generate_daily_newsletter(self):
        """Generate and publish daily newsletter"""
        try:
            self.logger.info("Starting daily newsletter generation...")
            
            with next(get_db()) as db:
                # Check if newsletter already exists for today
                today = datetime.now().strftime('%Y-%m-%d')
                existing = db.execute(
                    text("SELECT id FROM issues WHERE issue_date = :date"),
                    {"date": today}
                ).fetchone()
                
                if existing:
                    self.logger.info(f"Newsletter for {today} already exists")
                    return
                
                # Generate CEO voice content
                ceo_content = generate_ceo_voice(db)
                
                # Fetch macro data
                macro_content = fetch_macro_data(db)
                
                # Publish newsletter
                result = publish_newsletter(
                    db,
                    ceo_voice=ceo_content,
                    macro_data=macro_content
                )
                
                self.logger.info(f"Newsletter generated: {result}")
                
        except Exception as e:
            self.logger.error(f"Error generating newsletter: {e}")
            
    def cleanup_old_articles(self):
        """Clean up old articles to save space"""
        try:
            self.logger.info("Cleaning up old articles...")
            
            with engine.connect() as conn:
                # Delete articles older than 30 days that weren't selected
                cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                result = conn.execute(
                    text("""
                        DELETE FROM articles 
                        WHERE published_at < :cutoff 
                        AND status = 'discarded'
                    """),
                    {"cutoff": cutoff_date}
                )
                conn.commit()
                
                self.logger.info(f"Deleted {result.rowcount} old articles")
                
        except Exception as e:
            self.logger.error(f"Error cleaning up articles: {e}")
            
    def health_check(self):
        """Perform health check and log status"""
        try:
            with engine.connect() as conn:
                # Check database connection
                result = conn.execute(text("SELECT 1")).fetchone()
                
                # Get statistics
                stats = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_articles,
                        COUNT(CASE WHEN status = 'new' THEN 1 END) as new_articles,
                        COUNT(CASE WHEN status = 'scored' THEN 1 END) as scored_articles
                    FROM articles
                    WHERE fetched_at > datetime('now', '-24 hours')
                """)).fetchone()
                
                self.logger.info(
                    f"Health check OK - Articles (24h): "
                    f"Total: {stats[0]}, New: {stats[1]}, Scored: {stats[2]}"
                )
                
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            
    def run(self):
        """Main worker loop"""
        self.logger.info("Starting Newsletter Worker...")
        
        # Schedule jobs
        # Crawl every 2 hours
        schedule.every(2).hours.do(self.crawl_and_score)
        
        # Generate newsletter at 6 AM EST daily
        schedule.every().day.at("06:00").do(self.generate_daily_newsletter)
        
        # Cleanup at 2 AM daily
        schedule.every().day.at("02:00").do(self.cleanup_old_articles)
        
        # Health check every 30 minutes
        schedule.every(30).minutes.do(self.health_check)
        
        # Run initial crawl and health check
        self.crawl_and_score()
        self.health_check()
        
        # Main loop
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
            except KeyboardInterrupt:
                self.logger.info("Worker stopped by user")
                self.running = False
            except Exception as e:
                self.logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(60)  # Wait before retrying
                
        self.logger.info("Worker stopped")

if __name__ == "__main__":
    worker = NewsletterWorker()
    worker.run()