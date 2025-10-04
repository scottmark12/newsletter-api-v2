# app/main_v3_endpoints.py
# V3 endpoints to add to existing main.py

from fastapi import HTTPException, Query
from sqlalchemy import text
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta

def add_v3_endpoints(web_app):
    """Add v3 theme-based endpoints to existing FastAPI app"""
    
    @web_app.get("/api/v3/opportunities")
    def get_opportunities(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(20, ge=1, le=100),
        min_score: float = Query(50.0, ge=0.0, le=1000.0)
    ):
        """Get transformation stories, scaling examples, and wealth-building opportunities"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            from .db import SessionLocal
            db = SessionLocal()
            
            query = text("""
                SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score >= :min_score
                  AND a.published_at >= :cutoff
                  AND (
                    'opportunities' = ANY(s.topics) OR
                    'unique_developments' = ANY(s.topics) OR
                    'innovation' = ANY(s.topics) OR
                    s.composite_score >= 80
                  )
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT :limit
            """)
            
            rows = db.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
            db.close()
            
            return {
                "ok": True,
                "theme": "opportunities",
                "description": "Transformation stories, scaling examples, and wealth-building opportunities",
                "count": len(articles),
                "articles": articles,
                "filters_applied": {
                    "days": days,
                    "min_score": min_score
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @web_app.get("/api/v3/practices")
    def get_practices(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(20, ge=1, le=100),
        min_score: float = Query(50.0, ge=0.0, le=1000.0)
    ):
        """Get building methods, design principles, and process improvements"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            from .db import SessionLocal
            db = SessionLocal()
            
            query = text("""
                SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score >= :min_score
                  AND a.published_at >= :cutoff
                  AND (
                    'innovation' = ANY(s.topics) OR
                    s.summary2 ILIKE '%method%' OR
                    s.summary2 ILIKE '%process%' OR
                    s.summary2 ILIKE '%technique%' OR
                    s.summary2 ILIKE '%approach%'
                  )
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT :limit
            """)
            
            rows = db.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
            db.close()
            
            return {
                "ok": True,
                "theme": "practices",
                "description": "Building methods, design principles, and process improvements",
                "count": len(articles),
                "articles": articles,
                "filters_applied": {
                    "days": days,
                    "min_score": min_score
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @web_app.get("/api/v3/systems-codes")
    def get_systems_codes(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(20, ge=1, le=100),
        min_score: float = Query(50.0, ge=0.0, le=1000.0)
    ):
        """Get policy updates, building code changes, and regulatory unlocks"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            from .db import SessionLocal
            db = SessionLocal()
            
            query = text("""
                SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score >= :min_score
                  AND a.published_at >= :cutoff
                  AND (
                    'market_news' = ANY(s.topics) OR
                    s.summary2 ILIKE '%policy%' OR
                    s.summary2 ILIKE '%code%' OR
                    s.summary2 ILIKE '%regulation%' OR
                    s.summary2 ILIKE '%zoning%' OR
                    s.summary2 ILIKE '%legislation%'
                  )
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT :limit
            """)
            
            rows = db.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
            db.close()
            
            return {
                "ok": True,
                "theme": "systems_codes",
                "description": "Policy updates, building code changes, and regulatory unlocks",
                "count": len(articles),
                "articles": articles,
                "filters_applied": {
                    "days": days,
                    "min_score": min_score
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @web_app.get("/api/v3/vision")
    def get_vision(
        days: int = Query(7, ge=1, le=30),
        limit: int = Query(20, ge=1, le=100),
        min_score: float = Query(50.0, ge=0.0, le=1000.0)
    ):
        """Get smart cities, future-of-living models, and community impact stories"""
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        try:
            from .db import SessionLocal
            db = SessionLocal()
            
            query = text("""
                SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score >= :min_score
                  AND a.published_at >= :cutoff
                  AND (
                    s.summary2 ILIKE '%smart city%' OR
                    s.summary2 ILIKE '%future%' OR
                    s.summary2 ILIKE '%vision%' OR
                    s.summary2 ILIKE '%community%' OR
                    s.summary2 ILIKE '%sustainable%' OR
                    s.summary2 ILIKE '%green%'
                  )
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT :limit
            """)
            
            rows = db.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
            db.close()
            
            return {
                "ok": True,
                "theme": "vision",
                "description": "Smart cities, future-of-living models, and community impact stories",
                "count": len(articles),
                "articles": articles,
                "filters_applied": {
                    "days": days,
                    "min_score": min_score
                },
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @web_app.get("/api/v3/health")
    def v3_health_check():
        """V3 health check endpoint"""
        try:
            from .db import SessionLocal
            db = SessionLocal()
            
            # Check database connection
            db.execute(text("SELECT 1"))
            
            # Get basic stats
            stats_query = text("""
                SELECT 
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN s.id IS NOT NULL THEN 1 END) as scored_articles,
                    AVG(s.composite_score) as avg_score
                FROM articles a
                LEFT JOIN article_scores s ON s.article_id = a.id
            """)
            
            stats = db.execute(stats_query).fetchone()
            db.close()
            
            return {
                "status": "healthy",
                "version": "3.0.0 (compatible)",
                "database": "connected",
                "stats": dict(stats._mapping),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "version": "3.0.0 (compatible)",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
