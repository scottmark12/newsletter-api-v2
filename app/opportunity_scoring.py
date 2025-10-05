# app/opportunity_scoring.py
# V4 Opportunity-Focused Scoring System based on V3 thematic logic

from typing import List, Dict, Any, Tuple
import re
from datetime import datetime, timezone
from sqlalchemy import text
from .db import SessionLocal
from .llm import score_article_with_llm

# -------- OPPORTUNITY THEME DEFINITIONS --------
OPPORTUNITY_THEMES = {
    "big_returns": {
        "description": "Projects with proven financial success, high ROI, market transformation stories",
        "narrative_signals": {
            "transformation_language": ["grew from", "scaled up", "turned into", "transformed", "expanded from", "started with", "evolved into", "became a", "emerged as"],
            "impact_language": ["return on", "boosted productivity", "led to growth", "ROI over time", "profitability increased", "revenue growth", "market share"],
            "scale_indicators": ["billion dollar", "mega project", "record-breaking", "unprecedented", "largest", "biggest", "first-of-its-kind"]
        },
        "keywords": {
            "financial_success": ["roi", "return on investment", "profitability", "revenue", "earnings", "financial performance", "market cap", "valuation"],
            "market_impact": ["market transformation", "industry disruption", "paradigm shift", "game changer", "breakthrough", "revolutionary"],
            "scale_projects": ["billion", "mega", "large-scale", "massive", "significant", "major", "substantial", "extensive"]
        },
        "multipliers": {
            "roi_data": 1.8,
            "case_study": 1.6,
            "market_transformation": 1.5,
            "financial_metrics": 1.4
        }
    },
    
    "material_breakthroughs": {
        "description": "Revolutionary materials, construction science breakthroughs, game-changing technologies",
        "narrative_signals": {
            "innovation_language": ["breakthrough", "revolutionary", "pioneering", "groundbreaking", "cutting-edge", "state-of-the-art", "next-generation"],
            "scientific_language": ["research shows", "studies demonstrate", "testing reveals", "laboratory results", "scientific breakthrough", "engineering feat"],
            "future_language": ["future of", "next wave", "emerging technology", "promising development", "potential to", "could revolutionize"]
        },
        "keywords": {
            "advanced_materials": ["graphene", "carbon fiber", "aerogel", "self-healing", "smart materials", "nano-materials", "bio-based", "recycled materials"],
            "construction_tech": ["3d printing", "additive manufacturing", "robotic construction", "automation", "AI", "machine learning", "digital twin", "BIM"],
            "sustainable_tech": ["net zero", "carbon negative", "renewable energy", "energy storage", "smart grid", "microgrid", "solar", "wind"]
        },
        "multipliers": {
            "scientific_breakthrough": 1.7,
            "commercial_application": 1.5,
            "market_adoption": 1.4,
            "cost_reduction": 1.3
        }
    },
    
    "market_transformations": {
        "description": "Industries being disrupted, new market opportunities, regulatory unlocks",
        "narrative_signals": {
            "disruption_language": ["disrupting", "transforming", "revolutionizing", "changing the game", "shaking up", "redefining"],
            "opportunity_language": ["opportunity", "potential", "growth market", "emerging sector", "untapped", "new frontier"],
            "regulatory_language": ["policy change", "new regulations", "incentive program", "government support", "legislative update"]
        },
        "keywords": {
            "market_disruption": ["market disruption", "industry transformation", "paradigm shift", "new business model", "emerging market"],
            "regulatory_changes": ["zoning reform", "building code update", "tax incentive", "government funding", "policy initiative"],
            "emerging_sectors": ["renewable energy", "data centers", "5g infrastructure", "electric vehicles", "smart cities", "healthcare construction"]
        },
        "multipliers": {
            "market_disruption": 1.6,
            "regulatory_unlock": 1.5,
            "emerging_market": 1.4,
            "government_support": 1.3
        }
    }
}

def score_article_for_opportunities(title: str, content: str) -> Dict[str, Any]:
    """
    Score an article using opportunity-focused thematic analysis
    Returns score breakdown by theme with narrative signals
    """
    text_blob = f"{title} {content}".lower()
    
    theme_scores = {}
    narrative_signals_found = []
    
    for theme_name, theme_config in OPPORTUNITY_THEMES.items():
        theme_score = 0
        theme_signals = []
        
        # Check narrative signals (higher weight)
        for signal_type, signals in theme_config["narrative_signals"].items():
            for signal in signals:
                if signal.lower() in text_blob:
                    theme_score += 10  # High weight for narrative signals
                    theme_signals.append(f"{signal_type}: {signal}")
        
        # Check keywords (medium weight)
        for keyword_type, keywords in theme_config["keywords"].items():
            keyword_matches = []
            for keyword in keywords:
                if keyword.lower() in text_blob:
                    theme_score += 5
                    keyword_matches.append(keyword)
            if keyword_matches:
                theme_signals.append(f"{keyword_type}: {', '.join(keyword_matches)}")
        
        # Apply multipliers
        multiplier = 1.0
        for mult_type, mult_value in theme_config["multipliers"].items():
            if any(mult_type.replace("_", " ") in signal.lower() for signal in theme_signals):
                multiplier = max(multiplier, mult_value)
        
        final_theme_score = theme_score * multiplier
        theme_scores[theme_name] = {
            "score": final_theme_score,
            "signals": theme_signals,
            "multiplier": multiplier
        }
        
        narrative_signals_found.extend(theme_signals)
    
    # Calculate composite score
    composite_score = sum(theme["score"] for theme in theme_scores.values())
    
    # Boost score for articles with multiple themes (cross-cutting opportunities)
    if len([t for t in theme_scores.values() if t["score"] > 0]) > 1:
        composite_score *= 1.2
    
    return {
        "composite_score": min(composite_score, 100),  # Cap at 100
        "theme_scores": theme_scores,
        "narrative_signals": narrative_signals_found,
        "opportunity_level": "high" if composite_score > 60 else "medium" if composite_score > 30 else "low"
    }

def run_opportunity_scoring(limit: int = 50) -> Dict[str, Any]:
    """
    Run opportunity-focused scoring on unscored articles
    """
    db = SessionLocal()
    try:
        # Get unscored articles
        result = db.execute(text("""
            SELECT id, title, content FROM articles 
            WHERE status = 'ingested' 
            AND id NOT IN (SELECT article_id FROM article_scores)
            ORDER BY published_at DESC 
            LIMIT :limit
        """), {"limit": limit})
        
        articles = result.fetchall()
        scored_count = 0
        high_opportunity_count = 0
        
        print(f"🎯 Running Opportunity Scoring on {len(articles)} articles...")
        
        for article in articles:
            try:
                # Score using opportunity themes
                opp_score = score_article_for_opportunities(article.title, article.content)
                
                # Also get LLM score for comparison
                llm_score = score_article_with_llm(article.title, article.content)
                
                # Combine scores (opportunity score gets higher weight)
                final_score = (opp_score["composite_score"] * 0.7) + (llm_score.get("composite_score", 60) * 0.3)
                
                # Determine if high opportunity
                is_high_opportunity = opp_score["opportunity_level"] == "high" or final_score > 70
                
                if is_high_opportunity:
                    high_opportunity_count += 1
                    print(f"🚀 HIGH OPPORTUNITY: {article.title[:60]}... (Score: {final_score:.1f})")
                    for signal in opp_score["narrative_signals"][:3]:  # Show top 3 signals
                        print(f"    📈 {signal}")
                
                # Save to database (fix PostgreSQL array formatting)
                themes_list = [theme for theme, data in opp_score["theme_scores"].items() if data["score"] > 0]
                topics_str = "{" + ",".join(f'"{theme}"' for theme in themes_list) + "}"
                
                db.execute(text("""
                    INSERT INTO article_scores (
                        article_id, composite_score, summary2, why1, topics
                    ) VALUES (
                        :article_id, :score, :summary, :why, :topics
                    )
                """), {
                    "article_id": article.id,
                    "score": final_score,
                    "summary": llm_score.get("summary2", ""),
                    "why": f"Opportunity Level: {opp_score['opportunity_level']}. Signals: {'; '.join(opp_score['narrative_signals'][:3])}",
                    "topics": topics_str
                })
                
                # Update article status
                db.execute(text("UPDATE articles SET status = 'scored' WHERE id = :id"), {"id": article.id})
                
                scored_count += 1
                
            except Exception as e:
                print(f"Error scoring article {article.id}: {e}")
                continue
        
        db.commit()
        
        return {
            "ok": True,
            "scored": scored_count,
            "high_opportunity": high_opportunity_count,
            "system": "opportunity_thematic"
        }
        
    except Exception as e:
        db.rollback()
        return {"ok": False, "error": str(e)}
    finally:
        db.close()

def get_high_opportunity_articles(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get articles with highest opportunity scores
    """
    db = SessionLocal()
    try:
        result = db.execute(text("""
            SELECT a.title, a.url, a.published_at, s.composite_score, s.why1
            FROM articles a
            JOIN article_scores s ON a.id = s.article_id
            WHERE s.composite_score > 60
            ORDER BY s.composite_score DESC
            LIMIT :limit
        """), {"limit": limit})
        
        return [dict(row._mapping) for row in result.fetchall()]
        
    finally:
        db.close()
