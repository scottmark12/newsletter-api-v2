"""
Newsletter API v4 Database Initialization
Initialize database with sample data and configuration
"""

import logging
from datetime import datetime, timezone

from .config import get_config
from .models import init_database, get_session, ContentSource

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_sample_data():
    """Initialize database with sample content sources"""
    config = get_config()
    session = get_session(config.database.url)
    
    try:
        # Check if sources already exist
        existing_sources = session.query(ContentSource).count()
        if existing_sources > 0:
            logger.info("Content sources already exist, skipping initialization")
            return
        
        # Sample RSS feeds
        rss_sources = [
            {
                "domain": "constructiondive.com",
                "name": "Construction Dive",
                "type": "rss",
                "tier": "tier_2",
                "reliability_score": 0.8,
                "insight_quality_score": 0.7,
                "actionability_score": 0.6,
                "primary_themes": ["practices", "systems_codes"],
                "content_types": ["article", "news"]
            },
            {
                "domain": "bisnow.com",
                "name": "Bisnow",
                "type": "rss",
                "tier": "tier_2",
                "reliability_score": 0.8,
                "insight_quality_score": 0.7,
                "actionability_score": 0.7,
                "primary_themes": ["opportunities", "practices"],
                "content_types": ["article", "news"]
            },
            {
                "domain": "commercialobserver.com",
                "name": "Commercial Observer",
                "type": "rss",
                "tier": "tier_2",
                "reliability_score": 0.8,
                "insight_quality_score": 0.7,
                "actionability_score": 0.7,
                "primary_themes": ["opportunities", "practices"],
                "content_types": ["article", "news"]
            },
            {
                "domain": "globest.com",
                "name": "GlobeSt",
                "type": "rss",
                "tier": "tier_3",
                "reliability_score": 0.7,
                "insight_quality_score": 0.6,
                "actionability_score": 0.6,
                "primary_themes": ["opportunities", "vision"],
                "content_types": ["article", "news"]
            }
        ]
        
        # Create content sources
        for source_data in rss_sources:
            source = ContentSource(**source_data)
            session.add(source)
        
        session.commit()
        logger.info(f"✅ Initialized {len(rss_sources)} content sources")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error initializing sample data: {str(e)}")
        raise
    finally:
        session.close()

def main():
    """Main initialization function"""
    try:
        logger.info("🚀 Initializing Newsletter API v4 Database")
        
        # Get configuration
        config = get_config()
        
        # Initialize database
        init_database(config.database.url)
        
        # Initialize sample data
        init_sample_data()
        
        logger.info("✅ Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()
