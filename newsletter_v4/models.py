"""
Database models for Newsletter API v4
Clean, modern SQLAlchemy models
"""

from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class Article(Base):
    """Article model for v4"""
    __tablename__ = "articles_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    url = Column(String(1000), unique=True, nullable=False, index=True)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(200), nullable=False, index=True)
    author = Column(String(200))
    published_at = Column(DateTime(timezone=True), index=True)
    
    # Metadata
    word_count = Column(Integer, default=0)
    reading_time = Column(Integer, default=0)  # in minutes
    image_url = Column(String(1000))  # Extracted article image URL
    
    # Content analysis
    themes = Column(JSON)  # List of detected themes
    keywords = Column(JSON)  # List of extracted keywords
    why_it_matters = Column(Text)  # AI-generated "Why it Matters" content
    takeaways = Column(JSON)  # AI-generated bullet points
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    scores = relationship("ArticleScore", back_populates="article", cascade="all, delete-orphan")
    insights = relationship("ArticleInsight", back_populates="article", cascade="all, delete-orphan")


class ArticleScore(Base):
    """Article scoring model for v4"""
    __tablename__ = "article_scores_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles_v4.id"), nullable=False, index=True)
    
    # Overall score
    total_score = Column(Float, nullable=False, index=True)
    
    # Theme scores
    opportunities_score = Column(Float, default=0.0)
    practices_score = Column(Float, default=0.0)
    systems_score = Column(Float, default=0.0)
    vision_score = Column(Float, default=0.0)
    
    # Quality factors
    insight_quality_score = Column(Float, default=0.0)
    narrative_signal_score = Column(Float, default=0.0)
    source_credibility_score = Column(Float, default=0.0)
    
    # Scoring metadata
    scoring_version = Column(String(50), default="4.0.0")
    scoring_details = Column(JSON)  # Detailed scoring breakdown
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="scores")


class ArticleInsight(Base):
    """Article insights model for v4"""
    __tablename__ = "article_insights_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("articles_v4.id"), nullable=False, index=True)
    
    # Insight content
    insight_text = Column(Text, nullable=False)
    insight_type = Column(String(100), nullable=False, index=True)  # opportunity, practice, system, vision
    confidence_score = Column(Float, default=0.0)
    
    # Context
    supporting_evidence = Column(Text)
    related_keywords = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", back_populates="insights")


class Video(Base):
    """Video model for v4"""
    __tablename__ = "videos_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(500), nullable=False, index=True)
    youtube_id = Column(String(50), unique=True, nullable=False, index=True)
    url = Column(String(200), nullable=False)
    thumbnail_url = Column(String(500))
    
    # Video metadata
    channel_name = Column(String(200), index=True)
    duration = Column(Integer)  # in seconds
    view_count = Column(Integer)
    published_at = Column(DateTime(timezone=True), index=True)
    
    # Content analysis
    transcript = Column(Text)
    summary = Column(Text)
    themes = Column(JSON)
    
    # Scoring
    relevance_score = Column(Float, default=0.0)
    quality_score = Column(Float, default=0.0)
    total_score = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class ContentSource(Base):
    """Content source model for v4"""
    __tablename__ = "content_sources_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), unique=True, nullable=False, index=True)
    url = Column(String(500), nullable=False)
    source_type = Column(String(50), nullable=False, index=True)  # rss, google, youtube, scraper
    
    # Source configuration
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=1)  # 1-10, higher = more important
    last_collected = Column(DateTime(timezone=True))
    
    # Source metadata
    description = Column(Text)
    tags = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SystemMetrics(Base):
    """System metrics model for v4"""
    __tablename__ = "system_metrics_v4"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50))
    
    # Context
    source = Column(String(200))
    tags = Column(JSON)
    
    # Timestamps
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
