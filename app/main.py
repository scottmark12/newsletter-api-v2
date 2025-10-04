# app/main.py
import os
import re
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text

from .db import init_db
from . import crawler, scoring

web_app = FastAPI(
    title="Newsletter API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS so Lovable (or any browser client) can call your API
web_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # replace with your Lovable app origin when known
    allow_credentials=False,
    allow_methods=["*"],          # include OPTIONS automatically
    allow_headers=["*"],
)

# --- health & root ---
@web_app.get("/health")
@web_app.get("/healthz")
def health():
    return {"ok": True}

@web_app.get("/")
def root():
    return {"status": "ok", "docs": "/docs", "health": "/health"}

# --- startup: ensure schema exists ---
@web_app.on_event("startup")
def on_startup():
    init_db()

# --- actions ---
@web_app.post("/ingest/run")
def ingest_run(limit: int = Query(50, ge=1, le=500)):
    try:
        try:
            result = crawler.run(limit=limit)
        except TypeError:
            result = crawler.run()
        if isinstance(result, dict):
            return result
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@web_app.post("/ingest/start", status_code=202)
@web_app.get("/ingest/start", status_code=202)
def ingest_start(limit: int = Query(50, ge=1, le=500), tasks: BackgroundTasks = None):
    """
    Start ingest in the background. FastAPI will inject BackgroundTasks.
    We keep a tiny fallback to threading if for some reason it's not injected.
    """
    if tasks is None:
        import threading
        threading.Thread(target=crawler.run, kwargs={"limit": limit}, daemon=True).start()
    else:
        tasks.add_task(crawler.run, limit)
    return {"ok": True, "started": True, "limit": limit}

@web_app.post("/score/run")
def score_run(limit: int = Query(50, ge=1, le=500)):
    try:
        result = scoring.run(limit=limit)
        if isinstance(result, dict):
            return result
        return {"ok": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# ---- INTELLIGENCE SYNTHESIS ENDPOINTS ----

@web_app.post("/ingest/research")
def ingest_research(limit: int = Query(10, ge=1, le=50)):
    """Ingest research reports from major CRE firms (JLL, CBRE, etc.)"""
    try:
        from . import pdf_handler
        return pdf_handler.run(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.post("/ingest/videos")
def ingest_videos(limit: int = Query(20, ge=1, le=100)):
    """Ingest YouTube construction video transcripts"""
    try:
        from . import transcript_handler
        return transcript_handler.run(limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/brief/narrative")
def api_narrative_brief(days_back: int = Query(1, ge=1, le=7)):
    """
    Get AI-synthesized narrative brief that weaves together:
    - News articles
    - Research reports from JLL/CBRE  
    - Video/podcast content
    Into a coherent story with actual point of view
    """
    try:
        from . import narrative_synthesis
        result = narrative_synthesis.synthesize_daily_narrative(days_back=days_back)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/content/recommended")
def api_recommended_content(content_type: str = Query("video", regex="^(video|podcast)$")):
    """Get recommended video or podcast for the day"""
    try:
        from . import narrative_synthesis
        content = narrative_synthesis.get_recommended_content(content_type=content_type)
        if content:
            return {"ok": True, "recommended": content}
        else:
            return {"ok": True, "recommended": None, "message": f"No {content_type} content found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- read-only viewer (safe) ---
SAFE_TABLES = {"articles", "article_scores", "issues"}

def _get_engine():
    # Use the same database URL logic as app.db
    from .db import actual_db_url
    return create_engine(actual_db_url)

# ---- JSON FEED FOR LOVABLE (recent articles) ----
@web_app.get("/api/articles")
def api_articles(
    limit: int = Query(20, ge=1, le=100),
    since_hours: int = Query(24, ge=1, le=168),
):
    """
    Returns recent articles as JSON for the frontend.
    Use: GET /api/articles?limit=20&since_hours=24
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                           a.published_at, a.fetched_at, a.lang,
                           s.composite_score, s.topics, s.geography, s.macro_flag,
                           s.summary2, s.why1, s.project_stage, s.needs_fact_check, s.media_type
                    FROM articles a
                    LEFT JOIN article_scores s ON s.article_id = a.id
                    WHERE a.status != 'discarded' AND (
                        (a.published_at IS NOT NULL AND a.published_at >= :cutoff)
                        OR
                        (a.published_at IS NULL AND a.fetched_at >= :cutoff)
                    )
                    ORDER BY COALESCE(s.composite_score, 0) DESC, COALESCE(a.published_at, a.fetched_at) DESC
                    LIMIT :limit
                """),
                {"cutoff": cutoff.isoformat(), "limit": limit},
            ).mappings().all()
        return {"ok": True, "count": len(rows), "items": [dict(r) for r in rows]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@web_app.get("/admin/table/{name}")
def view_table(name: str, limit: int = Query(25, ge=1, le=500)):
    if name not in SAFE_TABLES:
        raise HTTPException(status_code=400, detail=f"table not allowed: {name}")
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text(f"SELECT * FROM {name} ORDER BY 1 DESC LIMIT :limit"),
                {"limit": limit},
            )
            return [dict(r._mapping) for r in rows]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# ---- JSON FEED FOR LOVABLE (top articles by category) ----
@web_app.get("/api/main")
def api_main_page(
    days: int = Query(7, ge=1, le=30)
):
    """
    Coherent main page with clear narrative flow and curated content sections.
    Creates a structured, digestible experience rather than scattered articles.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        db_engine = _get_engine()
        
        # Get the top story of the day (highest impact)
        with db_engine.connect() as conn:
            top_story_row = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 1
            """), {"cutoff": cutoff.isoformat()}).mappings().fetchone()
        
        # Get cutting edge projects (2-3 architectural/entrepreneurial innovation stories)
        with db_engine.connect() as conn:
            all_articles = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                ORDER BY s.composite_score DESC, a.published_at DESC
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
            
            # Filter for innovation articles in Python
            cutting_edge_projects_rows = []
            for row in all_articles:
                article = dict(row)
                topics = article.get('topics', [])
                if 'innovation' in topics and len(cutting_edge_projects_rows) < 3 and article.get('composite_score', 0) > 50:
                    cutting_edge_projects_rows.append(article)
        
        # Get cutting edge development (2-3 major infrastructure/city-changing stories)
        with db_engine.connect() as conn:
            all_articles_dev = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                ORDER BY s.composite_score DESC, a.published_at DESC
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
            
            # Filter for unique_developments articles in Python
            cutting_edge_development_rows = []
            for row in all_articles_dev:
                article = dict(row)
                topics = article.get('topics', [])
                if 'unique_developments' in topics and len(cutting_edge_development_rows) < 3 and article.get('composite_score', 0) > 60:
                    cutting_edge_development_rows.append(article)
        
        # Get market movers (3-4 significant market developments)
        with db_engine.connect() as conn:
            market_rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND ('market_news' = ANY(s.topics) OR 'unique_developments' = ANY(s.topics))
                  AND s.composite_score > 80  -- Only significant market developments
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 4
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Get insights & analysis (2-3 deep-dive pieces)
        with db_engine.connect() as conn:
            insights_rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND 'insights' = ANY(s.topics)
                  AND s.composite_score > 60  -- Only substantial insights
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 3
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Get quick hits (top 5 highest scores excluding the top story)
        with db_engine.connect() as conn:
            quick_hits_rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND a.id != :exclude_top_story_id  -- Exclude the top story
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 5
            """), {
                "cutoff": cutoff.isoformat(), 
                "exclude_top_story_id": top_story_row['id'] if top_story_row else None
            }).mappings().all()
        
        # Convert rows to dicts and add context
        top_story = dict(top_story_row) if top_story_row else None
        if top_story:
            top_story['section'] = 'top_story'
            top_story['context'] = 'Today\'s most important story'
        
        cutting_edge_projects = [dict(row) for row in cutting_edge_projects_rows]
        for article in cutting_edge_projects:
            article['section'] = 'cutting_edge_projects'
            article['context'] = 'Architectural innovation and entrepreneurial building science'
        
        cutting_edge_development = [dict(row) for row in cutting_edge_development_rows]
        for article in cutting_edge_development:
            article['section'] = 'cutting_edge_development'
            article['context'] = 'Major infrastructure projects that change cities forever'
        
        market_movers = [dict(row) for row in market_rows]
        for article in market_movers:
            article['section'] = 'market_news'
            article['context'] = 'Today\'s events affecting construction and real estate'
        
        insights_analysis = [dict(row) for row in insights_rows]
        for article in insights_analysis:
            article['section'] = 'insights'
            article['context'] = 'Market intelligence and opportunity analysis'
        
        quick_hits = [dict(row) for row in quick_hits_rows]
        for article in quick_hits:
            article['section'] = 'quick_hits'
            article['context'] = 'Brief updates and noteworthy developments'
        
        return {
            "ok": True,
            "page_title": "Building the Future - Today's Essential News",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "sections": {
                "top_story": {
                    "title": "Today's Top Story",
                    "description": "The most important development in construction and real estate",
                    "articles": [top_story] if top_story else []
                },
                "market_news": {
                    "title": "Market News",
                    "description": "Today's events affecting construction and real estate",
                    "articles": market_movers
                },
                "cutting_edge_projects": {
                    "title": "Cutting Edge Projects", 
                    "description": "Architectural innovation and entrepreneurial building science",
                    "articles": cutting_edge_projects
                },
                "cutting_edge_development": {
                    "title": "Cutting Edge Development",
                    "description": "Major infrastructure that changes cities forever",
                    "articles": cutting_edge_development
                },
                "insights": {
                    "title": "Insights",
                    "description": "Market intelligence and opportunity analysis", 
                    "articles": insights_analysis
                },
                "quick_hits": {
                    "title": "Quick Hits",
                    "description": "Brief updates and noteworthy developments",
                    "articles": quick_hits
                }
            },
            "total_articles": len(cutting_edge_projects) + len(cutting_edge_development) + len(market_movers) + len(insights_analysis) + len(quick_hits) + (1 if top_story else 0),
            "description": "Curated daily digest of the most important construction and real estate news"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@web_app.get("/api/categories/top")
def api_categories_top():
    """
    Returns the top 3 articles for each category with new naming structure.
    """
    db_engine = _get_engine()
    
    # Define category mapping: frontend_name -> internal_topic (with fallbacks)
    category_mapping = {
        "market_news": "market_news",
        "cutting_edge_projects": "innovation",  # Map to old topic name
        "cutting_edge_development": "unique_developments",  # Map to old topic name  
        "insights": "insights"
    }
    
    result = {}
    
    with db_engine.connect() as conn:
        # Get ALL articles and filter in Python - much simpler and more reliable
        all_rows = conn.execute(text("""
            SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                   s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                   s.project_stage, s.needs_fact_check, s.media_type
            FROM articles a
            JOIN article_scores s ON s.article_id = a.id
            WHERE s.composite_score > 0
              AND a.status != 'discarded'
            ORDER BY s.composite_score DESC, a.published_at DESC
        """)).mappings().all()
        
        # Filter articles by topics in Python
        for frontend_name, internal_topic in category_mapping.items():
            matching_articles = []
            for row in all_rows:
                article = dict(row)
                topics = article.get('topics', [])
                if internal_topic in topics and len(matching_articles) < 3:
                    matching_articles.append(article)
            result[frontend_name] = matching_articles
    
    return {"ok": True, "categories": result}
