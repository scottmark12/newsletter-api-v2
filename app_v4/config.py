"""
Newsletter API v4 Configuration
Clean, environment-based configuration with easy customization
"""

import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str
    pool_size: int = 10
    max_overflow: int = 20
    echo: bool = False

@dataclass
class ScoringConfig:
    """Flexible scoring system configuration"""
    # Base thresholds
    min_composite_score: float = 50.0
    min_actionability_score: float = 60.0
    
    # Theme weights (easily adjustable)
    theme_weights: Dict[str, float] = None
    
    # Content quality indicators
    roi_bonus: float = 1.5
    methodology_bonus: float = 1.4
    case_study_bonus: float = 1.6
    institutional_source_bonus: float = 1.3
    
    # Exclusion patterns
    exclude_keywords: List[str] = None
    
    def __post_init__(self):
        if self.theme_weights is None:
            self.theme_weights = {
                "opportunities": 1.2,
                "practices": 1.0,
                "systems_codes": 1.1,
                "vision": 0.9
            }
        
        if self.exclude_keywords is None:
            self.exclude_keywords = [
                "furniture", "interior design", "art gallery", "fashion",
                "experimental architecture", "student project"
            ]

@dataclass
class DataCollectionConfig:
    """Data collection configuration"""
    # RSS feeds
    rss_feeds: List[str] = None
    
    # Google Custom Search
    google_api_key: Optional[str] = None
    google_cse_id: Optional[str] = None
    google_queries: List[str] = None
    
    # YouTube
    youtube_api_key: Optional[str] = None
    youtube_channels: List[str] = None
    
    # Web scraping
    crawler_delay: float = 0.1
    crawler_timeout: int = 10
    max_articles_per_source: int = 50
    
    # Rate limiting
    requests_per_minute: int = 60
    
    def __post_init__(self):
        if self.rss_feeds is None:
            self.rss_feeds = [
                "https://feeds.feedburner.com/ConstructionDive",
                "https://www.bisnow.com/rss",
                "https://commercialobserver.com/feed/",
                "https://www.globest.com/rss"
            ]
        
        if self.google_queries is None:
            self.google_queries = [
                "construction innovation 2024",
                "real estate development opportunities",
                "building technology trends",
                "smart city development"
            ]

@dataclass
class APIConfig:
    """API configuration"""
    title: str = "Newsletter API v4"
    description: str = "Intelligent construction and real estate platform"
    version: str = "4.0.0"
    cors_origins: List[str] = None
    rate_limit_per_minute: int = 100
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

@dataclass
class AppConfig:
    """Main application configuration"""
    environment: Environment
    database: DatabaseConfig
    scoring: ScoringConfig
    data_collection: DataCollectionConfig
    api: APIConfig
    
    # Feature flags
    enable_video_support: bool = True
    enable_ai_synthesis: bool = True
    enable_real_time_scoring: bool = True

def get_config() -> AppConfig:
    """Get application configuration from environment variables"""
    
    # Environment
    env = Environment(os.getenv("ENVIRONMENT", "development"))
    
    # Database
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        database_url = "sqlite:///./newsletter_v4.db"
    
    database_config = DatabaseConfig(
        url=database_url,
        pool_size=int(os.getenv("DB_POOL_SIZE", "10")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "20")),
        echo=os.getenv("DB_ECHO", "false").lower() == "true"
    )
    
    # Scoring
    scoring_config = ScoringConfig(
        min_composite_score=float(os.getenv("MIN_COMPOSITE_SCORE", "50.0")),
        min_actionability_score=float(os.getenv("MIN_ACTIONABILITY_SCORE", "60.0")),
        roi_bonus=float(os.getenv("ROI_BONUS", "1.5")),
        methodology_bonus=float(os.getenv("METHODOLOGY_BONUS", "1.4")),
        case_study_bonus=float(os.getenv("CASE_STUDY_BONUS", "1.6")),
        institutional_source_bonus=float(os.getenv("INSTITUTIONAL_SOURCE_BONUS", "1.3"))
    )
    
    # Data Collection
    data_collection_config = DataCollectionConfig(
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        google_cse_id=os.getenv("GOOGLE_CSE_ID"),
        youtube_api_key=os.getenv("YOUTUBE_API_KEY"),
        crawler_delay=float(os.getenv("CRAWLER_DELAY", "0.1")),
        crawler_timeout=int(os.getenv("CRAWLER_TIMEOUT", "10")),
        max_articles_per_source=int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50")),
        requests_per_minute=int(os.getenv("REQUESTS_PER_MINUTE", "60"))
    )
    
    # API
    cors_origins_str = os.getenv("CORS_ORIGINS", "*")
    cors_origins = cors_origins_str.split(",") if cors_origins_str != "*" else ["*"]
    
    api_config = APIConfig(
        cors_origins=cors_origins,
        rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "100"))
    )
    
    return AppConfig(
        environment=env,
        database=database_config,
        scoring=scoring_config,
        data_collection=data_collection_config,
        api=api_config,
        enable_video_support=os.getenv("ENABLE_VIDEO_SUPPORT", "true").lower() == "true",
        enable_ai_synthesis=os.getenv("ENABLE_AI_SYNTHESIS", "true").lower() == "true",
        enable_real_time_scoring=os.getenv("ENABLE_REAL_TIME_SCORING", "true").lower() == "true"
    )

# Theme definitions (easily configurable)
THEMES = {
    "opportunities": {
        "name": "Opportunities",
        "description": "Transformation stories, scaling examples, and wealth-building opportunities",
        "color": "#10B981",
        "icon": "💰",
        "keywords": [
            "transformation", "scaling", "creative deals", "wealth building",
            "investment", "portfolio", "growth story", "success story"
        ]
    },
    "practices": {
        "name": "Practices",
        "description": "Building methods, design principles, and process improvements",
        "color": "#3B82F6",
        "icon": "🔧",
        "keywords": [
            "methodology", "process", "best practices", "lessons learned",
            "efficiency", "productivity", "innovation", "technology"
        ]
    },
    "systems_codes": {
        "name": "Systems & Codes",
        "description": "Policy updates, building code changes, and regulatory unlocks",
        "color": "#F59E0B",
        "icon": "📋",
        "keywords": [
            "policy", "regulation", "building codes", "zoning",
            "incentives", "compliance", "standards", "requirements"
        ]
    },
    "vision": {
        "name": "Vision",
        "description": "Smart cities, future-of-living models, and community impact",
        "color": "#8B5CF6",
        "icon": "🔮",
        "keywords": [
            "smart cities", "future", "innovation", "community",
            "sustainability", "design", "technology", "impact"
        ]
    }
}

# Source quality tiers
SOURCE_TIERS = {
    "tier_1": {
        "name": "Premium Sources",
        "min_score": 80.0,
        "sources": ["JLL", "CBRE", "Cushman & Wakefield", "McKinsey", "Deloitte"]
    },
    "tier_2": {
        "name": "High Quality",
        "min_score": 60.0,
        "sources": ["Bisnow", "Commercial Observer", "Construction Dive", "ENR"]
    },
    "tier_3": {
        "name": "Standard",
        "min_score": 40.0,
        "sources": ["Smart Cities Dive", "Architectural Record", "BuildingGreen"]
    }
}
