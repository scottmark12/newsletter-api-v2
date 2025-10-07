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
        """Extract the best image from HTML content using Lovable's improved strategy"""
        images = []
        
        # Strategy 1: JSON-LD structured data (highest priority - like Lovable)
        jsonld_images = self._extract_jsonld_images(html_content, base_url)
        images.extend(jsonld_images)
        
        # Strategy 2: Comprehensive meta tags (like Lovable)
        meta_images = self._extract_comprehensive_meta_images(html_content, base_url)
        images.extend(meta_images)
        
        # Strategy 3: Article/hero images with better detection
        hero_images = self._extract_hero_images(html_content, base_url)
        images.extend(hero_images)
        
        # Strategy 4: Content images
        content_images = self._extract_content_images(html_content, base_url)
        images.extend(content_images)
        
        # Filter and score images using Lovable's smart selection
        valid_images = self._filter_and_rank_images(images)
        
        if not valid_images:
            return None
        
        # Return the best image using Lovable's ranking
        return valid_images[0]['url']
    
    def _extract_jsonld_images(self, html_content: str, base_url: str) -> List[dict]:
        """Extract images from JSON-LD structured data (like Lovable)"""
        images = []
        
        # Find JSON-LD scripts
        script_pattern = r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>([\s\S]*?)</script>'
        matches = re.findall(script_pattern, html_content, re.IGNORECASE)
        
        for json_text in matches:
            try:
                import json as json_lib
                data = json_lib.loads(json_text.strip())
                
                # Recursively collect image URLs from JSON-LD
                def collect_images(node):
                    if not node:
                        return
                    if isinstance(node, str):
                        if node.startswith('http') and any(ext in node.lower() for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']):
                            image_url = urljoin(base_url, node)
                            images.append({
                                'url': image_url,
                                'type': 'jsonld',
                                'priority': 1,  # Highest priority like Lovable
                                'context': 'structured_data'
                            })
                        return
                    if isinstance(node, list):
                        for item in node:
                            collect_images(item)
                        return
                    if isinstance(node, dict):
                        # Look for common image fields
                        for key in ['image', 'thumbnailUrl', 'logo', 'contentUrl']:
                            if key in node:
                                collect_images(node[key])
                        # Special handling for NewsArticle/Article
                        if node.get('@type') in ['NewsArticle', 'Article'] and 'image' in node:
                            collect_images(node['image'])
                        # Recursively check all values
                        for value in node.values():
                            collect_images(value)
                
                collect_images(data)
                
            except Exception as e:
                logger.debug(f"Failed to parse JSON-LD: {e}")
                continue
        
        return images
    
    def _extract_comprehensive_meta_images(self, html_content: str, base_url: str) -> List[dict]:
        """Extract images using comprehensive meta tag patterns (like Lovable)"""
        images = []
        
        # Lovable's comprehensive meta patterns
        meta_patterns = [
            r'<meta[^>]+property=["\']og:image:secure_url["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+name=["\']og:image["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+name=["\']twitter:image:src["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
            r'<link[^>]+rel=["\']image_src["\'][^>]+href=["\']([^"\']+)["\'][^>]*>',
            r'<meta[^>]+itemprop=["\']image["\'][^>]+content=["\']([^"\']+)["\'][^>]*>',
        ]
        
        for pattern in meta_patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                image_url = urljoin(base_url, match)
                images.append({
                    'url': image_url,
                    'type': 'meta',
                    'priority': 2,
                    'context': 'meta_tag'
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
    
    def _filter_and_rank_images(self, images: List[dict]) -> List[dict]:
        """Filter and rank images using Lovable's smart selection approach"""
        valid_images = []
        
        for image in images:
            url = image['url']
            
            # Skip if URL is too short
            if len(url) < 20:
                continue
            
            # Lovable's skip patterns (more comprehensive)
            skip_patterns = [
                'sprite', 'logo', 'icon', 'spacer', 'pixel', '1x1',
                'avatar', 'profile', 'thumbnail', 'placeholder', 
                'banner', 'advertisement', 'ads', 'favicon'
            ]
            
            if any(pattern in url.lower() for pattern in skip_patterns):
                continue
            
            # Must have image extension or be from known image domains
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.avif']
            image_domains = ['images.', 'img.', 'cdn.', 'media.', 'static.', 'assets.']
            
            has_extension = any(ext in url.lower() for ext in image_extensions)
            has_domain = any(domain in url.lower() for domain in image_domains)
            
            if has_extension or has_domain:
                # Lovable's smart ranking system
                ranking_score = 0
                
                # Prefer images with featured keywords (like Lovable)
                featured_keywords = ['hero', 'featured', 'lead', 'main', 'social', 'share', 'og']
                if any(keyword in url.lower() for keyword in featured_keywords):
                    ranking_score += 2
                
                # Prefer larger images
                if any(size in url for size in ['1920', '1600', '1200', '800']):
                    ranking_score += 1.5
                elif any(size in url for size in ['600', 'large', 'full']):
                    ranking_score += 1
                elif any(size in url for size in ['400', 'medium']):
                    ranking_score += 0.5
                
                # Prefer CDN and media domains
                if any(domain in url.lower() for domain in ['cdn.', 'media.', 'images.']):
                    ranking_score += 0.5
                
                # Boost JSON-LD and meta tag images
                if image.get('type') == 'jsonld':
                    ranking_score += 1
                elif image.get('type') == 'meta':
                    ranking_score += 0.5
                
                image['ranking_score'] = ranking_score
                valid_images.append(image)
        
        # Sort by priority first, then by ranking score (like Lovable)
        valid_images.sort(key=lambda x: (x['priority'], -x.get('ranking_score', 0)))
        
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
