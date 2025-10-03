# Intelligence Synthesis System - Implementation Guide

## Overview
This system transforms the newsletter API from a news aggregator into an intelligence synthesis platform with narrative and point of view.

## New Modules Added

### 1. `app/pdf_handler.py`
**Purpose**: Downloads and extracts insights from CRE research firm PDFs (JLL, CBRE, Cushman & Wakefield)

**Key Functions**:
- `extract_text_from_pdf(pdf_content)` - Extracts text using pdfplumber or PyPDF2
- `crawl_research_firm(firm_domain, limit)` - Crawls a firm's insights page for PDFs
- `run(limit)` - Main entry point, ingests research reports into database

**Usage**:
```python
from app import pdf_handler
result = pdf_handler.run(limit=10)
# {"ok": True, "reports_ingested": 5}
```

### 2. `app/transcript_handler.py`
**Purpose**: Fetches YouTube video transcripts from construction/CRE channels

**Key Functions**:
- `get_transcript(video_id)` - Gets transcript using youtube-transcript-api
- `fetch_channel_videos(channel_id, max_results)` - Gets recent videos from a channel
- `is_relevant_video(title, summary, transcript)` - Filters for construction/CRE relevance
- `run(limit)` - Main entry point, ingests video transcripts into database

**Channels Monitored**:
- The B1M (construction megaprojects)
- Practical Engineering (technical deep dives)
- Building Better (sustainable construction)

**Usage**:
```python
from app import transcript_handler
result = transcript_handler.run(limit=20)
# {"ok": True, "videos_ingested": 15}
```

### 3. `app/narrative_synthesis.py`
**Purpose**: Weaves together news, research reports, and video/podcast content into coherent narrative briefs

**Key Functions**:
- `synthesize_daily_narrative(days_back)` - Creates narrative brief using LLM
- `get_recommended_content(content_type)` - Gets top recommended video/podcast
- `run()` - Main entry point for synthesis

**How It Works**:
1. Gathers top news articles (score > 80)
2. Pulls in research reports from major firms
3. Includes relevant video/podcast transcripts
4. Uses LLM to synthesize everything into a coherent narrative with:
   - Punchy headline
   - 2-3 paragraph story connecting the dots
   - Recommended video/podcast
   - Bottom line action

**Usage**:
```python
from app import narrative_synthesis
result = narrative_synthesis.run()
# Returns synthesized brief with narrative
```

## New API Endpoints to Add

Add these to `app/main.py`:

```python
# ---- INTELLIGENCE SYNTHESIS ENDPOINTS ----

@web_app.post("/ingest/research")
def ingest_research(limit: int = Query(10, ge=1, le=50)):
    """Ingest research reports from major CRE firms"""
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
    """Get AI-synthesized narrative brief weaving together news, research, and media"""
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
            return {"ok": True, "recommended": None, "message": "No content found"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Workflow

### Daily Intelligence Pipeline:

1. **Morning Crawl** (existing):
   ```bash
   POST /ingest/start?limit=100
   ```

2. **Research Supplement** (new):
   ```bash
   POST /ingest/research?limit=10
   ```

3. **Video Content** (new):
   ```bash
   POST /ingest/videos?limit=20
   ```

4. **Score Everything** (existing):
   ```bash
   POST /score/run?limit=150
   ```

5. **Generate Narrative** (new):
   ```bash
   GET /api/brief/narrative
   ```

## Frontend Integration

### Homepage with Narrative Brief:
```javascript
// Get the synthesized narrative brief
const narrativeBrief = await fetch('https://newsletter-api-v2.onrender.com/api/brief/narrative');
const data = await narrativeBrief.json();

// Display narrative with:
// - data.synthesis (the full LLM-generated brief)
// - data.sources_used (how many sources were synthesized)

// Get recommended content
const recommended = await fetch('https://newsletter-api-v2.onrender.com/api/content/recommended?content_type=video');
const videoData = await recommended.json();

// Display: videoData.recommended with title, url, why_relevant
```

## Dependencies Added

```txt
PyPDF2==3.0.1              # PDF text extraction
pdfplumber==0.11.0         # Better PDF extraction (tables, layout)
youtube-transcript-api==0.6.1  # YouTube transcript fetching
```

## Key Benefits

1. **Deep Intelligence**: Not just news headlines - actual insights from JLL, CBRE reports
2. **Multimedia Context**: YouTube videos provide visual/technical context
3. **Narrative Synthesis**: LLM weaves everything into coherent story with POV
4. **Actionable**: Every brief has specific "what this means" and "what to do"
5. **Recommended Content**: Suggested video/podcast that complements the brief

## Next Steps

1. Add the new endpoints to `main.py`
2. Deploy to Render (will install new dependencies automatically)
3. Test the new endpoints:
   - `/ingest/research` - Should find and ingest PDFs
   - `/ingest/videos` - Should fetch video transcripts
   - `/api/brief/narrative` - Should return synthesized brief

4. Schedule daily automation:
   - Run research + video ingestion once daily
   - Generate narrative brief after scoring

## Monitoring

Check logs for:
- `[pdf]` - PDF download/extraction progress
- `[transcript]` - Video transcript fetching
- `[synthesis]` - LLM synthesis calls

Monitor database for:
- Research reports with topics: `['research_report', 'market_insights', 'institutional_research']`
- Video content with topics: `['video_content', 'construction_tech']`
