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

# # from .db import init_db  # Commented out for V3 compatibility  # Removed to prevent startup database initialization
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
# Removed startup event handler to prevent database initialization during startup

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

@web_app.post("/score/run-v2")
def score_run_v2(limit: int = Query(50, ge=1, le=500)):
    """Run the enhanced thematic scoring system v2"""
    try:
        from . import scoring_v2
        result = scoring_v2.run_v2(limit=limit)
        return result
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
    # Use direct database URL from environment
    import os
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable not set")
    
    # Ensure we use the correct PostgreSQL driver
    if database_url.startswith("postgresql://"):
        # Use psycopg (newer driver) if available, fallback to psycopg2
        try:
            import psycopg
            database_url = database_url.replace("postgresql://", "postgresql+psycopg://")
        except ImportError:
            try:
                import psycopg2
                database_url = database_url.replace("postgresql://", "postgresql+psycopg2://")
            except ImportError:
                pass  # Use default driver
    
    return create_engine(database_url)

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
        # Exclude the top story to avoid duplicates
        with db_engine.connect() as conn:
            cutting_edge_projects_rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND 'innovation' = ANY(s.topics)
                  AND s.composite_score > 50
                  AND a.id != :exclude_top_story_id
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 3
            """), {
                "cutoff": cutoff.isoformat(),
                "exclude_top_story_id": top_story_row['id'] if top_story_row else None
            }).mappings().all()
        
        # Collect used article IDs to prevent duplicates
        used_article_ids = {top_story_row['id']} if top_story_row else set()
        used_article_ids.update(row['id'] for row in cutting_edge_projects_rows)
        
        # Get cutting edge development (2-3 major infrastructure/city-changing stories)
        # Exclude articles already used in other sections
        with db_engine.connect() as conn:
            cutting_edge_development_rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND 'unique_developments' = ANY(s.topics)
                  AND s.composite_score > 60
                  AND a.id NOT IN (SELECT unnest(:exclude_ids))
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 3
            """), {
                "cutoff": cutoff.isoformat(),
                "exclude_ids": list(used_article_ids) if used_article_ids else []
            }).mappings().all()
        
        # Update used article IDs
        used_article_ids.update(row['id'] for row in cutting_edge_development_rows)
        
        # Get market movers (3-4 significant market developments)
        # Exclude articles already used in other sections
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
                  AND a.id NOT IN (SELECT unnest(:exclude_ids))
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 4
            """), {
                "cutoff": cutoff.isoformat(),
                "exclude_ids": list(used_article_ids) if used_article_ids else []
            }).mappings().all()
        
        # Update used article IDs
        used_article_ids.update(row['id'] for row in market_rows)
        
        # Get insights & analysis (2-3 deep-dive pieces)
        # Exclude articles already used in other sections
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
                  AND a.id NOT IN (SELECT unnest(:exclude_ids))
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 3
            """), {
                "cutoff": cutoff.isoformat(),
                "exclude_ids": list(used_article_ids) if used_article_ids else []
            }).mappings().all()
        
        # Update used article IDs
        used_article_ids.update(row['id'] for row in insights_rows)
        
        # Get quick hits (top 5 highest scores excluding all previously used articles)
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
                  AND a.id NOT IN (SELECT unnest(:exclude_ids))  -- Exclude all previously used articles
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 5
            """), {
                "cutoff": cutoff.isoformat(),
                "exclude_ids": list(used_article_ids) if used_article_ids else []
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
    Returns the top 3 articles for each category using priority-based categorization.
    Each article appears in only its highest-priority category.
    """
    db_engine = _get_engine()
    
    # Define category priorities (higher number = higher priority)
    category_priorities = {
        "insights": 4,           # Highest priority - deep analysis
        "cutting_edge_projects": 3,  # Innovation and new tech
        "cutting_edge_development": 2,  # Major infrastructure 
        "market_news": 1         # Lowest priority - general news
    }
    
    # Map frontend names to internal topics
    category_mapping = {
        "market_news": "market_news",
        "cutting_edge_projects": "innovation",
        "cutting_edge_development": "unique_developments",  
        "insights": "insights"
    }
    
    result = {cat: [] for cat in category_mapping.keys()}
    
    with db_engine.connect() as conn:
        # Get ALL articles with their topics
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
        
        # Assign each article to its highest-priority category
        for row in all_rows:
            article = dict(row)
            topics = article.get('topics', [])
            
            # Find the highest-priority category this article qualifies for
            best_category = None
            best_priority = 0
            
            for frontend_name, internal_topic in category_mapping.items():
                if internal_topic in topics:
                    priority = category_priorities[frontend_name]
                    if priority > best_priority:
                        best_priority = priority
                        best_category = frontend_name
            
            # Add to the best category if we found one and it's not full
            if best_category and len(result[best_category]) < 3:
                result[best_category].append(article)
    
    return {"ok": True, "categories": result}

# ---- INDIVIDUAL FEED ENDPOINTS FOR LOVABLE ----
@web_app.get("/api/feed/{feed_type}")
def api_feed_by_type(feed_type: str, days: int = Query(7, ge=1, le=30)):
    """
    Returns articles for a specific feed type (market_news, cutting_edge_projects, etc.)
    This endpoint is designed for Lovable frontend integration.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    # Map feed types to internal topic names
    feed_mapping = {
        "market_news": "market_news",
        "cutting_edge_projects": "innovation", 
        "cutting_edge_development": "unique_developments",
        "insights": "insights"
    }
    
    if feed_type not in feed_mapping:
        raise HTTPException(status_code=404, detail=f"Feed type '{feed_type}' not found")
    
    internal_topic = feed_mapping[feed_type]
    
    try:
        db_engine = _get_engine()
        
        # Get articles for this specific topic
        with db_engine.connect() as conn:
            rows = conn.execute(text("""
                SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.published_at,
                       s.composite_score, s.topics, s.geography, s.summary2, s.why1,
                       s.project_stage, s.needs_fact_check, s.media_type
                FROM articles a
                JOIN article_scores s ON s.article_id = a.id
                WHERE a.status != 'discarded'
                  AND s.composite_score > 0
                  AND a.published_at >= :cutoff
                  AND :topic = ANY(s.topics)
                ORDER BY s.composite_score DESC, a.published_at DESC
                LIMIT 20
            """), {
                "cutoff": cutoff.isoformat(),
                "topic": internal_topic
            }).mappings().all()
        
        articles = [dict(row) for row in rows]
        
        # Add feed metadata
        feed_titles = {
            "market_news": "Market News",
            "cutting_edge_projects": "Cutting Edge Projects", 
            "cutting_edge_development": "Cutting Edge Development",
            "insights": "Insights"
        }
        
        feed_descriptions = {
            "market_news": "Today's events affecting construction and real estate",
            "cutting_edge_projects": "Architectural innovation and entrepreneurial building science",
            "cutting_edge_development": "Major infrastructure projects that change cities forever", 
            "insights": "Market intelligence and opportunity analysis"
        }
        
        return {
            "ok": True,
            "feed_type": feed_type,
            "title": feed_titles.get(feed_type, feed_type),
            "description": feed_descriptions.get(feed_type, ""),
            "count": len(articles),
            "articles": articles,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# V3 Theme-based endpoints - added directly to avoid import issues

@web_app.get("/api/v3/opportunities")
def get_opportunities(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0)
):
    """Get transformation stories, scaling examples, and wealth-building opportunities"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    
    try:
        db_engine = _get_engine()
        
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
        
        with db_engine.connect() as conn:
            rows = conn.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
        
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
        db_engine = _get_engine()
        
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
        
        with db_engine.connect() as conn:
            rows = conn.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
        
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
        db_engine = _get_engine()
        
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
        
        with db_engine.connect() as conn:
            rows = conn.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
        
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
        db_engine = _get_engine()
        
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
        
        with db_engine.connect() as conn:
            rows = conn.execute(query, {
                "cutoff": cutoff.isoformat(),
                "min_score": min_score,
                "limit": limit
            }).fetchall()
            
            articles = [dict(row._mapping) for row in rows]
        
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
        db_engine = _get_engine()
        
        with db_engine.connect() as conn:
            # Check database connection
            conn.execute(text("SELECT 1"))
            
            # Get basic stats
                   stats_query = text("""
                       SELECT 
                           COUNT(*) as total_articles,
                           COUNT(CASE WHEN s.article_id IS NOT NULL THEN 1 END) as scored_articles,
                           AVG(s.composite_score) as avg_score
                       FROM articles a
                       LEFT JOIN article_scores s ON s.article_id = a.id
                   """)
            
            stats = conn.execute(stats_query).fetchone()
        
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
