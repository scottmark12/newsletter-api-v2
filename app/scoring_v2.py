# app/scoring_v2.py
# Enhanced Newsletter Scoring System - Theme-Based Approach
# Focus: Insights, foresight, and pragmatic opportunities for developers and investors

from typing import List, Dict, Any, Optional
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal
import re
import json

# -------- THEME-BASED CATEGORIZATION --------
# Shift from rigid keywords to broader themes that capture the essence of valuable content

THEMES = {
    "opportunities": {
        "description": "Stories of transformation, small → big investments, creative deals, entrepreneurial case studies, wealth-building examples",
        "signals": {
            # Transformative language
            "grew_from": ["grew from", "started with", "began as", "evolved from", "transformed into", "scaled up", "turned into"],
            "investment_growth": ["investment grew", "valuation increased", "returns improved", "profitability rose", "revenue growth", "market cap"],
            "scaling_stories": ["scaled up", "expanded to", "grew from", "increased from", "multiplied by", "grew by", "increased by"],
            "creative_deals": ["creative financing", "innovative deal", "unique structure", "creative solution", "unconventional approach"],
            
            # Opportunity indicators
            "wealth_building": ["wealth creation", "asset appreciation", "value creation", "equity growth", "portfolio growth"],
            "entrepreneurial": ["entrepreneur", "startup", "venture", "pioneering", "trailblazing", "first-mover"],
            "case_studies": ["case study", "success story", "how they did it", "lessons learned", "what worked"],
            
            # Market opportunities
            "emerging_markets": ["emerging market", "untapped market", "new opportunity", "market gap", "underserved"],
            "timing_signals": ["perfect timing", "market timing", "right time", "opportunity window", "market shift"]
        }
    },
    
    "practices": {
        "description": "Building methods, design principles, process improvements, productivity studies, and lessons learned",
        "signals": {
            # Process improvements
            "methodology": ["methodology", "process", "approach", "framework", "system", "workflow", "procedure"],
            "productivity": ["productivity", "efficiency", "streamlined", "optimized", "improved", "enhanced", "better"],
            "lessons_learned": ["lessons learned", "what worked", "what didn't work", "insights", "takeaways", "key findings"],
            
            # Building methods
            "construction_methods": ["construction method", "building technique", "installation process", "assembly method"],
            "design_principles": ["design principle", "design approach", "design philosophy", "design strategy"],
            "best_practices": ["best practice", "industry standard", "proven method", "established practice"],
            
            # Performance metrics
            "performance_data": ["performance data", "test results", "metrics", "measurements", "benchmarks", "kpis"],
            "roi_metrics": ["roi", "return on investment", "payback period", "cost savings", "value delivered"],
            "time_savings": ["time savings", "faster", "quicker", "reduced time", "accelerated", "expedited"]
        }
    },
    
    "systems_codes": {
        "description": "Policy updates, building code changes, zoning reforms, incentives that unlock new development",
        "signals": {
            # Policy and regulatory changes
            "policy_updates": ["policy change", "new policy", "updated policy", "regulatory change", "new regulation"],
            "code_changes": ["building code", "code change", "new code", "updated code", "code revision", "code update"],
            "zoning_reforms": ["zoning change", "zoning reform", "rezoning", "zoning update", "zoning revision"],
            
            # Development incentives
            "incentives": ["incentive", "tax credit", "subsidy", "grant", "rebate", "financial incentive"],
            "development_unlocks": ["unlocks development", "enables development", "allows development", "permits development"],
            
            # Regulatory frameworks
            "permitting": ["permitting process", "approval process", "entitlement", "approval", "permit"],
            "compliance": ["compliance", "regulatory compliance", "code compliance", "standards compliance"],
            "certification": ["certification", "certified", "standard", "rating", "accreditation"]
        }
    },
    
    "vision": {
        "description": "Smart cities, future-of-living models, community impact, human-centered and biophilic design",
        "signals": {
            # Future vision
            "smart_cities": ["smart city", "intelligent city", "connected city", "digital city", "tech-enabled city"],
            "future_living": ["future of living", "next generation", "evolving lifestyle", "changing demographics"],
            "community_impact": ["community impact", "social impact", "community benefit", "neighborhood transformation"],
            
            # Human-centered design
            "human_centered": ["human-centered", "user-centered", "people-focused", "resident-focused", "community-focused"],
            "biophilic": ["biophilic", "nature-inspired", "natural elements", "green design", "wellness design"],
            "wellness": ["wellness", "health", "well-being", "mental health", "physical health", "quality of life"],
            
            # Sustainable vision
            "sustainability": ["sustainable", "green", "eco-friendly", "environmental", "carbon neutral", "net zero"],
            "resilience": ["resilient", "resilience", "adaptable", "flexible", "future-proof", "long-term"]
        }
    }
}

# -------- NARRATIVE SIGNAL DETECTION --------
# Beyond keywords - detect the type of narrative and its value

NARRATIVE_SIGNALS = {
    "transformative_language": {
        "patterns": [
            r"grew from \w+ to \w+",
            r"scaled up from \w+",
            r"transformed \w+ into \w+",
            r"turned \w+ around",
            r"evolved from \w+ to \w+",
            r"increased from \w+ to \w+"
        ],
        "bonus_multiplier": 1.4
    },
    
    "impact_language": {
        "patterns": [
            r"return on investment",
            r"boosted productivity by",
            r"led to \w+% growth",
            r"increased efficiency by",
            r"reduced costs by",
            r"improved performance by",
            r"roi over time",
            r"payback period of"
        ],
        "bonus_multiplier": 1.5
    },
    
    "prescriptive_language": {
        "patterns": [
            r"insights from",
            r"lessons learned",
            r"framework for",
            r"how to",
            r"roadmap to",
            r"step-by-step",
            r"methodology for",
            r"process for"
        ],
        "bonus_multiplier": 1.3
    }
}

# -------- PRAGMATIC INSIGHT WEIGHTING --------
# Score content by actual usefulness rather than just keyword density

INSIGHT_WEIGHTING = {
    "high_value_indicators": {
        "roi_data": ["roi", "return on investment", "payback period", "cost savings", "value delivered", "profit margin"],
        "performance_metrics": ["performance data", "test results", "benchmarks", "kpis", "metrics", "measurements"],
        "methodology": ["methodology", "process", "framework", "approach", "system", "workflow"],
        "before_after": ["before and after", "transformation", "improvement", "enhancement", "upgrade"],
        "multiplier": 2.0
    },
    
    "medium_value_indicators": {
        "visionary_content": ["vision", "future", "next generation", "emerging", "trending", "growing"],
        "industry_trends": ["industry trend", "market trend", "sector trend", "emerging trend"],
        "multiplier": 1.2
    },
    
    "low_value_indicators": {
        "hype_press_release": ["announces", "proud to announce", "excited to share", "pleased to announce"],
        "superficial_news": ["breaking news", "latest news", "just announced", "recently announced"],
        "multiplier": 0.7
    }
}

# -------- ENHANCED MULTIPLIERS --------
# Build on existing bonuses with new pragmatic multipliers

ENHANCED_MULTIPLIERS = {
    "case_study_bonus": {
        "indicators": [
            "case study", "success story", "how they did it", "lessons learned", "what worked",
            "before and after", "transformation story", "implementation story", "project profile"
        ],
        "multiplier": 1.6
    },
    
    "scalable_process_bonus": {
        "indicators": [
            "scalable", "repeatable", "replicable", "modular", "prefab", "prefabricated",
            "standardized", "systematic", "framework", "methodology", "process"
        ],
        "multiplier": 1.5
    },
    
    "code_policy_shift_bonus": {
        "indicators": [
            "new zoning", "zoning change", "building code change", "policy change", "regulatory change",
            "new regulation", "updated code", "code revision", "policy update", "regulatory update"
        ],
        "multiplier": 1.4
    },
    
    "thought_leadership_bonus": {
        "indicators": [
            "thought leadership", "expert analysis", "industry expert", "practitioner insights",
            "research report", "white paper", "market analysis", "expert opinion", "insight"
        ],
        "multiplier": 1.3
    }
}

# -------- EXISTING MULTIPLIERS (Enhanced) --------
# Keep and enhance existing institutional and dollar multipliers

INSTITUTIONAL_SOURCES = [
    "blackstone", "cbre", "jll", "cushman", "savills", "colliers",
    "kkr", "apollo", "carlyle", "brookfield", "tpg", "ares",
    "morgan stanley", "goldman sachs", "jpmorgan", "bank of america",
    "wells fargo", "citi", "freddie mac", "fannie mae", "hud",
    "urban land institute", "uli", "nareit", "ncrc", "u.s. green building council",
    "usgbc", "architecture 2030", "carbon leadership forum", "passive house institute",
    "international living future institute", "ilfi", "building green",
    "construction dive", "engineering news record", "enr", "architect magazine",
    "architectural record", "archdaily", "dezeen", "bd+c", "building design construction",
    "turner construction", "skanska", "fluor", "bechtel", "aecom", "jacobs",
    "hunt construction", "pcl construction", "whiting-turner", "suffolk construction"
]

# -------- CONTENT FILTERING --------
# Enhanced filtering for quality and relevance

EXCLUDE_KEYWORDS = {
    "furniture", "chair", "table", "desk", "sofa", "couch", "lamp", "lighting fixture",
    "interior design", "decor", "decoration", "aesthetic", "artistic", "conceptual",
    "installation", "exhibition", "museum", "gallery", "art ", "art.", "art,", "art:", "sculpture", "painting",
    "fashion", "clothing", "textile", "fabric", "wallpaper", "paint color", "color scheme",
    "experimental architecture", "avant-garde", "theoretical", "philosophical",
    "student project", "academic", "research paper", "thesis", "dissertation"
}

def detect_themes(text_blob: str) -> List[str]:
    """Detect themes in content using flexible signal matching"""
    t = (text_blob or "").lower()
    
    # First check if content should be excluded (use word boundaries for precision)
    import re
    for exclude_word in EXCLUDE_KEYWORDS:
        if re.search(r'\b' + re.escape(exclude_word) + r'\b', t):
            return []
    
    detected_themes = []
    
    for theme_name, theme_data in THEMES.items():
        theme_score = 0
        signal_groups = theme_data["signals"]
        
        # Score based on signal group matches
        for signal_group, signals in signal_groups.items():
            matches = sum(1 for signal in signals if signal in t)
            if matches > 0:
                theme_score += matches  # Simplified scoring
        
        # Include theme if it has sufficient signal strength
        if theme_score >= 1:  # Lower threshold for theme inclusion
            detected_themes.append(theme_name)
    
    return detected_themes

def detect_narrative_signals(text_blob: str) -> Dict[str, float]:
    """Detect narrative signals and calculate bonuses"""
    t = (text_blob or "").lower()
    bonuses = {}
    
    for signal_type, signal_data in NARRATIVE_SIGNALS.items():
        matches = 0
        for pattern in signal_data["patterns"]:
            matches += len(re.findall(pattern, t))
        
        if matches > 0:
            bonuses[signal_type] = signal_data["bonus_multiplier"] ** min(matches, 3)  # Cap at 3 matches
    
    return bonuses

def calculate_insight_weighting(text_blob: str) -> float:
    """Calculate pragmatic insight weighting based on content usefulness"""
    t = (text_blob or "").lower()
    
    # High value indicators
    high_value_score = 0
    for indicator in INSIGHT_WEIGHTING["high_value_indicators"]["roi_data"]:
        high_value_score += t.count(indicator)
    for indicator in INSIGHT_WEIGHTING["high_value_indicators"]["performance_metrics"]:
        high_value_score += t.count(indicator)
    for indicator in INSIGHT_WEIGHTING["high_value_indicators"]["methodology"]:
        high_value_score += t.count(indicator)
    
    # Medium value indicators
    medium_value_score = 0
    for indicator in INSIGHT_WEIGHTING["medium_value_indicators"]["visionary_content"]:
        medium_value_score += t.count(indicator)
    for indicator in INSIGHT_WEIGHTING["medium_value_indicators"]["industry_trends"]:
        medium_value_score += t.count(indicator)
    
    # Low value indicators
    low_value_score = 0
    for indicator in INSIGHT_WEIGHTING["low_value_indicators"]["hype_press_release"]:
        low_value_score += t.count(indicator)
    for indicator in INSIGHT_WEIGHTING["low_value_indicators"]["superficial_news"]:
        low_value_score += t.count(indicator)
    
    # Calculate weighted score
    weighted_score = (
        high_value_score * INSIGHT_WEIGHTING["high_value_indicators"]["multiplier"] +
        medium_value_score * INSIGHT_WEIGHTING["medium_value_indicators"]["multiplier"] -
        low_value_score * INSIGHT_WEIGHTING["low_value_indicators"]["multiplier"]
    )
    
    return max(weighted_score, 0.5)  # Minimum weighting of 0.5

def apply_enhanced_multipliers(text_blob: str) -> Dict[str, float]:
    """Apply enhanced multipliers for pragmatic value"""
    t = (text_blob or "").lower()
    multipliers = {}
    
    for multiplier_name, multiplier_data in ENHANCED_MULTIPLIERS.items():
        matches = sum(1 for indicator in multiplier_data["indicators"] if indicator in t)
        if matches > 0:
            multipliers[multiplier_name] = multiplier_data["multiplier"] ** min(matches, 2)  # Cap at 2 matches
    
    return multipliers

def semantic_insight_check(text_blob: str) -> float:
    """Simple semantic check for actionable insight content"""
    t = (text_blob or "").lower()
    
    # Actionable insight indicators
    actionable_indicators = [
        "actionable", "implementable", "practical", "useful", "valuable",
        "insightful", "informative", "educational", "instructional",
        "how to", "step by step", "process", "method", "approach",
        "framework", "strategy", "tactic", "technique", "best practice"
    ]
    
    # Developer/investor value indicators
    value_indicators = [
        "developer", "investor", "investment", "development", "construction",
        "real estate", "property", "building", "project", "deal",
        "financing", "funding", "capital", "equity", "debt",
        "market", "opportunity", "growth", "returns", "profitability"
    ]
    
    actionable_score = sum(1 for indicator in actionable_indicators if indicator in t)
    value_score = sum(1 for indicator in value_indicators if indicator in t)
    
    # Combine scores with weighting
    semantic_score = (actionable_score * 1.5 + value_score * 1.0) / 10.0  # Normalize to 0-1
    return min(semantic_score, 1.0)

def enhanced_developer_focused_score(row: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Enhanced scoring system focused on themes, narratives, and pragmatic insights"""
    
    text_blob = f"{row.get('title', '')} {row.get('content', '')}".lower()
    
    # Detect themes using flexible signal matching
    themes = detect_themes(text_blob)
    
    # If no themes detected (excluded content), return None
    if not themes:
        return None
    
    # Start with base score
    composite_score = 10.0  # Base score for relevant content
    
    # Apply theme-based scoring
    for theme in themes:
        if theme == "opportunities":
            composite_score += 25  # High value for transformation stories
        elif theme == "practices":
            composite_score += 20  # High value for actionable methods
        elif theme == "systems_codes":
            composite_score += 22  # High value for regulatory unlocks
        elif theme == "vision":
            composite_score += 15  # Medium value for future vision
    
    # Detect narrative signals
    narrative_bonuses = detect_narrative_signals(text_blob)
    for bonus_type, bonus_value in narrative_bonuses.items():
        composite_score *= bonus_value
    
    # Apply pragmatic insight weighting
    insight_weighting = calculate_insight_weighting(text_blob)
    composite_score *= insight_weighting
    
    # Apply enhanced multipliers
    enhanced_multipliers = apply_enhanced_multipliers(text_blob)
    for multiplier_type, multiplier_value in enhanced_multipliers.items():
        composite_score *= multiplier_value
    
    # Apply existing institutional source bonus
    if any(source in text_blob for source in INSTITUTIONAL_SOURCES):
        composite_score *= 1.7
    
    # Apply existing dollar amount multipliers
    dollar_matches = re.findall(r'\$([0-9]+(?:\.[0-9]+)?)\s*(billion|million|b|m)\b', text_blob)
    if dollar_matches:
        max_value = 0
        for amount, unit in dollar_matches:
            value = float(amount)
            if unit.lower() in ['billion', 'b']:
                value *= 1000  # Convert to millions
            max_value = max(max_value, value)
        
        # Enhanced major project multipliers
        if max_value >= 1000:  # $1B+
            composite_score *= 3.5
        elif max_value >= 500:  # $500M+
            composite_score *= 2.8
        elif max_value >= 100:  # $100M+
            composite_score *= 2.2
        elif max_value >= 50:   # $50M+
            composite_score *= 1.8
        elif max_value >= 25:   # $25M+
            composite_score *= 1.5
    
    # Apply semantic insight check
    semantic_bonus = semantic_insight_check(text_blob)
    composite_score *= (1.0 + semantic_bonus)
    
    # Length bonus for substantial content
    word_count = len((row.get("content") or "").split())
    if word_count > 300:
        composite_score += min(word_count / 500.0, 5.0)  # Up to +5 points
    
    # Ensure minimum score
    if composite_score < 0:
        composite_score = 0
    
    # Detect project stage and media type
    project_stage = _detect_project_stage(text_blob)
    media_type = _detect_media_type(row.get("url", ""), row.get("title", ""), row.get("content", ""))
    needs_fact_check = _assess_fact_check_need(text_blob, composite_score)
    
    return {
        "rel_building_practices": int(composite_score * 0.1),
        "rel_market": int(composite_score * 0.1),
        "rel_design_business": int(composite_score * 0.1),
        "importance_multiplier": 1.0,
        "freshness_bonus": 0.0,
        "composite_score": float(composite_score),
        "themes": themes,  # New: store detected themes
        "narrative_signals": list(narrative_bonuses.keys()),  # New: store narrative signals
        "insight_weighting": insight_weighting,  # New: store insight weighting
        "geography": [],
        "macro_flag": any(word in text_blob for word in ["macro", "federal", "policy", "regulation"]),
        "summary2": None,
        "why1": None,
        "project_stage": project_stage,
        "needs_fact_check": needs_fact_check,
        "media_type": media_type,
    }

# Import helper functions from original scoring system
def _detect_project_stage(text_blob: str) -> str:
    """Detect project development stage from article text"""
    t = text_blob.lower()
    
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
    """Assess if article needs fact-checking based on claims and score"""
    t = text_blob.lower()
    
    # High-stakes claims that need verification
    risky_patterns = [
        r"\$[0-9]+(?:\.[0-9]+)?\s*(billion|million)\b",  # Large dollar amounts
        r"world's first", r"largest", r"biggest", r"record-breaking",
        r"breakthrough", r"revolutionary", r"game-changing"
    ]
    
    risky_claims = sum(len(re.findall(pattern, t)) for pattern in risky_patterns)
    
    # High-scoring articles with risky claims need fact-checking
    return composite_score > 100 and risky_claims > 0

def save_scores_v2(article_id: str, scores: Dict[str, Any]) -> None:
    """Save scores with enhanced theme and narrative data"""
    db = SessionLocal()
    try:
        # Handle different database types
        from .db import is_sqlite
        if is_sqlite():
            themes_data = json.dumps(scores.get("themes", []))
            narrative_data = json.dumps(scores.get("narrative_signals", []))
        else:
            themes_data = scores.get("themes", [])
            narrative_data = scores.get("narrative_signals", [])
        
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
            "topics": themes_data,  # Store themes in topics field for now
            "geo": json.dumps(scores.get("geography", [])),
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

def fetch_new_articles(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetch articles that need scoring"""
    db = SessionLocal()
    try:
        rows = db.execute(text("""
            SELECT id, url, title, content, published_at, fetched_at
            FROM articles 
            WHERE status = 'fetched' 
            ORDER BY fetched_at DESC 
            LIMIT :limit
        """), {"limit": limit})
        return [dict(row._mapping) for row in rows]
    finally:
        db.close()

def run_v2(limit: int = 50) -> Dict[str, Any]:
    """Run the enhanced scoring system"""
    arts = fetch_new_articles(limit=limit)
    scored = 0
    excluded = 0
    
    print(f"🎯 Running Enhanced Scoring System v2 on {len(arts)} articles...")
    
    for a in arts:
        scores = enhanced_developer_focused_score(a)
        
        if scores is None:
            print(f"❌ Excluding non-developer content: {a.get('title', 'No title')[:60]}...")
            # Mark article as discarded
            db = SessionLocal()
            try:
                db.execute(text("UPDATE articles SET status='discarded' WHERE id=:id"), {"id": a["id"]})
                db.commit()
            finally:
                db.close()
            excluded += 1
        else:
            save_scores_v2(a["id"], scores)
            themes = scores.get("themes", [])
            narrative_signals = scores.get("narrative_signals", [])
            score = scores.get("composite_score", 0)
            print(f"✅ Scored: {score:.1f} | Themes: {themes} | Signals: {narrative_signals}")
            scored += 1
    
    print(f"🎯 Enhanced Scoring Complete: {scored} scored, {excluded} excluded")
    return {"ok": True, "scored": scored, "excluded": excluded, "system": "v2_thematic"}
