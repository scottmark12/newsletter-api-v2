# app/ceo_voice.py
"""
V2 "Chill CEO" Voice Implementation
Transforms neutral summaries into executive-focused, actionable insights
"""
from typing import Dict, List, Any
import re

def generate_ceo_summary(article: Dict[str, Any]) -> Dict[str, str]:
    """
    Generate CEO-style summary with:
    - Tight headline (max 100 chars)
    - 2 bullets "why it matters"
    - CEO takeaway/action line
    """
    title = article.get("title", "")
    content = article.get("content", "")
    summary = article.get("summary_raw", "")
    topics = article.get("topics", [])
    project_stage = article.get("project_stage")
    
    # Generate tight headline
    headline = _create_tight_headline(title)
    
    # Generate "why it matters" bullets
    why_bullets = _generate_why_bullets(content, summary, topics, project_stage)
    
    # Generate CEO takeaway
    takeaway = _generate_ceo_takeaway(topics, project_stage, content)
    
    return {
        "headline": headline,
        "why_it_matters": why_bullets,
        "ceo_takeaway": takeaway
    }

def _create_tight_headline(title: str) -> str:
    """Create punchy, sub-100 char headline"""
    if not title:
        return "Industry Update"
    
    # Remove fluff words and tighten
    title = title.strip()
    
    # Remove common fluff
    fluff_patterns = [
        r"^(The|A|An)\s+",
        r"\s+(Report|Analysis|Study|News|Update)$",
        r"\s*:\s*.*$",  # Remove subtitle after colon
        r"\s+\|\s+.*$", # Remove subtitle after pipe
    ]
    
    for pattern in fluff_patterns:
        title = re.sub(pattern, "", title, flags=re.IGNORECASE)
    
    # Truncate if needed
    if len(title) > 100:
        title = title[:97] + "..."
    
    return title

def _generate_why_bullets(content: str, summary: str, topics: List[str], project_stage: str) -> List[str]:
    """Generate 2 'why it matters' bullets"""
    bullets = []
    
    # Combine available text
    text = f"{summary} {content}".lower()
    
    # Bullet 1: Market/timing signal
    if "market_news" in topics or "market_insight" in topics:
        if any(word in text for word in ["rate", "fed", "inflation", "cost"]):
            bullets.append("Signals shift in project financing costs and timing")
        elif any(word in text for word in ["demand", "supply", "inventory", "vacancy"]):
            bullets.append("Indicates market demand shift affecting development strategy")
        else:
            bullets.append("Market signal for construction activity timing")
    elif "innovation" in topics or "tech_innovation" in topics:
        bullets.append("Early adoption opportunity for competitive advantage")
    elif project_stage:
        stage_messages = {
            "approved": "Regulatory precedent for similar projects",
            "breaks_ground": "Market confidence signal for development activity", 
            "tops_out": "Construction timeline benchmark for planning",
            "opens": "Market reception data for future developments"
        }
        bullets.append(stage_messages.get(project_stage, "Development milestone with strategic implications"))
    else:
        bullets.append("Strategic implications for active portfolio")
    
    # Bullet 2: Action/opportunity angle
    if "unique_developments" in topics or "unique_development" in topics:
        bullets.append("Approach methodology worth studying for replication")
    elif "insights" in topics or "construction_insight" in topics:
        if any(word in text for word in ["policy", "zoning", "regulation", "code"]):
            bullets.append("Regulatory change affecting future project feasibility")
        elif any(word in text for word in ["material", "labor", "cost", "supply"]):
            bullets.append("Cost structure impact requiring procurement strategy review")
        else:
            bullets.append("Industry trend affecting long-term positioning")
    elif any(word in text for word in ["partnership", "joint venture", "acquisition"]):
        bullets.append("Partnership model worth evaluating for expansion")
    else:
        bullets.append("Operational insight applicable to current projects")
    
    # Ensure exactly 2 bullets, truncate if needed
    bullets = bullets[:2]
    while len(bullets) < 2:
        bullets.append("Strategic relevance for portfolio positioning")
    
    # Truncate long bullets
    bullets = [bullet[:200] + ("..." if len(bullet) > 200 else "") for bullet in bullets]
    
    return bullets

def _generate_ceo_takeaway(topics: List[str], project_stage: str, content: str) -> str:
    """Generate actionable CEO takeaway line"""
    text = content.lower() if content else ""
    
    # Stage-specific takeaways
    if project_stage:
        stage_actions = {
            "approved": "Monitor approval process for pipeline applications",
            "breaks_ground": "Assess market timing for similar developments",
            "tops_out": "Benchmark construction timeline against current projects", 
            "opens": "Evaluate market reception for future positioning"
        }
        return stage_actions.get(project_stage, "Track development for strategic insights")
    
    # Topic-specific takeaways
    if "market_news" in topics or "market_insight" in topics:
        if any(word in text for word in ["rate", "fed", "financing"]):
            return "Review financing strategy for rate environment"
        elif any(word in text for word in ["demand", "rental", "occupancy"]):
            return "Adjust unit mix and pricing strategy accordingly"
        else:
            return "Monitor for cost/timing impact on active projects"
    
    elif "innovation" in topics or "tech_innovation" in topics:
        if any(word in text for word in ["modular", "prefab", "offsite"]):
            return "Evaluate construction method for next development"
        elif any(word in text for word in ["ai", "automation", "digital"]):
            return "Assess technology adoption for operational advantage"
        else:
            return "Consider pilot program for competitive advantage"
    
    elif "insights" in topics or "construction_insight" in topics:
        if any(word in text for word in ["policy", "zoning", "regulation"]):
            return "Review pipeline projects for regulatory alignment"
        elif any(word in text for word in ["sustainability", "carbon", "energy"]):
            return "Integrate ESG considerations into development strategy"
        else:
            return "Apply insights to optimize current operations"
    
    elif "unique_developments" in topics or "unique_development" in topics:
        return "Study approach for potential replication opportunities"
    
    else:
        return "Assess strategic relevance for portfolio positioning"

def format_quick_hit(title: str, source: str) -> str:
    """Format one-liner for quick hits section"""
    if not title:
        return f"Industry update — {source}"
    
    # Remove fluff and tighten
    title = re.sub(r"^(The|A|An)\s+", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\s+(Report|Analysis|Study)$", "", title, flags=re.IGNORECASE)
    
    # Truncate
    if len(title) > 80:
        title = title[:77] + "..."
    
    return f"{title} — {source}"

def enhance_with_ceo_voice(articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Apply CEO voice formatting to list of articles"""
    enhanced = []
    
    for article in articles:
        ceo_format = generate_ceo_summary(article)
        
        enhanced_article = article.copy()
        enhanced_article.update({
            "headline": ceo_format["headline"],
            "why_it_matters": ceo_format["why_it_matters"],
            "ceo_takeaway": ceo_format["ceo_takeaway"]
        })
        
        enhanced.append(enhanced_article)
    
    return enhanced

