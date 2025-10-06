"""
FastAPI application for Newsletter API v4
Clean, modern API with comprehensive endpoints
"""

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, func, desc, and_
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta
import asyncio
import json

from .config import get_config
from .models import Base, Article, ArticleScore, ArticleInsight, Video, ContentSource
from .scoring import score_article_v4, extract_insights_v4
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
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get articles in the Opportunities category"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        ArticleScore.opportunities_score > 0
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
            "published_at": article.published_at.isoformat() if article.published_at else None,
            "score": {
                "opportunities": score.opportunities_score,
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/practices")
async def get_practices(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get articles in the Practices category"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        ArticleScore.practices_score > 0
    ).order_by(
        desc(ArticleScore.practices_score)
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
                "practices": score.practices_score,
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/systems-codes")
async def get_systems_codes(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get articles in the Systems & Codes category"""
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
    ).filter(
        ArticleScore.systems_score > 0
    ).order_by(
        desc(ArticleScore.systems_score)
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
                "systems": score.systems_score,
                "total": score.total_score
            },
            "themes": article.themes
        })
    
    return {"articles": result, "count": len(result)}


@app.get("/api/v4/vision")
async def get_vision(
    limit: int = Query(10, ge=1, le=50),
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
    limit: int = Query(10, ge=1, le=50),
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
    limit: int = Query(15, ge=1, le=50),
    db: Session = Depends(get_db)
):
    """Get homepage content with featured video"""
    # Get top articles
    articles = db.query(Article, ArticleScore).join(
        ArticleScore, Article.id == ArticleScore.article_id
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
    limit: int = Query(10, ge=1, le=50),
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
    limit: int = Query(10, ge=1, le=50),
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
    limit: int = Query(10, ge=1, le=50),
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
                tags=article_data.tags
            )
            
            db.add(article)
            db.flush()  # Get the ID
            
            # Score the article
            scoring_result = score_article_v4(
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
