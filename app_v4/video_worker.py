"""
Newsletter API v4 Video Processing Worker
Specialized worker for video content processing
"""

import asyncio
import logging
import time
from datetime import datetime, timezone

from .config import get_config
from .video_processor import YouTubeProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VideoWorkerService:
    """Specialized worker service for video processing"""
    
    def __init__(self):
        self.config = get_config()
        self.video_processor = YouTubeProcessor()
        self.running = True
        
        # Task intervals (in seconds)
        self.video_processing_interval = 1800  # 30 minutes
        self.batch_size = 20  # Process videos in smaller batches
        
        # Last run time
        self.last_video_processing = None
    
    async def run(self):
        """Main video worker loop"""
        logger.info("🎥 Starting Newsletter API v4 Video Worker")
        
        # Run initial video processing
        await self._run_video_processing()
        
        # Main loop
        while self.running:
            try:
                current_time = datetime.now(timezone.utc)
                
                # Video processing
                if self._should_run_video_processing(current_time):
                    await self._run_video_processing()
                    self.last_video_processing = current_time
                
                # Sleep for 60 seconds before next iteration
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in video worker loop: {str(e)}")
                await asyncio.sleep(60)  # Wait before retrying
    
    def _should_run_video_processing(self, current_time: datetime) -> bool:
        """Check if video processing should run"""
        if not self.config.enable_video_support:
            return False
        
        if self.last_video_processing is None:
            return True
        
        time_since_last = (current_time - self.last_video_processing).total_seconds()
        return time_since_last >= self.video_processing_interval
    
    async def _run_video_processing(self):
        """Run video processing"""
        try:
            logger.info("🎥 Starting video processing...")
            start_time = time.time()
            
            result = await self.video_processor.process_video_batch(limit=self.batch_size)
            
            elapsed_time = time.time() - start_time
            
            logger.info(f"✅ Video processing completed in {elapsed_time:.2f}s")
            logger.info(f"   - Processed: {result['processed']}")
            logger.info(f"   - High quality: {result['high_quality']}")
            logger.info(f"   - Articles created: {result['articles_created']}")
            logger.info(f"   - Errors: {result['errors']}")
            
        except Exception as e:
            logger.error(f"❌ Video processing failed: {str(e)}")
    
    def stop(self):
        """Stop the video worker"""
        logger.info("🛑 Stopping video worker...")
        self.running = False

async def main():
    """Main entry point for the video worker"""
    worker = VideoWorkerService()
    
    try:
        await worker.run()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
        worker.stop()
    except Exception as e:
        logger.error(f"Video worker failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
