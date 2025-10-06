"""
Newsletter API v4 Main API
Clean, modern FastAPI with 5 main endpoints and comprehensive functionality
"""

from fastapi import FastAPI, HTTPException, Query, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text, desc, and_
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone, timedelta
import logging

from .config import get_config, THEMES
from .models import Article, ArticleScore, ArticleInsight, VideoContent, get_session, init_database
from .scoring import run_scoring_batch
from .data_collectors import DataCollectionOrchestrator
from .video_processor import VideoIntegrationService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Newsletter API v4",
    description="Intelligent construction and real estate platform with video support",
    version="4.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Get configuration
config = get_config()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database dependency
def get_db():
    session = get_session(config.database.url)
    try:
        yield session
    finally:
        session.close()

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and run initial setup"""
    try:
        init_database(config.database.url)
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")

# ==================== MAIN ENDPOINTS ====================

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Newsletter API v4",
        "description": "Intelligent construction and real estate platform",
        "version": "4.0.0",
        "features": [
            "RSS feed collection",
            "Google Custom Search",
            "YouTube video analysis",
            "AI-powered scoring",
            "Theme-based categorization",
            "Video content integration"
        ],
        "main_endpoints": {
            "home": "/api/v4/home",
            "top_stories": "/api/v4/top-stories",
            "opportunities": "/api/v4/opportunities",
            "practices": "/api/v4/practices",
            "systems_codes": "/api/v4/systems-codes",
            "vision": "/api/v4/vision"
        },
        "admin_endpoints": {
            "collect_data": "/api/v4/admin/collect",
            "run_scoring": "/api/v4/admin/score",
            "process_videos": "/api/v4/admin/process-videos",
            "health": "/api/v4/health"
        },
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@app.get("/api/v4/home")
async def get_homepage_data(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(10, ge=1, le=50),
    include_videos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get homepage data with top articles from each theme and featured video"""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get top articles by theme
        theme_data = {}
        for theme_name, theme_config in THEMES.items():
            articles = db.query(Article).join(ArticleScore).filter(
                and_(
                    Article.primary_theme == theme_name,
                    Article.published_at >= cutoff,
                    Article.status != 'discarded',
                    ArticleScore.composite_score >= config.scoring.min_composite_score
                )
            ).order_by(desc(ArticleScore.composite_score)).limit(limit).all()
            
            theme_data[theme_name] = {
                "theme": theme_config,
                "articles": [_format_article_response(article) for article in articles],
                "count": len(articles)
            }
        
        # Get featured video if enabled
        featured_video = None
        if include_videos and config.enable_video_support:
            video_service = VideoIntegrationService()
            videos_by_theme = await video_service.get_videos_for_homepage()
            if videos_by_theme:
                # Get the highest scoring video
                best_video = max(videos_by_theme.values(), key=lambda v: v.get('actionability_score', 0))
                featured_video = best_video
        
        # Get overall stats
        stats = _get_overall_stats(db, cutoff)
        
        return {
            "ok": True,
            "endpoint": "homepage",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "filters": {
                "days": days,
                "limit": limit,
                "include_videos": include_videos
            },
            "stats": stats,
            "themes": theme_data,
            "featured_video": featured_video
        }
        
    except Exception as e:
        logger.error(f"Error getting homepage data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/top-stories")
async def get_top_stories(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(70.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get top stories across all themes based on composite score"""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get top articles across all themes
        articles = db.query(Article).join(ArticleScore).filter(
            and_(
                Article.published_at >= cutoff,
                Article.status != 'discarded',
                ArticleScore.composite_score >= min_score
            )
        ).order_by(desc(ArticleScore.composite_score)).limit(limit).all()
        
        # Format response
        formatted_articles = []
        for article in articles:
            article_data = _format_article_response(article, include_insights, db)
            formatted_articles.append(article_data)
        
        return {
            "ok": True,
            "endpoint": "top_stories",
            "description": "Highest scoring articles across all themes",
            "count": len(formatted_articles),
            "articles": formatted_articles,
            "filters": {
                "days": days,
                "limit": limit,
                "min_score": min_score,
                "include_insights": include_insights
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting top stories: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v4/opportunities")
async def get_opportunities(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True),
    include_videos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get opportunities articles - transformation stories and wealth-building examples"""
    return await _get_theme_articles(
        theme="opportunities",
        days=days,
        limit=limit,
        min_score=min_score,
        include_insights=include_insights,
        include_videos=include_videos,
        db=db
    )

@app.get("/api/v4/practices")
async def get_practices(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True),
    include_videos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get practices articles - building methods and process improvements"""
    return await _get_theme_articles(
        theme="practices",
        days=days,
        limit=limit,
        min_score=min_score,
        include_insights=include_insights,
        include_videos=include_videos,
        db=db
    )

@app.get("/api/v4/systems-codes")
async def get_systems_codes(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True),
    include_videos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get systems & codes articles - policy updates and regulatory changes"""
    return await _get_theme_articles(
        theme="systems_codes",
        days=days,
        limit=limit,
        min_score=min_score,
        include_insights=include_insights,
        include_videos=include_videos,
        db=db
    )

@app.get("/api/v4/vision")
async def get_vision(
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(50.0, ge=0.0, le=1000.0),
    include_insights: bool = Query(True),
    include_videos: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get vision articles - smart cities and future-of-living models"""
    return await _get_theme_articles(
        theme="vision",
        days=days,
        limit=limit,
        min_score=min_score,
        include_insights=include_insights,
        include_videos=include_videos,
        db=db
    )

# ==================== ADMIN ENDPOINTS ====================

@app.post("/api/v4/admin/collect")
async def collect_data(background_tasks: BackgroundTasks):
    """Trigger data collection from all sources"""
    background_tasks.add_task(_run_data_collection)
    return {
        "ok": True,
        "message": "Data collection started in background",
        "status": "started"
    }

@app.post("/api/v4/admin/score")
async def run_scoring(
    limit: int = Query(100, ge=1, le=500),
    background_tasks: BackgroundTasks = None
):
    """Run scoring on unscored articles"""
    if background_tasks:
        background_tasks.add_task(_run_scoring_task, limit)
        return {
            "ok": True,
            "message": "Scoring started in background",
            "status": "started"
        }
    else:
        result = _run_scoring_task(limit)
        return result

@app.post("/api/v4/admin/process-videos")
async def process_videos(
    limit: int = Query(50, ge=1, le=200),
    background_tasks: BackgroundTasks = None
):
    """Process unprocessed videos"""
    if background_tasks:
        background_tasks.add_task(_run_video_processing, limit)
        return {
            "ok": True,
            "message": "Video processing started in background",
            "status": "started"
        }
    else:
        result = _run_video_processing(limit)
        return result

@app.get("/api/v4/health")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute(text("SELECT 1"))
        
        # Get basic stats
        stats = _get_health_stats(db)
        
        return {
            "status": "healthy",
            "version": "4.0.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "stats": stats,
            "features": {
                "video_support": config.enable_video_support,
                "ai_synthesis": config.enable_ai_synthesis,
                "real_time_scoring": config.enable_real_time_scoring
            }
        }
        
    except Exception as e:
        return {
            "status": "unhealthy",
            "version": "4.0.0",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# ==================== UTILITY FUNCTIONS ====================

async def _get_theme_articles(
    theme: str,
    days: int,
    limit: int,
    min_score: float,
    include_insights: bool,
    include_videos: bool,
    db: Session
):
    """Get articles for a specific theme"""
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Get articles for the theme
        articles = db.query(Article).join(ArticleScore).filter(
            and_(
                Article.primary_theme == theme,
                Article.published_at >= cutoff,
                Article.status != 'discarded',
                ArticleScore.composite_score >= min_score
            )
        ).order_by(desc(ArticleScore.composite_score)).limit(limit).all()
        
        # Format response
        formatted_articles = []
        for article in articles:
            article_data = _format_article_response(article, include_insights, db)
            formatted_articles.append(article_data)
        
        # Get best video for theme if requested
        featured_video = None
        if include_videos and config.enable_video_support:
            video_service = VideoIntegrationService()
            featured_video = await video_service.get_best_video_for_theme(theme)
        
        theme_config = THEMES.get(theme, {})
        
        return {
            "ok": True,
            "theme": theme,
            "theme_config": theme_config,
            "count": len(formatted_articles),
            "articles": formatted_articles,
            "featured_video": featured_video,
            "filters": {
                "days": days,
                "limit": limit,
                "min_score": min_score,
                "include_insights": include_insights,
                "include_videos": include_videos
            },
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting {theme} articles: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def _format_article_response(article: Article, include_insights: bool = True, db: Session = None) -> Dict[str, Any]:
    """Format article for API response"""
    response = {
        "id": str(article.id),
        "url": article.url,
        "title": article.title,
        "summary": article.summary,
        "source": article.source,
        "published_at": article.published_at.isoformat() if article.published_at else None,
        "primary_theme": article.primary_theme,
        "secondary_themes": article.secondary_themes,
        "media_type": article.media_type,
        "actionability_score": article.actionability_score,
        "insight_quality": article.insight_quality,
        "content_depth": article.content_depth
    }
    
    # Add video-specific fields
    if article.media_type == 'video':
        response.update({
            "video_url": article.video_url,
            "video_duration": article.video_duration,
            "video_thumbnail": article.video_thumbnail
        })
    
    # Add scoring data
    if article.scores:
        score = article.scores[0]  # Get the latest score
        response.update({
            "composite_score": score.composite_score,
            "theme_scores": {
                "opportunities": score.opportunities_score,
                "practices": score.practices_score,
                "systems_codes": score.systems_codes_score,
                "vision": score.vision_score
            },
            "quality_indicators": {
                "roi_data_present": score.roi_data_present,
                "methodology_present": score.methodology_present,
                "case_study_present": score.case_study_present,
                "performance_metrics_present": score.performance_metrics_present
            },
            "scoring_confidence": score.scoring_confidence
        })
    
    # Add insights if requested
    if include_insights and article.insights:
        response["insights"] = [
            {
                "type": insight.insight_type,
                "category": insight.category,
                "title": insight.title,
                "content": insight.content,
                "value": insight.value,
                "is_actionable": insight.is_actionable,
                "implementation_difficulty": insight.implementation_difficulty,
                "estimated_impact": insight.estimated_impact,
                "confidence_score": insight.confidence_score
            }
            for insight in article.insights
        ]
    
    return response

def _get_overall_stats(db: Session, cutoff: datetime) -> Dict[str, Any]:
    """Get overall platform statistics"""
    try:
        # Total articles
        total_articles = db.query(Article).count()
        
        # Articles in date range
        recent_articles = db.query(Article).filter(Article.published_at >= cutoff).count()
        
        # High quality articles
        high_quality = db.query(Article).join(ArticleScore).filter(
            ArticleScore.composite_score >= config.scoring.min_composite_score
        ).count()
        
        # Articles by theme
        theme_counts = {}
        for theme in THEMES.keys():
            count = db.query(Article).filter(Article.primary_theme == theme).count()
            theme_counts[theme] = count
        
        # Video content
        video_count = db.query(VideoContent).count()
        processed_videos = db.query(VideoContent).filter(VideoContent.processed == True).count()
        
        return {
            "total_articles": total_articles,
            "recent_articles": recent_articles,
            "high_quality_articles": high_quality,
            "theme_distribution": theme_counts,
            "video_content": {
                "total_videos": video_count,
                "processed_videos": processed_videos
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        return {}

def _get_health_stats(db: Session) -> Dict[str, Any]:
    """Get health check statistics"""
    try:
        total_articles = db.query(Article).count()
        scored_articles = db.query(Article).join(ArticleScore).count()
        total_videos = db.query(VideoContent).count()
        
        return {
            "total_articles": total_articles,
            "scored_articles": scored_articles,
            "total_videos": total_videos,
            "scoring_coverage": (scored_articles / max(total_articles, 1)) * 100
        }
    except Exception as e:
        logger.error(f"Error getting health stats: {str(e)}")
        return {}

# ==================== BACKGROUND TASKS ====================

async def _run_data_collection():
    """Run data collection in background"""
    try:
        logger.info("Starting background data collection")
        orchestrator = DataCollectionOrchestrator()
        
        # Collect data
        results = await orchestrator.collect_all_data()
        
        # Save to database
        saved_counts = await orchestrator.save_collected_data(results)
        
        logger.info(f"Data collection completed: {saved_counts}")
        
    except Exception as e:
        logger.error(f"Background data collection failed: {str(e)}")

def _run_scoring_task(limit: int):
    """Run scoring in background"""
    try:
        logger.info(f"Starting background scoring (limit: {limit})")
        result = run_scoring_batch(limit)
        logger.info(f"Scoring completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Background scoring failed: {str(e)}")
        return {"status": "error", "message": str(e)}

async def _run_video_processing(limit: int):
    """Run video processing in background"""
    try:
        logger.info(f"Starting background video processing (limit: {limit})")
        from .video_processor import YouTubeProcessor
        processor = YouTubeProcessor()
        result = await processor.process_video_batch(limit)
        logger.info(f"Video processing completed: {result}")
        return result
    except Exception as e:
        logger.error(f"Background video processing failed: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
