"""
Newsletter API v4 Background Worker
Handles data collection, scoring, and video processing
"""

import asyncio
import logging
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Any

from .config import get_config
from .data_collectors import DataCollectionOrchestrator
from .scoring import run_scoring_batch
from .video_processor import YouTubeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkerService:
    """Main worker service that coordinates all background tasks"""
    
    def __init__(self):
        self.config = get_config()
        self.data_orchestrator = DataCollectionOrchestrator()
        self.video_processor = YouTubeProcessor()
        self.running = True
        
        # Task intervals (in seconds)
        self.data_collection_interval = 3600  # 1 hour
        self.scoring_interval = 1800  # 30 minutes
        self.video_processing_interval = 7200  # 2 hours
        self.health_check_interval = 300  # 5 minutes
        
        # Last run times
        self.last_data_collection = None
        self.last_scoring = None
        self.last_video_processing = None
    
    async def run(self):
        """Main worker loop"""
        logger.info("🚀 Starting Newsletter API v4 Worker")
        
        # Run initial tasks
        await self._run_initial_tasks()
        
        # Main loop
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Data collection
                if self._should_run_data_collection(current_time):
                    await self._run_data_collection()
                    self.last_data_collection = current_time
                
                # Scoring
                if self._should_run_scoring(current_time):
                    await self._run_scoring()
                    self.last_scoring = current_time
                
                # Video processing
                if self._should_run_video_processing(current_time):
                    await self._run_video_processing()
                    self.last_video_processing = current_time
                
                # Health check
                if self._should_run_health_check(current_time):
                    await self._run_health_check()
                
                # Sleep for 60 seconds before next iteration
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _run_initial_tasks(self):
        """Run initial setup tasks"""
        logger.info("Running initial tasks...")
        
        try:
            # Initialize database if needed
            from .models import init_database
            init_database(self.config.database.url)
            logger.info("✅ Database initialized")
            
            # Run initial data collection
            await self._run_data_collection()
            
            # Run initial scoring
            await self._run_scoring()
            
            # Run initial video processing
            if self.config.enable_video_support:
                await self._run_video_processing()
            
            logger.info("✅ Initial tasks completed")
            
        except Exception as e:
            logger.error(f"Error in initial tasks: {str(e)}")
    
    def _should_run_data_collection(self, current_time: datetime) -> bool:
        """Check if data collection should run"""
        if self.last_data_collection is None:
            return True
        
        time_since_last = (current_time - self.last_data_collection).total_seconds()
        return time_since_last >= self.data_collection_interval
    
    def _should_run_scoring(self, current_time: datetime) -> bool:
        """Check if scoring should run"""
        if self.last_scoring is None:
            return True
        
        time_since_last = (current_time - self.last_scoring).total_seconds()
        return time_since_last >= self.scoring_interval
    
    def _should_run_video_processing(self, current_time: datetime) -> bool:
        """Check if video processing should run"""
        if not self.config.enable_video_support:
            return False
        
        if self.last_video_processing is None:
            return True
        
        time_since_last = (current_time - self.last_video_processing).total_seconds()
        return time_since_last >= self.video_processing_interval
    
    def _should_run_health_check(self, current_time: datetime) -> bool:
        """Check if health check should run"""
        return True  # Always run health checks
    
    async def _run_data_collection(self):
        """Run data collection from all sources"""
        try:
            logger.info("📊 Starting data collection...")
            start_time = time.time()
            
            # Collect data
            results = await self.data_orchestrator.collect_all_data()
            
            # Save to database
            saved_counts = await self.data_orchestrator.save_collected_data(results)
            
            elapsed_time = time.time() - start_time
            
            logger.info(f"✅ Data collection completed in {elapsed_time:.2f}s")
            logger.info(f"   - Articles: {saved_counts['articles']}")
            logger.info(f"   - Videos: {saved_counts['videos']}")
            logger.info(f"   - Errors: {saved_counts['errors']}")
            
        except Exception as e:
            logger.error(f"❌ Data collection failed: {str(e)}")
    
    async def _run_scoring(self):
        """Run scoring on unscored articles"""
        try:
            logger.info("🎯 Starting scoring...")
            start_time = time.time()
            
            result = run_scoring_batch(limit=100)
            
            elapsed_time = time.time() - start_time
            
            if result['status'] == 'success':
                logger.info(f"✅ Scoring completed in {elapsed_time:.2f}s")
                logger.info(f"   - Scored: {result['scored_articles']}")
                logger.info(f"   - Excluded: {result['excluded_articles']}")
                logger.info(f"   - Insights: {result['insights_extracted']}")
            else:
                logger.error(f"❌ Scoring failed: {result['message']}")
            
        except Exception as e:
            logger.error(f"❌ Scoring failed: {str(e)}")
    
    async def _run_video_processing(self):
        """Run video processing"""
        try:
            logger.info("🎥 Starting video processing...")
            start_time = time.time()
            
            result = await self.video_processor.process_video_batch(limit=50)
            
            elapsed_time = time.time() - start_time
            
            logger.info(f"✅ Video processing completed in {elapsed_time:.2f}s")
            logger.info(f"   - Processed: {result['processed']}")
            logger.info(f"   - High quality: {result['high_quality']}")
            logger.info(f"   - Articles created: {result['articles_created']}")
            logger.info(f"   - Errors: {result['errors']}")
            
        except Exception as e:
            logger.error(f"❌ Video processing failed: {str(e)}")
    
    async def _run_health_check(self):
        """Run health check"""
        try:
            # Simple health check - just log current status
            current_time = datetime.now(timezone.utc)
            
            status = {
                "timestamp": current_time.isoformat(),
                "last_data_collection": self.last_data_collection.isoformat() if self.last_data_collection else None,
                "last_scoring": self.last_scoring.isoformat() if self.last_scoring else None,
                "last_video_processing": self.last_video_processing.isoformat() if self.last_video_processing else None,
                "worker_status": "healthy"
            }
            
            logger.debug(f"Health check: {status}")
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
    
    def stop(self):
        """Stop the worker"""
        logger.info("🛑 Stopping worker...")
        self.running = False

async def main():
    """Main entry point for the worker"""
    worker = WorkerService()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        worker.stop()
    except Exception as e:
        logger.error(f"Worker failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
