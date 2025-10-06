"""
FastAPI application for Newsletter API v4
Clean, modern API with comprehensive endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, func, desc, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import asyncio
import json

from .config import get_config
from .models import Base, Article, ArticleScore, ArticleInsight, Video, ContentSource
from .scoring import score_article_v4, extract_insights_v4
from .enhanced_scoring import score_article_enhanced
from .data_collectors import collect_all_articles
from .video_processor import find_construction_videos, process_youtube_video

# Initialize configuration
config = get_config()

# Create database engine and session
from .database import create_database_engine, get_session_maker, create_tables

engine = create_database_engine()
SessionLocal = get_session_maker()

# Create tables
create_tables()

# Initialize FastAPI app
app = FastAPI(
    title=config.api.title,
    description=config.api.description,
    version=config.api.version,
    debug=config.api.debug
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": config.api.title,
        "description": config.api.description,
        "version": config.api.version,
        "status": "running",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "v4 API successfully deployed!"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": config.api.version
    }


# ============================================================================
# THEME CATEGORY ENDPOINTS
# ============================================================================

@app.get("/api/v4/opportunities")
async def get_opportunities(
    limit: int = Query(10, ge=1, le=500),
    min_score: float = Query(0.3, ge=0.0, le=1.0),
    hours: int = Query(168, ge=1, le=720, description="Only articles from last N hours"),
    db: Session = Depends(get_db)
):
    """Get high-relevance articles in the Opportunities category"""
    # Calculate cutoff time for recent articles
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Enhanced query with relevance filtering and better ranking
    # Include both opportunities and systems & codes articles
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        and_(
            or_(
                ArticleScore.opportunities_score >= min_score,
                ArticleScore.systems_score >= min_score  # Include systems & codes articles
            ),
            ArticleScore.total_score >= 0.2,  # Minimum overall quality
            or_(Article.content.isnot(None), Article.summary.isnot(None)),
            or_(func.length(Article.content) > 200, func.length(Article.summary) > 200),  # Minimum content length
            Article.published_at >= cutoff_time  # Only recent articles
        )
    ).order_by(
        desc(ArticleScore.total_score),  # Rank by total score first
        desc(ArticleScore.opportunities_score)  # Then by opportunities score
    ).limit(limit * 2).all()  # Get more to filter further
    
    # Additional relevance filtering
    relevant_articles = []
    for article, score in articles:
        # Check for high-value content indicators
        content_lower = (article.content or "").lower()
        title_lower = article.title.lower()
        
        # Look for transformation/success indicators
        transformation_indicators = [
            'turned into', 'grew from', 'scaled up', 'transformed', 'converted',
            'success story', 'case study', 'wealth creation', 'portfolio growth',
            'investment returns', 'market opportunity', 'emerging market'
        ]
        
        has_transformation = any(indicator in content_lower or indicator in title_lower 
                               for indicator in transformation_indicators)
        
        # Look for actionable insights
        insight_indicators = [
            'how to', 'framework', 'strategy', 'approach', 'methodology',
            'best practices', 'lessons learned', 'insights', 'analysis'
        ]
        
        has_insights = any(indicator in content_lower or indicator in title_lower 
                          for indicator in insight_indicators)
        
        # Include if meets relevance criteria
        if has_transformation or has_insights or score.total_score >= 0.2:
            relevant_articles.append((article, score))
            
        if len(relevant_articles) >= limit:
            break
    
    articles = relevant_articles[:limit]
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "opportunities": score.opportunities_score,
                "systems": score.systems_score,  # Show systems score too
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/practices")
async def get_practices(
    limit: int = Query(10, ge=1, le=500),
    min_score: float = Query(0.3, ge=0.0, le=1.0),
    hours: int = Query(168, ge=1, le=720, description="Only articles from last N hours"),
    db: Session = Depends(get_db)
):
    """Get high-relevance articles in the Practices category"""
    # Calculate cutoff time for recent articles
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Enhanced query with relevance filtering for actionable insights
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        and_(
            ArticleScore.practices_score >= min_score,
            ArticleScore.total_score >= 0.2,
            or_(Article.content.isnot(None), Article.summary.isnot(None)),
            or_(func.length(Article.content) > 200, func.length(Article.summary) > 200),
            Article.published_at >= cutoff_time  # Only recent articles
        )
    ).order_by(
        desc(ArticleScore.total_score),
        desc(ArticleScore.practices_score)
    ).limit(limit * 2).all()
    
    # Filter for actionable practices and methodologies
    relevant_articles = []
    for article, score in articles:
        content_lower = (article.content or "").lower()
        title_lower = article.title.lower()
        
        # Look for methodology/practice indicators
        practice_indicators = [
            'how to', 'step by step', 'methodology', 'process', 'workflow',
            'best practices', 'innovative approach', 'efficiency gains',
            'productivity improvement', 'cutting edge', 'advanced technique',
            'implementation', 'framework', 'strategy'
        ]
        
        has_practices = any(indicator in content_lower or indicator in title_lower 
                          for indicator in practice_indicators)
        
        # Look for innovation indicators
        innovation_indicators = [
            'breakthrough', 'innovation', 'new method', 'revolutionary',
            'advanced', 'next generation', 'futuristic', 'emerging technology'
        ]
        
        has_innovation = any(indicator in content_lower or indicator in title_lower 
                           for indicator in innovation_indicators)
        
        if has_practices or has_innovation or score.total_score >= 0.2:
            relevant_articles.append((article, score))
            
        if len(relevant_articles) >= limit:
            break
    
    articles = relevant_articles[:limit]
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "practices": score.practices_score,
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/systems-codes")
async def get_systems_codes(
    limit: int = Query(10, ge=1, le=500),
    min_score: float = Query(0.1, ge=0.0, le=1.0),
    hours: int = Query(168, ge=1, le=720, description="Only articles from last N hours"),
    db: Session = Depends(get_db)
):
    """Get articles in the Systems & Codes category - redirected to Opportunities for better visibility"""
    # Calculate cutoff time for recent articles
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Get Systems & Codes articles but treat them as opportunities for better visibility
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        and_(
            ArticleScore.systems_score >= min_score,
            ArticleScore.total_score >= 0.2,  # Minimum overall quality
            or_(Article.content.isnot(None), Article.summary.isnot(None)),
            or_(func.length(Article.content) > 200, func.length(Article.summary) > 200),  # Minimum content length
            Article.published_at >= cutoff_time  # Only recent articles
        )
    ).order_by(
        desc(ArticleScore.total_score),  # Rank by total score first
        desc(ArticleScore.systems_score)  # Then by systems score
    ).limit(limit * 2).all()  # Get more to filter further
    
    # Additional relevance filtering for systems/codes content
    relevant_articles = []
    for article, score in articles:
        # Check for high-value content indicators
        content_lower = (article.content or "").lower()
        title_lower = article.title.lower()
        
        # Look for policy/regulation indicators
        policy_indicators = [
            'policy', 'regulation', 'code', 'zoning', 'incentive', 'reform',
            'legislation', 'compliance', 'standard', 'framework', 'guideline',
            'permit', 'approval', 'government', 'municipal', 'federal'
        ]
        
        has_policy = any(indicator in content_lower or indicator in title_lower 
                        for indicator in policy_indicators)
        
        # Look for opportunity indicators
        opportunity_indicators = [
            'opportunity', 'investment', 'growth', 'development', 'market',
            'potential', 'emerging', 'new', 'breakthrough', 'innovation'
        ]
        
        has_opportunity = any(indicator in content_lower or indicator in title_lower 
                             for indicator in opportunity_indicators)
        
        if has_policy or has_opportunity or score.total_score >= 0.2:
            relevant_articles.append((article, score))
            
        if len(relevant_articles) >= limit:
            break
    
    articles = relevant_articles[:limit]
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "systems": score.systems_score,
                "opportunities": score.opportunities_score,  # Show both scores
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/vision")
async def get_vision(
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get articles in the Vision category"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        ArticleScore.vision_score > 0
    ).order_by(
        desc(ArticleScore.vision_score)
    ).limit(limit).all()
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "vision": score.vision_score,
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


# ============================================================================
# MAIN ENDPOINTS
# ============================================================================

@app.get("/api/v4/top-stories")
async def get_top_stories(
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get top stories across all categories"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).order_by(
        desc(ArticleScore.total_score)
    ).limit(limit).all()
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "total": score.total_score,
                "opportunities": score.opportunities_score,
                "practices": score.practices_score,
                "systems": score.systems_score,
                "vision": score.vision_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/home")
async def get_home_page(
    limit: int = Query(15, ge=1, le=500),
    hours: int = Query(168, ge=1, le=720, description="Only articles from last N hours"),
    db: Session = Depends(get_db)
):
    """Get homepage content with featured video"""
    # Calculate cutoff time
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
    
    # Get top articles from the specified time period
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        Article.published_at >= cutoff_time
    ).order_by(
        desc(ArticleScore.total_score)
    ).limit(limit).all()
    
    # Get featured video
    featured_video = db.query(Video).order_by(desc(Video.total_score)).first()
    
    article_list = []
    for article, score in articles:
        article_list.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "total": score.total_score,
                "opportunities": score.opportunities_score,
                "practices": score.practices_score,
                "systems": score.systems_score,
                "vision": score.vision_score
            },
            "themes": article.themes
        })
    
    video_data = None
    if featured_video:
        video_data = {
            "id": featured_video.id,
            "title": featured_video.title,
            "youtube_id": featured_video.youtube_id,
            "url": featured_video.url,
            "thumbnail_url": featured_video.thumbnail_url,
            "channel_name": featured_video.channel_name,
            "duration": featured_video.duration,
            "view_count": featured_video.view_count,
            "score": featured_video.total_score,
            "summary": featured_video.summary
        }
    
    return {
        "articles": article_list,
        "featured_video": video_data,
        "count": len(article_list)
    }


# ============================================================================
# INTELLIGENCE ENDPOINTS
# ============================================================================

@app.get("/api/v4/insights/high-impact")
async def get_high_impact_insights(
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get high-impact insights from articles"""
    insights = db.query(ArticleInsight).join(
        Article, ArticleInsight.article_id == Article.id
    ).order_by(
        desc(ArticleInsight.confidence_score)
    ).limit(limit).all()
    
    result = []
    for insight in insights:
        result.append({
            "id": insight.id,
            "insight_text": insight.insight_text,
            "insight_type": insight.insight_type,
            "confidence_score": insight.confidence_score,
            "supporting_evidence": insight.supporting_evidence,
            "article": {
                "id": insight.article.id,
                "title": insight.article.title,
                "url": insight.article.url,
                "source": insight.article.source
            },
            "created_at": insight.created_at.isoformat()
        })
    
    return {"insights": result, "count": len(result)}


@app.get("/api/v4/insights/methodology")
async def get_methodology_insights(
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get methodology and process insights"""
    insights = db.query(ArticleInsight).join(
        Article, ArticleInsight.article_id == Article.id
    ).filter(
        ArticleInsight.insight_type == "practices"
    ).order_by(
        desc(ArticleInsight.confidence_score)
    ).limit(limit).all()
    
    result = []
    for insight in insights:
        result.append({
            "id": insight.id,
            "insight_text": insight.insight_text,
            "confidence_score": insight.confidence_score,
            "supporting_evidence": insight.supporting_evidence,
            "article": {
                "id": insight.article.id,
                "title": insight.article.title,
                "url": insight.article.url,
                "source": insight.article.source
            }
        })
    
    return {"insights": result, "count": len(result)}


# ============================================================================
# DEVELOPER ENDPOINTS
# ============================================================================

@app.get("/api/v4/developer/opportunities")
async def get_developer_opportunities(
    limit: int = Query(10, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """Get developer and technology opportunities"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        and_(
            ArticleScore.opportunities_score > 0,
            Article.content.ilike("%technology%")
        )
    ).order_by(
        desc(ArticleScore.opportunities_score)
    ).limit(limit).all()
    
    result = []
    for article, score in articles:
        result.append({
            "id": article.id,
            "title": article.title,
            "url": article.url,
            "summary": article.summary,
            "source": article.source,
            "score": {
                "opportunities": score.opportunities_score,
                "total": score.total_score
            }
        })
    
    return {"opportunities": result, "count": len(result)}


# ============================================================================
# SYNTHESIS ENDPOINTS
# ============================================================================

@app.get("/api/v4/synthesis/daily-brief")
async def get_daily_brief(
    days_back: int = Query(1, ge=1, le=7),
    db: Session = Depends(get_db)
):
    """Get AI-synthesized daily brief"""
    # Get recent articles
    since_date = datetime.now(timezone.utc) - timedelta(days=days_back)
    
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        Article.created_at >= since_date
    ).order_by(
        desc(ArticleScore.total_score)
    ).limit(20).all()
    
    # Get recent insights
    insights = db.query(ArticleInsight).join(
        Article, ArticleInsight.article_id == Article.id
    ).filter(
        Article.created_at >= since_date
    ).order_by(
        desc(ArticleInsight.confidence_score)
    ).limit(10).all()
    
    # Create brief summary
    brief_summary = f"Daily Brief for {days_back} day(s) back:\n\n"
    brief_summary += f"Found {len(articles)} articles and {len(insights)} insights.\n\n"
    
    if articles:
        brief_summary += "Top Stories:\n"
        for i, (article, score) in enumerate(articles[:5], 1):
            brief_summary += f"{i}. {article.title} (Score: {score.total_score:.1f})\n"
    
    if insights:
        brief_summary += "\nKey Insights:\n"
        for i, insight in enumerate(insights[:3], 1):
            brief_summary += f"{i}. {insight.insight_text[:100]}...\n"
    
    return {
        "brief": brief_summary,
        "article_count": len(articles),
        "insight_count": len(insights),
        "period_days": days_back,
        "generated_at": datetime.now(timezone.utc).isoformat()
    }


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.post("/api/v4/admin/collect")
async def collect_articles():
    """Collect articles from all sources"""
    try:
        # Run data collection
        articles = await collect_all_articles()
        
        # Store in database
        db = SessionLocal()
        stored_count = 0
        
        for article_data in articles:
            # Check if article already exists
            existing = db.query(Article).filter(Article.url == article_data.url).first()
            if existing:
                continue
            
            # Create new article
            article = Article(
                title=article_data.title,
                url=article_data.url,
                content=article_data.content,
                summary=article_data.summary,
                source=article_data.source,
                author=article_data.author,
                published_at=article_data.published_at,
                themes=json.dumps(getattr(article_data, 'tags', []) or [])
            )
            
            db.add(article)
            db.flush()  # Get the ID
            
            # Score the article with enhanced system
            scoring_result = score_article_enhanced(
                article_data.title,
                article_data.content or "",
                article_data.source,
                article_data.url
            )
            
            # Store score
            score = ArticleScore(
                article_id=article.id,
                total_score=scoring_result.total_score,
                opportunities_score=scoring_result.theme_scores.get("opportunities", 0),
                practices_score=scoring_result.theme_scores.get("practices", 0),
                systems_score=scoring_result.theme_scores.get("systems", 0),
                vision_score=scoring_result.theme_scores.get("vision", 0),
                insight_quality_score=scoring_result.insight_quality,
                narrative_signal_score=scoring_result.narrative_signal,
                source_credibility_score=scoring_result.source_credibility,
                scoring_details=scoring_result.scoring_details
            )
            
            db.add(score)
            
            # Extract insights
            insights = extract_insights_v4(
                article_data.content or "",
                scoring_result.theme_scores
            )
            
            for insight_data in insights:
                insight = ArticleInsight(
                    article_id=article.id,
                    insight_text=insight_data["text"],
                    insight_type=insight_data["theme"],
                    confidence_score=insight_data["confidence"]
                )
                db.add(insight)
            
            stored_count += 1
        
        db.commit()
        db.close()
        
        return {
            "ok": True,
            "message": f"Collected and stored {stored_count} new articles",
            "total_collected": len(articles),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v4/admin/collect-corporate")
async def collect_corporate_articles():
    """Collect articles from corporate insights only"""
    try:
        from .data_collectors import collect_corporate_articles
        
        # Run corporate data collection
        articles = await collect_corporate_articles()
        
        # Store in database
        db = SessionLocal()
        stored_count = 0
        
        for article_data in articles:
            # Check if article already exists
            existing = db.query(Article).filter(Article.url == article_data.url).first()
            if existing:
                continue
            
            # Create new article
            article = Article(
                title=article_data.title,
                url=article_data.url,
                content=article_data.content or "",
                summary=article_data.summary or "",
                source=article_data.source,
                author=article_data.author,
                published_at=article_data.published_at,
                word_count=len(article_data.content.split()) if article_data.content else 0,
                reading_time=len(article_data.content.split()) // 200 if article_data.content else 0,
                themes=json.dumps(getattr(article_data, 'tags', []) or []),
                keywords=json.dumps([])
            )
            
            db.add(article)
            db.flush()  # Get the ID
            
            # Score the article with enhanced system
            scoring_result = score_article_enhanced(
                article_data.title,
                article_data.content or "",
                article_data.source,
                article_data.url
            )
            
            # Store score
            score = ArticleScore(
                article_id=article.id,
                total_score=scoring_result.total_score,
                opportunities_score=scoring_result.theme_scores.get('opportunities', 0),
                practices_score=scoring_result.theme_scores.get('practices', 0),
                systems_score=scoring_result.theme_scores.get('systems', 0),
                vision_score=scoring_result.theme_scores.get('vision', 0),
                insight_quality_score=scoring_result.insight_quality,
                narrative_signal_score=scoring_result.narrative_signal,
                source_credibility_score=scoring_result.source_credibility,
                scoring_details=json.dumps(scoring_result.scoring_details)
            )
            
            db.add(score)
            stored_count += 1
        
        db.commit()
        db.close()
        
        return {
            "ok": True,
            "message": f"Collected and stored {stored_count} new corporate articles",
            "total_collected": len(articles),
            "source": "corporate_insights",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/v4/admin/clear-articles")
async def clear_all_articles():
    """Clear all articles and scores from the database"""
    try:
        db = SessionLocal()
        
        # Delete in correct order due to foreign key constraints
        db.query(ArticleInsight).delete()
        db.query(ArticleScore).delete()
        db.query(Article).delete()
        
        db.commit()
        db.close()
        
        return {
            "ok": True,
            "message": "All articles and scores cleared from database",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v4/admin/score")
async def run_scoring():
    """Run scoring on all unscored articles"""
    try:
        db = SessionLocal()
        
        # Find articles without scores
        unscored_articles = db.query(Article).filter(
            ~Article.id.in_(
                db.query(ArticleScore.article_id)
            )
        ).all()
        
        scored_count = 0
        for article in unscored_articles:
            # Score the article
            scoring_result = score_article_v4(
                article.title,
                article.content or "",
                article.source,
                article.url
            )
            
            # Store score
            score = ArticleScore(
                article_id=article.id,
                total_score=scoring_result.total_score,
                opportunities_score=scoring_result.theme_scores.get("opportunities", 0),
                practices_score=scoring_result.theme_scores.get("practices", 0),
                systems_score=scoring_result.theme_scores.get("systems", 0),
                vision_score=scoring_result.theme_scores.get("vision", 0),
                insight_quality_score=scoring_result.insight_quality,
                narrative_signal_score=scoring_result.narrative_signal,
                source_credibility_score=scoring_result.source_credibility,
                scoring_details=scoring_result.scoring_details
            )
            
            db.add(score)
            scored_count += 1
        
        db.commit()
        db.close()
        
        return {
            "ok": True,
            "message": f"Scored {scored_count} articles",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v4/admin/process-videos")
async def process_videos():
    """Process and score YouTube videos"""
    try:
        # Find construction-related videos
        videos = await find_construction_videos()
        
        db = SessionLocal()
        processed_count = 0
        
        for video_result in videos:
            video_data = video_result["video_data"]
            scores = video_result["scores"]
            
            # Check if video already exists
            existing = db.query(Video).filter(Video.youtube_id == video_data.youtube_id).first()
            if existing:
                continue
            
            # Create new video record
            video = Video(
                title=video_data.title,
                youtube_id=video_data.youtube_id,
                url=video_data.url,
                thumbnail_url=video_data.thumbnail_url,
                channel_name=video_data.channel_name,
                duration=video_data.duration,
                view_count=video_data.view_count,
                published_at=video_data.published_at,
                transcript=video_data.transcript,
                summary=video_data.summary,
                relevance_score=scores["relevance_score"],
                quality_score=scores["content_score"],
                total_score=scores["total_score"]
            )
            
            db.add(video)
            processed_count += 1
        
        db.commit()
        db.close()
        
        return {
            "ok": True,
            "message": f"Processed {processed_count} videos",
            "total_found": len(videos),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v4/admin/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get admin statistics"""
    total_articles = db.query(Article).count()
    scored_articles = db.query(ArticleScore).count()
    total_videos = db.query(Video).count()
    total_insights = db.query(ArticleInsight).count()
    
    recent_articles = db.query(Article).filter(
        Article.created_at >= datetime.now(timezone.utc) - timedelta(days=1)
    ).count()
    
    return {
        "total_articles": total_articles,
        "scored_articles": scored_articles,
        "total_videos": total_videos,
        "total_insights": total_insights,
        "recent_articles_24h": recent_articles,
        "scoring_coverage": f"{(scored_articles / total_articles * 100):.1f}%" if total_articles > 0 else "0%"
    }


# ============================================================================
# STATIC FILE SERVING
# ============================================================================

@app.get("/website", response_class=HTMLResponse)
async def serve_website():
    """Serve the main website"""
    try:
        import os
        website_path = os.path.join(os.path.dirname(__file__), 'website.html')
        with open(website_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading website: {str(e)}"


@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the scoring dashboard"""
    try:
        import os
        dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard.html')
        with open(dashboard_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error loading dashboard: {str(e)}"


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
