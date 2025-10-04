# app/worker_v3.py
# V3 Background Worker for Crawling and Scoring

import time
import schedule
from datetime import datetime, timezone
import logging
from typing import Dict, Any

from .crawler_v3 import run_crawler_v3, crawl_specific_sources_v3
from .scoring_v3 import run_scoring_v3
from .config_v3 import get_v3_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def crawl_job():
    """Scheduled crawling job"""
    try:
        logger.info("🕷️  Starting scheduled crawl job")
        
        config = get_v3_config()
        result = run_crawler_v3(limit_per_source=config.max_articles_per_source)
        
        if result["status"] == "success":
            logger.info(f"✅ Crawl job completed: {result['total_articles_saved']} articles saved")
        else:
            logger.error(f"❌ Crawl job failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in crawl job: {str(e)}")

def scoring_job():
    """Scheduled scoring job"""
    try:
        logger.info("📊 Starting scheduled scoring job")
        
        config = get_v3_config()
        result = run_scoring_v3(limit=config.max_articles_per_scoring_run)
        
        if result["status"] == "success":
            logger.info(f"✅ Scoring job completed: {result['scored_articles']} articles scored")
        else:
            logger.error(f"❌ Scoring job failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in scoring job: {str(e)}")

def crawl_high_priority_sources():
    """Crawl high-priority sources more frequently"""
    try:
        logger.info("🎯 Crawling high-priority sources")
        
        high_priority_sources = [
            "https://www.jll.com/en/trends-and-insights",
            "https://www.cbre.com/insights",
            "https://www.cushmanwakefield.com/en/insights",
            "https://www.bisnow.com/rss",
            "https://commercialobserver.com/feed/"
        ]
        
        result = crawl_specific_sources_v3(high_priority_sources, limit_per_source=30)
        
        if result["status"] == "success":
            logger.info(f"✅ High-priority crawl completed: {result['total_articles_saved']} articles saved")
        else:
            logger.error(f"❌ High-priority crawl failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error in high-priority crawl: {str(e)}")

def health_check_job():
    """Health check job"""
    try:
        logger.info("🏥 Running health check")
        
        # Basic health checks
        from .db import SessionLocal
        
        db = SessionLocal()
        try:
            # Check database connection
            result = db.execute("SELECT 1").scalar()
            logger.info("✅ Database connection healthy")
            
            # Check recent activity
            from sqlalchemy import text
            recent_articles = db.execute(text("""
                SELECT COUNT(*) FROM articles_v3 
                WHERE fetched_at >= NOW() - INTERVAL '24 hours'
            """)).scalar()
            
            logger.info(f"📊 Recent articles (24h): {recent_articles}")
            
        except Exception as e:
            logger.error(f"❌ Database health check failed: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in health check: {str(e)}")

def setup_scheduler():
    """Setup the job scheduler"""
    logger.info("⏰ Setting up v3 worker scheduler")
    
    # High-priority sources crawl every 2 hours
    schedule.every(2).hours.do(crawl_high_priority_sources)
    
    # Full crawl every 6 hours
    schedule.every(6).hours.do(crawl_job)
    
    # Scoring every 4 hours
    schedule.every(4).hours.do(scoring_job)
    
    # Health check every hour
    schedule.every().hour.do(health_check_job)
    
    logger.info("✅ Scheduler setup complete")
    logger.info("📅 Scheduled jobs:")
    logger.info("  - High-priority crawl: Every 2 hours")
    logger.info("  - Full crawl: Every 6 hours")
    logger.info("  - Scoring: Every 4 hours")
    logger.info("  - Health check: Every hour")

def run_worker():
    """Main worker loop"""
    logger.info("🚀 Starting Newsletter API v3 Worker")
    
    # Setup scheduler
    setup_scheduler()
    
    # Run initial jobs
    logger.info("🔄 Running initial jobs...")
    
    try:
        # Initial crawl
        crawl_job()
        time.sleep(10)
        
        # Initial scoring
        scoring_job()
        time.sleep(10)
        
        # Initial health check
        health_check_job()
        
    except Exception as e:
        logger.error(f"❌ Error running initial jobs: {str(e)}")
    
    logger.info("🔄 Starting scheduler loop...")
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Worker stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in scheduler loop: {str(e)}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    run_worker()
