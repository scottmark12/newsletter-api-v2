# Transcript Handler - Fetches YouTube video transcripts
import re
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy import text

try:
    from youtube_transcript_api import YouTubeTranscriptApi
except ImportError:
    YouTubeTranscriptApi = None

from .db import SessionLocal
from .utils import sha1

# Construction/CRE focused YouTube channels
CONSTRUCTION_CHANNELS = [
    {"id": "UC6x-dVzO-0q_VEy3G69V2Dw", "name": "The B1M"},
    {"id": "UCHnyfMqiRRG1u-2MsSQLbXA", "name": "Practical Engineering"},
    {"id": "UC0intLFzLaudFG-xAvUEO-A", "name": "Building Better"},
]

RELEVANT_KEYWORDS = [
    "construction", "building", "real estate", "development", "architecture",
    "modular", "prefab", "3d print", "mass timber", "concrete", "steel",
    "infrastructure", "project", "developer", "contractor"
]

def extract_video_id(url: str) -> Optional[str]:
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([\w-]+)',
        r'youtube\.com\/embed\/([\w-]+)',
    ]
    for pattern in patterns:
        if match := re.search(pattern, url):
            return match.group(1)
    return None

def get_transcript(video_id: str) -> Optional[str]:
    if not YouTubeTranscriptApi:
        return None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join(entry['text'] for entry in transcript)
    except Exception as e:
        print(f"[transcript] Failed for {video_id}: {e}")
        return None

def fetch_channel_videos(channel_id: str, max_results: int = 10) -> List[Dict[str, Any]]:
    url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        import feedparser
        feed = feedparser.parse(url)
        videos = []
        for entry in feed.entries[:max_results]:
            videos.append({
                "id": extract_video_id(entry.link),
                "title": entry.title,
                "url": entry.link,
                "published": entry.get("published"),
                "summary": entry.get("summary", "")
            })
        return videos
    except Exception as e:
        print(f"[transcript] Error fetching channel {channel_id}: {e}")
        return []

def is_relevant_video(title: str, summary: str, transcript: str) -> bool:
    combined = f"{title} {summary} {transcript[:2000]}".lower()
    return any(keyword in combined for keyword in RELEVANT_KEYWORDS)

def run(limit: int = 20):
    if not YouTubeTranscriptApi:
        return {"ok": False, "error": "Install youtube-transcript-api"}
    
    db = SessionLocal()
    try:
        count = 0
        
        for channel in CONSTRUCTION_CHANNELS:
            if count >= limit:
                break
            
            videos = fetch_channel_videos(channel["id"], max_results=10)
            
            for video in videos:
                if count >= limit:
                    break
                
                if not video["id"]:
                    continue
                
                # Get transcript
                transcript = get_transcript(video["id"])
                if not transcript:
                    continue
                
                # Check relevance
                if not is_relevant_video(video["title"], video["summary"], transcript):
                    continue
                
                # Insert into database
                try:
                    sql = text("""INSERT INTO articles (url, source, title, summary_raw, content, published_at, canonical_hash, lang)
                        VALUES (:url, :source, :title, :summary_raw, :content, :published_at, :canonical_hash, :lang)
                        ON CONFLICT (url) DO NOTHING RETURNING id""")
                    
                    res = db.execute(sql, {
                        "url": video["url"],
                        "source": f"YouTube - {channel['name']}",
                        "title": video["title"][:500],
                        "summary_raw": video["summary"][:1000],
                        "content": f"VIDEO TRANSCRIPT:\n\n{transcript[:30000]}",
                        "published_at": video.get("published", datetime.now(timezone.utc).isoformat()),
                        "canonical_hash": sha1(video["url"]),
                        "lang": "en"
                    })
                    
                    if row := res.fetchone():
                        count += 1
                        # Mark as video content
                        db.execute(text("UPDATE articles SET topics = ARRAY['video_content', 'construction_tech'] WHERE id = :id"), {"id": row[0]})
                        print(f"[transcript] Inserted video: {video['title'][:60]}...")
                
                except Exception as e:
                    print(f"[transcript] Error inserting video: {e}")
        
        db.commit()
        return {"ok": True, "videos_ingested": count}
    
    finally:
        db.close()
