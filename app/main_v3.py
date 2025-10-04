# app/main_v3.py
# Complete v3 API - Theme-Based Architecture

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import uuid

from .db import SessionLocal, get_database_url
from .schema_v3 import ArticleV3, ArticleScoreV3, ArticleInsightV3, DeveloperProfile, ContentSource, LearningPath, IntelligenceSynthesis
from .scoring_v3 import run_scoring_v3, score_article_v3

# Initialize FastAPI app
web_app = FastAPI(
    title="Newsletter API v3",
    description="Theme-based construction and real estate intelligence platform",
    version="3.0.0"
)

# CORS middleware
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- THEME-BASED ENDPOINTS --------

@web_app.get("/api/v3/opportunities")
def get_opportunities(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True)
):
    """Get transformation stories, scaling examples, and wealth-building opportunities"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        # Base query for opportunities
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.content_depth, a.actionability_score, a.insight_quality,
                   s.opportunities_score, s.composite_score, s.roi_data_present,
                   s.case_study_present, s.transformative_language_score
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE a.primary_theme = 'opportunities'
              AND a.published_at >= :cutoff
              AND s.composite_score >= :min_score
              AND a.status != 'discarded'
            ORDER BY s.opportunities_score DESC, s.composite_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "min_score": min_score,
            "limit": limit
        }).fetchall()
        
        articles = []
        for row in rows:
            article = dict(row._mapping)
            
            # Add insights if requested
            if include_insights:
                insights_query = text("""
                    SELECT insight_type, insight_title, insight_content, insight_value, is_actionable
                    FROM article_insights_v3
                    WHERE article_id = :article_id
                    ORDER BY confidence_score DESC
                """)
                insights = db.execute(insights_query, {"article_id": article['id']}).fetchall()
                article['insights'] = [dict(insight._mapping) for insight in insights]
            
            articles.append(article)
        
        db.close()
        
        return {
            "ok": True,
            "theme": "opportunities",
            "description": "Transformation stories, scaling examples, and wealth-building opportunities",
            "count": len(articles),
            "articles": articles,
            "filters_applied": {
                "days": days,
                "min_score": min_score,
                "include_insights": include_insights
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/v3/practices")
def get_practices(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    content_depth: Optional[str] = Query(None, regex="^(shallow|medium|deep)$"),
    include_insights: bool = Query(True)
):
    """Get building methods, design principles, and process improvements"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        # Build query with optional content depth filter
        where_clause = """
            WHERE a.primary_theme = 'practices'
              AND a.published_at >= :cutoff
              AND s.composite_score >= :min_score
              AND a.status != 'discarded'
        """
        params = {
            "cutoff": cutoff.isoformat(),
            "min_score": min_score,
            "limit": limit
        }
        
        if content_depth:
            where_clause += " AND a.content_depth = :content_depth"
            params["content_depth"] = content_depth
        
        query = text(f"""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.content_depth, a.actionability_score, a.insight_quality,
                   s.practices_score, s.composite_score, s.methodology_present,
                   s.prescriptive_language_score, s.case_study_present
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            {where_clause}
            ORDER BY s.practices_score DESC, s.composite_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, params).fetchall()
        
        articles = []
        for row in rows:
            article = dict(row._mapping)
            
            if include_insights:
                insights_query = text("""
                    SELECT insight_type, insight_title, insight_content, insight_value, is_actionable
                    FROM article_insights_v3
                    WHERE article_id = :article_id
                    ORDER BY confidence_score DESC
                """)
                insights = db.execute(insights_query, {"article_id": article['id']}).fetchall()
                article['insights'] = [dict(insight._mapping) for insight in insights]
            
            articles.append(article)
        
        db.close()
        
        return {
            "ok": True,
            "theme": "practices",
            "description": "Building methods, design principles, and process improvements",
            "count": len(articles),
            "articles": articles,
            "filters_applied": {
                "days": days,
                "min_score": min_score,
                "content_depth": content_depth,
                "include_insights": include_insights
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/v3/systems-codes")
def get_systems_codes(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True)
):
    """Get policy updates, building code changes, and regulatory unlocks"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.content_depth, a.actionability_score, a.insight_quality,
                   s.systems_codes_score, s.composite_score, s.policy_shift_multiplier,
                   s.thought_leadership_multiplier
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE a.primary_theme = 'systems_codes'
              AND a.published_at >= :cutoff
              AND s.composite_score >= :min_score
              AND a.status != 'discarded'
            ORDER BY s.systems_codes_score DESC, s.composite_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "min_score": min_score,
            "limit": limit
        }).fetchall()
        
        articles = []
        for row in rows:
            article = dict(row._mapping)
            
            if include_insights:
                insights_query = text("""
                    SELECT insight_type, insight_title, insight_content, insight_value, is_actionable
                    FROM article_insights_v3
                    WHERE article_id = :article_id
                    ORDER BY confidence_score DESC
                """)
                insights = db.execute(insights_query, {"article_id": article['id']}).fetchall()
                article['insights'] = [dict(insight._mapping) for insight in insights]
            
            articles.append(article)
        
        db.close()
        
        return {
            "ok": True,
            "theme": "systems_codes",
            "description": "Policy updates, building code changes, and regulatory unlocks",
            "count": len(articles),
            "articles": articles,
            "filters_applied": {
                "days": days,
                "min_score": min_score,
                "include_insights": include_insights
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/v3/vision")
def get_vision(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True)
):
    """Get smart cities, future-of-living models, and community impact stories"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.content_depth, a.actionability_score, a.insight_quality,
                   s.vision_score, s.composite_score, s.impact_language_score,
                   s.thought_leadership_multiplier
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE a.primary_theme = 'vision'
              AND a.published_at >= :cutoff
              AND s.composite_score >= :min_score
              AND a.status != 'discarded'
            ORDER BY s.vision_score DESC, s.composite_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "min_score": min_score,
            "limit": limit
        }).fetchall()
        
        articles = []
        for row in rows:
            article = dict(row._mapping)
            
            if include_insights:
                insights_query = text("""
                    SELECT insight_type, insight_title, insight_content, insight_value, is_actionable
                    FROM article_insights_v3
                    WHERE article_id = :article_id
                    ORDER BY confidence_score DESC
                """)
                insights = db.execute(insights_query, {"article_id": article['id']}).fetchall()
                article['insights'] = [dict(insight._mapping) for insight in insights]
            
            articles.append(article)
        
        db.close()
        
        return {
            "ok": True,
            "theme": "vision",
            "description": "Smart cities, future-of-living models, and community impact stories",
            "count": len(articles),
            "articles": articles,
            "filters_applied": {
                "days": days,
                "min_score": min_score,
                "include_insights": include_insights
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- INTELLIGENCE & INSIGHTS ENDPOINTS --------

@web_app.get("/api/v3/insights/high-impact")
def get_high_impact_insights(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    min_actionability: float = Query(70.0, ge=0.0, le=100.0)
):
    """Get the most actionable and high-impact insights across all themes"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.primary_theme, a.content_depth, a.actionability_score, a.insight_quality,
                   s.composite_score, s.roi_data_present, s.methodology_present, s.case_study_present,
                   i.insight_type, i.insight_title, i.insight_content, i.insight_value, i.is_actionable
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            JOIN article_insights_v3 i ON i.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND a.actionability_score >= :min_actionability
              AND i.is_actionable = true
              AND a.status != 'discarded'
            ORDER BY a.actionability_score DESC, s.composite_score DESC, i.confidence_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "min_actionability": min_actionability,
            "limit": limit
        }).fetchall()
        
        insights = []
        for row in rows:
            insight = dict(row._mapping)
            insights.append(insight)
        
        db.close()
        
        return {
            "ok": True,
            "insight_type": "high_impact",
            "description": "Most actionable and high-impact insights across all themes",
            "count": len(insights),
            "insights": insights,
            "filters_applied": {
                "days": days,
                "min_actionability": min_actionability
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/v3/insights/methodology")
def get_methodology_insights(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(15, ge=1, le=50)
):
    """Get articles containing implementation methodologies and processes"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.primary_theme, a.content_depth, a.actionability_score,
                   s.composite_score, s.methodology_present, s.prescriptive_language_score,
                   i.insight_type, i.insight_title, i.insight_content, i.insight_value
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            LEFT JOIN article_insights_v3 i ON i.article_id = a.id AND i.insight_type = 'methodology'
            WHERE a.published_at >= :cutoff
              AND s.methodology_present = true
              AND a.status != 'discarded'
            ORDER BY s.prescriptive_language_score DESC, s.composite_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "limit": limit
        }).fetchall()
        
        methodologies = []
        for row in rows:
            methodology = dict(row._mapping)
            methodologies.append(methodology)
        
        db.close()
        
        return {
            "ok": True,
            "insight_type": "methodology",
            "description": "Implementation methodologies and processes",
            "count": len(methodologies),
            "methodologies": methodologies,
            "filters_applied": {
                "days": days
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- DEVELOPER-CENTRIC ENDPOINTS --------

@web_app.get("/api/v3/developer/opportunities")
def get_developer_opportunities(
    company_size: str = Query("medium", regex="^(small|medium|large|enterprise)$"),
    development_focus: Optional[str] = Query(None),
    experience_level: str = Query("intermediate", regex="^(beginner|intermediate|advanced|expert)$"),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50)
):
    """Get opportunities tailored to developer profile"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db = SessionLocal()
        
        # Base query - can be enhanced with personalization logic
        query = text("""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.primary_theme, a.actionability_score, a.insight_quality,
                   s.composite_score, s.roi_data_present, s.case_study_present,
                   i.insight_type, i.insight_title, i.insight_content, i.insight_value
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            LEFT JOIN article_insights_v3 i ON i.article_id = a.id AND i.insight_type IN ('roi_data', 'case_study', 'market_opportunity')
            WHERE a.published_at >= :cutoff
              AND a.primary_theme = 'opportunities'
              AND a.actionability_score >= 60
              AND a.status != 'discarded'
            ORDER BY s.composite_score DESC, a.actionability_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {
            "cutoff": cutoff.isoformat(),
            "limit": limit
        }).fetchall()
        
        opportunities = []
        for row in rows:
            opportunity = dict(row._mapping)
            opportunities.append(opportunity)
        
        db.close()
        
        return {
            "ok": True,
            "endpoint": "developer_opportunities",
            "description": f"Opportunities for {company_size} {development_focus or 'general'} developers at {experience_level} level",
            "count": len(opportunities),
            "opportunities": opportunities,
            "profile": {
                "company_size": company_size,
                "development_focus": development_focus,
                "experience_level": experience_level
            },
            "filters_applied": {
                "days": days
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- INTELLIGENCE SYNTHESIS ENDPOINTS --------

@web_app.get("/api/v3/synthesis/daily-brief")
def get_daily_brief(
    days_back: int = Query(1, ge=1, le=7)
):
    """Get AI-generated daily intelligence brief"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    try:
        db = SessionLocal()
        
        # Get recent high-scoring articles across all themes
        query = text("""
            SELECT a.primary_theme, COUNT(*) as article_count,
                   AVG(s.composite_score) as avg_score,
                   SUM(CASE WHEN s.roi_data_present THEN 1 ELSE 0 END) as roi_articles,
                   SUM(CASE WHEN s.methodology_present THEN 1 ELSE 0 END) as methodology_articles,
                   SUM(CASE WHEN s.case_study_present THEN 1 ELSE 0 END) as case_study_articles
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND s.composite_score >= 50
              AND a.status != 'discarded'
            GROUP BY a.primary_theme
            ORDER BY avg_score DESC
        """)
        
        theme_stats = db.execute(query, {"cutoff": cutoff.isoformat()}).fetchall()
        
        # Get top articles by theme
        top_articles_query = text("""
            SELECT a.id, a.title, a.source, a.primary_theme, s.composite_score,
                   s.roi_data_present, s.methodology_present, s.case_study_present
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND s.composite_score >= 50
              AND a.status != 'discarded'
            ORDER BY s.composite_score DESC
            LIMIT 10
        """)
        
        top_articles = db.execute(top_articles_query, {"cutoff": cutoff.isoformat()}).fetchall()
        
        db.close()
        
        # Generate brief structure
        brief = {
            "date": datetime.now(timezone.utc).isoformat(),
            "period": f"Last {days_back} day{'s' if days_back > 1 else ''}",
            "theme_analysis": [dict(row._mapping) for row in theme_stats],
            "top_stories": [dict(row._mapping) for row in top_articles],
            "key_insights": {
                "total_high_quality_articles": sum(row.article_count for row in theme_stats),
                "roi_data_articles": sum(row.roi_articles for row in theme_stats),
                "methodology_articles": sum(row.methodology_articles for row in theme_stats),
                "case_study_articles": sum(row.case_study_articles for row in theme_stats)
            }
        }
        
        return {
            "ok": True,
            "brief_type": "daily_intelligence",
            "brief": brief,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- SCORING ENDPOINTS --------

@web_app.post("/api/v3/score/run")
def run_v3_scoring(
    limit: int = Query(100, ge=1, le=500)
):
    """Run the v3 scoring system on new articles"""
    try:
        result = run_scoring_v3(limit)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# -------- HEALTH CHECK --------

@web_app.get("/api/v3/health")
def health_check():
    """Health check endpoint"""
    try:
        db = SessionLocal()
        
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Get basic stats
        stats_query = text("""
            SELECT 
                COUNT(*) as total_articles,
                COUNT(CASE WHEN s.id IS NOT NULL THEN 1 END) as scored_articles,
                COUNT(CASE WHEN a.primary_theme IS NOT NULL THEN 1 END) as themed_articles
            FROM articles_v3 a
            LEFT JOIN article_scores_v3 s ON s.article_id = a.id
        """)
        
        stats = db.execute(stats_query).fetchone()
        db.close()
        
        return {
            "status": "healthy",
            "version": "3.0.0",
            "database": "connected",
            "stats": dict(stats._mapping),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "3.0.0",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# -------- ROOT ENDPOINT --------

@web_app.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Newsletter API v3",
        "description": "Theme-based construction and real estate intelligence platform",
        "version": "3.0.0",
        "endpoints": {
            "themes": [
                "/api/v3/opportunities",
                "/api/v3/practices", 
                "/api/v3/systems-codes",
                "/api/v3/vision"
            ],
            "insights": [
                "/api/v3/insights/high-impact",
                "/api/v3/insights/methodology"
            ],
            "developer": [
                "/api/v3/developer/opportunities"
            ],
            "synthesis": [
                "/api/v3/synthesis/daily-brief"
            ],
            "admin": [
                "/api/v3/score/run",
                "/api/v3/health"
            ]
        },
        "documentation": "https://github.com/your-repo/newsletter-api-v3",
        "last_updated": datetime.now(timezone.utc).isoformat()
    }
