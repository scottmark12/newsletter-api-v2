from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal

# -------- Category keyword sets --------
# We tag each article with one or more of these:
# "innovation", "market_news", "insights", "unique_developments"
KWS = {
    "innovation": {
        "ai campus","ai factory","hyperscale","data center","robotic","robotics",
        "3d printed","3d printing","bim","digital twin","prefab","modular",
        "offsite","automation","computer vision","generative ai","llm","r&d",
        "breakthrough","pilot program","prototype","patent"
    },
    "market_news": {
        "refinance","bond","cmbs","term sheet","bridge loan","construction loan",
        "cap rate","dscr","occupancy","vacancy","absorption","pipeline","starts",
        "transaction","deal","acquisition","raises","funding","yoy","qoq",
        "rent growth","foreclosure"
    },
    "insights": {   # <— renamed from "trends"
        "mass timber","electrification","heat pump","embodied carbon",
        "operational carbon","leed","passive house","energy code","stretch code",
        "upzoning","by-right","inclusionary","office-to-residential","conversion",
        "student housing","life science","industrial","logistics","macro","headwinds"
    },
    "unique_developments": {
        "groundbreaking","opens","topped out","topping out","approved",
        "wins approval","entitled","rezoned","permits issued","milestone",
        "first-of-its-kind","world’s first","largest","record-breaking"
    },
}

def _tag_categories(text_blob: str) -> list[str]:
    t = (text_blob or "").lower()
    tags = []
    for cat, words in KWS.items():
        if any(w in t for w in words):
            tags.append(cat)
    # de-duplicate while preserving order
    seen = set()
    out = []
    for x in tags:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# If you later wire LLM scoring, import here and merge into composite_score
# from .llm import score_article_with_llm

def fetch_new_articles(limit: int = 50) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT id, title, summary_raw, content, published_at, fetched_at
                FROM articles
                WHERE status = 'new'
                ORDER BY fetched_at DESC NULLS LAST
                LIMIT :lim
            """),
            {"lim": limit}
        ).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()

def save_scores(article_id: str, scores: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        import json
        
        # For PostgreSQL, we can use arrays directly
        topics_array = scores.get("topics", [])
        geography_array = scores.get("geography", [])
        
        db.execute(text("""
            INSERT INTO article_scores (
                article_id, rel_building_practices, rel_market, rel_design_business,
                importance_multiplier, freshness_bonus, composite_score, topics,
                geography, macro_flag, summary2, why1, project_stage, needs_fact_check, media_type
            )
            VALUES (
                :article_id, :rbp, :rm, :rdb, :imp, :fresh, :comp, :topics,
                :geo, :macro, :summary2, :why1, :project_stage, :needs_fact_check, :media_type
            )
            ON CONFLICT (article_id) DO UPDATE SET
                rel_building_practices = EXCLUDED.rel_building_practices,
                rel_market = EXCLUDED.rel_market,
                rel_design_business = EXCLUDED.rel_design_business,
                importance_multiplier = EXCLUDED.importance_multiplier,
                freshness_bonus = EXCLUDED.freshness_bonus,
                composite_score = EXCLUDED.composite_score,
                topics = EXCLUDED.topics,
                geography = EXCLUDED.geography,
                macro_flag = EXCLUDED.macro_flag,
                summary2 = EXCLUDED.summary2,
                why1 = EXCLUDED.why1,
                project_stage = EXCLUDED.project_stage,
                needs_fact_check = EXCLUDED.needs_fact_check,
                media_type = EXCLUDED.media_type
        """), {
            "article_id": article_id,
            "rbp": scores.get("rel_building_practices", 0),
            "rm": scores.get("rel_market", 0),
            "rdb": scores.get("rel_design_business", 0),
            "imp": scores.get("importance_multiplier", 1.0),
            "fresh": scores.get("freshness_bonus", 0.0),
            "comp": scores.get("composite_score", 0.0),
            "topics": topics_array,
            "geo": geography_array,
            "macro": scores.get("macro_flag", False),
            "summary2": scores.get("summary2", None),
            "why1": scores.get("why1", None),
            "project_stage": scores.get("project_stage", None),
            "needs_fact_check": scores.get("needs_fact_check", False),
            "media_type": scores.get("media_type", "article"),
        })
        db.execute(text("UPDATE articles SET status='scored' WHERE id=:id"), {"id": article_id})
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()

def _detect_project_stage(text_blob: str) -> str:
    """Detect project development stage from article text"""
    t = text_blob.lower()
    
    # Stage detection patterns
    if any(phrase in t for phrase in ["approved", "wins approval", "gets approval", "city approves", "planning approval"]):
        return "approved"
    elif any(phrase in t for phrase in ["breaks ground", "groundbreaking", "construction begins", "starts construction"]):
        return "breaks_ground" 
    elif any(phrase in t for phrase in ["tops out", "topping out", "topped out", "reaches full height"]):
        return "tops_out"
    elif any(phrase in t for phrase in ["opens", "opening", "grand opening", "now open", "officially opened"]):
        return "opens"
    else:
        return None

def _detect_media_type(url: str, title: str, content: str) -> str:
    """Detect if content is podcast, video, or article"""
    # Check URL first for definitive identification
    if "youtube.com" in url or "youtu.be" in url:
        return "video"
    if "vimeo.com" in url:
        return "video"
    
    text = f"{url} {title} {content}".lower()
    
    if any(word in text for word in ["podcast", "episode", "listen", "audio", "spotify", "apple podcasts"]):
        return "podcast"
    elif any(word in text for word in ["video", "watch", "youtube", "vimeo", "webinar"]):
        return "video"
    else:
        return "article"

def _assess_fact_check_need(text_blob: str, composite_score: float) -> bool:
    """Determine if article needs fact checking based on content patterns"""
    t = text_blob.lower()
    
    # High-stakes claims that need verification
    risky_patterns = [
        "breaking:", "exclusive:", "first reported", "sources say", "unnamed source",
        "leaked", "confidential", "insider", "rumor", "alleged", "reportedly",
        "unconfirmed", "developing story"
    ]
    
    # Financial/numerical claims
    financial_patterns = [
        "$", "billion", "million", "percent", "%", "rate", "price", "cost"
    ]
    
    has_risky = any(pattern in t for pattern in risky_patterns)
    has_financial = any(pattern in t for pattern in financial_patterns)
    
    # Need fact check if: risky language OR high-stakes financial claims with low confidence
    return has_risky or (has_financial and composite_score < 3.0)

def developer_focused_score(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scoring system optimized for aspiring developer looking for:
    - Tech-enabled repeatable projects
    - Construction innovation opportunities  
    - Market/policy changes creating openings
    - Pragmatic focus on human-centered spaces
    """
    text_blob = " ".join([
        row.get("title") or "",
        row.get("summary_raw") or "",
        row.get("content") or ""
    ])
    t = text_blob.lower()
    
    composite_score = 0.0
    
    # 🚀 TIER 1: BREAKTHROUGH TECH (10-15 points)
    breakthrough_tech = {
        "3d print": 15, "additive manufacturing": 14, "robotic construction": 13,
        "ai design": 12, "generative design": 12, "parametric": 11,
        "mass timber": 12, "clt": 11, "cross laminated": 11,
        "modular construction": 10, "prefab": 9, "offsite construction": 10,
        "digital twin": 8, "bim": 7, "virtual reality": 8,
        "drone construction": 9, "autonomous": 8, "machine learning": 7
    }
    
    # 🏗️ TIER 2: MAJOR CONSTRUCTION PROJECTS & OPPORTUNITIES (8-25 points)  
    project_opportunities = {
        # Mega projects (15-25 points)
        "stadium": 25, "arena": 20, "convention center": 18, "airport": 20,
        "hospital": 18, "university": 16, "data center": 22,
        
        # Project stages (10-15 points)
        "groundbreaking": 15, "breaks ground": 15, "construction begins": 14,
        "topped out": 12, "topping out": 12, "opens": 10,
        "construction manager": 18, "general contractor": 15, "cm/gc": 16,
        
        # Approvals & permits (8-12 points)  
        "approved": 12, "planning approval": 12, "permits issued": 11,
        "rezoning": 15, "zoning change": 15, "upzoning": 13,
        
        # Development types (8-12 points)
        "affordable housing": 12, "mixed-use": 11, "transit-oriented": 13,
        "multifamily": 10, "student housing": 11, "senior housing": 10,
        "industrial": 9, "logistics": 10, "warehouse": 8,
        
        # Innovation projects (12-18 points)
        "first-of-its-kind": 18, "pilot project": 14, "demonstration": 12,
        "prototype": 13, "proof of concept": 12
    }
    
    # 💰 TIER 3: FINANCING & DEALS (6-10 points)
    financing_deals = {
        "construction loan": 10, "development financing": 9, "bridge loan": 8,
        "tax credit": 9, "lihtc": 9, "opportunity zone": 10,
        "subsidies": 11, "grants": 9, "incentives": 8,
        "joint venture": 8, "partnership": 7, "acquisition": 7,
        "development rights": 9, "air rights": 8, "land assembly": 8
    }
    
    # 📊 TIER 4: MARKET SIGNALS (5-8 points)
    market_signals = {
        "housing starts": 8, "building permits": 8, "construction spending": 7,
        "cap rate": 6, "vacancy": 6, "absorption": 6,
        "material costs": 7, "labor shortage": 6, "supply chain": 6,
        "interest rates": 5, "fed": 5, "inflation": 5
    }
    
    # 🌱 TIER 5: SUSTAINABILITY & INNOVATION (7-10 points)
    sustainability = {
        "net zero": 10, "carbon neutral": 9, "embodied carbon": 8,
        "passive house": 8, "energy efficiency": 7, "solar": 6,
        "geothermal": 7, "heat pump": 6, "electrification": 7,
        "circular economy": 8, "waste reduction": 7, "recycled materials": 7
    }
    
    # Calculate scores for each category
    for keyword, points in breakthrough_tech.items():
        if keyword in t:
            composite_score += points * (1 + t.count(keyword) * 0.5)  # Bonus for multiple mentions
    
    for keyword, points in project_opportunities.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in financing_deals.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in market_signals.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in sustainability.items():
        if keyword in t:
            composite_score += points
    
    # ❌ PENALTIES: Filter out irrelevant content
    penalties = {
        "starbucks": -20, "retail chain": -15, "restaurant": -10,
        "layoffs": -10, "earnings": -8, "stock price": -8,
        "celebrity": -15, "entertainment": -10, "sports": -8,
        "fashion": -10, "luxury goods": -8, "automotive": -5,
        "tech stocks": -8, "cryptocurrency": -10, "social media": -8
    }
    
    for keyword, penalty in penalties.items():
        if keyword in t:
            composite_score += penalty
    
    # 🎯 BONUSES: Developer-specific multipliers
    
    # 💰 BIG PROJECT VALUE MULTIPLIER
    import re
    dollar_matches = re.findall(r'\$([0-9]+(?:\.[0-9]+)?)\s*(billion|million|b|m)\b', t)
    if dollar_matches:
        max_value = 0
        for amount, unit in dollar_matches:
            value = float(amount)
            if unit.lower() in ['billion', 'b']:
                value *= 1000  # Convert to millions
            max_value = max(max_value, value)
        
        # Major project multipliers based on size
        if max_value >= 1000:  # $1B+
            composite_score *= 2.5
        elif max_value >= 500:  # $500M+
            composite_score *= 2.0
        elif max_value >= 100:  # $100M+
            composite_score *= 1.7
        elif max_value >= 50:   # $50M+
            composite_score *= 1.4
    
    # Repeatable/scalable project bonus
    if any(word in t for word in ["scalable", "repeatable", "replicable", "standardized", "systematic"]):
        composite_score *= 1.3
    
    # Human-centered design bonus
    if any(word in t for word in ["community", "placemaking", "human-centered", "social impact", "wellness"]):
        composite_score *= 1.2
    
    # Innovation + practicality bonus
    if any(word in t for word in ["cost-effective", "efficient", "practical", "feasible", "viable"]):
        composite_score *= 1.15
    
    # Geographic opportunity bonus (emerging markets)
    if any(word in t for word in ["emerging market", "underserved", "opportunity zone", "revitalization"]):
        composite_score *= 1.25
    
    # Joint venture/partnership bonus (shows collaboration opportunities)
    if any(word in t for word in ["joint venture", "jv", "partnership", "consortium", "alliance"]):
        composite_score *= 1.2
    
    # Ensure minimum score for highly relevant content
    if composite_score < 0:
        composite_score = 0
    
    # Length bonus for substantial content
    word_count = len((row.get("content") or "").split())
    if word_count > 300:
        composite_score += min(word_count / 500.0, 3.0)  # Up to +3 points

    topics = _tag_categories(text_blob)
    project_stage = _detect_project_stage(text_blob)
    media_type = _detect_media_type(row.get("url", ""), row.get("title", ""), row.get("content", ""))
    needs_fact_check = _assess_fact_check_need(text_blob, composite_score)
    
    # Enhanced scoring for YouTube videos
    if media_type == "video" and ("youtube.com" in row.get("url", "") or "youtu.be" in row.get("url", "")):
        try:
            from .youtube_handler import process_youtube_video
            youtube_data = process_youtube_video(
                row.get("url", ""), 
                row.get("title", ""), 
                row.get("content", ""),
                row.get("published_at")
            )
            if youtube_data:
                composite_score = max(composite_score, youtube_data.get("composite_score", 0))
                needs_fact_check = youtube_data.get("needs_fact_check", needs_fact_check)
        except ImportError:
            pass
    
    return {
        "rel_building_practices": int(composite_score * 0.1),  # Convert to legacy format
        "rel_market": int(composite_score * 0.1),
        "rel_design_business": int(composite_score * 0.1),
        "importance_multiplier": 1.0,
        "freshness_bonus": 0.0,
        "composite_score": float(composite_score),
        "topics": topics,
        "geography": [],
        "macro_flag": any(word in t for word in ["macro", "federal", "policy", "regulation"]),
        "summary2": None,
        "why1": None,
        "project_stage": project_stage,
        "needs_fact_check": needs_fact_check,
        "media_type": media_type,
    }

# Use the new developer-focused scoring
def naive_score(row: Dict[str, Any]) -> Dict[str, Any]:
    return developer_focused_score(row)

def run(limit: int = 50) -> Dict[str, Any]:
    arts = fetch_new_articles(limit=limit)
    scored = 0
    for a in arts:
        # scores = score_article_with_llm(...)
        scores = naive_score(a)
        save_scores(a["id"], scores)
        scored += 1
    return {"ok": True, "scored": scored}
