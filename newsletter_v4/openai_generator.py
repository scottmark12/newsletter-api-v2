import openai
import json
import re
from typing import Dict, List, Optional
from datetime import datetime, timezone

class OpenAIContentGenerator:
    def __init__(self, api_key: str):
        """Initialize OpenAI client with API key"""
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_takeaways(self, title: str, content: str, summary: str) -> List[str]:
        """Generate 3 unique bullet points summarizing key insights from the article"""
        
        # Clean and prepare content
        full_content = f"Title: {title}\n\n"
        if content:
            # Remove HTML tags and clean content
            clean_content = re.sub(r'<[^>]*>', '', content)
            full_content += f"Content: {clean_content[:2000]}\n\n"  # Limit content length
        if summary:
            clean_summary = re.sub(r'<[^>]*>', '', summary)
            full_content += f"Summary: {clean_summary}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert content analyst for the construction and real estate industry. 
                        Your task is to extract 3 key bullet points from articles that highlight the most important, 
                        actionable, or interesting insights. Focus on:
                        - Specific data points, numbers, percentages, or metrics
                        - Business implications and ROI insights
                        - Market trends and opportunities
                        - Technical innovations or methodologies
                        - Regulatory or policy changes
                        
                        Each bullet point should start with a green checkmark emoji (✅) and be concise but informative.
                        Avoid generic statements - extract the meat and potatoes of the article."""
                    },
                    {
                        "role": "user",
                        "content": f"Extract 3 key bullet points from this article:\n\n{full_content}"
                    }
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            # Parse the response and format as bullet points
            content = response.choices[0].message.content.strip()
            
            # Split into bullet points and clean them up
            bullets = []
            for line in content.split('\n'):
                line = line.strip()
                if line:
                    # Remove common bullet markers
                    if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                        line = line[1:].strip()
                    
                    # Ensure checkmark is present
                    if not line.startswith('✅'):
                        line = f"✅ {line}"
                    
                    if len(line) > 15:  # Only include substantial bullets
                        bullets.append(line)
            
            # Ensure we have exactly 3 bullets
            while len(bullets) < 3 and len(bullets) > 0:
                bullets.append(f"✅ Key insight from {title.split(' ')[0]} development sector.")
            
            return bullets[:3]
            
        except Exception as e:
            print(f"Error generating takeaways: {e}")
            # Fallback to basic extraction
            return [
                f"✅ Important development in {title.split(' ')[0]} sector",
                f"✅ Key insights for construction and real estate professionals", 
                f"✅ Market implications from {title.split(' ')[0]} project"
            ]
    
    def generate_why_it_matters(self, title: str, content: str, summary: str, theme_scores: Dict) -> str:
        """Generate a unique 'Why it matters' explanation for the article"""
        
        # Determine the most relevant theme
        most_relevant_theme = "development_deals"
        max_score = 0.0
        
        # Map API theme names to internal theme names
        theme_mapping = {
            "opportunities": "development_deals",
            "practices": "building_better", 
            "vision": "forces_frameworks"
        }
        
        for api_theme, internal_theme in theme_mapping.items():
            score = theme_scores.get(api_theme, 0.0)
            if score > max_score:
                max_score = score
                most_relevant_theme = internal_theme
        
        # Clean and prepare content
        full_content = f"Title: {title}\n\n"
        if content:
            clean_content = re.sub(r'<[^>]*>', '', content)
            full_content += f"Content: {clean_content[:2000]}\n\n"
        if summary:
            clean_summary = re.sub(r'<[^>]*>', '', summary)
            full_content += f"Summary: {clean_summary}"
        
        # Theme-specific prompts
        theme_contexts = {
            "development_deals": "This article is about development deals, investment opportunities, ROI, and wealth creation in real estate development.",
            "building_better": "This article is about construction innovation, building practices, prefabrication, modular construction, and efficiency improvements.",
            "forces_frameworks": "This article is about policy changes, zoning reforms, demographic shifts, infrastructure investment, and market forces."
        }
        
        theme_context = theme_contexts.get(most_relevant_theme, theme_contexts["development_deals"])
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": f"""You are an expert construction and real estate analyst. {theme_context}
                        
                        Your task is to write a compelling 1-2 sentence explanation of why this article matters to industry professionals.
                        Focus on:
                        - Specific business impact and opportunities
                        - Market implications and competitive advantages
                        - ROI potential and strategic positioning
                        - Industry transformation and future trends
                        
                        Write in a confident, insightful tone that helps readers understand the strategic importance.
                        Be specific about the impact and avoid generic statements."""
                    },
                    {
                        "role": "user", 
                        "content": f"Explain why this article matters to construction and real estate professionals:\n\n{full_content}"
                    }
                ],
                max_tokens=150,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Error generating why it matters: {e}")
            # Fallback based on theme
            fallbacks = {
                "development_deals": f"This {title.split(' ')[0]} development represents a significant investment opportunity with strong ROI potential for forward-thinking developers and investors.",
                "building_better": f"The {title.split(' ')[0]} approach showcases innovative construction methods that can dramatically improve efficiency and reduce costs for industry professionals.",
                "forces_frameworks": f"This {title.split(' ')[0]} policy change creates new opportunities and challenges that will reshape how developers approach future projects."
            }
            return fallbacks.get(most_relevant_theme, fallbacks["development_deals"])
    
    def generate_article_content(self, title: str, content: str, summary: str, theme_scores: Dict) -> Dict:
        """Generate both takeaways and why it matters for an article"""
        return {
            "why_it_matters": self.generate_why_it_matters(title, content, summary, theme_scores),
            "takeaways": self.generate_takeaways(title, content, summary)
        }

def get_openai_generator() -> Optional[OpenAIContentGenerator]:
    """Get OpenAI content generator if API key is available"""
    import os
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Warning: OPENAI_API_KEY not found. Content generation will use fallback methods.")
        return None
    return OpenAIContentGenerator(api_key)
