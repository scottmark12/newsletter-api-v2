"""
Video processing system for Newsletter API v4
YouTube integration with transcript analysis and scoring
"""

import re
import asyncio
import aiohttp
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
import json

from .config import get_config
from .scoring import V4Scorer


@dataclass
class VideoData:
    """Video data structure"""
    title: str
    youtube_id: str
    url: str
    channel_name: str
    duration: Optional[int] = None
    view_count: Optional[int] = None
    published_at: Optional[datetime] = None
    thumbnail_url: Optional[str] = None
    transcript: Optional[str] = None
    summary: Optional[str] = None


class YouTubeExtractor:
    """Extracts YouTube video information"""
    
    def __init__(self):
        self.config = get_config()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Newsletter API v4 Bot'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def extract_youtube_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/v\/([^&\n?#]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    async def get_video_info(self, youtube_id: str) -> Optional[VideoData]:
        """Get video information from YouTube"""
        if not self.config.data_sources.youtube_api_key:
            print("YouTube API key not configured")
            return None
        
        try:
            url = "https://www.googleapis.com/youtube/v3/videos"
            params = {
                'key': self.config.data_sources.youtube_api_key,
                'id': youtube_id,
                'part': 'snippet,statistics,contentDetails'
            }
            
            async with self.session.get(url, params=params) as response:
                if response.status != 200:
                    print(f"YouTube API error: Status {response.status}")
                    return None
                
                data = await response.json()
                items = data.get('items', [])
                
                if not items:
                    return None
                
                video = items[0]
                snippet = video['snippet']
                statistics = video.get('statistics', {})
                content_details = video.get('contentDetails', {})
                
                # Parse duration (ISO 8601 format)
                duration_str = content_details.get('duration', '')
                duration = self._parse_duration(duration_str)
                
                # Parse view count
                view_count = None
                if 'viewCount' in statistics:
                    view_count = int(statistics['viewCount'])
                
                # Parse published date
                published_at = None
                if 'publishedAt' in snippet:
                    published_at = datetime.fromisoformat(
                        snippet['publishedAt'].replace('Z', '+00:00')
                    )
                
                return VideoData(
                    title=snippet.get('title', ''),
                    youtube_id=youtube_id,
                    url=f"https://www.youtube.com/watch?v={youtube_id}",
                    channel_name=snippet.get('channelTitle', ''),
                    duration=duration,
                    view_count=view_count,
                    published_at=published_at,
                    thumbnail_url=snippet.get('thumbnails', {}).get('high', {}).get('url')
                )
                
        except Exception as e:
            print(f"YouTube API error: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> Optional[int]:
        """Parse ISO 8601 duration to seconds"""
        if not duration_str:
            return None
        
        # Remove PT prefix
        duration_str = duration_str.replace('PT', '')
        
        total_seconds = 0
        
        # Parse hours
        if 'H' in duration_str:
            hours = re.search(r'(\d+)H', duration_str)
            if hours:
                total_seconds += int(hours.group(1)) * 3600
        
        # Parse minutes
        if 'M' in duration_str:
            minutes = re.search(r'(\d+)M', duration_str)
            if minutes:
                total_seconds += int(minutes.group(1)) * 60
        
        # Parse seconds
        if 'S' in duration_str:
            seconds = re.search(r'(\d+)S', duration_str)
            if seconds:
                total_seconds += int(seconds.group(1))
        
        return total_seconds if total_seconds > 0 else None


class TranscriptExtractor:
    """Extracts and processes video transcripts"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_transcript(self, youtube_id: str) -> Optional[str]:
        """Extract transcript from YouTube video"""
        try:
            # Try to get transcript from YouTube's transcript API
            transcript_url = f"https://www.youtube.com/api/timedtext?v={youtube_id}&lang=en"
            
            async with self.session.get(transcript_url) as response:
                if response.status == 200:
                    content = await response.text()
                    # Parse XML transcript
                    transcript = self._parse_transcript_xml(content)
                    if transcript:
                        return transcript
            
            # Fallback: try different language codes
            for lang in ['en-US', 'en-GB', 'en']:
                transcript_url = f"https://www.youtube.com/api/timedtext?v={youtube_id}&lang={lang}"
                async with self.session.get(transcript_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        transcript = self._parse_transcript_xml(content)
                        if transcript:
                            return transcript
            
            return None
            
        except Exception as e:
            print(f"Transcript extraction error: {e}")
            return None
    
    def _parse_transcript_xml(self, xml_content: str) -> Optional[str]:
        """Parse YouTube transcript XML"""
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(xml_content)
            
            transcript_parts = []
            for text_elem in root.findall('.//text'):
                text = text_elem.text
                if text:
                    transcript_parts.append(text.strip())
            
            return ' '.join(transcript_parts) if transcript_parts else None
            
        except Exception as e:
            print(f"Transcript XML parsing error: {e}")
            return None
    
    def summarize_transcript(self, transcript: str) -> str:
        """Create a summary of the transcript"""
        if not transcript:
            return ""
        
        # Simple summarization - take first few sentences
        sentences = re.split(r'[.!?]+', transcript)
        summary_sentences = sentences[:3]  # Take first 3 sentences
        
        summary = '. '.join([s.strip() for s in summary_sentences if s.strip()])
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary


class VideoScorer:
    """Scores videos based on content relevance and quality"""
    
    def __init__(self):
        self.scorer = V4Scorer()
    
    def score_video(self, video_data: VideoData) -> Dict[str, float]:
        """Score a video based on content and metadata"""
        if not video_data.transcript:
            return {
                "total_score": 0.0,
                "content_score": 0.0,
                "engagement_score": 0.0,
                "relevance_score": 0.0
            }
        
        # Score content based on transcript
        content_score = self._score_content(video_data.transcript, video_data.title)
        
        # Score engagement based on metadata
        engagement_score = self._score_engagement(video_data)
        
        # Score relevance based on channel and keywords
        relevance_score = self._score_relevance(video_data)
        
        # Calculate total score
        total_score = (
            content_score * 0.5 +
            engagement_score * 0.3 +
            relevance_score * 0.2
        )
        
        return {
            "total_score": min(total_score, 10.0),
            "content_score": content_score,
            "engagement_score": engagement_score,
            "relevance_score": relevance_score
        }
    
    def _score_content(self, transcript: str, title: str) -> float:
        """Score video content based on transcript analysis"""
        if not transcript:
            return 0.0
        
        # Use the main scorer to analyze content
        scoring_result = self.scorer.score_article(title, transcript, "YouTube", "")
        
        # Focus on insight quality and narrative signal for videos
        return (
            scoring_result.insight_quality * 2.0 +
            scoring_result.narrative_signal * 1.5 +
            scoring_result.total_score * 0.5
        ) / 4.0
    
    def _score_engagement(self, video_data: VideoData) -> float:
        """Score video engagement based on metadata"""
        score = 5.0  # Base score
        
        # View count scoring
        if video_data.view_count:
            if video_data.view_count > 1000000:  # 1M+ views
                score += 2.0
            elif video_data.view_count > 100000:  # 100K+ views
                score += 1.5
            elif video_data.view_count > 10000:  # 10K+ views
                score += 1.0
        
        # Duration scoring (prefer 5-30 minute videos)
        if video_data.duration:
            if 300 <= video_data.duration <= 1800:  # 5-30 minutes
                score += 1.0
            elif video_data.duration > 3600:  # Over 1 hour
                score -= 1.0
        
        return min(score, 10.0)
    
    def _score_relevance(self, video_data: VideoData) -> float:
        """Score video relevance based on channel and content"""
        score = 5.0  # Base score
        
        # Channel relevance
        channel_lower = video_data.channel_name.lower()
        relevant_keywords = [
            'construction', 'engineering', 'architecture', 'real estate',
            'building', 'infrastructure', 'development', 'property',
            'commercial', 'residential', 'industrial', 'sustainability'
        ]
        
        for keyword in relevant_keywords:
            if keyword in channel_lower:
                score += 1.0
                break
        
        # Title relevance
        title_lower = video_data.title.lower()
        for keyword in relevant_keywords:
            if keyword in title_lower:
                score += 0.5
        
        return min(score, 10.0)


class VideoProcessor:
    """Main video processing orchestrator"""
    
    def __init__(self):
        self.config = get_config()
        self.scorer = VideoScorer()
    
    async def process_video_url(self, url: str) -> Optional[Dict]:
        """Process a single video URL"""
        async with YouTubeExtractor() as extractor:
            # Extract YouTube ID
            youtube_id = extractor.extract_youtube_id(url)
            if not youtube_id:
                print(f"Could not extract YouTube ID from: {url}")
                return None
            
            # Get video info
            video_data = await extractor.get_video_info(youtube_id)
            if not video_data:
                print(f"Could not get video info for: {youtube_id}")
                return None
            
            # Get transcript
            async with TranscriptExtractor() as transcript_extractor:
                transcript = await transcript_extractor.get_transcript(youtube_id)
                video_data.transcript = transcript
                
                # Create summary
                if transcript:
                    video_data.summary = transcript_extractor.summarize_transcript(transcript)
            
            # Score the video
            scores = self.scorer.score_video(video_data)
            
            # Return processed video data
            return {
                "video_data": video_data,
                "scores": scores,
                "youtube_id": youtube_id
            }
    
    async def process_video_urls(self, urls: List[str]) -> List[Dict]:
        """Process multiple video URLs"""
        results = []
        
        for url in urls:
            print(f"Processing video: {url}")
            result = await self.process_video_url(url)
            if result:
                results.append(result)
            
            # Rate limiting
            await asyncio.sleep(1.0)
        
        return results
    
    async def find_relevant_videos(self, query: str, max_results: int = 10) -> List[Dict]:
        """Find and process relevant videos based on search query"""
        if not self.config.data_sources.youtube_api_key:
            print("YouTube API key not configured for search")
            return []
        
        try:
            async with YouTubeExtractor() as extractor:
                # Search for videos
                search_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'key': self.config.data_sources.youtube_api_key,
                    'part': 'snippet',
                    'q': query,
                    'type': 'video',
                    'maxResults': max_results,
                    'order': 'relevance',
                    'publishedAfter': '2024-01-01T00:00:00Z'  # Recent videos
                }
                
                async with extractor.session.get(search_url, params=params) as response:
                    if response.status != 200:
                        print(f"YouTube search error: Status {response.status}")
                        return []
                    
                    data = await response.json()
                    video_urls = []
                    
                    for item in data.get('items', []):
                        video_id = item['id']['videoId']
                        video_urls.append(f"https://www.youtube.com/watch?v={video_id}")
                    
                    # Process found videos
                    return await self.process_video_urls(video_urls)
                    
        except Exception as e:
            print(f"YouTube search error: {e}")
            return []


# Convenience functions
async def process_youtube_video(url: str) -> Optional[Dict]:
    """Process a single YouTube video"""
    processor = VideoProcessor()
    return await processor.process_video_url(url)


async def find_construction_videos() -> List[Dict]:
    """Find and process construction-related videos"""
    processor = VideoProcessor()
    queries = [
        "construction technology 2024",
        "sustainable building practices",
        "construction industry trends",
        "real estate development projects",
        "construction innovation"
    ]
    
    all_videos = []
    for query in queries:
        videos = await processor.find_relevant_videos(query, 3)
        all_videos.extend(videos)
    
    return all_videos
