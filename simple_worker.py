#!/usr/bin/env python3
"""
Ultra-simple worker that just logs and waits - no complex imports
This will help us identify if the issue is with imports or with Render configuration
"""
import os
import sys
import time
import logging
from datetime import datetime

print("=== Simple Worker Starting ===")
print(f"Python version: {sys.version}")
print(f"Current working directory: {os.getcwd()}")
print(f"Python path: {sys.path}")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("Simple worker started successfully!")

# Set up environment variables
os.environ.setdefault("DATABASE_URL", "sqlite:///newsletter.db")
os.environ.setdefault("FORCE_SQLITE", "true")

logger.info(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
logger.info(f"FORCE_SQLITE: {os.environ.get('FORCE_SQLITE')}")

def simple_task():
    """Simple task that just logs"""
    logger.info(f"Simple task running at {datetime.now()}")
    return "Task completed successfully"

# Main loop
logger.info("Starting simple worker loop...")

try:
    while True:
        try:
            result = simple_task()
            logger.info(f"Task result: {result}")
            time.sleep(60)  # Wait 1 minute between tasks
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in worker loop: {e}")
            time.sleep(60)  # Wait before retrying
            
except Exception as e:
    logger.error(f"Fatal error in simple worker: {e}")
    sys.exit(1)

logger.info("Simple worker stopped")
