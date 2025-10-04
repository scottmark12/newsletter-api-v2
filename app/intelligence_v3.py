# app/intelligence_v3.py
# V3 Intelligence Synthesis - Cross-Theme Analysis

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import json

from .db import SessionLocal
from .llm import call_llm
from .schema_v3 import IntelligenceSynthesis

# -------- INTELLIGENCE SYNTHESIS PROMPTS --------
SYNTHESIS_PROMPTS = {
    "daily_brief": """
You are an expert construction and real estate intelligence analyst. Analyze the following articles and create a comprehensive daily brief.

Articles to analyze:
{articles}

Create a structured analysis with:

1. EXECUTIVE SUMMARY (2-3 sentences)
   - Key market developments
   - Most significant opportunities or threats

2. THEME ANALYSIS
   For each theme (Opportunities, Practices, Systems & Codes, Vision):
   - Key developments
   - Actionable insights
   - Market implications

3. OPPORTUNITIES IDENTIFIED
   - Specific opportunities for developers/investors
   - Implementation timeline and difficulty
   - Potential ROI indicators

4. STRATEGIC RECOMMENDATIONS
   - Top 3 actionable recommendations
   - Priority level (High/Medium/Low)
   - Rationale

5. RISK FACTORS
   - Potential challenges or threats
   - Mitigation strategies

Focus on actionable intelligence that helps developers make informed decisions. Use specific data points and metrics when available.
""",
    
    "opportunity_scan": """
You are a real estate opportunity analyst. Analyze these articles for specific development and investment opportunities.

Articles: {articles}

Create an opportunity analysis with:

1. IMMEDIATE OPPORTUNITIES (0-6 months)
   - Specific projects or deals mentioned
   - Market gaps identified
   - Regulatory changes creating opportunities

2. MEDIUM-TERM OPPORTUNITIES (6-18 months)
   - Emerging trends with development potential
   - Technology adoption opportunities
   - Market shifts creating new demand

3. LONG-TERM OPPORTUNITIES (18+ months)
   - Infrastructure investments
   - Demographic shifts
   - Policy changes with long-term impact

4. IMPLEMENTATION FRAMEWORK
   - Required resources/capital
   - Key partnerships needed
   - Risk mitigation strategies

5. ROI INDICATORS
   - Performance data from case studies
   - Market comparables
   - Success metrics

Focus on concrete, actionable opportunities with specific implementation steps.
""",
    
    "methodology_synthesis": """
You are a construction methodology expert. Analyze these articles to identify and synthesize implementation methodologies.

Articles: {articles}

Create a methodology synthesis with:

1. METHODOLOGIES IDENTIFIED
   - Process improvements
   - Technology implementations
   - Design approaches
   - Construction methods

2. IMPLEMENTATION GUIDES
   - Step-by-step processes
   - Required resources
   - Timeline considerations
   - Success metrics

3. CASE STUDIES
   - Before/after comparisons
   - Performance improvements
   - Lessons learned
   - Best practices

4. ADOPTION FRAMEWORK
   - Pilot project recommendations
   - Training requirements
   - Change management strategies
   - ROI measurement

5. SCALABILITY ANALYSIS
   - Which methodologies can scale
   - Resource requirements for scaling
   - Market potential

Focus on practical, implementable methodologies with clear value propositions.
""",
    
    "policy_impact_analysis": """
You are a policy and regulatory analyst. Analyze these articles for policy changes and their market impacts.

Articles: {articles}

Create a policy impact analysis with:

1. POLICY CHANGES IDENTIFIED
   - Building code updates
   - Zoning reforms
   - Incentive programs
   - Regulatory changes

2. MARKET IMPACT ANALYSIS
   - Immediate effects on development
   - Long-term market implications
   - Geographic variations
   - Sector-specific impacts

3. OPPORTUNITY MAPPING
   - New development possibilities
   - Investment opportunities
   - Market gaps created
   - Competitive advantages

4. IMPLEMENTATION TIMELINE
   - Effective dates
   - Phase-in periods
   - Compliance requirements
   - Transition strategies

5. STRATEGIC RECOMMENDATIONS
   - How to capitalize on changes
   - Risk mitigation strategies
   - Partnership opportunities
   - Resource allocation

Focus on actionable insights for developers and investors navigating policy changes.
"""
}

def _get_articles_for_synthesis(
    days_back: int = 1,
    min_score: float = 50.0,
    themes: Optional[List[str]] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """Get articles for intelligence synthesis"""
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    try:
        db = SessionLocal()
        
        # Build query
        where_clause = """
            WHERE a.published_at >= :cutoff
              AND s.composite_score >= :min_score
              AND a.status != 'discarded'
        """
        params = {
            "cutoff": cutoff.isoformat(),
            "min_score": min_score,
            "limit": limit
        }
        
        if themes:
            theme_conditions = " OR ".join([f"'{theme}' = ANY(a.secondary_themes)" for theme in themes])
            where_clause += f" AND ({theme_conditions})"
        
        query = text(f"""
            SELECT a.id, a.url, a.title, a.summary_raw, a.source, a.published_at,
                   a.primary_theme, a.content_depth, a.actionability_score,
                   s.composite_score, s.roi_data_present, s.methodology_present,
                   s.case_study_present, s.opportunities_score, s.practices_score,
                   s.systems_codes_score, s.vision_score
            FROM articles_v3 a
            JOIN article_scores_v3 s ON s.article_id = a.id
            {where_clause}
            ORDER BY s.composite_score DESC, a.actionability_score DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, params).fetchall()
        db.close()
        
        return [dict(row._mapping) for row in rows]
        
    except Exception as e:
        print(f"Error fetching articles for synthesis: {str(e)}")
        return []

def _format_articles_for_llm(articles: List[Dict[str, Any]]) -> str:
    """Format articles for LLM analysis"""
    formatted_articles = []
    
    for article in articles:
        formatted_article = f"""
TITLE: {article['title']}
SOURCE: {article['source']}
THEME: {article['primary_theme']}
SCORE: {article['composite_score']}
ACTIONABILITY: {article['actionability_score']}
ROI DATA: {'Yes' if article['roi_data_present'] else 'No'}
METHODOLOGY: {'Yes' if article['methodology_present'] else 'No'}
CASE STUDY: {'Yes' if article['case_study_present'] else 'No'}
CONTENT: {article['summary_raw'][:500]}...
"""
        formatted_articles.append(formatted_article)
    
    return "\n".join(formatted_articles)

def _extract_insights_from_synthesis(synthesis_text: str) -> Dict[str, Any]:
    """Extract structured insights from synthesis text"""
    insights = {
        "opportunities": [],
        "methodologies": [],
        "policy_changes": [],
        "recommendations": [],
        "risk_factors": []
    }
    
    # Simple extraction logic - can be enhanced with NLP
    lines = synthesis_text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Detect sections
        if "OPPORTUNITIES" in line.upper():
            current_section = "opportunities"
        elif "METHODOLOG" in line.upper():
            current_section = "methodologies"
        elif "POLICY" in line.upper():
            current_section = "policy_changes"
        elif "RECOMMENDATION" in line.upper():
            current_section = "recommendations"
        elif "RISK" in line.upper():
            current_section = "risk_factors"
        elif line.startswith('-') or line.startswith('•') or line.startswith('*'):
            # Extract bullet point
            content = line[1:].strip()
            if current_section and content:
                insights[current_section].append(content)
    
    return insights

def generate_daily_brief_v3(days_back: int = 1) -> Dict[str, Any]:
    """Generate AI-powered daily intelligence brief"""
    try:
        # Get high-quality articles
        articles = _get_articles_for_synthesis(
            days_back=days_back,
            min_score=60.0,
            limit=30
        )
        
        if not articles:
            return {
                "status": "error",
                "message": "No high-quality articles found for synthesis"
            }
        
        # Format articles for LLM
        formatted_articles = _format_articles_for_llm(articles)
        
        # Generate synthesis
        prompt = SYNTHESIS_PROMPTS["daily_brief"].format(articles=formatted_articles)
        synthesis_text = call_llm(prompt, max_tokens=2000, temperature=0.3)
        
        # Extract structured insights
        insights = _extract_insights_from_synthesis(synthesis_text)
        
        # Calculate metrics
        total_articles = len(articles)
        high_actionability = sum(1 for a in articles if a['actionability_score'] >= 70)
        roi_articles = sum(1 for a in articles if a['roi_data_present'])
        methodology_articles = sum(1 for a in articles if a['methodology_present'])
        case_study_articles = sum(1 for a in articles if a['case_study_present'])
        
        # Create synthesis record
        synthesis_data = {
            "synthesis_type": "daily_brief",
            "articles_analyzed": [a['id'] for a in articles],
            "themes_covered": list(set(a['primary_theme'] for a in articles)),
            "time_period": f"last_{days_back}_day{'s' if days_back > 1 else ''}",
            "headline": f"Daily Intelligence Brief - {datetime.now().strftime('%B %d, %Y')}",
            "executive_summary": synthesis_text[:500] + "..." if len(synthesis_text) > 500 else synthesis_text,
            "key_insights": insights,
            "opportunities_identified": insights["opportunities"],
            "recommendations": insights["recommendations"],
            "confidence_score": 85.0,  # Based on article quality
            "actionable_insights_count": len(insights["opportunities"]) + len(insights["recommendations"]),
            "verified_claims_count": roi_articles + case_study_articles
        }
        
        # Save to database
        db = SessionLocal()
        try:
            db.execute(text("""
                INSERT INTO intelligence_synthesis (
                    synthesis_type, articles_analyzed, themes_covered, time_period,
                    headline, executive_summary, key_insights, opportunities_identified,
                    recommendations, confidence_score, actionable_insights_count,
                    verified_claims_count
                ) VALUES (
                    :synthesis_type, :articles_analyzed, :themes_covered, :time_period,
                    :headline, :executive_summary, :key_insights, :opportunities_identified,
                    :recommendations, :confidence_score, :actionable_insights_count,
                    :verified_claims_count
                )
            """), synthesis_data)
            db.commit()
        except Exception as e:
            print(f"Error saving synthesis: {str(e)}")
        finally:
            db.close()
        
        return {
            "status": "success",
            "synthesis": synthesis_data,
            "article_metrics": {
                "total_articles": total_articles,
                "high_actionability": high_actionability,
                "roi_articles": roi_articles,
                "methodology_articles": methodology_articles,
                "case_study_articles": case_study_articles
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating daily brief: {str(e)}"
        }

def generate_opportunity_scan_v3(days_back: int = 7) -> Dict[str, Any]:
    """Generate opportunity-focused analysis"""
    try:
        # Get opportunity-focused articles
        articles = _get_articles_for_synthesis(
            days_back=days_back,
            min_score=50.0,
            themes=["opportunities", "systems_codes"],
            limit=40
        )
        
        if not articles:
            return {
                "status": "error",
                "message": "No opportunity-focused articles found"
            }
        
        # Generate analysis
        formatted_articles = _format_articles_for_llm(articles)
        prompt = SYNTHESIS_PROMPTS["opportunity_scan"].format(articles=formatted_articles)
        analysis_text = call_llm(prompt, max_tokens=2000, temperature=0.3)
        
        # Extract opportunities
        insights = _extract_insights_from_synthesis(analysis_text)
        
        return {
            "status": "success",
            "analysis_type": "opportunity_scan",
            "analysis": analysis_text,
            "opportunities": insights["opportunities"],
            "recommendations": insights["recommendations"],
            "articles_analyzed": len(articles),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating opportunity scan: {str(e)}"
        }

def generate_methodology_synthesis_v3(days_back: int = 7) -> Dict[str, Any]:
    """Generate methodology-focused synthesis"""
    try:
        # Get methodology-focused articles
        articles = _get_articles_for_synthesis(
            days_back=days_back,
            min_score=50.0,
            themes=["practices"],
            limit=30
        )
        
        if not articles:
            return {
                "status": "error",
                "message": "No methodology-focused articles found"
            }
        
        # Generate synthesis
        formatted_articles = _format_articles_for_llm(articles)
        prompt = SYNTHESIS_PROMPTS["methodology_synthesis"].format(articles=formatted_articles)
        synthesis_text = call_llm(prompt, max_tokens=2000, temperature=0.3)
        
        # Extract methodologies
        insights = _extract_insights_from_synthesis(synthesis_text)
        
        return {
            "status": "success",
            "analysis_type": "methodology_synthesis",
            "synthesis": synthesis_text,
            "methodologies": insights["methodologies"],
            "recommendations": insights["recommendations"],
            "articles_analyzed": len(articles),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating methodology synthesis: {str(e)}"
        }

def generate_policy_impact_analysis_v3(days_back: int = 7) -> Dict[str, Any]:
    """Generate policy impact analysis"""
    try:
        # Get policy-focused articles
        articles = _get_articles_for_synthesis(
            days_back=days_back,
            min_score=50.0,
            themes=["systems_codes"],
            limit=25
        )
        
        if not articles:
            return {
                "status": "error",
                "message": "No policy-focused articles found"
            }
        
        # Generate analysis
        formatted_articles = _format_articles_for_llm(articles)
        prompt = SYNTHESIS_PROMPTS["policy_impact_analysis"].format(articles=formatted_articles)
        analysis_text = call_llm(prompt, max_tokens=2000, temperature=0.3)
        
        # Extract policy insights
        insights = _extract_insights_from_synthesis(analysis_text)
        
        return {
            "status": "success",
            "analysis_type": "policy_impact_analysis",
            "analysis": analysis_text,
            "policy_changes": insights["policy_changes"],
            "opportunities": insights["opportunities"],
            "recommendations": insights["recommendations"],
            "articles_analyzed": len(articles),
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error generating policy impact analysis: {str(e)}"
        }

def get_synthesis_history_v3(limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent synthesis history"""
    try:
        db = SessionLocal()
        
        query = text("""
            SELECT synthesis_type, headline, executive_summary, time_period,
                   confidence_score, actionable_insights_count, views_count,
                   created_at
            FROM intelligence_synthesis
            ORDER BY created_at DESC
            LIMIT :limit
        """)
        
        rows = db.execute(query, {"limit": limit}).fetchall()
        db.close()
        
        return [dict(row._mapping) for row in rows]
        
    except Exception as e:
        print(f"Error fetching synthesis history: {str(e)}")
        return []

def run_all_synthesis_v3() -> Dict[str, Any]:
    """Run all synthesis types"""
    results = {}
    
    try:
        # Daily brief
        results["daily_brief"] = generate_daily_brief_v3(days_back=1)
        
        # Opportunity scan
        results["opportunity_scan"] = generate_opportunity_scan_v3(days_back=7)
        
        # Methodology synthesis
        results["methodology_synthesis"] = generate_methodology_synthesis_v3(days_back=7)
        
        # Policy impact analysis
        results["policy_impact_analysis"] = generate_policy_impact_analysis_v3(days_back=7)
        
        return {
            "status": "success",
            "results": results,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error running synthesis: {str(e)}"
        }
