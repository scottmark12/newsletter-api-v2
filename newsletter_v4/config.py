"""
Configuration for Newsletter API v4
Clean, environment-based configuration system
"""

import os
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class DatabaseConfig:
    """Database configuration"""
    url: str = os.getenv("DATABASE_URL", "sqlite:///./newsletter_v4.db")
    echo: bool = os.getenv("DATABASE_ECHO", "false").lower() == "true"


@dataclass
class APIConfig:
    """API configuration"""
    title: str = "Newsletter API v4"
    description: str = "Intelligent construction and real estate platform"
    version: str = "4.0.0"
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    cors_origins: List[str] = None

    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]


@dataclass
class ScoringConfig:
    """Scoring system configuration"""
    # Theme weights
    opportunities_weight: float = float(os.getenv("OPPORTUNITIES_WEIGHT", "1.0"))
    practices_weight: float = float(os.getenv("PRACTICES_WEIGHT", "1.0"))
    systems_weight: float = float(os.getenv("SYSTEMS_WEIGHT", "1.0"))
    vision_weight: float = float(os.getenv("VISION_WEIGHT", "1.0"))
    
    # Quality factors
    insight_quality_weight: float = float(os.getenv("INSIGHT_QUALITY_WEIGHT", "1.5"))
    narrative_signal_weight: float = float(os.getenv("NARRATIVE_SIGNAL_WEIGHT", "1.2"))
    
    # Source multipliers
    institutional_source_bonus: float = float(os.getenv("INSTITUTIONAL_BONUS", "1.3"))
    premium_source_bonus: float = float(os.getenv("PREMIUM_BONUS", "1.2"))


@dataclass
class DataSourcesConfig:
    """Data sources configuration"""
    # RSS feeds
    rss_feeds: List[str] = None
    
    # Google search
    google_api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    google_cse_id: Optional[str] = os.getenv("GOOGLE_CSE_ID")
    
    # YouTube
    youtube_api_key: Optional[str] = os.getenv("YOUTUBE_API_KEY")
    
    # Web scraping
    max_articles_per_source: int = int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50"))
    request_delay: float = float(os.getenv("REQUEST_DELAY", "1.0"))

    def __post_init__(self):
        if self.rss_feeds is None:
            self.rss_feeds = [
                "https://feeds.feedburner.com/ConstructionDive",
                "https://www.constructiondive.com/feeds/news/",
                "https://www.enr.com/rss.xml",
                "https://feeds.feedburner.com/CommercialObserver",
                "https://www.bisnow.com/rss",
            ]


@dataclass
class V4Config:
    """Main configuration container"""
    database: DatabaseConfig
    api: APIConfig
    scoring: ScoringConfig
    data_sources: DataSourcesConfig

    def __init__(self):
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.scoring = ScoringConfig()
        self.data_sources = DataSourcesConfig()


# Global config instance
config = V4Config()


def get_config() -> V4Config:
    """Get the global configuration instance"""
    return config
