"""
Newsletter API v4 Database Models
Clean, modern SQLAlchemy models with proper relationships
"""

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timezone

Base = declarative_base()

class Article(Base):
    """Enhanced articles table with flexible categorization"""
    __tablename__ = 'articles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, unique=True, nullable=False, index=True)
    title = Column(Text, nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(255), index=True)
    published_at = Column(DateTime(timezone=True), index=True)
    fetched_at = Column(DateTime(timezone=True), default=func.now())
    lang = Column(String(10), default='en')
    status = Column(String(50), default='fetched', index=True)  # fetched, scored, discarded, featured
    
    # Flexible categorization
    primary_theme = Column(String(50), index=True)  # opportunities, practices, systems_codes, vision
    secondary_themes = Column(JSON)  # Array of additional themes
    tags = Column(JSON)  # Flexible tagging system
    
    # Content quality metrics
    content_depth = Column(String(20))  # shallow, medium, deep
    actionability_score = Column(Float, index=True)  # 0-100
    insight_quality = Column(Float, index=True)  # 0-100
    
    # Media support
    media_type = Column(String(20), default='article')  # article, video, podcast, pdf
    video_url = Column(Text)  # YouTube or other video URLs
    video_duration = Column(Integer)  # Duration in seconds
    video_thumbnail = Column(Text)
    
    # Enhanced metadata
    project_stage = Column(String(20))  # planning, approved, breaks_ground, etc.
    needs_fact_check = Column(Boolean, default=False)
    source_reliability = Column(Float, default=0.5)  # 0-1 reliability score
    
    # Relationships
    scores = relationship("ArticleScore", back_populates="article", cascade="all, delete-orphan")
    insights = relationship("ArticleInsight", back_populates="article", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_article_theme_status', 'primary_theme', 'status'),
        Index('idx_article_published_score', 'published_at', 'actionability_score'),
        Index('idx_article_source_published', 'source', 'published_at'),
    )

class ArticleScore(Base):
    """Flexible scoring system with configurable metrics"""
    __tablename__ = 'article_scores'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), nullable=False, index=True)
    
    # Theme-based scores
    opportunities_score = Column(Float, default=0, index=True)
    practices_score = Column(Float, default=0, index=True)
    systems_codes_score = Column(Float, default=0, index=True)
    vision_score = Column(Float, default=0, index=True)
    
    # Narrative signal scores
    transformative_language_score = Column(Float, default=0)
    impact_language_score = Column(Float, default=0)
    prescriptive_language_score = Column(Float, default=0)
    
    # Content quality indicators
    roi_data_present = Column(Boolean, default=False)
    performance_metrics_present = Column(Boolean, default=False)
    methodology_present = Column(Boolean, default=False)
    case_study_present = Column(Boolean, default=False)
    
    # Configurable multipliers
    multipliers_applied = Column(JSON)  # Store all multipliers for transparency
    
    # Final composite score
    composite_score = Column(Float, default=0, index=True)
    
    # Scoring metadata
    scoring_version = Column(String(20), default='4.0')
    scoring_confidence = Column(Float, default=0.8)  # 0-1 confidence in scoring
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="scores")

class ArticleInsight(Base):
    """Extracted insights and actionable information"""
    __tablename__ = 'article_insights'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'), nullable=False, index=True)
    
    # Insight classification
    insight_type = Column(String(50), index=True)  # roi_data, methodology, case_study, etc.
    category = Column(String(50))  # financial, operational, strategic, etc.
    
    # Extracted content
    title = Column(String(255))
    content = Column(Text)
    value = Column(Text)  # Specific value, percentage, dollar amount
    
    # Actionability metrics
    is_actionable = Column(Boolean, default=False, index=True)
    implementation_difficulty = Column(String(20))  # easy, medium, hard
    time_to_implement = Column(String(50))  # "1-3 months", "6-12 months"
    estimated_impact = Column(String(50))  # low, medium, high
    
    # Quality metrics
    confidence_score = Column(Float, default=0.5)  # 0-1 confidence
    needs_verification = Column(Boolean, default=False)
    verification_status = Column(String(20))  # pending, verified, disputed
    
    # Metadata
    extracted_at = Column(DateTime(timezone=True), default=func.now())
    extracted_by = Column(String(50), default='system')  # system, human, ai
    
    # Relationships
    article = relationship("Article", back_populates="insights")

class ContentSource(Base):
    """Enhanced source management with quality tracking"""
    __tablename__ = 'content_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    type = Column(String(50))  # rss, youtube, web_scraper, api
    
    # Quality metrics (updated over time)
    reliability_score = Column(Float, default=0.5)  # 0-1
    insight_quality_score = Column(Float, default=0.5)  # 0-1
    actionability_score = Column(Float, default=0.5)  # 0-1
    content_freshness = Column(Float, default=0.5)  # 0-1
    
    # Source characteristics
    tier = Column(String(20), default='tier_3')  # tier_1, tier_2, tier_3
    primary_themes = Column(JSON)  # Array of themes this source typically covers
    content_types = Column(JSON)  # Array of content types
    
    # Performance tracking
    articles_scraped = Column(Integer, default=0)
    high_scoring_articles = Column(Integer, default=0)
    average_score = Column(Float, default=0)
    last_successful_scrape = Column(DateTime(timezone=True))
    
    # Configuration
    is_active = Column(Boolean, default=True, index=True)
    scrape_frequency = Column(Integer, default=3600)  # Seconds between scrapes
    max_articles_per_scrape = Column(Integer, default=50)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class VideoContent(Base):
    """YouTube and video content tracking"""
    __tablename__ = 'video_content'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(String(100), unique=True, nullable=False, index=True)  # YouTube video ID
    title = Column(Text, nullable=False)
    description = Column(Text)
    channel_id = Column(String(100), index=True)
    channel_name = Column(String(255))
    
    # Video metadata
    duration = Column(Integer)  # Duration in seconds
    published_at = Column(DateTime(timezone=True), index=True)
    view_count = Column(Integer)
    like_count = Column(Integer)
    thumbnail_url = Column(Text)
    
    # Content analysis
    primary_theme = Column(String(50), index=True)
    actionability_score = Column(Float, index=True)
    insight_quality = Column(Float, index=True)
    
    # Processing status
    processed = Column(Boolean, default=False, index=True)
    transcript_available = Column(Boolean, default=False)
    transcript = Column(Text)
    
    # Relationships
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles.id'))
    article = relationship("Article")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class ScoringMetrics(Base):
    """Track scoring system performance and adjustments"""
    __tablename__ = 'scoring_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Metrics metadata
    date = Column(DateTime(timezone=True), default=func.now(), index=True)
    scoring_version = Column(String(20), default='4.0')
    
    # Performance metrics
    total_articles_scored = Column(Integer, default=0)
    average_composite_score = Column(Float, default=0)
    high_quality_articles = Column(Integer, default=0)  # Score > 70
    medium_quality_articles = Column(Integer, default=0)  # Score 40-70
    low_quality_articles = Column(Integer, default=0)  # Score < 40
    
    # Theme distribution
    opportunities_count = Column(Integer, default=0)
    practices_count = Column(Integer, default=0)
    systems_codes_count = Column(Integer, default=0)
    vision_count = Column(Integer, default=0)
    
    # Quality indicators
    articles_with_roi_data = Column(Integer, default=0)
    articles_with_methodology = Column(Integer, default=0)
    articles_with_case_studies = Column(Integer, default=0)
    
    # Source performance
    tier_1_articles = Column(Integer, default=0)
    tier_2_articles = Column(Integer, default=0)
    tier_3_articles = Column(Integer, default=0)

# Database initialization
def init_database(database_url: str):
    """Initialize the database with all tables"""
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    print("✅ Database initialized successfully")
    return engine

def get_session(database_url: str):
    """Get a database session"""
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()
