# app/schema_v3.py
# Complete v3 Database Schema - Theme-Based Architecture

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

Base = declarative_base()

class ArticleV3(Base):
    """Enhanced articles table with theme-based categorization"""
    __tablename__ = 'articles_v3'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    url = Column(Text, unique=True, nullable=False)
    title = Column(Text, nullable=False)
    content = Column(Text)
    summary_raw = Column(Text)
    source = Column(String(255))
    published_at = Column(DateTime(timezone=True))
    fetched_at = Column(DateTime(timezone=True), default=func.now())
    lang = Column(String(10), default='en')
    status = Column(String(50), default='fetched')  # fetched, scored, discarded, featured
    
    # Theme-based categorization
    primary_theme = Column(String(50))  # opportunities, practices, systems_codes, vision
    secondary_themes = Column(JSON)  # Array of additional themes
    
    # Content quality metrics
    content_depth = Column(String(20))  # shallow, medium, deep
    actionability_score = Column(Float)  # 0-100, how actionable is this content
    insight_quality = Column(Float)  # 0-100, quality of insights provided
    
    # Enhanced metadata
    media_type = Column(String(20))  # article, video, podcast, pdf, white_paper
    project_stage = Column(String(20))  # planning, approved, breaks_ground, tops_out, opens
    needs_fact_check = Column(Boolean, default=False)
    
    # Relationships
    scores = relationship("ArticleScoreV3", back_populates="article", cascade="all, delete-orphan")
    insights = relationship("ArticleInsightV3", back_populates="article", cascade="all, delete-orphan")

class ArticleScoreV3(Base):
    """Enhanced scoring with theme-based metrics"""
    __tablename__ = 'article_scores_v3'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles_v3.id'), nullable=False)
    
    # Theme-based scores
    opportunities_score = Column(Float, default=0)
    practices_score = Column(Float, default=0)
    systems_codes_score = Column(Float, default=0)
    vision_score = Column(Float, default=0)
    
    # Narrative signal scores
    transformative_language_score = Column(Float, default=0)
    impact_language_score = Column(Float, default=0)
    prescriptive_language_score = Column(Float, default=0)
    
    # Pragmatic insight metrics
    roi_data_present = Column(Boolean, default=False)
    performance_metrics_present = Column(Boolean, default=False)
    methodology_present = Column(Boolean, default=False)
    case_study_present = Column(Boolean, default=False)
    
    # Enhanced multipliers applied
    case_study_multiplier = Column(Float, default=1.0)
    scalable_process_multiplier = Column(Float, default=1.0)
    policy_shift_multiplier = Column(Float, default=1.0)
    thought_leadership_multiplier = Column(Float, default=1.0)
    
    # Final composite score
    composite_score = Column(Float, default=0)
    
    # Institutional and dollar bonuses
    institutional_source_bonus = Column(Float, default=1.0)
    dollar_amount_multiplier = Column(Float, default=1.0)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    
    # Relationships
    article = relationship("ArticleV3", back_populates="scores")

class ArticleInsightV3(Base):
    """Extracted insights and actionable information"""
    __tablename__ = 'article_insights_v3'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey('articles_v3.id'), nullable=False)
    
    # Insight types
    insight_type = Column(String(50))  # roi_data, methodology, case_study, policy_change, market_opportunity
    
    # Extracted content
    insight_title = Column(String(255))
    insight_content = Column(Text)
    insight_value = Column(Text)  # Specific value, percentage, dollar amount, etc.
    
    # Actionability
    is_actionable = Column(Boolean, default=False)
    implementation_difficulty = Column(String(20))  # easy, medium, hard
    time_to_implement = Column(String(50))  # "1-3 months", "6-12 months", etc.
    
    # Confidence and verification
    confidence_score = Column(Float)  # 0-100, confidence in this insight
    needs_verification = Column(Boolean, default=False)
    
    # Relationships
    article = relationship("ArticleV3", back_populates="insights")

class DeveloperProfile(Base):
    """Developer preferences and learning progress"""
    __tablename__ = 'developer_profiles'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    
    # Preferences
    primary_themes = Column(JSON)  # Array of preferred themes
    company_size = Column(String(50))  # small, medium, large, enterprise
    development_focus = Column(String(100))  # residential, commercial, infrastructure, etc.
    experience_level = Column(String(20))  # beginner, intermediate, advanced, expert
    
    # Learning progress
    implemented_methodologies = Column(JSON)  # Array of methodologies they've used
    saved_opportunities = Column(JSON)  # Array of opportunity article IDs
    learning_path = Column(String(100))  # Current learning path they're following
    
    # Engagement metrics
    articles_read = Column(Integer, default=0)
    insights_saved = Column(Integer, default=0)
    methodologies_implemented = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class ContentSource(Base):
    """Enhanced source management with quality ratings"""
    __tablename__ = 'content_sources'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    domain = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    
    # Source quality metrics
    reliability_score = Column(Float, default=0.5)  # 0-1, how reliable is this source
    insight_quality_score = Column(Float, default=0.5)  # 0-1, quality of insights provided
    actionability_score = Column(Float, default=0.5)  # 0-1, how actionable is content
    
    # Source characteristics
    source_type = Column(String(50))  # news, research, white_paper, case_study, video, podcast
    institutional_level = Column(String(50))  # none, low, medium, high, top_tier
    
    # Content themes this source typically covers
    primary_themes = Column(JSON)
    
    # Performance metrics
    articles_scraped = Column(Integer, default=0)
    high_scoring_articles = Column(Integer, default=0)
    average_score = Column(Float, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_scraped = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), default=func.now())

class LearningPath(Base):
    """Structured learning paths for developers"""
    __tablename__ = 'learning_paths'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Path characteristics
    target_audience = Column(String(100))  # beginner, intermediate, advanced, expert
    estimated_duration = Column(String(50))  # "3 months", "6 months", etc.
    difficulty_level = Column(String(20))  # easy, medium, hard
    
    # Path structure
    modules = Column(JSON)  # Array of module objects with articles, exercises, etc.
    prerequisites = Column(JSON)  # Array of required knowledge/skills
    
    # Content curation
    featured_articles = Column(JSON)  # Array of article IDs
    case_studies = Column(JSON)  # Array of case study article IDs
    methodologies = Column(JSON)  # Array of methodology article IDs
    
    # Engagement metrics
    enrolled_count = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0)
    
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class IntelligenceSynthesis(Base):
    """AI-generated insights and synthesis across themes"""
    __tablename__ = 'intelligence_synthesis'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Synthesis metadata
    synthesis_date = Column(DateTime(timezone=True), default=func.now())
    synthesis_type = Column(String(50))  # daily_brief, weekly_analysis, theme_deep_dive, opportunity_scan
    
    # Input data
    articles_analyzed = Column(JSON)  # Array of article IDs used
    themes_covered = Column(JSON)  # Array of themes included
    time_period = Column(String(50))  # "last_24_hours", "last_week", etc.
    
    # Generated content
    headline = Column(String(255))
    executive_summary = Column(Text)
    key_insights = Column(JSON)  # Array of insight objects
    opportunities_identified = Column(JSON)  # Array of opportunity objects
    recommendations = Column(JSON)  # Array of recommendation objects
    
    # Quality metrics
    confidence_score = Column(Float)  # 0-100, confidence in synthesis quality
    actionable_insights_count = Column(Integer, default=0)
    verified_claims_count = Column(Integer, default=0)
    
    # Engagement
    views_count = Column(Integer, default=0)
    saves_count = Column(Integer, default=0)
    shares_count = Column(Integer, default=0)

def init_db_v3():
    """Initialize the v3 database schema"""
    from .db import get_database_url
    from sqlalchemy import create_engine
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(engine)
    print("✅ Database schema v3 initialized successfully")

def get_session_v3():
    """Get a database session for v3"""
    from .db import get_database_url
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    database_url = get_database_url()
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

# Migration utilities
def migrate_from_v2_to_v3():
    """Migrate existing v2 data to v3 schema"""
    # This would contain migration logic to move data from v2 tables to v3 tables
    # Implementation would depend on specific migration requirements
    pass
