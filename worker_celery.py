"""
Celery-based background worker (Alternative to simple worker)
For production use with Redis as message broker
"""
import os
import sys
from datetime import datetime, timedelta
from celery import Celery
from celery.schedules import crontab
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import get_db, engine
from app.crawler import crawl_sources
from app.scoring import score_articles
from app.ceo_voice import generate_ceo_voice
from app.macro_data import fetch_macro_data
from app.publish import publish_newsletter
from sqlalchemy import text

# Configure Celery
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')

app = Celery('newsletter_tasks', broker=REDIS_URL, backend=REDIS_URL)

# Configure Celery settings
app.conf.update(
    timezone='America/New_York',
    enable_utc=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# Configure periodic tasks
app.conf.beat_schedule = {
    'crawl-and-score': {
        'task': 'worker_celery.crawl_and_score_task',
        'schedule': timedelta(hours=2),
        'options': {'queue': 'crawling'}
    },
    'generate-daily-newsletter': {
        'task': 'worker_celery.generate_newsletter_task',
        'schedule': crontab(hour=6, minute=0),  # 6 AM daily
        'options': {'queue': 'newsletter'}
    },
    'cleanup-old-articles': {
        'task': 'worker_celery.cleanup_articles_task',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
        'options': {'queue': 'maintenance'}
    },
    'health-check': {
        'task': 'worker_celery.health_check_task',
        'schedule': timedelta(minutes=30),
        'options': {'queue': 'health'}
    },
}

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.task(name='worker_celery.crawl_and_score_task', bind=True, max_retries=3)
def crawl_and_score_task(self):
    """Crawl sources and score articles"""
    try:
        logger.info(f"Starting crawl and score task {self.request.id}")
        
        # Crawl sources
        with next(get_db()) as db:
            crawl_results = crawl_sources(db)
            articles_added = crawl_results.get('articles_added', 0)
            logger.info(f"Crawled {articles_added} new articles")
        
        # Score new articles
        with next(get_db()) as db:
            score_results = score_articles(db)
            articles_scored = score_results.get('articles_scored', 0)
            logger.info(f"Scored {articles_scored} articles")
            
        return {
            'status': 'success',
            'articles_added': articles_added,
            'articles_scored': articles_scored,
            'task_id': self.request.id
        }
        
    except Exception as exc:
        logger.error(f"Task {self.request.id} failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

@app.task(name='worker_celery.generate_newsletter_task', bind=True, max_retries=2)
def generate_newsletter_task(self):
    """Generate daily newsletter"""
    try:
        logger.info(f"Starting newsletter generation task {self.request.id}")
        
        with next(get_db()) as db:
            # Check if newsletter already exists for today
            today = datetime.now().strftime('%Y-%m-%d')
            existing = db.execute(
                text("SELECT id FROM issues WHERE issue_date = :date"),
                {"date": today}
            ).fetchone()
            
            if existing:
                logger.info(f"Newsletter for {today} already exists")
                return {
                    'status': 'skipped',
                    'reason': 'Newsletter already exists',
                    'date': today
                }
            
            # Generate CEO voice content
            ceo_content = generate_ceo_voice(db)
            
            # Fetch macro data
            macro_content = fetch_macro_data(db)
            
            # Publish newsletter
            result = publish_newsletter(
                db,
                ceo_voice=ceo_content,
                macro_data=macro_content
            )
            
            logger.info(f"Newsletter generated: {result}")
            
            return {
                'status': 'success',
                'result': result,
                'date': today,
                'task_id': self.request.id
            }
            
    except Exception as exc:
        logger.error(f"Newsletter generation failed: {exc}")
        raise self.retry(exc=exc, countdown=300)

@app.task(name='worker_celery.cleanup_articles_task', bind=True)
def cleanup_articles_task(self):
    """Clean up old articles"""
    try:
        logger.info(f"Starting cleanup task {self.request.id}")
        
        with engine.connect() as conn:
            # Delete articles older than 30 days that weren't selected
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            
            # For PostgreSQL
            if 'postgresql' in str(engine.url):
                result = conn.execute(
                    text("""
                        DELETE FROM articles 
                        WHERE published_at < :cutoff::timestamp 
                        AND status = 'discarded'
                    """),
                    {"cutoff": cutoff_date}
                )
            else:
                # For SQLite
                result = conn.execute(
                    text("""
                        DELETE FROM articles 
                        WHERE published_at < :cutoff 
                        AND status = 'discarded'
                    """),
                    {"cutoff": cutoff_date}
                )
            
            conn.commit()
            deleted_count = result.rowcount
            
            logger.info(f"Deleted {deleted_count} old articles")
            
            return {
                'status': 'success',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff_date,
                'task_id': self.request.id
            }
            
    except Exception as exc:
        logger.error(f"Cleanup task failed: {exc}")
        return {
            'status': 'failed',
            'error': str(exc),
            'task_id': self.request.id
        }

@app.task(name='worker_celery.health_check_task', bind=True)
def health_check_task(self):
    """Health check task"""
    try:
        with engine.connect() as conn:
            # Check database connection
            conn.execute(text("SELECT 1")).fetchone()
            
            # Get statistics based on database type
            if 'postgresql' in str(engine.url):
                stats = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_articles,
                        COUNT(CASE WHEN status = 'new' THEN 1 END) as new_articles,
                        COUNT(CASE WHEN status = 'scored' THEN 1 END) as scored_articles
                    FROM articles
                    WHERE fetched_at > NOW() - INTERVAL '24 hours'
                """)).fetchone()
            else:
                # SQLite version
                stats = conn.execute(text("""
                    SELECT 
                        COUNT(*) as total_articles,
                        COUNT(CASE WHEN status = 'new' THEN 1 END) as new_articles,
                        COUNT(CASE WHEN status = 'scored' THEN 1 END) as scored_articles
                    FROM articles
                    WHERE fetched_at > datetime('now', '-24 hours')
                """)).fetchone()
            
            health_status = {
                'status': 'healthy',
                'database': 'connected',
                'articles_24h': {
                    'total': stats[0] if stats else 0,
                    'new': stats[1] if stats else 0,
                    'scored': stats[2] if stats else 0
                },
                'timestamp': datetime.now().isoformat(),
                'task_id': self.request.id
            }
            
            logger.info(f"Health check: {health_status}")
            return health_status
            
    except Exception as exc:
        logger.error(f"Health check failed: {exc}")
        return {
            'status': 'unhealthy',
            'error': str(exc),
            'timestamp': datetime.now().isoformat(),
            'task_id': self.request.id
        }

@app.task(name='worker_celery.manual_crawl', bind=True)
def manual_crawl_task(self, sources=None):
    """Manual crawl task that can be triggered via API"""
    try:
        logger.info(f"Starting manual crawl task {self.request.id}")
        
        with next(get_db()) as db:
            crawl_results = crawl_sources(db, sources=sources)
            
        return {
            'status': 'success',
            'results': crawl_results,
            'task_id': self.request.id
        }
        
    except Exception as exc:
        logger.error(f"Manual crawl failed: {exc}")
        raise self.retry(exc=exc, countdown=60)

if __name__ == '__main__':
    # Run worker
    app.start()