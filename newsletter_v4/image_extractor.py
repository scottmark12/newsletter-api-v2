"""
Image extraction utility for articles
Extracts images from article URLs using server-side web scraping
"""

import re
import asyncio
import aiohttp
from typing import Optional, List
from urllib.parse import urljoin, urlparse
import logging

logger = logging.getLogger(__name__)


class ImageExtractor:
    """Extract images from article URLs"""
    
    def __init__(self):
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=5)
        timeout = aiohttp.ClientTimeout(total=10, connect=5)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=self.headers
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def extract_image_from_url(self, url: str) -> Optional[str]:
        """Extract the best image URL from an article URL"""
        if not url:
            return None
        
        try:
            logger.info(f"Extracting image from: {url}")
            
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status}")
                    return None
                
                content = await response.text()
                
                # Extract images using multiple strategies
                image_url = await self._extract_best_image(content, url)
                
                if image_url:
                    logger.info(f"Found image: {image_url}")
                    return image_url
                else:
                    logger.info(f"No suitable image found for {url}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error extracting image from {url}: {e}")
            return None
    
    async def _extract_best_image(self, html_content: str, base_url: str) -> Optional[str]:
        """Extract the best image from HTML content"""
        images = []
        
        # Strategy 1: Open Graph images (most reliable)
        og_images = self._extract_open_graph_images(html_content, base_url)
        images.extend(og_images)
        
        # Strategy 2: Article/hero images
        hero_images = self._extract_hero_images(html_content, base_url)
        images.extend(hero_images)
        
        # Strategy 3: First large content image
        content_images = self._extract_content_images(html_content, base_url)
        images.extend(content_images)
        
        # Filter and score images
        valid_images = self._filter_valid_images(images)
        
        if not valid_images:
            return None
        
        # Return the best image (first valid one)
        return valid_images[0]['url']
    
    def _extract_open_graph_images(self, html_content: str, base_url: str) -> List[dict]:
        """Extract Open Graph images"""
        images = []
        
        # Look for og:image meta tags
        og_patterns = [
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\'][^>]*>',
        ]
        
        for pattern in og_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                image_url = urljoin(base_url, match)
                images.append({
                    'url': image_url,
                    'type': 'og',
                    'priority': 1
                })
        
        return images
    
    def _extract_hero_images(self, html_content: str, base_url: str) -> List[dict]:
        """Extract hero/featured images"""
        images = []
        
        # Look for common hero image patterns
        hero_patterns = [
            # Article hero images
            r'<img[^>]+class=["\'][^"\']*hero[^"\']*["\'][^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<img[^>]+class=["\'][^"\']*featured[^"\']*["\'][^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<img[^>]+class=["\'][^"\']*main[^"\']*["\'][^>]+src=["\']([^"\']+)["\'][^>]*>',
            r'<img[^>]+class=["\'][^"\']*article[^"\']*["\'][^>]+src=["\']([^"\']+)["\'][^>]*>',
            # WordPress featured images
            r'<img[^>]+class=["\'][^"\']*wp-post-image[^"\']*["\'][^>]+src=["\']([^"\']+)["\'][^>]*>',
        ]
        
        for pattern in hero_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                image_url = urljoin(base_url, match)
                images.append({
                    'url': image_url,
                    'type': 'hero',
                    'priority': 2
                })
        
        return images
    
    def _extract_content_images(self, html_content: str, base_url: str) -> List[dict]:
        """Extract content images"""
        images = []
        
        # Look for all img tags
        img_pattern = r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>'
        matches = re.findall(img_pattern, html_content, re.IGNORECASE)
        
        for match in matches:
            image_url = urljoin(base_url, match)
            images.append({
                'url': image_url,
                'type': 'content',
                'priority': 3
            })
        
        return images
    
    def _filter_valid_images(self, images: List[dict]) -> List[dict]:
        """Filter and score images"""
        valid_images = []
        
        for image in images:
            url = image['url']
            
            # Skip if URL is too short
            if len(url) < 20:
                continue
            
            # Skip common non-content images
            skip_patterns = [
                'logo', 'icon', 'avatar', 'profile', 'thumbnail',
                'placeholder', 'spacer', 'pixel', 'banner', 'advertisement',
                'ads', 'favicon', 'social', 'share', 'button'
            ]
            
            if any(pattern in url.lower() for pattern in skip_patterns):
                continue
            
            # Must have image extension or be from known image domains
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
            image_domains = ['images.', 'img.', 'cdn.', 'media.', 'static.']
            
            has_extension = any(ext in url.lower() for ext in image_extensions)
            has_domain = any(domain in url.lower() for domain in image_domains)
            
            if has_extension or has_domain:
                # Prefer larger images (common size indicators)
                size_score = 0
                if any(size in url for size in ['800', '1200', '1600', '1920', 'large', 'full']):
                    size_score = 1
                elif any(size in url for size in ['600', 'medium']):
                    size_score = 0.5
                
                image['size_score'] = size_score
                valid_images.append(image)
        
        # Sort by priority and size score
        valid_images.sort(key=lambda x: (x['priority'], -x.get('size_score', 0)))
        
        return valid_images


async def extract_article_image(url: str) -> Optional[str]:
    """Convenience function to extract image from article URL"""
    async with ImageExtractor() as extractor:
        return await extractor.extract_image_from_url(url)


# Fallback images for when extraction fails
FALLBACK_IMAGES = [
    'https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800&h=600&fit=crop&crop=center&auto=format&q=80',
    'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800&h=600&fit=crop&crop=center&auto=format&q=80',
    'https://images.unsplash.com/photo-1541888946425-d81bb19240f5?w=800&h=600&fit=crop&crop=center&auto=format&q=80',
    'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop&crop=center&auto=format&q=80',
    'https://images.unsplash.com/photo-1581094794329-c8112a89af12?w=800&h=600&fit=crop&crop=center&auto=format&q=80',
]


def get_fallback_image(article_id: int) -> str:
    """Get a unique fallback image based on article ID"""
    index = article_id % len(FALLBACK_IMAGES)
    return FALLBACK_IMAGES[index]
