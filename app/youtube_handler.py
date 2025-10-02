# app/youtube_handler.py
"""
YouTube Video Handler for V2 Newsletter
Processes YouTube videos from RSS feeds and scores them like articles
"""
import re
import json
import pathlib
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup
import httpx

# Load YouTube channel metadata
CHANNELS_PATH = pathlib.Path(__file__).parent / "youtube_channels.json"

def load_youtube_channels() -> Dict[str, List[Dict[str, Any]]]:
    """Load curated YouTube channel metadata"""
    try:
        with CHANNELS_PATH.open() as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def extract_video_id(url: str) -> Optional[str]:
    """Extract YouTube video ID from various URL formats"""
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]+)',
        r'youtube\.com\/v\/([a-zA-Z0-9_-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def get_channel_info(channel_id: str) -> Dict[str, Any]:
    """Get channel metadata from our curated list"""
    channels = load_youtube_channels()
    
    for category, channel_list in channels.items():
        for channel in channel_list:
            if channel.get("channel_id") == channel_id:
                return {
                    "name": channel.get("name", "Unknown Channel"),
                    "description": channel.get("description", ""),
                    "tier": channel.get("tier", 3),
                    "category": category
                }
    
    return {
        "name": "Unknown Channel",
        "description": "",
        "tier": 3,
        "category": "uncategorized"
    }

def extract_youtube_metadata(url: str, html: str) -> Dict[str, Any]:
    """Extract YouTube-specific metadata from video page"""
    soup = BeautifulSoup(html, 'lxml')
    metadata = {
        "video_id": extract_video_id(url),
        "channel_name": "",
        "channel_id": "",
        "duration": "",
        "view_count": "",
        "thumbnail_url": ""
    }
    
    # Extract from meta tags
    channel_url = soup.find("meta", {"property": "og:url"})
    if channel_url:
        # Try to extract channel ID from various sources
        for script in soup.find_all("script"):
            script_text = script.string or ""
            if "channelId" in script_text:
                # Look for channel ID in JSON data
                channel_match = re.search(r'"channelId":"([^"]+)"', script_text)
                if channel_match:
                    metadata["channel_id"] = channel_match.group(1)
                    break
    
    # Get channel info from our curated list
    if metadata["channel_id"]:
        channel_info = get_channel_info(metadata["channel_id"])
        metadata.update(channel_info)
    
    # Extract thumbnail
    thumbnail = soup.find("meta", {"property": "og:image"})
    if thumbnail:
        metadata["thumbnail_url"] = thumbnail.get("content", "")
    
    # Extract duration from structured data
    duration_meta = soup.find("meta", {"itemprop": "duration"})
    if duration_meta:
        metadata["duration"] = duration_meta.get("content", "")
    
    return metadata

def calculate_video_score(metadata: Dict[str, Any], content: str, title: str) -> float:
    """Calculate video relevance score using same logic as articles"""
    base_score = 0.0
    
    # Channel tier bonus
    tier = metadata.get("tier", 3)
    tier_bonus = {1: 2.0, 2: 1.0, 3: 0.0}.get(tier, 0.0)
    base_score += tier_bonus
    
    # Category relevance
    category = metadata.get("category", "")
    category_bonus = {
        "construction_tech": 2.5,
        "architecture_design": 2.0,
        "sustainability": 1.8,
        "real_estate_business": 1.5
    }.get(category, 0.5)
    base_score += category_bonus
    
    # Content keyword matching (reuse article keywords)
    text_blob = f"{title} {content}".lower()
    construction_keywords = [
        "construction", "building", "architecture", "engineering", "development",
        "real estate", "housing", "infrastructure", "design", "planning",
        "3d printing", "modular", "prefab", "sustainable", "green building",
        "mass timber", "concrete", "steel", "materials", "technology"
    ]
    
    keyword_score = sum(1.2 for kw in construction_keywords if kw in text_blob)
    base_score += min(keyword_score, 5.0)  # Cap at 5 points
    
    # Duration preference (prefer 5-20 minute videos)
    duration = metadata.get("duration", "")
    if duration:
        # Parse ISO 8601 duration (PT15M30S format)
        duration_match = re.search(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', duration)
        if duration_match:
            hours = int(duration_match.group(1) or 0)
            minutes = int(duration_match.group(2) or 0)
            total_minutes = hours * 60 + minutes
            
            if 5 <= total_minutes <= 20:
                base_score += 1.0  # Sweet spot bonus
            elif total_minutes > 60:
                base_score -= 0.5  # Penalty for very long videos
    
    return base_score

def is_youtube_url(url: str) -> bool:
    """Check if URL is a YouTube video"""
    return "youtube.com" in url or "youtu.be" in url

def process_youtube_video(url: str, title: str, content: str, published_at: str = None) -> Dict[str, Any]:
    """Process a YouTube video and return scoring data"""
    if not is_youtube_url(url):
        return {}
    
    try:
        # Fetch video page for metadata
        with httpx.Client(timeout=15) as client:
            response = client.get(url)
            if response.status_code != 200:
                return {}
            
            metadata = extract_youtube_metadata(url, response.text)
            score = calculate_video_score(metadata, content, title)
            
            return {
                "media_type": "video",
                "platform": "youtube",
                "video_metadata": metadata,
                "composite_score": score,
                "needs_fact_check": False,  # Videos generally need less fact-checking
                "project_stage": None  # Not applicable for videos
            }
    
    except Exception as e:
        print(f"Error processing YouTube video {url}: {e}")
        return {
            "media_type": "video",
            "platform": "youtube",
            "composite_score": 1.0,  # Default low score
            "needs_fact_check": False
        }

def get_video_of_week(days: int = 7) -> Optional[Dict[str, Any]]:
    """Get the highest-scored video from the last week"""
    from .db import SessionLocal
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone
    
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        row = db.execute(text("""
            SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                   a.published_at, s.composite_score, s.topics, s.summary2, s.why1
            FROM articles a
            JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND s.media_type = 'video'
              AND a.lang = 'en'
            ORDER BY s.composite_score DESC, a.published_at DESC
            LIMIT 1
        """), {"cutoff": cutoff.isoformat()}).fetchone()
        
        if row:
            return {
                "id": row.id,
                "url": row.url,
                "source": row.source,
                "title": row.title,
                "summary": row.summary2 or row.summary_raw,
                "published_at": row.published_at,
                "score": float(row.composite_score),
                "topics": row.topics or [],
                "why_relevant": row.why1 or "Video insights for construction/development strategy"
            }
    
    finally:
        db.close()
    
    return None

def get_video_feed(limit: int = 20, days: int = 30) -> List[Dict[str, Any]]:
    """Get browsable feed of recent videos"""
    from .db import SessionLocal
    from sqlalchemy import text
    from datetime import datetime, timedelta, timezone
    
    db = SessionLocal()
    try:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        
        rows = db.execute(text("""
            SELECT a.id, a.url, a.source, a.title, a.summary_raw, a.content,
                   a.published_at, s.composite_score, s.topics, s.summary2, s.why1
            FROM articles a
            JOIN article_scores s ON s.article_id = a.id
            WHERE a.published_at >= :cutoff
              AND s.media_type = 'video'
              AND a.lang = 'en'
              AND s.composite_score > 0
            ORDER BY s.composite_score DESC, a.published_at DESC
            LIMIT :limit
        """), {"cutoff": cutoff.isoformat(), "limit": limit}).fetchall()
        
        videos = []
        for row in rows:
            videos.append({
                "id": row.id,
                "url": row.url,
                "source": row.source,
                "title": row.title,
                "summary": row.summary2 or row.summary_raw,
                "published_at": row.published_at,
                "score": float(row.composite_score),
                "topics": row.topics or [],
                "video_id": extract_video_id(row.url),
                "thumbnail": f"https://img.youtube.com/vi/{extract_video_id(row.url)}/maxresdefault.jpg" if extract_video_id(row.url) else None
            })
        
        return videos
    
    finally:
        db.close()

