# Narrative Synthesis - Weaves together news, research, and media into coherent intelligence
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone, timedelta

from sqlalchemy import text
from .db import SessionLocal
from .llm import call_llm

SYNTHESIS_PROMPT = """You are a construction and real estate intelligence analyst creating a daily executive brief.

Given the following sources:
- NEWS ARTICLES: Recent developments from industry publications
- RESEARCH REPORTS: Market insights from major CRE firms (JLL, CBRE, etc.)
- VIDEO/PODCAST CONTENT: Industry thought leadership and technical insights

Your task is to synthesize these into a coherent narrative that:
1. Identifies the 2-3 most important themes or trends emerging across all sources
2. Explains WHY these matter for developers, contractors, and real estate professionals
3. Provides specific, actionable takeaways
4. References a recommended video/podcast that complements the narrative

CRITICAL RULES:
- Create an actual point of view and narrative arc - don't just list facts
- Weave research insights INTO the news analysis (e.g., "This $2.4B stadium aligns with CBRE's Q3 report showing...")
- Make connections between seemingly disparate stories
- Be specific about dollar amounts, companies, locations
- Sound like a sharp analyst, not a generic news aggregator
- Keep it under 300 words total

SOURCES:
{sources}

Create a brief with:
- HEADLINE: One punchy line (under 100 chars)
- THE STORY: 2-3 paragraphs weaving everything together
- WATCH THIS: One recommended video/podcast with why it's relevant
- BOTTOM LINE: One sentence action for readers
"""

def synthesize_daily_narrative(days_back: int = 1) -> Dict[str, Any]:
    """Generate narrative brief by synthesizing multiple content types"""
    
    db = SessionLocal()
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    try:
        # Get top news articles
        news_rows = db.execute(text("""
            SELECT a.title, a.source, a.content, a.url, s.composite_score, s.topics
            FROM articles a
            JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND s.composite_score > 80
              AND 'research_report' != ANY(COALESCE(s.topics, ARRAY[]::text[]))
              AND 'video_content' != ANY(COALESCE(s.topics, ARRAY[]::text[]))
            ORDER BY s.composite_score DESC
            LIMIT 10
        """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Get research reports
        research_rows = db.execute(text("""
            SELECT a.title, a.source, a.content, a.url
            FROM articles a
            LEFT JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND ('research_report' = ANY(COALESCE(s.topics, ARRAY[]::text[]))
                   OR a.source IN ('JLL', 'CBRE', 'Cushman & Wakefield', 'Savills', 'Colliers'))
            ORDER BY a.published_at DESC
            LIMIT 5
        """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Get video/podcast content
        video_rows = db.execute(text("""
            SELECT a.title, a.source, a.content, a.url, s.composite_score
            FROM articles a
            LEFT JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND 'video_content' = ANY(COALESCE(s.topics, ARRAY[]::text[]))
            ORDER BY COALESCE(s.composite_score, 0) DESC
            LIMIT 5
        """), {"cutoff": cutoff.isoformat()}).mappings().all()
        
        # Format sources for LLM
        sources_text = "=== NEWS ARTICLES ===\n"
        for i, row in enumerate(news_rows, 1):
            sources_text += f"\n{i}. {row['title']} ({row['source']})\n"
            sources_text += f"   Score: {row.get('composite_score', 0)}\n"
            sources_text += f"   Topics: {row.get('topics', [])}\n"
            sources_text += f"   Content: {row['content'][:500]}...\n"
        
        sources_text += "\n\n=== RESEARCH REPORTS ===\n"
        for i, row in enumerate(research_rows, 1):
            sources_text += f"\n{i}. {row['title']} ({row['source']})\n"
            sources_text += f"   Content: {row['content'][:800]}...\n"
        
        sources_text += "\n\n=== VIDEO/PODCAST CONTENT ===\n"
        for i, row in enumerate(video_rows, 1):
            sources_text += f"\n{i}. {row['title']} ({row['source']})\n"
            sources_text += f"   URL: {row['url']}\n"
            sources_text += f"   Transcript excerpt: {row['content'][:400]}...\n"
        
        # Call LLM for synthesis
        prompt = SYNTHESIS_PROMPT.format(sources=sources_text)
        
        try:
            synthesis = call_llm(prompt, max_tokens=800)
            
            # Parse the synthesis response
            result = {
                "ok": True,
                "type": "narrative_brief",
                "date": datetime.now(timezone.utc).date().isoformat(),
                "synthesis": synthesis,
                "sources_used": {
                    "news_count": len(news_rows),
                    "research_count": len(research_rows),
                    "video_count": len(video_rows)
                }
            }
            
            return result
            
        except Exception as e:
            print(f"[synthesis] LLM call failed: {e}")
            # Fallback to basic summary
            return {
                "ok": False,
                "error": "Synthesis failed",
                "sources_available": {
                    "news": len(news_rows),
                    "research": len(research_rows),
                    "videos": len(video_rows)
                }
            }
    
    finally:
        db.close()

def get_recommended_content(content_type: str = "video") -> Optional[Dict[str, Any]]:
    """Get the top recommended video or podcast for the day"""
    
    db = SessionLocal()
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    
    try:
        row = db.execute(text("""
            SELECT a.title, a.source, a.url, a.summary_raw, s.composite_score, s.topics
            FROM articles a
            JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND 'video_content' = ANY(s.topics)
            ORDER BY s.composite_score DESC
            LIMIT 1
        """), {"cutoff": cutoff.isoformat()}).mappings().fetchone()
        
        if row:
            return {
                "title": row['title'],
                "source": row['source'],
                "url": row['url'],
                "summary": row['summary_raw'],
                "score": row['composite_score'],
                "topics": row['topics']
            }
        
        return None
    
    finally:
        db.close()

def run():
    """Generate and return narrative synthesis"""
    return synthesize_daily_narrative(days_back=1)
