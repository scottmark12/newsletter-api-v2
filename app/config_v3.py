# app/config_v3.py
# V3 Configuration and Environment Management

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class V3Config:
    """V3 Application Configuration"""
    
    # Database Configuration
    database_url: str
    force_sqlite: bool = False
    
    # API Configuration
    api_title: str = "Newsletter API v3"
    api_description: str = "Theme-based construction and real estate intelligence platform"
    api_version: str = "3.0.0"
    
    # CORS Configuration
    cors_origins: list = None
    
    # Crawler Configuration
    crawler_delay: float = 0.1  # Delay between requests
    crawler_timeout: int = 10   # Request timeout
    max_articles_per_source: int = 50
    
    # Scoring Configuration
    min_composite_score: float = 50.0
    min_actionability_score: float = 60.0
    max_articles_per_scoring_run: int = 500
    
    # Intelligence Synthesis Configuration
    synthesis_max_tokens: int = 2000
    synthesis_temperature: float = 0.3
    max_articles_for_synthesis: int = 50
    
    # Source Quality Thresholds
    tier_1_min_score: float = 80.0
    tier_2_min_score: float = 60.0
    tier_3_min_score: float = 40.0
    
    # Content Quality Thresholds
    min_content_length: int = 200
    min_title_length: int = 10
    max_title_length: int = 200
    
    def __post_init__(self):
        if self.cors_origins is None:
            self.cors_origins = ["*"]

def get_v3_config() -> V3Config:
    """Get V3 configuration from environment variables"""
    
    # Database URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback to SQLite for development
        database_url = "sqlite:///./newsletter_v3.db"
    
    # Force SQLite if specified
    force_sqlite = os.getenv("FORCE_SQLITE", "false").lower() == "true"
    if force_sqlite:
        database_url = "sqlite:///./newsletter_v3.db"
    
    # CORS origins
    cors_origins_str = os.getenv("CORS_ORIGINS", "*")
    cors_origins = cors_origins_str.split(",") if cors_origins_str != "*" else ["*"]
    
    return V3Config(
        database_url=database_url,
        force_sqlite=force_sqlite,
        cors_origins=cors_origins,
        crawler_delay=float(os.getenv("CRAWLER_DELAY", "0.1")),
        crawler_timeout=int(os.getenv("CRAWLER_TIMEOUT", "10")),
        max_articles_per_source=int(os.getenv("MAX_ARTICLES_PER_SOURCE", "50")),
        min_composite_score=float(os.getenv("MIN_COMPOSITE_SCORE", "50.0")),
        min_actionability_score=float(os.getenv("MIN_ACTIONABILITY_SCORE", "60.0")),
        max_articles_per_scoring_run=int(os.getenv("MAX_ARTICLES_PER_SCORING_RUN", "500")),
        synthesis_max_tokens=int(os.getenv("SYNTHESIS_MAX_TOKENS", "2000")),
        synthesis_temperature=float(os.getenv("SYNTHESIS_TEMPERATURE", "0.3")),
        max_articles_for_synthesis=int(os.getenv("MAX_ARTICLES_FOR_SYNTHESIS", "50")),
        tier_1_min_score=float(os.getenv("TIER_1_MIN_SCORE", "80.0")),
        tier_2_min_score=float(os.getenv("TIER_2_MIN_SCORE", "60.0")),
        tier_3_min_score=float(os.getenv("TIER_3_MIN_SCORE", "40.0")),
        min_content_length=int(os.getenv("MIN_CONTENT_LENGTH", "200")),
        min_title_length=int(os.getenv("MIN_TITLE_LENGTH", "10")),
        max_title_length=int(os.getenv("MAX_TITLE_LENGTH", "200"))
    )

# V3 Theme Configuration
V3_THEMES = {
    "opportunities": {
        "name": "Opportunities",
        "description": "Transformation stories, scaling examples, and wealth-building opportunities",
        "color": "#10B981",  # Green
        "icon": "💰",
        "priority": 1
    },
    "practices": {
        "name": "Practices", 
        "description": "Building methods, design principles, and process improvements",
        "color": "#3B82F6",  # Blue
        "icon": "🔧",
        "priority": 2
    },
    "systems_codes": {
        "name": "Systems & Codes",
        "description": "Policy updates, building code changes, and regulatory unlocks",
        "color": "#F59E0B",  # Amber
        "icon": "📋",
        "priority": 3
    },
    "vision": {
        "name": "Vision",
        "description": "Smart cities, future-of-living models, and community impact",
        "color": "#8B5CF6",  # Purple
        "icon": "🔮",
        "priority": 4
    }
}

# V3 Source Quality Configuration
V3_SOURCE_QUALITY = {
    "tier_1": {
        "name": "Tier 1 - Premium",
        "min_score": 80.0,
        "description": "Top-tier institutional sources with high-quality insights",
        "examples": ["JLL", "CBRE", "Cushman & Wakefield", "McKinsey", "Deloitte"]
    },
    "tier_2": {
        "name": "Tier 2 - High Quality",
        "min_score": 60.0,
        "description": "High-quality industry sources with reliable information",
        "examples": ["Bisnow", "Commercial Observer", "Construction Dive", "ENR"]
    },
    "tier_3": {
        "name": "Tier 3 - Standard",
        "min_score": 40.0,
        "description": "Standard industry sources with good coverage",
        "examples": ["Smart Cities Dive", "Architectural Record", "BuildingGreen"]
    }
}

# V3 Content Quality Indicators
V3_CONTENT_QUALITY = {
    "deep": {
        "name": "Deep Analysis",
        "min_score": 80.0,
        "description": "Comprehensive analysis with methodology and ROI data",
        "indicators": ["ROI data", "Methodology", "Case study", "Performance metrics"]
    },
    "medium": {
        "name": "Medium Depth",
        "min_score": 60.0,
        "description": "Good analysis with some actionable insights",
        "indicators": ["Methodology", "Case study", "Best practices"]
    },
    "shallow": {
        "name": "Shallow Content",
        "min_score": 40.0,
        "description": "Basic information with limited actionable value",
        "indicators": ["General information", "News updates", "Announcements"]
    }
}

# V3 Actionability Levels
V3_ACTIONABILITY = {
    "high": {
        "name": "High Actionability",
        "min_score": 80.0,
        "description": "Immediately actionable with clear implementation steps",
        "indicators": ["ROI data", "Step-by-step process", "Implementation guide"]
    },
    "medium": {
        "name": "Medium Actionability",
        "min_score": 60.0,
        "description": "Actionable with some planning required",
        "indicators": ["Best practices", "Lessons learned", "Case study"]
    },
    "low": {
        "name": "Low Actionability",
        "min_score": 40.0,
        "description": "Informational with limited immediate action",
        "indicators": ["Trend analysis", "Market updates", "General information"]
    }
}

# V3 Learning Paths Configuration
V3_LEARNING_PATHS = {
    "beginner": {
        "name": "Beginner Developer",
        "description": "New to development, learning fundamentals",
        "duration": "3-6 months",
        "focus_themes": ["practices", "vision"],
        "content_types": ["methodology", "case_study", "best_practices"]
    },
    "intermediate": {
        "name": "Intermediate Developer", 
        "description": "Some experience, looking to scale operations",
        "duration": "6-12 months",
        "focus_themes": ["practices", "opportunities"],
        "content_types": ["roi_data", "methodology", "case_study"]
    },
    "advanced": {
        "name": "Advanced Developer",
        "description": "Experienced developer seeking market opportunities",
        "duration": "12+ months",
        "focus_themes": ["opportunities", "systems_codes"],
        "content_types": ["roi_data", "policy_change", "market_opportunity"]
    },
    "expert": {
        "name": "Expert Developer",
        "description": "Industry leader shaping market direction",
        "duration": "Ongoing",
        "focus_themes": ["systems_codes", "vision", "opportunities"],
        "content_types": ["policy_change", "thought_leadership", "market_opportunity"]
    }
}

def get_theme_config(theme_name: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific theme"""
    return V3_THEMES.get(theme_name)

def get_source_quality_config(tier: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific source quality tier"""
    return V3_SOURCE_QUALITY.get(tier)

def get_content_quality_config(quality_level: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific content quality level"""
    return V3_CONTENT_QUALITY.get(quality_level)

def get_actionability_config(actionability_level: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific actionability level"""
    return V3_ACTIONABILITY.get(actionability_level)

def get_learning_path_config(experience_level: str) -> Optional[Dict[str, Any]]:
    """Get configuration for a specific learning path"""
    return V3_LEARNING_PATHS.get(experience_level)

def validate_v3_config() -> Dict[str, Any]:
    """Validate V3 configuration"""
    config = get_v3_config()
    
    validation_results = {
        "database": {
            "url_configured": bool(config.database_url),
            "sqlite_fallback": config.force_sqlite
        },
        "api": {
            "title_configured": bool(config.api_title),
            "version_configured": bool(config.api_version)
        },
        "crawler": {
            "delay_configured": config.crawler_delay > 0,
            "timeout_configured": config.crawler_timeout > 0
        },
        "scoring": {
            "min_scores_configured": config.min_composite_score > 0,
            "max_articles_configured": config.max_articles_per_scoring_run > 0
        },
        "synthesis": {
            "max_tokens_configured": config.synthesis_max_tokens > 0,
            "temperature_configured": 0 <= config.synthesis_temperature <= 1
        }
    }
    
    # Overall validation
    all_valid = all(
        all(category.values()) for category in validation_results.values()
    )
    
    return {
        "valid": all_valid,
        "results": validation_results,
        "config": config
    }
