"""
Intelligent scoring system for Newsletter API v4
Clean, configurable scoring with theme detection and insight analysis
"""

import re
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from .config import get_config


@dataclass
class ScoringResult:
    """Result of article scoring"""
    total_score: float
    theme_scores: Dict[str, float]
    insight_quality: float
    narrative_signal: float
    source_credibility: float
    scoring_details: Dict


class ThemeDetector:
    """Detects themes in article content using comprehensive keyword sets"""
    
    def __init__(self):
        # Comprehensive keyword sets based on v3 system
        self.theme_keywords = {
            "opportunities": {
                # Market growth and investment
                "market growth", "expansion", "investment", "funding", "acquisition", "merger",
                "venture capital", "private equity", "investment opportunity", "market opportunity",
                "emerging market", "growth market", "hot market", "booming market",
                
                # Development and construction
                "new project", "development", "construction starts", "permit", "zoning",
                "groundbreaking", "ground breaking", "project announcement", "project launch",
                "construction project", "development project", "infrastructure project",
                
                # Business opportunities
                "business opportunity", "market opportunity", "investment opportunity",
                "revenue opportunity", "profit opportunity", "growth opportunity",
                "expansion opportunity", "development opportunity", "partnership opportunity",
                
                # Market trends
                "market trend", "industry trend", "emerging trend", "growing trend",
                "market shift", "industry shift", "paradigm shift", "market transformation",
                "industry transformation", "market disruption", "industry disruption",
                
                # Financial terms
                "million", "billion", "investment", "funding", "capital", "equity",
                "revenue", "profit", "earnings", "growth", "expansion", "acquisition",
                
                # Project stages
                "approved", "permitted", "entitled", "rezoned", "funded", "financed",
                "designed", "planned", "proposed", "announced", "launched", "started",
                "begins", "opens", "completed", "finished", "delivered", "operational"
            },
            
            "practices": {
                # Technology and innovation
                "technology", "digital", "automation", "AI", "artificial intelligence",
                "machine learning", "software", "app", "platform", "system", "tool",
                "innovation", "innovative", "cutting-edge", "state-of-the-art", "advanced",
                "digital transformation", "tech adoption", "technology implementation",
                
                # Building practices
                "best practice", "methodology", "process", "workflow", "efficiency",
                "optimization", "improvement", "enhancement", "streamlining",
                "construction method", "building method", "construction technique",
                "building technique", "construction practice", "building practice",
                
                # Sustainability
                "sustainability", "sustainable", "green", "LEED", "energy efficiency",
                "carbon", "carbon neutral", "net zero", "zero energy", "passive house",
                "green building", "eco-friendly", "environmentally friendly", "green tech",
                "renewable energy", "solar", "wind", "energy storage", "battery",
                
                # Safety and compliance
                "safety", "compliance", "regulation", "standard", "protocol", "guideline",
                "safety protocol", "safety standard", "compliance standard", "safety procedure",
                "safety measure", "safety practice", "safety requirement", "safety guideline",
                
                # Materials and construction
                "material", "materials", "construction material", "building material",
                "prefab", "prefabricated", "modular", "mass timber", "cross-laminated timber",
                "steel", "concrete", "wood", "bamboo", "composite", "fiber-reinforced",
                "smart material", "advanced material", "innovative material", "new material"
            },
            
            "systems": {
                # Systems and infrastructure
                "system", "systems", "infrastructure", "platform", "framework", "architecture",
                "network", "database", "cloud", "server", "data center", "facility",
                "integration", "connectivity", "interconnection", "interoperability",
                
                # Workflow and process
                "workflow", "process", "processes", "automation", "standardization",
                "streamlining", "optimization", "efficiency", "productivity", "performance",
                "management system", "control system", "monitoring system", "tracking system",
                
                # Governance and policy
                "governance", "policy", "policies", "regulation", "regulations", "compliance",
                "audit", "standard", "standards", "guideline", "guidelines", "protocol",
                "requirement", "requirements", "specification", "specifications",
                
                # Building codes and regulations
                "building code", "building codes", "code compliance", "code requirement",
                "zoning", "zoning code", "zoning regulation", "zoning requirement",
                "permit", "permits", "permitting", "approval", "approvals", "certification",
                "inspection", "inspections", "enforcement", "violation", "violations",
                
                # Technology systems
                "smart building", "smart buildings", "IoT", "internet of things", "sensors",
                "automation system", "building automation", "HVAC system", "electrical system",
                "plumbing system", "fire safety system", "security system", "access control",
                "energy management", "building management", "facility management"
            },
            
            "vision": {
                # Future and strategy
                "future", "vision", "strategy", "roadmap", "planning", "forecast",
                "prediction", "projection", "outlook", "scenario", "plan", "strategy",
                "strategic", "strategic plan", "strategic vision", "future vision",
                
                # Transformation and evolution
                "transformation", "evolution", "paradigm shift", "next generation",
                "revolutionary", "game-changing", "breakthrough", "innovation", "disruption",
                "disruptive", "transformative", "evolutionary", "progressive", "advanced",
                
                # Industry outlook
                "industry outlook", "market prediction", "trend analysis", "market analysis",
                "industry analysis", "market forecast", "industry forecast", "market projection",
                "industry projection", "market trend", "industry trend", "future trend",
                
                # Smart cities and future living
                "smart city", "smart cities", "urban planning", "city planning", "urban design",
                "community", "community development", "neighborhood", "district", "zone",
                "mixed-use", "transit-oriented", "walkable", "sustainable community",
                
                # Innovation and technology
                "innovation", "innovative", "breakthrough", "revolutionary", "cutting-edge",
                "state-of-the-art", "advanced", "next-generation", "future-ready", "future-proof",
                "emerging technology", "new technology", "advanced technology", "innovative technology",
                
                # Sustainability and environment
                "sustainable future", "green future", "carbon neutral", "net zero", "zero waste",
                "circular economy", "sustainable development", "green development", "eco-city",
                "biophilic design", "nature-based", "environmental", "climate", "climate change"
            }
        }
    
    def detect_themes(self, content: str) -> Dict[str, float]:
        """Detect theme relevance scores using comprehensive keyword matching"""
        if not content:
            return {"opportunities": 0.0, "practices": 0.0, "systems": 0.0, "vision": 0.0}
        
        content_lower = content.lower()
        theme_scores = {}
        
        for theme, keywords in self.theme_keywords.items():
            score = 0.0
            matches = 0
            
            # Count keyword matches
            for keyword in keywords:
                if keyword in content_lower:
                    # Weight longer keywords more heavily
                    weight = len(keyword.split()) * 0.2
                    score += weight
                    matches += 1
            
            # Normalize score based on keyword density and content length
            if matches > 0:
                # Base score from matches
                base_score = score / len(keywords) * 10  # Scale to 0-10
                
                # Bonus for multiple matches (indicates strong theme relevance)
                match_bonus = min(matches * 0.5, 2.0)
                
                # Density bonus (more matches relative to content length)
                content_words = len(content_lower.split())
                if content_words > 0:
                    density_bonus = (matches / content_words) * 100
                    density_bonus = min(density_bonus, 3.0)
                else:
                    density_bonus = 0.0
                
                final_score = base_score + match_bonus + density_bonus
                theme_scores[theme] = min(final_score / 10.0, 1.0)  # Normalize to 0-1
            else:
                theme_scores[theme] = 0.0
        
        return theme_scores


class InsightAnalyzer:
    """Analyzes article content for insights and quality"""
    
    def __init__(self):
        self.insight_indicators = [
            r"\b(insight|analysis|finding|discovery|conclusion|implication)\b",
            r"\b(data shows|research indicates|studies reveal|evidence suggests)\b",
            r"\b(trend|pattern|correlation|causation|relationship)\b",
            r"\b(impact|effect|outcome|result|consequence)\b",
        ]
        
        self.quality_indicators = [
            r"\b(comprehensive|detailed|thorough|extensive|in-depth)\b",
            r"\b(statistical|data-driven|evidence-based|empirical)\b",
            r"\b(expert|professional|industry|specialist|authority)\b",
            r"\b(case study|example|illustration|demonstration)\b",
        ]
    
    def analyze_insight_quality(self, content: str) -> float:
        """Analyze the quality of insights in content"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        insight_score = 0.0
        quality_score = 0.0
        
        # Count insight indicators
        for pattern in self.insight_indicators:
            matches = len(re.findall(pattern, content_lower))
            insight_score += matches * 0.2
        
        # Count quality indicators
        for pattern in self.quality_indicators:
            matches = len(re.findall(pattern, content_lower))
            quality_score += matches * 0.15
        
        # Combine scores (normalize to 0-1)
        total_score = (insight_score + quality_score) / 2.0
        return min(total_score, 1.0)


class NarrativeSignalDetector:
    """Detects narrative signals and storytelling quality"""
    
    def __init__(self):
        self.narrative_patterns = [
            r"\b(story|narrative|journey|evolution|transformation)\b",
            r"\b(beginning|start|launch|introduction|background)\b",
            r"\b(challenge|problem|issue|obstacle|barrier)\b",
            r"\b(solution|approach|strategy|method|resolution)\b",
            r"\b(outcome|result|success|achievement|impact)\b",
            r"\b(lesson|learned|takeaway|implication|future)\b",
        ]
    
    def detect_narrative_signal(self, content: str) -> float:
        """Detect narrative storytelling quality"""
        if not content:
            return 0.0
        
        content_lower = content.lower()
        signal_score = 0.0
        
        for pattern in self.narrative_patterns:
            matches = len(re.findall(pattern, content_lower))
            signal_score += matches * 0.1
        
        # Normalize score
        return min(signal_score / 2.0, 1.0)


class SourceCredibilityAnalyzer:
    """Analyzes source credibility and authority"""
    
    def __init__(self):
        self.premium_sources = [
            "construction dive", "engineering news record", "enr",
            "commercial observer", "bisnow", "globest", "costar",
            "jll", "cbre", "cushman", "colliers", "marcus millichap",
            "deloitte", "pwc", "kpmg", "mckinsey", "boston consulting"
        ]
        
        self.institutional_sources = [
            "government", "federal", "state", "municipal", "department",
            "bureau", "commission", "association", "institute", "society",
            "university", "college", "research", "academic"
        ]
    
    def analyze_source_credibility(self, source: str, url: str) -> float:
        """Analyze source credibility score"""
        if not source and not url:
            return 0.5  # Default neutral score
        
        source_lower = (source or "").lower()
        url_lower = (url or "").lower()
        combined_text = f"{source_lower} {url_lower}"
        
        # Check for premium sources
        for premium in self.premium_sources:
            if premium in combined_text:
                return 1.0
        
        # Check for institutional sources
        for institutional in self.institutional_sources:
            if institutional in combined_text:
                return 0.8
        
        # Check for .edu domains (academic)
        if ".edu" in url_lower:
            return 0.9
        
        # Check for .gov domains (government)
        if ".gov" in url_lower:
            return 0.9
        
        # Check for .org domains (non-profit)
        if ".org" in url_lower:
            return 0.7
        
        # Default score for unknown sources
        return 0.5


class V4Scorer:
    """Main scoring engine for v4"""
    
    def __init__(self):
        self.config = get_config()
        self.theme_detector = ThemeDetector()
        self.insight_analyzer = InsightAnalyzer()
        self.narrative_detector = NarrativeSignalDetector()
        self.source_analyzer = SourceCredibilityAnalyzer()
    
    def score_article(self, title: str, content: str, source: str, url: str) -> ScoringResult:
        """Score an article comprehensively"""
        
        # Detect themes
        theme_scores = self.theme_detector.detect_themes(f"{title} {content}")
        
        # Apply theme weights from config
        weighted_theme_scores = {}
        for theme, score in theme_scores.items():
            weight = getattr(self.config.scoring, f"{theme}_weight")
            weighted_theme_scores[theme] = score * weight
        
        # Analyze insights
        insight_quality = self.insight_analyzer.analyze_insight_quality(content)
        weighted_insight_quality = insight_quality * self.config.scoring.insight_quality_weight
        
        # Detect narrative signals
        narrative_signal = self.narrative_detector.detect_narrative_signal(content)
        weighted_narrative_signal = narrative_signal * self.config.scoring.narrative_signal_weight
        
        # Analyze source credibility
        source_credibility = self.source_analyzer.analyze_source_credibility(source, url)
        
        # Apply source bonuses
        if source_credibility >= 0.8:
            source_credibility *= self.config.scoring.institutional_source_bonus
        elif source_credibility >= 0.6:
            source_credibility *= self.config.scoring.premium_source_bonus
        
        # Calculate total score
        theme_total = sum(weighted_theme_scores.values())
        total_score = (
            theme_total * 0.4 +
            weighted_insight_quality * 0.3 +
            weighted_narrative_signal * 0.2 +
            source_credibility * 0.1
        )
        
        # Create scoring details
        scoring_details = {
            "theme_scores": theme_scores,
            "weighted_theme_scores": weighted_theme_scores,
            "insight_quality": insight_quality,
            "narrative_signal": narrative_signal,
            "source_credibility": source_credibility,
            "weights_applied": {
                "insight_quality_weight": self.config.scoring.insight_quality_weight,
                "narrative_signal_weight": self.config.scoring.narrative_signal_weight,
                "institutional_bonus": self.config.scoring.institutional_source_bonus,
                "premium_bonus": self.config.scoring.premium_source_bonus,
            }
        }
        
        return ScoringResult(
            total_score=min(total_score, 10.0),  # Cap at 10.0
            theme_scores=weighted_theme_scores,
            insight_quality=weighted_insight_quality,
            narrative_signal=weighted_narrative_signal,
            source_credibility=source_credibility,
            scoring_details=scoring_details
        )
    
    def extract_insights(self, content: str, theme_scores: Dict[str, float]) -> List[Dict]:
        """Extract specific insights from content"""
        if not content:
            return []
        
        insights = []
        
        # Find sentences that might contain insights
        sentences = re.split(r'[.!?]+', content)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip short sentences
                continue
            
            # Determine which theme this sentence relates to most
            sentence_themes = self.theme_detector.detect_themes(sentence)
            dominant_theme = max(sentence_themes, key=sentence_themes.get)
            
            # Only extract if it has strong theme relevance
            if sentence_themes[dominant_theme] > 0.3:
                insights.append({
                    "text": sentence,
                    "theme": dominant_theme,
                    "confidence": sentence_themes[dominant_theme],
                    "type": "theme_insight"
                })
        
        return insights


# Global scorer instance
scorer = V4Scorer()


def score_article_v4(title: str, content: str, source: str, url: str) -> ScoringResult:
    """Convenience function to score an article"""
    return scorer.score_article(title, content, source, url)


def extract_insights_v4(content: str, theme_scores: Dict[str, float]) -> List[Dict]:
    """Convenience function to extract insights"""
    return scorer.extract_insights(content, theme_scores)
