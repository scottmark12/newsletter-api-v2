"""
Worker management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

from ..db import get_db
from ..crawler import crawl_sources
from ..scoring import score_articles
from ..publish import publish_newsletter
from ..ceo_voice import generate_ceo_voice
from ..macro_data import fetch_macro_data

router = APIRouter(prefix="/api/worker", tags=["worker"])
logger = logging.getLogger(__name__)

@router.get("/status")
async def get_worker_status(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get worker status and statistics"""
    try:
        # Get statistics from the last 24 hours
        if 'postgresql' in str(db.bind.url):
            stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN status = 'new' THEN 1 END) as new_articles,
                    COUNT(CASE WHEN status = 'scored' THEN 1 END) as scored_articles,
                    COUNT(CASE WHEN status = 'selected' THEN 1 END) as selected_articles,
                    MAX(fetched_at) as last_crawl
                FROM articles
                WHERE fetched_at > NOW() - INTERVAL '24 hours'
            """)).fetchone()
            
            recent_issues = db.execute(text("""
                SELECT issue_date, created_at 
                FROM issues 
                ORDER BY created_at DESC 
                LIMIT 5
            """)).fetchall()
        else:
            # SQLite version
            stats = db.execute(text("""
                SELECT 
                    COUNT(*) as total_articles,
                    COUNT(CASE WHEN status = 'new' THEN 1 END) as new_articles,
                    COUNT(CASE WHEN status = 'scored' THEN 1 END) as scored_articles,
                    COUNT(CASE WHEN status = 'selected' THEN 1 END) as selected_articles,
                    MAX(fetched_at) as last_crawl
                FROM articles
                WHERE fetched_at > datetime('now', '-24 hours')
            """)).fetchone()
            
            recent_issues = db.execute(text("""
                SELECT issue_date, created_at 
                FROM issues 
                ORDER BY created_at DESC 
                LIMIT 5
            """)).fetchall()
        
        return {
            "status": "operational",
            "statistics": {
                "last_24_hours": {
                    "total_articles": stats[0] if stats else 0,
                    "new_articles": stats[1] if stats else 0,
                    "scored_articles": stats[2] if stats else 0,
                    "selected_articles": stats[3] if stats else 0,
                },
                "last_crawl": stats[4] if stats else None,
                "recent_newsletters": [
                    {
                        "date": str(issue[0]),
                        "created": str(issue[1])
                    } for issue in recent_issues
                ] if recent_issues else []
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting worker status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/crawl")
async def trigger_crawl(
    background_tasks: BackgroundTasks,
    sources: Optional[list] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger a crawl operation"""
    
    def run_crawl():
        try:
            with next(get_db()) as db_session:
                result = crawl_sources(db_session, sources=sources)
                logger.info(f"Manual crawl completed: {result}")
        except Exception as e:
            logger.error(f"Manual crawl failed: {e}")
    
    background_tasks.add_task(run_crawl)
    
    return {
        "status": "started",
        "message": "Crawl operation has been queued",
        "sources": sources if sources else "all",
        "timestamp": datetime.now().isoformat()
    }

@router.post("/score")
async def trigger_scoring(
    background_tasks: BackgroundTasks,
    force: bool = False,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger article scoring"""
    
    def run_scoring():
        try:
            with next(get_db()) as db_session:
                result = score_articles(db_session, force=force)
                logger.info(f"Manual scoring completed: {result}")
        except Exception as e:
            logger.error(f"Manual scoring failed: {e}")
    
    background_tasks.add_task(run_scoring)
    
    return {
        "status": "started",
        "message": "Scoring operation has been queued",
        "force": force,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/newsletter/generate")
async def generate_newsletter_manual(
    background_tasks: BackgroundTasks,
    date: Optional[str] = None,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually generate a newsletter"""
    
    newsletter_date = date if date else datetime.now().strftime('%Y-%m-%d')
    
    # Check if newsletter already exists
    existing = db.execute(
        text("SELECT id FROM issues WHERE issue_date = :date"),
        {"date": newsletter_date}
    ).fetchone()
    
    if existing and not date:
        raise HTTPException(
            status_code=400,
            detail=f"Newsletter for {newsletter_date} already exists"
        )
    
    def run_generation():
        try:
            with next(get_db()) as db_session:
                # Generate CEO voice content
                ceo_content = generate_ceo_voice(db_session)
                
                # Fetch macro data
                macro_content = fetch_macro_data(db_session)
                
                # Publish newsletter
                result = publish_newsletter(
                    db_session,
                    ceo_voice=ceo_content,
                    macro_data=macro_content,
                    issue_date=newsletter_date
                )
                logger.info(f"Manual newsletter generated: {result}")
        except Exception as e:
            logger.error(f"Manual newsletter generation failed: {e}")
    
    background_tasks.add_task(run_generation)
    
    return {
        "status": "started",
        "message": "Newsletter generation has been queued",
        "date": newsletter_date,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/cleanup")
async def trigger_cleanup(
    background_tasks: BackgroundTasks,
    days: int = 30,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Manually trigger cleanup of old articles"""
    
    def run_cleanup():
        try:
            with db.bind.connect() as conn:
                cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
                
                if 'postgresql' in str(db.bind.url):
                    result = conn.execute(
                        text("""
                            DELETE FROM articles 
                            WHERE published_at < :cutoff::timestamp 
                            AND status = 'discarded'
                        """),
                        {"cutoff": cutoff_date}
                    )
                else:
                    result = conn.execute(
                        text("""
                            DELETE FROM articles 
                            WHERE published_at < :cutoff 
                            AND status = 'discarded'
                        """),
                        {"cutoff": cutoff_date}
                    )
                
                conn.commit()
                logger.info(f"Cleanup completed: {result.rowcount} articles deleted")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    background_tasks.add_task(run_cleanup)
    
    return {
        "status": "started",
        "message": f"Cleanup operation has been queued (removing articles older than {days} days)",
        "days": days,
        "timestamp": datetime.now().isoformat()
    }

@router.get("/schedule")
async def get_schedule() -> Dict[str, Any]:
    """Get the worker schedule"""
    return {
        "schedule": {
            "crawl_and_score": {
                "frequency": "every 2 hours",
                "description": "Crawl RSS feeds and score new articles"
            },
            "generate_newsletter": {
                "frequency": "daily at 6:00 AM EST",
                "description": "Generate and publish daily newsletter"
            },
            "cleanup": {
                "frequency": "daily at 2:00 AM EST",
                "description": "Remove old discarded articles"
            },
            "health_check": {
                "frequency": "every 30 minutes",
                "description": "Check system health and database connection"
            }
        },
        "timezone": "America/New_York"
    }

@router.get("/logs")
async def get_recent_logs(
    limit: int = 100,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get recent worker activity logs"""
    try:
        # This would typically fetch from a logging system
        # For now, return recent database activity
        
        if 'postgresql' in str(db.bind.url):
            recent_activity = db.execute(text("""
                SELECT 
                    'crawl' as activity_type,
                    COUNT(*) as count,
                    MAX(fetched_at) as last_activity
                FROM articles
                WHERE fetched_at > NOW() - INTERVAL '7 days'
                
                UNION ALL
                
                SELECT 
                    'newsletter' as activity_type,
                    COUNT(*) as count,
                    MAX(created_at) as last_activity
                FROM issues
                WHERE created_at > NOW() - INTERVAL '7 days'
            """)).fetchall()
        else:
            recent_activity = db.execute(text("""
                SELECT 
                    'crawl' as activity_type,
                    COUNT(*) as count,
                    MAX(fetched_at) as last_activity
                FROM articles
                WHERE fetched_at > datetime('now', '-7 days')
                
                UNION ALL
                
                SELECT 
                    'newsletter' as activity_type,
                    COUNT(*) as count,
                    MAX(created_at) as last_activity
                FROM issues
                WHERE created_at > datetime('now', '-7 days')
            """)).fetchall()
        
        return {
            "recent_activity": [
                {
                    "type": activity[0],
                    "count": activity[1],
                    "last_activity": str(activity[2]) if activity[2] else None
                } for activity in recent_activity
            ],
            "limit": limit,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))