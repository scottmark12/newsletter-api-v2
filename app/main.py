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
                    WHERE (
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

# ---- read-side cap: max 8 per source, order by composite_score ----
@web_app.get("/api/articles_capped")
def api_articles_capped(
    limit: int = Query(200, ge=1, le=500),
    days: int = Query(7, ge=1, le=30),
):
    """
    Returns up to 8 per source, favoring highest score and recent.
    Use: GET /api/articles_capped?limit=200&days=7
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            rows = conn.execute(text("""
                WITH recent AS (
                  SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                         a.published_at, a.fetched_at, a.lang,
                         COALESCE(s.composite_score, 0) AS composite_score
                  FROM articles a
                  LEFT JOIN article_scores s ON s.article_id = a.id
                  WHERE a.published_at IS NOT NULL
                    AND a.published_at >= :cutoff
                ),
                ranked AS (
                  SELECT recent.*,
                         ROW_NUMBER() OVER (
                           PARTITION BY source
                           ORDER BY composite_score DESC, published_at DESC
                         ) rn
                  FROM recent
                )
                SELECT *
                FROM ranked
                WHERE rn <= 8
                ORDER BY composite_score DESC, published_at DESC
                LIMIT :limit
            """), {"cutoff": cutoff.isoformat(), "limit": limit}).mappings().all()
        data = [dict(r) for r in rows]
        return {"ok": True, "count": len(data), "items": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# ---- DEV-RELEVANT TOP ARTICLES (with de-dup) ----
DEV_KEYWORDS = {
    # policy / entitlements
    "zoning": 3.0, "rezoning": 3.2, "by-right": 3.0, "upzoning": 3.2,
    "permit": 2.6, "permitting": 2.6, "entitlement": 3.0,
    "inclusionary": 2.5, "tax credit": 2.8, "lihtc": 3.0, "tif": 2.5,
    "impact fee": 2.2, "rent control": 2.4, "rent stabilization": 2.4,
    "adu": 2.6, "office-to-residential": 3.4, "conversion": 2.6,

    # capital markets
    "construction loan": 3.2, "term sheet": 2.8, "mezz": 2.3, "bridge loan": 2.4,
    "bond": 2.0, "refinance": 2.2, "cap rate": 2.6, "dscr": 2.2, "lender": 2.2,
    "private equity": 2.2, "reit": 2.0, "cmbs": 2.0,

    # secular demand / asset types
    "data center": 3.6, "ai campus": 3.4, "hyperscale": 3.2,
    "industrial": 2.2, "logistics": 2.2, "life science": 2.6,
    "student housing": 2.2, "affordable housing": 3.0,

    # construction tech / methods
    "modular": 3.0, "prefab": 2.8, "offsite": 2.6, "robotic": 2.3,
    "3d printed": 3.0, "bim": 2.0, "digital twin": 2.4,

    # sustainability / codes
    "mass timber": 3.2, "embodied carbon": 2.8, "operational carbon": 2.6,
    "electrification": 2.6, "heat pump": 2.4, "leed": 2.0, "passive house": 2.6,
    "energy code": 2.6, "building code": 2.2, "stretch code": 2.4,

    # macro / supply
    "starts": 1.8, "pipeline": 1.8, "vacancy": 1.8, "absorption": 1.8,
    "construction costs": 2.4, "materials cost": 2.2, "labor shortage": 2.2,
}

SOURCE_WEIGHTS = {
    # Tier 1 - Premium industry sources
    "enr.com": 1.0,             # Engineering News-Record - top construction industry source
    "construction.com": 0.9,    # Dodge Data & Analytics
    "commercialobserver.com": 0.8,  # Commercial Observer
    "bisnow.com": 0.7,          # Bisnow commercial real estate
    "urbanland.uli.org": 0.8,  # Urban Land Institute
    
    # Tier 2 - Quality news sources
    "bloomberg.com": 0.6, "citylab.com": 0.4,
    "brookings.edu": 0.6, "urban.org": 0.6,
    "therealdeal.com": 0.5,     # Upgraded from 0.35
    "constructiondive.com": 0.4, # Upgraded from 0.3
    
    # Tier 3 - Research firms and data providers
    "cbre.com": 0.3, "jll.com": 0.3, "cushmanwakefield.com": 0.3,
    "rmi.org": 0.4,
    "redfin.com": 0.2, "zillow.com": 0.2,
    "smartcitiesdive.com": 0.2,
    
    # Downweighted - design-only sources
    "archdaily.com": -0.25,
    "dezeen.com": -0.1,
}

HIGH_SIGNAL_DOMAINS = {
    # Tier 1 - Always include regardless of keyword score
    "enr.com", "construction.com", "commercialobserver.com", 
    "bisnow.com", "urbanland.uli.org",
    # Tier 2 - High quality sources
    "bloomberg.com", "citylab.com", "brookings.edu", "urban.org",
    "constructiondive.com", "smartcitiesdive.com", "therealdeal.com",
    "cbre.com", "jll.com", "cushmanwakefield.com",
    "redfin.com", "zillow.com", "apartmentlist.com", "realpage.com",
}

STOPWORDS = {
    "the","a","an","and","or","of","to","in","for","on","with","at","by","from",
    "as","new","how","why","what","is","are","be","this","that","it","its",
    "2023","2024","2025"
}

MIN_KW_SCORE = 2.0          # drop low-signal posts unless from HIGH_SIGNAL_DOMAINS
PER_DOMAIN_CAP = 3          # <= per domain for /top
RECENCY_HALF_LIFE_H = 24.0  # recency multiplier half-life

def _host(url: str) -> str:
    try:
        return urlparse(url).netloc.lower().replace("www.", "")
    except Exception:
        return ""

def _domain_weight(url: str) -> float:
    return SOURCE_WEIGHTS.get(_host(url), 0.0)

def _parse_dt_any(dt_val):
    if isinstance(dt_val, datetime):
        return dt_val if dt_val.tzinfo else dt_val.replace(tzinfo=timezone.utc)
    if isinstance(dt_val, str):
        try:
            return datetime.fromisoformat(dt_val.replace("Z", "+00:00"))
        except Exception:
            try:
                from dateutil import parser as _dp
                return _dp.parse(dt_val)
            except Exception:
                return None
    return None

def _recency_mult(published_at, fetched_at, half_life_hours: float = RECENCY_HALF_LIFE_H) -> float:
    dt = _parse_dt_any(published_at) or _parse_dt_any(fetched_at)
    if not dt:
        return 0.8
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=timezone.utc)
    hours = max((datetime.now(timezone.utc) - dt).total_seconds() / 3600.0, 0.0)
    return 0.5 ** (hours / half_life_hours)

def _kw_score(text: str) -> float:
    if not text:
        return 0.0
    t = text.lower()
    score = 0.0
    for kw, w in DEV_KEYWORDS.items():
        cnt = t.count(kw)
        if cnt:
            score += w * min(cnt, 3)
    return score

def _len_bonus(text: str) -> float:
    words = max(0, len((text or "").split()))
    return min(words / 900.0, 1.0) * 0.6  # up to +0.6

def _dev_relevance(row: dict) -> tuple[float, float]:
    """
    Returns (score, kw_score) so we can threshold by keywords before ranking.
    """
    base_text = " ".join(
        x for x in [row.get("title"), row.get("summary_raw"), row.get("content")] if x
    )
    kw = _kw_score(base_text)
    rec = _recency_mult(row.get("published_at"), row.get("fetched_at"))
    dom = _domain_weight(row.get("url", ""))
    ln  = _len_bonus(row.get("content", ""))
    score = (kw + dom + ln) * (1.0 + 2.0 * rec)
    return score, kw

# --------- de-dup helpers ----------
def _title_tokens(title: str) -> set[str]:
    if not title:
        return set()
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s\-]", " ", t)
    toks = [w for w in t.split() if w not in STOPWORDS and len(w) >= 3 and not w.isdigit()]
    return set(toks)

def _is_near_duplicate(toks_a: set[str], toks_b: set[str], thr: float = 0.62) -> bool:
    if not toks_a or not toks_b:
        return False
    inter = len(toks_a & toks_b)
    if inter == 0:
        return False
    union = len(toks_a | toks_b)
    j = inter / union
    return j >= thr

def _dedupe_by_title(scored_rows: list[dict]) -> list[dict]:
    """Rows must already be sorted DESC by score. Keeps first in each cluster."""
    kept = []
    clusters = []  # token sets of kept titles
    for d in scored_rows:
        toks = _title_tokens(d.get("title", ""))
        dup = any(_is_near_duplicate(toks, c) for c in clusters)
        if dup:
            continue
        kept.append(d)
        clusters.append(toks)
    return kept

def _limit_per_domain(items: list[dict], per_domain: int) -> list[dict]:
    counts: dict[str, int] = {}
    out = []
    for d in items:
        h = _host(d.get("url", ""))
        c = counts.get(h, 0)
        if c >= per_domain:
            continue
        counts[h] = c + 1
        out.append(d)
    return out

@web_app.get("/api/articles/top")
def api_articles_top(
    limit: int = Query(20, ge=1, le=50),
    since_hours: int = Query(24, ge=6, le=168),
):
    """
    Top developer-relevant, de-duplicated stories.
    - Drops low-signal posts (unless the domain is high-signal)
    - Downranks design-only sources
    - De-duplicates similar titles
    - Caps to <= PER_DOMAIN_CAP per domain
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=since_hours)
    try:
        engine = _get_engine()
        with engine.connect() as conn:
            rows = conn.execute(
                text("""
                    SELECT id, url, source, title, summary_raw, content,
                           published_at, fetched_at, lang
                    FROM articles
                    WHERE lang = 'en'
                      AND (
                        (published_at IS NOT NULL AND published_at >= :cutoff)
                        OR
                        (published_at IS NULL AND fetched_at >= :cutoff)
                      )
                    ORDER BY COALESCE(published_at, fetched_at) DESC
                    LIMIT 500
                """),
                {"cutoff": cutoff.isoformat()},
            ).mappings().all()

        # score + filter
        scored = []
        for r in rows:
            d = dict(r)
            score, kw = _dev_relevance(d)

            host = urlparse(d.get("url", "")).netloc.replace("www.", "").lower()
            # Filter out very low-signal items unless they come from a high-signal domain
            if kw < MIN_KW_SCORE and host not in HIGH_SIGNAL_DOMAINS:
                continue

            d["score"] = round(float(score), 3)
            d["kw_score"] = round(float(kw), 3)
            # lightweight summary for the UI
            if d.get("summary_raw"):
                summary = d["summary_raw"]
            else:
                summary = " ".join((d.get("content") or "").split())[:450]
            d["summary"] = summary
            scored.append(d)

        scored.sort(key=lambda x: x["score"], reverse=True)

        # de-dup by title similarity, then cap per domain
        deduped = _dedupe_by_title(scored)
        capped = _limit_per_domain(deduped, PER_DOMAIN_CAP)
        top = capped[:limit]

        return {"ok": True, "count": len(top), "items": top}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# ---- Newsletter set: top N per section (innovation, market_news, insights, unique_developments)
@web_app.get("/api/newsletter")
def api_newsletter(
    days: int = Query(7, ge=1, le=30),
    per_section: int = Query(5, ge=1, le=10),
):
    """
    Returns up to `per_section` articles for each section:
    innovation, market_news, insights, unique_developments.
    Enforces a per-domain cap (2) inside each section.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    engine = _get_engine()
    sections = ["innovation", "market_news", "insights", "unique_developments"]

    def get_section(cat: str) -> List[Dict[str, Any]]:
        with engine.connect() as conn:
            rows = conn.execute(text("""
                WITH recent AS (
                  SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                         a.published_at, a.fetched_at, a.lang,
                         COALESCE(s.composite_score, 0) AS composite_score
                  FROM articles a
                  JOIN article_scores s ON s.article_id = a.id
                  WHERE a.published_at IS NOT NULL
                    AND a.published_at >= :cutoff
                    AND :cat = ANY(s.topics)
                    AND a.lang = 'en'
                ),
                ranked AS (
                  SELECT recent.*,
                         ROW_NUMBER() OVER (
                           PARTITION BY source
                           ORDER BY composite_score DESC, published_at DESC
                         ) rn
                  FROM recent
                )
                SELECT *
                FROM ranked
                WHERE rn <= 2                    -- per-domain cap inside this section
                ORDER BY composite_score DESC, published_at DESC
                LIMIT :lim
            """), {"cutoff": cutoff.isoformat(), "cat": cat, "lim": per_section}).mappings().all()
            return [dict(r) for r in rows]

    out = {sec: get_section(sec) for sec in sections}
    return {"ok": True, "sections": out}

# ---- V2 API ENDPOINTS ----

@web_app.get("/api/brief/daily")
def api_brief_daily():
    """
    V2 Daily Brief: What moved + Top 3 stories + Quick hits (optional)
    Format: Chill CEO style with tight headlines and takeaways
    """
    try:
        engine = _get_engine()
        
        # Get macro meters (placeholder - integrate with real data sources)
        macro_meters = _get_macro_meters()
        
        # Get top 3 diverse stories from last 24 hours
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
        
        with engine.connect() as conn:
            # Get top scored articles with diversity
            rows = conn.execute(text("""
                WITH scored AS (
                  SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                         a.published_at, a.fetched_at, a.lang,
                         COALESCE(s.composite_score, 0) AS composite_score,
                         s.topics, s.summary2, s.why1, s.project_stage, s.needs_fact_check
                  FROM articles a
                  JOIN article_scores s ON s.article_id = a.id
                  WHERE a.published_at IS NOT NULL
                    AND a.published_at >= :cutoff
                    AND a.lang = 'en'
                    AND s.composite_score > 0
                ),
                diverse AS (
                  SELECT scored.*,
                         ROW_NUMBER() OVER (
                           PARTITION BY source
                           ORDER BY composite_score DESC, published_at DESC
                         ) rn
                  FROM scored
                )
                SELECT *
                FROM diverse
                WHERE rn <= 2  -- max 2 per source for diversity
                ORDER BY composite_score DESC, published_at DESC
                LIMIT 15
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Format top 3 with CEO voice
        top_stories = []
        quick_hits = []
        
        for i, row in enumerate(rows):
            story = _format_ceo_story(dict(row))
            if i < 3:
                top_stories.append(story)
            elif i < 8:  # Additional quick hits
                quick_hits.append(_format_quick_hit(dict(row)))
        
        return {
            "ok": True,
            "type": "daily_brief",
            "date": datetime.now(timezone.utc).date().isoformat(),
            "what_moved": macro_meters,
            "top_stories": top_stories,
            "quick_hits": quick_hits if len(quick_hits) > 0 else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@web_app.get("/api/brief/weekly")
def api_brief_weekly():
    """
    V2 Weekly Brief: Best podcast + Best video aligned to the 4 buckets
    """
    try:
        engine = _get_engine()
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        
        with engine.connect() as conn:
            # Get media content (podcasts/videos) from last week
            rows = conn.execute(text("""
                WITH media AS (
                  SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                         a.published_at, a.fetched_at, a.lang,
                         COALESCE(s.composite_score, 0) AS composite_score,
                         s.topics, s.summary2, s.why1, s.media_type
                  FROM articles a
                  JOIN article_scores s ON s.article_id = a.id
                  WHERE a.published_at IS NOT NULL
                    AND a.published_at >= :cutoff
                    AND a.lang = 'en'
                    AND s.media_type IN ('podcast', 'video')
                    AND s.composite_score > 0
                )
                SELECT *
                FROM media
                ORDER BY composite_score DESC, published_at DESC
                LIMIT 20
            """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Separate and rank by type
        podcasts = [dict(r) for r in rows if dict(r).get('media_type') == 'podcast']
        videos = [dict(r) for r in rows if dict(r).get('media_type') == 'video']
        
        best_podcast = _format_media_pick(podcasts[0]) if podcasts else None
        best_video = _format_media_pick(videos[0]) if videos else None
        
        # Fallback: get video from YouTube handler if no videos found in articles
        if not best_video:
            try:
                from .youtube_handler import get_video_of_week
                video_of_week = get_video_of_week(days=7)
                if video_of_week:
                    best_video = {
                        "title": video_of_week["title"],
                        "url": video_of_week["url"],
                        "source": video_of_week["source"],
                        "summary": video_of_week["summary"],
                        "why_relevant": video_of_week["why_relevant"],
                        "media_type": "video",
                        "topics": video_of_week["topics"]
                    }
            except ImportError:
                pass
        
        return {
            "ok": True,
            "type": "weekly_brief", 
            "week_ending": datetime.now(timezone.utc).date().isoformat(),
            "best_podcast": best_podcast,
            "best_video": best_video
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

@web_app.get("/api/feed/{bucket}")
def api_feed_bucket(
    bucket: str,
    limit: int = Query(20, ge=1, le=100),
    days: int = Query(7, ge=1, le=30)
):
    """
    V2 Feed by Bucket: Get articles for a specific classification bucket
    Buckets: tech_innovation, market_insight, construction_insight, unique_development
    """
    # Map v2 bucket names to current internal names
    bucket_mapping = {
        "tech_innovation": "innovation",
        "market_insight": "market_news", 
        "construction_insight": "insights",
        "unique_development": "unique_developments"
    }
    
    internal_bucket = bucket_mapping.get(bucket)
    if not internal_bucket:
        raise HTTPException(status_code=400, detail=f"Invalid bucket: {bucket}")
    
    try:
        engine = _get_engine()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        with engine.connect() as conn:
            rows = conn.execute(text("""
                WITH bucket_articles AS (
                  SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                         a.published_at, a.fetched_at, a.lang,
                         COALESCE(s.composite_score, 0) AS composite_score,
                         s.topics, s.summary2, s.why1, s.project_stage, s.needs_fact_check
                  FROM articles a
                  JOIN article_scores s ON s.article_id = a.id
                  WHERE a.published_at IS NOT NULL
                    AND a.published_at >= :cutoff
                    AND :bucket = ANY(s.topics)
                    AND a.lang = 'en'
                    AND s.composite_score > 0
                )
                SELECT *
                FROM bucket_articles
                ORDER BY composite_score DESC, published_at DESC
                LIMIT :limit
            """), {
                "cutoff": cutoff.isoformat(), 
                "bucket": internal_bucket, 
                "limit": limit
            }).mappings().all()
        
        articles = [_format_feed_article(dict(r)) for r in rows]
        
        return {
            "ok": True,
            "bucket": bucket,
            "count": len(articles),
            "articles": articles
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

# ---- V2 MACRO METRICS ENDPOINT ----

@web_app.get("/api/metrics/macro")
def api_macro_metrics():
    """Get detailed macro economic indicators"""
    try:
        from .macro_data import get_detailed_metrics
        return {"ok": True, "metrics": get_detailed_metrics()}
    except ImportError:
        return {"ok": False, "error": "Macro data module not available"}

@web_app.post("/api/cse/backfill")
def api_cse_backfill(target_per_bucket: int = Query(5, ge=1, le=10)):
    """Run CSE backfill to supplement RSS content when buckets are low"""
    try:
        from .cse_backfill import run_cse_backfill
        result = run_cse_backfill(target_per_bucket=target_per_bucket)
        return result
    except ImportError:
        return {"ok": False, "error": "CSE backfill module not available"}

@web_app.get("/api/cse/suggestions/{bucket}")
def api_cse_suggestions(bucket: str, limit: int = Query(5, ge=1, le=10)):
    """Get CSE search suggestions for a specific bucket"""
    try:
        from .cse_backfill import get_cse_suggestions
        results = get_cse_suggestions(bucket, limit=limit)
        return {"ok": True, "bucket": bucket, "suggestions": results}
    except ImportError:
        return {"ok": False, "error": "CSE backfill module not available"}

@web_app.get("/api/cse/quota")
def api_cse_quota():
    """Check CSE quota status"""
    try:
        from .cse_client import get_quota_status
        return {"ok": True, "quota": get_quota_status()}
    except ImportError:
        return {"ok": False, "error": "CSE client not available"}

# ---- V2 YOUTUBE VIDEO ENDPOINTS ----

@web_app.get("/api/video/week")
def api_video_of_week():
    """Get the highest-scored video from the last week"""
    try:
        from .youtube_handler import get_video_of_week
        video = get_video_of_week(days=7)
        if video:
            return {"ok": True, "video_of_week": video}
        else:
            return {"ok": True, "video_of_week": None, "message": "No videos found this week"}
    except ImportError:
        return {"ok": False, "error": "YouTube handler not available"}

@web_app.get("/api/videos/feed")
def api_videos_feed(
    limit: int = Query(20, ge=1, le=50),
    days: int = Query(30, ge=7, le=90)
):
    """Get browsable feed of recent construction/real estate videos"""
    try:
        from .youtube_handler import get_video_feed
        videos = get_video_feed(limit=limit, days=days)
        return {
            "ok": True,
            "count": len(videos),
            "videos": videos,
            "period_days": days
        }
    except ImportError:
        return {"ok": False, "error": "YouTube handler not available"}

@web_app.get("/api/channels/youtube")
def api_youtube_channels():
    """Get list of curated YouTube channels"""
    try:
        from .youtube_handler import load_youtube_channels
        channels = load_youtube_channels()
        return {"ok": True, "channels": channels}
    except ImportError:
        return {"ok": False, "error": "YouTube handler not available"}

# ---- V2 HELPER FUNCTIONS ----

def _get_macro_meters() -> str:
    """Get macro indicators from real data sources"""
    try:
        from .macro_data import get_macro_indicators
        return get_macro_indicators()
    except ImportError:
        # Fallback if macro_data module not available
        return "10Y +6 bps | Dodge Momentum +2.1% MoM | NAHB −2"

def _format_ceo_story(article: dict) -> dict:
    """Format article in 'Chill CEO' style"""
    try:
        from .ceo_voice import generate_ceo_summary
        ceo_format = generate_ceo_summary(article)
        
        return {
            "id": article.get("id"),
            "url": article.get("url"),
            "source": article.get("source"),
            "headline": ceo_format["headline"],
            "why_it_matters": ceo_format["why_it_matters"],
            "ceo_takeaway": ceo_format["ceo_takeaway"],
            "link": article.get("url"),
            "score": round(float(article.get("composite_score", 0)), 2),
            "topics": article.get("topics", []),
            "project_stage": article.get("project_stage"),
            "needs_fact_check": article.get("needs_fact_check", False)
        }
    except ImportError:
        # Fallback to basic formatting
        return {
            "id": article.get("id"),
            "url": article.get("url"),
            "source": article.get("source"),
            "headline": article.get("title", "")[:100] + ("..." if len(article.get("title", "")) > 100 else ""),
            "why_it_matters": [
                article.get("why1", "Market signal for construction activity")[:200],
                "Timing opportunity for strategic positioning"[:200]
            ],
            "ceo_takeaway": _generate_ceo_takeaway(article),
            "link": article.get("url"),
            "score": round(float(article.get("composite_score", 0)), 2),
            "topics": article.get("topics", []),
            "project_stage": article.get("project_stage"),
            "needs_fact_check": article.get("needs_fact_check", False)
        }

def _format_quick_hit(article: dict) -> dict:
    """Format article as one-liner quick hit"""
    try:
        from .ceo_voice import format_quick_hit
        headline = format_quick_hit(article.get("title", ""), article.get("source", ""))
        return {
            "headline": headline,
            "url": article.get("url"),
            "source": article.get("source")
        }
    except ImportError:
        # Fallback formatting
        return {
            "headline": article.get("title", "")[:80] + ("..." if len(article.get("title", "")) > 80 else ""),
            "url": article.get("url"),
            "source": article.get("source")
        }

def _format_media_pick(article: dict) -> dict:
    """Format podcast/video pick"""
    return {
        "title": article.get("title"),
        "url": article.get("url"), 
        "source": article.get("source"),
        "summary": article.get("summary2", article.get("summary_raw", ""))[:300],
        "why_relevant": article.get("why1", "Insights for construction/development strategy"),
        "media_type": article.get("media_type"),
        "topics": article.get("topics", [])
    }

def _format_feed_article(article: dict) -> dict:
    """Format article for feed endpoint"""
    return {
        "id": article.get("id"),
        "url": article.get("url"),
        "source": article.get("source"), 
        "title": article.get("title"),
        "summary": article.get("summary2", article.get("summary_raw", "")),
        "published_at": article.get("published_at"),
        "score": round(float(article.get("composite_score", 0)), 2),
        "topics": article.get("topics", []),
        "project_stage": article.get("project_stage"),
        "needs_fact_check": article.get("needs_fact_check", False)
    }

def _generate_ceo_takeaway(article: dict) -> str:
    """Generate CEO-focused takeaway line"""
    topics = article.get("topics", [])
    
    if "market_news" in topics:
        return "Monitor for cost/timing impact on active projects"
    elif "innovation" in topics:
        return "Evaluate for competitive advantage in next development"
    elif "unique_developments" in topics:
        return "Study approach for replication opportunities"
    elif "insights" in topics:
        return "Consider policy/regulatory implications for pipeline"
    else:
        return "Assess strategic relevance for portfolio positioning"

# ---- (Optional) one-time migration if you previously used "trends" tag ----
# @web_app.post("/admin/migrate_trends_to_insights_once")
# def migrate_trends_to_insights_once():
#     sql = """
#     UPDATE article_scores
#     SET topics = (
#       SELECT ARRAY(
#         SELECT DISTINCT CASE WHEN x = 'trends' THEN 'insights' ELSE x END
#         FROM unnest(COALESCE(topics, ARRAY[]::text[])) AS x
#       )
#     )
#     WHERE 'trends' = ANY(topics);
#     """
#     try:
#         engine = _get_engine()
#         with engine.begin() as conn:
#             conn.execute(text(sql))
#         return {"ok": True, "message": "migrated 'trends' -> 'insights'"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
