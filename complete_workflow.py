#!/usr/bin/env python3
"""
Complete Newsletter Workflow Script
Ingests articles, scores them, pulls photos, creates summaries/why it matters, and refreshes the site
"""

import requests
import time
import json
import sys
from datetime import datetime, timezone
from typing import Dict, Any, Optional

# Configuration
API_BASE = "https://newsletter-api-v2.onrender.com"
TARGET_ARTICLES = 100
DELAY_BETWEEN_STEPS = 5  # seconds

def log_step(step: str, message: str):
    """Log a step with timestamp"""
    timestamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
    print(f"[{timestamp}] {step}: {message}")

def check_api_health() -> bool:
    """Check if the API is healthy and ready"""
    try:
        response = requests.get(f"{API_BASE}/health", timeout=30)
        if response.status_code == 200:
            log_step("HEALTH", "API is healthy and ready")
            return True
        else:
            log_step("HEALTH", f"API health check failed: {response.status_code}")
            return False
    except Exception as e:
        log_step("HEALTH", f"API health check error: {e}")
        return False

def get_current_stats() -> Dict[str, int]:
    """Get current article and score counts"""
    try:
        response = requests.get(f"{API_BASE}/api/v4/admin/stats", timeout=30)
        if response.status_code == 200:
            data = response.json()
            return {
                "total_articles": data.get("total_articles", 0),
                "scored_articles": data.get("scored_articles", 0),
                "unscored_articles": data.get("unscored_articles", 0)
            }
        else:
            log_step("STATS", f"Failed to get stats: {response.status_code}")
            return {"total_articles": 0, "scored_articles": 0, "unscored_articles": 0}
    except Exception as e:
        log_step("STATS", f"Error getting stats: {e}")
        return {"total_articles": 0, "scored_articles": 0, "unscored_articles": 0}

def ingest_articles() -> int:
    """Ingest new articles from RSS feeds and other sources"""
    log_step("INGEST", "Starting article ingestion...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/collect", timeout=300)
        if response.status_code == 200:
            data = response.json()
            ingested = data.get("collected", 0)
            log_step("INGEST", f"Successfully ingested {ingested} new articles")
            return ingested
        else:
            log_step("INGEST", f"Ingestion failed: {response.status_code}")
            return 0
    except Exception as e:
        log_step("INGEST", f"Ingestion error: {e}")
        return 0

def clear_old_scores() -> bool:
    """Clear old scores to start fresh"""
    log_step("CLEAR", "Clearing old scores...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/clear-scores", timeout=60)
        if response.status_code == 200:
            data = response.json()
            log_step("CLEAR", f"Successfully cleared {data.get('deleted_count', 0)} old scores")
            return True
        else:
            log_step("CLEAR", f"Clear scores failed: {response.status_code}")
            return False
    except Exception as e:
        log_step("CLEAR", f"Clear scores error: {e}")
        return False

def score_articles() -> Dict[str, int]:
    """Score articles using the BUILT grader"""
    log_step("SCORE", "Starting article scoring with BUILT grader...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/score", timeout=600)
        if response.status_code == 200:
            data = response.json()
            scored = data.get("scored", 0)
            rejected = data.get("rejected", 0)
            log_step("SCORE", f"Successfully scored {scored} articles, rejected {rejected}")
            return {"scored": scored, "rejected": rejected}
        else:
            log_step("SCORE", f"Scoring failed: {response.status_code}")
            return {"scored": 0, "rejected": 0}
    except Exception as e:
        log_step("SCORE", f"Scoring error: {e}")
        return {"scored": 0, "rejected": 0}

def pull_photos() -> int:
    """Extract images/photos for articles"""
    log_step("PHOTOS", "Extracting photos/images...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/extract-images", timeout=600)
        if response.status_code == 200:
            data = response.json()
            images = data.get("images_extracted", 0)
            log_step("PHOTOS", f"Successfully extracted {images} photos")
            return images
        else:
            log_step("PHOTOS", f"Photo extraction failed: {response.status_code}")
            return 0
    except Exception as e:
        log_step("PHOTOS", f"Photo extraction error: {e}")
        return 0

def create_summaries() -> int:
    """Generate summaries and 'why it matters' content"""
    log_step("SUMMARIES", "Creating summaries and 'why it matters' content...")
    try:
        response = requests.post(f"{API_BASE}/api/v4/admin/generate-content", timeout=600)
        if response.status_code == 200:
            data = response.json()
            enhanced = data.get("enhanced", 0)
            log_step("SUMMARIES", f"Successfully created {enhanced} summaries")
            return enhanced
        else:
            log_step("SUMMARIES", f"Summary creation failed: {response.status_code}")
            return 0
    except Exception as e:
        log_step("SUMMARIES", f"Summary creation error: {e}")
        return 0

def cleanup_old_articles() -> int:
    """Clean up articles older than a week"""
    log_step("CLEANUP", "Cleaning up articles older than a week...")
    try:
        # We'll need to add a cleanup endpoint to the API
        # For now, we'll create a simple cleanup function
        response = requests.post(f"{API_BASE}/api/v4/admin/cleanup-old-articles", timeout=60)
        if response.status_code == 200:
            data = response.json()
            cleaned = data.get("cleaned_count", 0)
            log_step("CLEANUP", f"Successfully cleaned up {cleaned} old articles")
            return cleaned
        else:
            log_step("CLEANUP", f"Cleanup failed: {response.status_code}")
            return 0
    except Exception as e:
        log_step("CLEANUP", f"Cleanup error: {e}")
        return 0

def refresh_site_data() -> bool:
    """Refresh the site data to account for new rankings"""
    log_step("REFRESH", "Refreshing site data with new rankings...")
    try:
        # The website endpoint should automatically show the latest ranked content
        response = requests.get(f"{API_BASE}/website", timeout=30)
        if response.status_code == 200:
            log_step("REFRESH", "Site data refreshed - new rankings are live")
            return True
        else:
            log_step("REFRESH", f"Site refresh failed: {response.status_code}")
            return False
    except Exception as e:
        log_step("REFRESH", f"Site refresh error: {e}")
        return False

def wait_for_target_articles(target: int) -> bool:
    """Keep ingesting until we reach the target number of articles"""
    log_step("TARGET", f"Working towards {target} articles...")
    
    max_attempts = 10  # Limit attempts to prevent infinite loops
    attempts = 0
    
    while attempts < max_attempts:
        stats = get_current_stats()
        current_total = stats["total_articles"]
        
        if current_total >= target:
            log_step("TARGET", f"Target reached: {current_total}/{target} articles")
            return True
        
        log_step("TARGET", f"Current: {current_total}/{target} articles. Ingesting more...")
        
        ingested = ingest_articles()
        if ingested == 0:
            log_step("TARGET", "No new articles ingested. Waiting before retrying...")
            time.sleep(30)
        else:
            time.sleep(DELAY_BETWEEN_STEPS)
        
        attempts += 1
        
        # If we're close to target, proceed anyway
        if current_total >= target * 0.8:
            log_step("TARGET", f"Close enough to target: {current_total}/{target}")
            return True
    
    log_step("TARGET", f"Reached max attempts ({max_attempts}), proceeding with current articles")
    return True

def main():
    """Main workflow execution"""
    print("=" * 80)
    print("🚀 NEWSLETTER COMPLETE WORKFLOW")
    print("=" * 80)
    print(f"Target: {TARGET_ARTICLES} articles")
    print(f"API Base: {API_BASE}")
    print(f"Start Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    
    # Step 0: Health Check
    log_step("START", "Checking API health...")
    if not check_api_health():
        log_step("ERROR", "API is not healthy. Exiting.")
        sys.exit(1)
    
    # Step 1: Get initial stats
    initial_stats = get_current_stats()
    log_step("INITIAL", f"Starting with {initial_stats['total_articles']} articles")
    
    # Step 2: Ingest articles to reach target
    log_step("INGEST", "Starting article ingestion phase...")
    if not wait_for_target_articles(TARGET_ARTICLES):
        log_step("WARNING", "Could not reach target article count, proceeding anyway")
    
    # Step 3: Clear old scores for fresh ranking
    log_step("CLEAR", "Clearing old scores for fresh ranking...")
    if not clear_old_scores():
        log_step("WARNING", "Could not clear old scores, proceeding anyway")
    
    # Step 4: Score articles with BUILT grader
    log_step("SCORE", "Scoring articles with BUILT grader...")
    score_results = score_articles()
    
    # Step 5: Create summaries and 'why it matters'
    log_step("SUMMARIES", "Creating summaries and 'why it matters' content...")
    summary_results = create_summaries()
    
    # Step 6: Pull photos/images
    log_step("PHOTOS", "Extracting photos and images...")
    photo_results = pull_photos()
    
    # Step 7: Clean up old articles (older than a week)
    log_step("CLEANUP", "Cleaning up articles older than a week...")
    cleanup_results = cleanup_old_articles()
    
    # Step 8: Refresh site data with new rankings
    log_step("REFRESH", "Refreshing site data with new rankings...")
    refresh_results = refresh_site_data()
    
    # Final stats
    final_stats = get_current_stats()
    
    # Summary
    print("\n" + "=" * 80)
    print("✅ WORKFLOW COMPLETE!")
    print("=" * 80)
    print(f"Initial Articles: {initial_stats['total_articles']}")
    print(f"Final Articles: {final_stats['total_articles']}")
    print(f"Articles Added: {final_stats['total_articles'] - initial_stats['total_articles']}")
    print(f"Articles Scored: {score_results['scored']}")
    print(f"Articles Rejected: {score_results['rejected']}")
    print(f"Summaries Created: {summary_results}")
    print(f"Photos Extracted: {photo_results}")
    print(f"Old Articles Cleaned: {cleanup_results}")
    print(f"Site Data Refreshed: {'✅' if refresh_results else '❌'}")
    print(f"End Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print("=" * 80)
    
    if final_stats['total_articles'] >= TARGET_ARTICLES:
        print("🎉 SUCCESS: Target article count reached!")
    else:
        print(f"⚠️  PARTIAL: Only {final_stats['total_articles']}/{TARGET_ARTICLES} articles collected")
    
    print(f"\n🌐 View your newsletter with new rankings: {API_BASE}/website")

if __name__ == "__main__":
    main()
