"""
Newsletter API v4 Video Processing
YouTube video analysis and scoring integration
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import logging

from .config import get_config
from .models import VideoContent, Article, get_session
from .scoring import ScoringEngine

logger = logging.getLogger(__name__)

class YouTubeProcessor:
    """Processes YouTube videos for content analysis"""
    
    def __init__(self):
        self.config = get_config()
        self.scoring_engine = ScoringEngine()
    
    async def process_video(self, video_id: str) -> Dict[str, Any]:
        """Process a single YouTube video"""
        session = get_session(self.config.database.url)
        
        try:
            video = session.query(VideoContent).filter(VideoContent.video_id == video_id).first()
            if not video:
                logger.error(f"Video {video_id} not found in database")
                return {"status": "error", "message": "Video not found"}
            
            # Get video transcript if available
            transcript = await self._get_video_transcript(video_id)
            
            # Extract video metadata
            metadata = await self._extract_video_metadata(video_id)
            
            # Score the video content
            scoring_result = await self._score_video_content(video, transcript, metadata)
            
            # Update video record
            self._update_video_record(video, scoring_result, transcript, session)
            
            # Create associated article if high quality
            if scoring_result.composite_score >= self.config.scoring.min_composite_score:
                article = self._create_article_from_video(video, scoring_result, transcript)
                session.add(article)
            
            session.commit()
            
            return {
                "status": "success",
                "video_id": video_id,
                "composite_score": scoring_result.composite_score,
                "primary_theme": max(scoring_result.theme_scores.keys(), key=lambda k: scoring_result.theme_scores[k]) if scoring_result.theme_scores else None,
                "insights_count": len(scoring_result.insights)
            }
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing video {video_id}: {str(e)}")
            return {"status": "error", "message": str(e)}
        finally:
            session.close()
    
    async def _get_video_transcript(self, video_id: str) -> Optional[str]:
        """Get video transcript using YouTube API or alternative methods"""
        # For now, we'll use a simple approach
        # In production, you might want to use youtube-transcript-api or similar
        
        try:
            # Try to get transcript from YouTube API
            transcript = await self._fetch_youtube_transcript(video_id)
            if transcript:
                return transcript
            
            # Fallback: extract from description
            video_details = await self._get_video_details(video_id)
            if video_details and video_details.get('description'):
                return self._extract_text_from_description(video_details['description'])
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting transcript for video {video_id}: {str(e)}")
            return None
    
    async def _fetch_youtube_transcript(self, video_id: str) -> Optional[str]:
        """Fetch transcript using YouTube API or third-party service"""
        # This is a placeholder - you would implement actual transcript fetching
        # For example, using youtube-transcript-api:
        # from youtube_transcript_api import YouTubeTranscriptApi
        # try:
        #     transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        #     transcript_text = ' '.join([item['text'] for item in transcript_list])
        #     return transcript_text
        # except:
        #     return None
        
        return None
    
    async def _get_video_details(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video details from YouTube API"""
        if not self.config.data_collection.youtube_api_key:
            return None
        
        url = "https://www.googleapis.com/youtube/v3/videos"
        params = {
            'key': self.config.data_collection.youtube_api_key,
            'id': video_id,
            'part': 'snippet,statistics'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('items'):
                            return data['items'][0]
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
        
        return None
    
    def _extract_text_from_description(self, description: str) -> Optional[str]:
        """Extract meaningful text from video description"""
        if not description:
            return None
        
        # Clean up description
        text = description.strip()
        
        # Remove common YouTube description patterns
        patterns_to_remove = [
            r'Subscribe to.*?channel.*?\n',
            r'Follow us on.*?\n',
            r'Like and subscribe.*?\n',
            r'For more videos.*?\n',
            r'Music:.*?\n',
            r'Equipment:.*?\n',
            r'Links:.*?\n',
            r'https?://\S+',
            r'@\w+',
            r'#\w+'
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Only return if substantial content
        if len(text) > 100:
            return text
        
        return None
    
    async def _extract_video_metadata(self, video_id: str) -> Dict[str, Any]:
        """Extract metadata from video"""
        metadata = {
            "video_id": video_id,
            "has_transcript": False,
            "description_length": 0,
            "title_keywords": [],
            "description_keywords": []
        }
        
        try:
            video_details = await self._get_video_details(video_id)
            if video_details:
                snippet = video_details.get('snippet', {})
                statistics = video_details.get('statistics', {})
                
                metadata.update({
                    "has_transcript": False,  # Would be determined by transcript availability
                    "description_length": len(snippet.get('description', '')),
                    "view_count": int(statistics.get('viewCount', 0)),
                    "like_count": int(statistics.get('likeCount', 0)),
                    "comment_count": int(statistics.get('commentCount', 0))
                })
                
                # Extract keywords from title and description
                title = snippet.get('title', '')
                description = snippet.get('description', '')
                
                metadata["title_keywords"] = self._extract_keywords(title)
                metadata["description_keywords"] = self._extract_keywords(description)
        
        except Exception as e:
            logger.error(f"Error extracting metadata for video {video_id}: {str(e)}")
        
        return metadata
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract relevant keywords from text"""
        if not text:
            return []
        
        # Simple keyword extraction - in production, you might use NLP libraries
        # Remove common words and extract meaningful terms
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        keywords = [word for word in words if word not in stop_words]
        
        # Return unique keywords, limited to top 20
        return list(set(keywords))[:20]
    
    async def _score_video_content(self, video: VideoContent, transcript: Optional[str], metadata: Dict[str, Any]) -> Any:
        """Score video content using the scoring engine"""
        
        # Prepare content for scoring
        content_parts = []
        
        if video.title:
            content_parts.append(video.title)
        
        if video.description:
            content_parts.append(video.description)
        
        if transcript:
            content_parts.append(transcript)
        
        content_text = ' '.join(content_parts)
        
        # Create article-like data structure for scoring
        article_data = {
            'title': video.title,
            'content': content_text,
            'summary': video.description,
            'source': video.channel_name or 'youtube',
            'media_type': 'video'
        }
        
        # Score using the main scoring engine
        scoring_result = self.scoring_engine.score_article(article_data)
        
        # Adjust scoring for video-specific factors
        video_bonus = self._calculate_video_bonus(video, metadata)
        scoring_result.composite_score *= video_bonus
        
        return scoring_result
    
    def _calculate_video_bonus(self, video: VideoContent, metadata: Dict[str, Any]) -> float:
        """Calculate bonus multiplier for video content"""
        bonus = 1.0
        
        # Engagement bonus based on view count
        view_count = metadata.get('view_count', 0)
        if view_count > 100000:
            bonus += 0.2
        elif view_count > 10000:
            bonus += 0.1
        
        # Like ratio bonus
        like_count = metadata.get('like_count', 0)
        if view_count > 0 and like_count > 0:
            like_ratio = like_count / view_count
            if like_ratio > 0.05:  # 5% like ratio
                bonus += 0.1
        
        # Duration bonus (longer videos often have more depth)
        if video.duration:
            if video.duration > 1800:  # 30 minutes
                bonus += 0.15
            elif video.duration > 600:  # 10 minutes
                bonus += 0.1
        
        # Transcript bonus
        if metadata.get('has_transcript'):
            bonus += 0.2
        
        return min(bonus, 1.5)  # Cap at 50% bonus
    
    def _update_video_record(self, video: VideoContent, scoring_result: Any, transcript: Optional[str], session):
        """Update video record with scoring results"""
        video.processed = True
        video.transcript_available = bool(transcript)
        video.transcript = transcript
        
        # Set primary theme
        if scoring_result.theme_scores:
            video.primary_theme = max(scoring_result.theme_scores.keys(), key=lambda k: scoring_result.theme_scores[k])
        
        # Set quality scores
        video.actionability_score = min(100, scoring_result.composite_score / 5)
        video.insight_quality = scoring_result.confidence * 100
        
        # Update timestamps
        video.updated_at = datetime.now(timezone.utc)
    
    def _create_article_from_video(self, video: VideoContent, scoring_result: Any, transcript: Optional[str]) -> Article:
        """Create an article record from a high-quality video"""
        
        # Use transcript if available, otherwise use description
        content = transcript or video.description or ''
        
        article = Article(
            url=video.video_url,
            title=video.title,
            content=content,
            summary=video.description or content[:500] + '...' if len(content) > 500 else content,
            source=video.channel_name or 'youtube',
            published_at=video.published_at,
            lang='en',
            status='fetched',
            media_type='video',
            video_url=video.video_url,
            video_duration=video.duration,
            video_thumbnail=video.thumbnail_url,
            primary_theme=video.primary_theme,
            actionability_score=video.actionability_score,
            insight_quality=video.insight_quality
        )
        
        return article
    
    async def process_video_batch(self, limit: int = 50) -> Dict[str, Any]:
        """Process a batch of unprocessed videos"""
        session = get_session(self.config.database.url)
        
        try:
            # Get unprocessed videos
            videos = session.query(VideoContent).filter(
                VideoContent.processed == False
            ).limit(limit).all()
            
            results = {
                'processed': 0,
                'high_quality': 0,
                'articles_created': 0,
                'errors': 0
            }
            
            for video in videos:
                try:
                    result = await self.process_video(video.video_id)
                    
                    if result['status'] == 'success':
                        results['processed'] += 1
                        
                        if result['composite_score'] >= self.config.scoring.min_composite_score:
                            results['high_quality'] += 1
                            results['articles_created'] += 1
                    else:
                        results['errors'] += 1
                
                except Exception as e:
                    logger.error(f"Error processing video {video.video_id}: {str(e)}")
                    results['errors'] += 1
                    continue
            
            return results
            
        except Exception as e:
            logger.error(f"Error in video batch processing: {str(e)}")
            return {'status': 'error', 'message': str(e)}
        finally:
            session.close()

class VideoIntegrationService:
    """Service to integrate video content with the main platform"""
    
    def __init__(self):
        self.processor = YouTubeProcessor()
        self.config = get_config()
    
    async def get_best_video_for_theme(self, theme: str, limit: int = 1) -> Optional[Dict[str, Any]]:
        """Get the best video for a specific theme"""
        session = get_session(self.config.database.url)
        
        try:
            # Query for best videos in the theme
            videos = session.query(VideoContent).filter(
                VideoContent.primary_theme == theme,
                VideoContent.processed == True,
                VideoContent.actionability_score >= 60
            ).order_by(VideoContent.actionability_score.desc()).limit(limit).all()
            
            if not videos:
                return None
            
            video = videos[0]
            
            # Get associated article if exists
            article = session.query(Article).filter(Article.video_url == video.video_url).first()
            
            return {
                'video_id': video.video_id,
                'title': video.title,
                'description': video.description,
                'video_url': video.video_url,
                'thumbnail_url': video.thumbnail_url,
                'duration': video.duration,
                'channel_name': video.channel_name,
                'actionability_score': video.actionability_score,
                'insight_quality': video.insight_quality,
                'published_at': video.published_at,
                'article_id': str(article.id) if article else None,
                'transcript_available': video.transcript_available
            }
            
        except Exception as e:
            logger.error(f"Error getting best video for theme {theme}: {str(e)}")
            return None
        finally:
            session.close()
    
    async def get_videos_for_homepage(self) -> Dict[str, Any]:
        """Get the best video for each theme for homepage display"""
        videos = {}
        
        themes = ['opportunities', 'practices', 'systems_codes', 'vision']
        
        for theme in themes:
            video = await self.get_best_video_for_theme(theme)
            if video:
                videos[theme] = video
        
        return videos
