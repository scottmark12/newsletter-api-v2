# app/synthesis_worker_v3.py
# V3 Intelligence Synthesis Worker

import time
import schedule
from datetime import datetime, timezone
import logging
from typing import Dict, Any

from .intelligence_v3 import (
    generate_daily_brief_v3,
    generate_opportunity_scan_v3,
    generate_methodology_synthesis_v3,
    generate_policy_impact_analysis_v3
)
from .config_v3 import get_v3_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def daily_brief_job():
    """Generate daily intelligence brief"""
    try:
        logger.info("📰 Generating daily intelligence brief")
        
        result = generate_daily_brief_v3(days_back=1)
        
        if result["status"] == "success":
            logger.info("✅ Daily brief generated successfully")
            logger.info(f"📊 Analyzed {result['article_metrics']['total_articles']} articles")
            logger.info(f"🎯 {result['article_metrics']['high_actionability']} high-actionability articles")
        else:
            logger.error(f"❌ Daily brief generation failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error generating daily brief: {str(e)}")

def opportunity_scan_job():
    """Generate opportunity scan"""
    try:
        logger.info("🔍 Generating opportunity scan")
        
        result = generate_opportunity_scan_v3(days_back=7)
        
        if result["status"] == "success":
            logger.info("✅ Opportunity scan generated successfully")
            logger.info(f"📊 Analyzed {result['articles_analyzed']} articles")
            logger.info(f"💡 {len(result['opportunities'])} opportunities identified")
        else:
            logger.error(f"❌ Opportunity scan failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error generating opportunity scan: {str(e)}")

def methodology_synthesis_job():
    """Generate methodology synthesis"""
    try:
        logger.info("🔧 Generating methodology synthesis")
        
        result = generate_methodology_synthesis_v3(days_back=7)
        
        if result["status"] == "success":
            logger.info("✅ Methodology synthesis generated successfully")
            logger.info(f"📊 Analyzed {result['articles_analyzed']} articles")
            logger.info(f"📋 {len(result['methodologies'])} methodologies identified")
        else:
            logger.error(f"❌ Methodology synthesis failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error generating methodology synthesis: {str(e)}")

def policy_analysis_job():
    """Generate policy impact analysis"""
    try:
        logger.info("📋 Generating policy impact analysis")
        
        result = generate_policy_impact_analysis_v3(days_back=7)
        
        if result["status"] == "success":
            logger.info("✅ Policy analysis generated successfully")
            logger.info(f"📊 Analyzed {result['articles_analyzed']} articles")
            logger.info(f"📜 {len(result['policy_changes'])} policy changes identified")
        else:
            logger.error(f"❌ Policy analysis failed: {result.get('message', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Error generating policy analysis: {str(e)}")

def weekly_synthesis_job():
    """Generate comprehensive weekly synthesis"""
    try:
        logger.info("📊 Generating weekly synthesis")
        
        # Generate all synthesis types
        daily_brief_job()
        time.sleep(30)
        
        opportunity_scan_job()
        time.sleep(30)
        
        methodology_synthesis_job()
        time.sleep(30)
        
        policy_analysis_job()
        
        logger.info("✅ Weekly synthesis completed")
        
    except Exception as e:
        logger.error(f"❌ Error in weekly synthesis: {str(e)}")

def synthesis_health_check():
    """Health check for synthesis system"""
    try:
        logger.info("🏥 Running synthesis health check")
        
        # Check if we have recent articles to synthesize
        from .db import SessionLocal
        from sqlalchemy import text
        
        db = SessionLocal()
        try:
            # Check recent high-quality articles
            recent_articles = db.execute(text("""
                SELECT COUNT(*) FROM articles_v3 a
                JOIN article_scores_v3 s ON s.article_id = a.id
                WHERE a.published_at >= NOW() - INTERVAL '24 hours'
                  AND s.composite_score >= 50
            """)).scalar()
            
            logger.info(f"📊 Recent high-quality articles (24h): {recent_articles}")
            
            # Check recent synthesis
            recent_synthesis = db.execute(text("""
                SELECT COUNT(*) FROM intelligence_synthesis
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)).scalar()
            
            logger.info(f"🧠 Recent synthesis (24h): {recent_synthesis}")
            
            # Health status
            if recent_articles > 10:
                logger.info("✅ Synthesis system healthy - sufficient content")
            elif recent_articles > 5:
                logger.info("⚠️  Synthesis system warning - limited content")
            else:
                logger.warning("❌ Synthesis system unhealthy - insufficient content")
                
        except Exception as e:
            logger.error(f"❌ Synthesis health check failed: {str(e)}")
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Error in synthesis health check: {str(e)}")

def setup_synthesis_scheduler():
    """Setup the synthesis scheduler"""
    logger.info("⏰ Setting up v3 synthesis scheduler")
    
    # Daily brief every day at 6 AM UTC
    schedule.every().day.at("06:00").do(daily_brief_job)
    
    # Opportunity scan every 3 days
    schedule.every(3).days.at("08:00").do(opportunity_scan_job)
    
    # Methodology synthesis every 4 days
    schedule.every(4).days.at("10:00").do(methodology_synthesis_job)
    
    # Policy analysis every 5 days
    schedule.every(5).days.at("12:00").do(policy_analysis_job)
    
    # Weekly comprehensive synthesis every Sunday at 2 PM
    schedule.every().sunday.at("14:00").do(weekly_synthesis_job)
    
    # Health check every 6 hours
    schedule.every(6).hours.do(synthesis_health_check)
    
    logger.info("✅ Synthesis scheduler setup complete")
    logger.info("📅 Scheduled synthesis jobs:")
    logger.info("  - Daily brief: Every day at 6:00 AM UTC")
    logger.info("  - Opportunity scan: Every 3 days at 8:00 AM UTC")
    logger.info("  - Methodology synthesis: Every 4 days at 10:00 AM UTC")
    logger.info("  - Policy analysis: Every 5 days at 12:00 PM UTC")
    logger.info("  - Weekly synthesis: Every Sunday at 2:00 PM UTC")
    logger.info("  - Health check: Every 6 hours")

def run_synthesis_worker():
    """Main synthesis worker loop"""
    logger.info("🧠 Starting Newsletter API v3 Synthesis Worker")
    
    # Setup scheduler
    setup_synthesis_scheduler()
    
    # Run initial synthesis
    logger.info("🔄 Running initial synthesis...")
    
    try:
        # Generate daily brief
        daily_brief_job()
        time.sleep(30)
        
        # Health check
        synthesis_health_check()
        
    except Exception as e:
        logger.error(f"❌ Error running initial synthesis: {str(e)}")
    
    logger.info("🔄 Starting synthesis scheduler loop...")
    
    # Main scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("🛑 Synthesis worker stopped by user")
            break
        except Exception as e:
            logger.error(f"❌ Error in synthesis scheduler loop: {str(e)}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    run_synthesis_worker()
