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
    """Detects themes in article content"""
    
    def __init__(self):
        self.theme_patterns = {
            "opportunities": [
                r"\b(opportunity|market growth|expansion|investment|funding|acquisition|merger)\b",
                r"\b(emerging|trending|hot market|breakthrough|innovation|disruption)\b",
                r"\b(new project|development|construction starts|permit|zoning)\b",
            ],
            "practices": [
                r"\b(best practice|methodology|process|workflow|efficiency|optimization)\b",
                r"\b(technology|digital|automation|AI|machine learning|software)\b",
                r"\b(sustainability|green|LEED|energy efficiency|carbon)\b",
                r"\b(safety|compliance|regulation|standard|protocol)\b",
            ],
            "systems": [
                r"\b(system|infrastructure|platform|framework|architecture)\b",
                r"\b(integration|connectivity|network|database|cloud)\b",
                r"\b(workflow|process|automation|standardization)\b",
                r"\b(governance|policy|regulation|compliance|audit)\b",
            ],
            "vision": [
                r"\b(future|vision|strategy|roadmap|planning|forecast)\b",
                r"\b(transformation|evolution|paradigm shift|next generation)\b",
                r"\b(industry outlook|market prediction|trend analysis)\b",
                r"\b(innovation|breakthrough|revolutionary|game-changing)\b",
            ]
        }
    
    def detect_themes(self, content: str) -> Dict[str, float]:
        """Detect theme relevance scores"""
        if not content:
            return {"opportunities": 0.0, "practices": 0.0, "systems": 0.0, "vision": 0.0}
        
        content_lower = content.lower()
        theme_scores = {}
        
        for theme, patterns in self.theme_patterns.items():
            score = 0.0
            for pattern in patterns:
                matches = len(re.findall(pattern, content_lower))
                score += matches * 0.1  # Weight per match
            
            # Normalize score (max ~3.0 based on pattern count)
            theme_scores[theme] = min(score / 3.0, 1.0)
        
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
