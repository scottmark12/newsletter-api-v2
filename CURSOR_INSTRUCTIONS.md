# CURSOR AI INSTRUCTIONS - Add Intelligence Synthesis Endpoints

## Task: Add 4 new endpoints to `app/main.py`

**Location:** Insert these endpoints right after the `score_run` function (around line 84, right after the `@web_app.post("/score/run")` endpoint)

**Code to add:**

```python
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
```

## Steps:
1. Open `app/main.py`
2. Find line ~84 where the `score_run` function ends (right after the last line with `raise HTTPException(status_code=500, detail=str(e)) from e`)
3. Add a blank line
4. Paste the entire code block above
5. Save the file
6. Commit with message: "Add intelligence synthesis endpoints"
7. Push to GitHub

The new modules (`pdf_handler.py`, `transcript_handler.py`, `narrative_synthesis.py`) are already in the repo, and `requirements.txt` already has the dependencies.

## What these endpoints do:
- `POST /ingest/research` - Scrapes PDFs from JLL, CBRE, Cushman & Wakefield
- `POST /ingest/videos` - Fetches YouTube transcripts from construction channels
- `GET /api/brief/narrative` - Creates AI narrative brief from all sources
- `GET /api/content/recommended` - Returns top recommended video/podcast

Done! ✅
