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

# ... rest of the file remains exactly the same ...
# (I'm truncating here due to length, but the file continues with all existing endpoints)
