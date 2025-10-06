"""
Newsletter API v4 Scoring System
Flexible, configurable scoring with easy adjustment capabilities
"""

import re
import json
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timezone
from dataclasses import dataclass

from .config import THEMES, SOURCE_TIERS, get_config
from .models import Article, ArticleScore, ArticleInsight

@dataclass
class ScoringResult:
    """Result of scoring an article"""
    composite_score: float
    theme_scores: Dict[str, float]
    narrative_signals: Dict[str, float]
    quality_indicators: Dict[str, bool]
    multipliers: Dict[str, float]
    insights: List[Dict[str, Any]]
    confidence: float

class ThemeDetector:
    """Detects themes in article content"""
    
    def __init__(self):
        self.themes = THEMES
        self._build_keyword_patterns()
    
    def _build_keyword_patterns(self):
        """Build regex patterns for theme detection"""
        self.patterns = {}
        for theme_name, theme_data in self.themes.items():
            keywords = theme_data.get('keywords', [])
            # Create case-insensitive patterns
            pattern = '|'.join(re.escape(keyword) for keyword in keywords)
            self.patterns[theme_name] = re.compile(pattern, re.IGNORECASE)
    
    def detect_themes(self, text: str) -> Dict[str, float]:
        """Detect themes in text with scoring"""
        if not text:
            return {}
        
        text_lower = text.lower()
        theme_scores = {}
        
        for theme_name, pattern in self.patterns.items():
            matches = pattern.findall(text_lower)
            if matches:
                # Score based on number of matches and keyword density
                match_count = len(matches)
                text_length = len(text_lower.split())
                density = match_count / max(text_length, 1)
                theme_scores[theme_name] = match_count * 10 + density * 100
        
        return theme_scores

class NarrativeSignalDetector:
    """Detects narrative signals that indicate quality content"""
    
    def __init__(self):
        self.signals = {
            "transformative_language": {
                "keywords": ["grew from", "scaled up", "turned into", "transformed", "evolved into", "pivoted to"],
                "multiplier": 1.4,
                "description": "Language indicating transformation or evolution"
            },
            "impact_language": {
                "keywords": ["roi", "return on investment", "boosted productivity", "led to growth", "increased efficiency", "reduced costs", "performance data", "metrics show"],
                "multiplier": 1.5,
                "description": "Language indicating measurable impact"
            },
            "prescriptive_language": {
                "keywords": ["insights", "lessons learned", "framework", "how-to guide", "roadmap", "strategy for", "methodology", "best practices", "actionable advice"],
                "multiplier": 1.3,
                "description": "Language indicating actionable guidance"
            }
        }
        self._build_patterns()
    
    def _build_patterns(self):
        """Build regex patterns for signal detection"""
        self.patterns = {}
        for signal_name, signal_data in self.signals.items():
            keywords = signal_data['keywords']
            pattern = '|'.join(re.escape(keyword) for keyword in keywords)
            self.patterns[signal_name] = re.compile(pattern, re.IGNORECASE)
    
    def detect_signals(self, text: str) -> Dict[str, Dict[str, Any]]:
        """Detect narrative signals in text"""
        if not text:
            return {}
        
        signals_detected = {}
        for signal_name, pattern in self.patterns.items():
            matches = pattern.findall(text.lower())
            if matches:
                signal_data = self.signals[signal_name]
                signals_detected[signal_name] = {
                    "matches": len(matches),
                    "multiplier": signal_data["multiplier"],
                    "description": signal_data["description"],
                    "matched_terms": list(set(matches))
                }
        
        return signals_detected

class QualityIndicatorDetector:
    """Detects content quality indicators"""
    
    def __init__(self):
        self.indicators = {
            "roi_data_present": [
                r"roi of (\d+(?:\.\d+)?%)",
                r"return on investment.*?(\d+(?:\.\d+)?%)",
                r"(\d+(?:\.\d+)?%)\s*(?:increase|improvement|gain|boost)",
                r"cost.*?reduced by (\d+(?:\.\d+)?%)",
                r"efficiency.*?improved by (\d+(?:\.\d+)?%)"
            ],
            "performance_metrics_present": [
                "performance data", "metrics", "kpi", "benchmark", "measurement", "analytics", "data shows"
            ],
            "methodology_present": [
                "methodology", "process", "framework", "approach", "system", "workflow", "step-by-step"
            ],
            "case_study_present": [
                "case study", "success story", "example", "implementation", "before and after", "project spotlight"
            ]
        }
    
    def detect_indicators(self, text: str) -> Dict[str, Any]:
        """Detect quality indicators in text"""
        if not text:
            return {"indicators": {}, "confidence": 0.0}
        
        text_lower = text.lower()
        indicators = {}
        total_confidence = 0.0
        
        # ROI data detection
        roi_patterns = self.indicators["roi_data_present"]
        roi_found = False
        for pattern in roi_patterns:
            if re.search(pattern, text_lower):
                roi_found = True
                break
        indicators["roi_data_present"] = roi_found
        if roi_found:
            total_confidence += 0.3
        
        # Performance metrics
        perf_keywords = self.indicators["performance_metrics_present"]
        perf_found = any(keyword in text_lower for keyword in perf_keywords)
        indicators["performance_metrics_present"] = perf_found
        if perf_found:
            total_confidence += 0.2
        
        # Methodology
        method_keywords = self.indicators["methodology_present"]
        method_found = any(keyword in text_lower for keyword in method_keywords)
        indicators["methodology_present"] = method_found
        if method_found:
            total_confidence += 0.25
        
        # Case study
        case_keywords = self.indicators["case_study_present"]
        case_found = any(keyword in text_lower for keyword in case_keywords)
        indicators["case_study_present"] = case_found
        if case_found:
            total_confidence += 0.25
        
        return {
            "indicators": indicators,
            "confidence": min(total_confidence, 1.0)
        }

class InsightExtractor:
    """Extracts actionable insights from article content"""
    
    def extract_insights(self, text: str, title: str) -> List[Dict[str, Any]]:
        """Extract actionable insights from article"""
        insights = []
        
        if not text or not title:
            return insights
        
        # ROI insights
        roi_insights = self._extract_roi_insights(text)
        insights.extend(roi_insights)
        
        # Methodology insights
        method_insights = self._extract_methodology_insights(text)
        insights.extend(method_insights)
        
        # Case study insights
        case_insights = self._extract_case_study_insights(text)
        insights.extend(case_insights)
        
        return insights
    
    def _extract_roi_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract ROI and performance data"""
        insights = []
        roi_patterns = [
            r"roi of (\d+(?:\.\d+)?%)",
            r"return on investment.*?(\d+(?:\.\d+)?%)",
            r"(\d+(?:\.\d+)?%)\s*(?:increase|improvement|gain|boost)",
            r"cost.*?reduced by (\d+(?:\.\d+)?%)",
            r"efficiency.*?improved by (\d+(?:\.\d+)?%)"
        ]
        
        for pattern in roi_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                insights.append({
                    "insight_type": "roi_data",
                    "category": "financial",
                    "title": "ROI/Performance Data",
                    "content": f"Found performance metric: {match}",
                    "value": match,
                    "is_actionable": True,
                    "implementation_difficulty": "easy",
                    "estimated_impact": "high",
                    "confidence_score": 0.85
                })
        
        return insights
    
    def _extract_methodology_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract methodology and process insights"""
        insights = []
        
        methodology_patterns = [
            r"methodology.*?([^.]{20,100})",
            r"process.*?([^.]{20,100})",
            r"framework.*?([^.]{20,100})",
            r"approach.*?([^.]{20,100})"
        ]
        
        for pattern in methodology_patterns:
            matches = re.findall(pattern, text.lower())
            for match in matches:
                if len(match.strip()) > 20:
                    insights.append({
                        "insight_type": "methodology",
                        "category": "operational",
                        "title": "Implementation Methodology",
                        "content": match.strip(),
                        "value": "Methodology identified",
                        "is_actionable": True,
                        "implementation_difficulty": "medium",
                        "estimated_impact": "high",
                        "confidence_score": 0.75
                    })
        
        return insights
    
    def _extract_case_study_insights(self, text: str) -> List[Dict[str, Any]]:
        """Extract case study insights"""
        insights = []
        text_lower = text.lower()
        
        case_study_indicators = ["case study", "success story", "before and after", "project spotlight"]
        
        if any(indicator in text_lower for indicator in case_study_indicators):
            insights.append({
                "insight_type": "case_study",
                "category": "strategic",
                "title": "Case Study Analysis",
                "content": "Article contains case study or success story elements",
                "value": "Case study identified",
                "is_actionable": True,
                "implementation_difficulty": "medium",
                "estimated_impact": "high",
                "confidence_score": 0.80
            })
        
        return insights

class ScoringEngine:
    """Main scoring engine that coordinates all scoring components"""
    
    def __init__(self):
        self.config = get_config().scoring
        self.theme_detector = ThemeDetector()
        self.signal_detector = NarrativeSignalDetector()
        self.quality_detector = QualityIndicatorDetector()
        self.insight_extractor = InsightExtractor()
    
    def score_article(self, article_data: Dict[str, Any]) -> ScoringResult:
        """Score an article using the v4 scoring system"""
        
        # Extract text content
        title = article_data.get('title', '')
        content = article_data.get('content', '') or article_data.get('summary', '')
        source = article_data.get('source', '')
        
        text_blob = f"{title} {content}"
        
        # Check for exclusions
        if self._should_exclude_content(text_blob):
            return ScoringResult(
                composite_score=0.0,
                theme_scores={},
                narrative_signals={},
                quality_indicators={},
                multipliers={},
                insights=[],
                confidence=0.0
            )
        
        # Detect themes
        theme_scores = self.theme_detector.detect_themes(text_blob)
        
        # Detect narrative signals
        narrative_signals = self.signal_detector.detect_signals(text_blob)
        
        # Detect quality indicators
        quality_result = self.quality_detector.detect_indicators(text_blob)
        quality_indicators = quality_result["indicators"]
        
        # Extract insights
        insights = self.insight_extractor.extract_insights(text_blob, title)
        
        # Calculate multipliers
        multipliers = self._calculate_multipliers(narrative_signals, quality_indicators, source)
        
        # Calculate final scores
        final_theme_scores = {}
        for theme, score in theme_scores.items():
            weight = self.config.theme_weights.get(theme, 1.0)
            final_theme_scores[theme] = score * weight
        
        # Apply multipliers
        for theme, score in final_theme_scores.items():
            for multiplier_name, multiplier_value in multipliers.items():
                if multiplier_name in ['case_study_multiplier', 'methodology_multiplier', 'roi_multiplier']:
                    final_theme_scores[theme] *= multiplier_value
        
        # Calculate composite score
        composite_score = sum(final_theme_scores.values()) * multipliers.get('institutional_source_multiplier', 1.0)
        
        # Calculate confidence
        confidence = self._calculate_confidence(quality_result["confidence"], len(insights), len(narrative_signals))
        
        return ScoringResult(
            composite_score=composite_score,
            theme_scores=final_theme_scores,
            narrative_signals=narrative_signals,
            quality_indicators=quality_indicators,
            multipliers=multipliers,
            insights=insights,
            confidence=confidence
        )
    
    def _should_exclude_content(self, text: str) -> bool:
        """Check if content should be excluded"""
        text_lower = text.lower()
        
        for keyword in self.config.exclude_keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text_lower):
                return True
        
        return False
    
    def _calculate_multipliers(self, narrative_signals: Dict, quality_indicators: Dict, source: str) -> Dict[str, float]:
        """Calculate all applicable multipliers"""
        multipliers = {
            "case_study_multiplier": 1.0,
            "methodology_multiplier": 1.0,
            "roi_multiplier": 1.0,
            "narrative_multiplier": 1.0,
            "institutional_source_multiplier": 1.0
        }
        
        # Quality indicator multipliers
        if quality_indicators.get("case_study_present"):
            multipliers["case_study_multiplier"] = self.config.case_study_bonus
        
        if quality_indicators.get("methodology_present"):
            multipliers["methodology_multiplier"] = self.config.methodology_bonus
        
        if quality_indicators.get("roi_data_present"):
            multipliers["roi_multiplier"] = self.config.roi_bonus
        
        # Narrative signal multipliers
        narrative_multiplier = 1.0
        for signal_name, signal_data in narrative_signals.items():
            narrative_multiplier *= signal_data.get("multiplier", 1.0)
        multipliers["narrative_multiplier"] = narrative_multiplier
        
        # Institutional source multiplier
        multipliers["institutional_source_multiplier"] = self._get_source_multiplier(source)
        
        return multipliers
    
    def _get_source_multiplier(self, source: str) -> float:
        """Get multiplier based on source quality"""
        if not source:
            return 1.0
        
        source_lower = source.lower()
        
        for tier_name, tier_data in SOURCE_TIERS.items():
            for tier_source in tier_data["sources"]:
                if tier_source.lower() in source_lower:
                    if tier_name == "tier_1":
                        return 1.5
                    elif tier_name == "tier_2":
                        return 1.3
                    elif tier_name == "tier_3":
                        return 1.2
        
        return 1.0
    
    def _calculate_confidence(self, quality_confidence: float, insights_count: int, signals_count: int) -> float:
        """Calculate overall confidence in scoring"""
        base_confidence = quality_confidence
        insights_bonus = min(insights_count * 0.1, 0.3)
        signals_bonus = min(signals_count * 0.05, 0.2)
        
        return min(base_confidence + insights_bonus + signals_bonus, 1.0)

# Utility functions for database operations
def save_scoring_result(article_id: str, result: ScoringResult, session) -> Tuple[ArticleScore, List[ArticleInsight]]:
    """Save scoring result to database"""
    
    # Create ArticleScore record
    score_record = ArticleScore(
        article_id=article_id,
        opportunities_score=result.theme_scores.get('opportunities', 0),
        practices_score=result.theme_scores.get('practices', 0),
        systems_codes_score=result.theme_scores.get('systems_codes', 0),
        vision_score=result.theme_scores.get('vision', 0),
        transformative_language_score=result.narrative_signals.get('transformative_language', {}).get('matches', 0),
        impact_language_score=result.narrative_signals.get('impact_language', {}).get('matches', 0),
        prescriptive_language_score=result.narrative_signals.get('prescriptive_language', {}).get('matches', 0),
        roi_data_present=result.quality_indicators.get('roi_data_present', False),
        performance_metrics_present=result.quality_indicators.get('performance_metrics_present', False),
        methodology_present=result.quality_indicators.get('methodology_present', False),
        case_study_present=result.quality_indicators.get('case_study_present', False),
        multipliers_applied=result.multipliers,
        composite_score=result.composite_score,
        scoring_confidence=result.confidence
    )
    
    session.add(score_record)
    
    # Create ArticleInsight records
    insight_records = []
    for insight_data in result.insights:
        insight_record = ArticleInsight(
            article_id=article_id,
            insight_type=insight_data['insight_type'],
            category=insight_data['category'],
            title=insight_data['title'],
            content=insight_data['content'],
            value=insight_data['value'],
            is_actionable=insight_data['is_actionable'],
            implementation_difficulty=insight_data['implementation_difficulty'],
            estimated_impact=insight_data['estimated_impact'],
            confidence_score=insight_data['confidence_score']
        )
        insight_records.append(insight_record)
        session.add(insight_record)
    
    return score_record, insight_records

def run_scoring_batch(limit: int = 100, session=None) -> Dict[str, Any]:
    """Run scoring on a batch of unscored articles"""
    if session is None:
        from .models import get_session
        config = get_config()
        session = get_session(config.database.url)
    
    try:
        # Get unscored articles
        unscored_articles = session.query(Article).filter(
            Article.status != 'discarded',
            ~Article.scores.any()
        ).limit(limit).all()
        
        scoring_engine = ScoringEngine()
        scored_count = 0
        excluded_count = 0
        insights_extracted = 0
        
        for article in unscored_articles:
            article_data = {
                'id': str(article.id),
                'title': article.title,
                'content': article.content,
                'summary': article.summary,
                'source': article.source
            }
            
            result = scoring_engine.score_article(article_data)
            
            # Skip if no themes detected or low confidence
            if result.composite_score < 10 or result.confidence < 0.3:
                excluded_count += 1
                continue
            
            # Save scoring result
            save_scoring_result(str(article.id), result, session)
            
            # Update article with theme and quality data
            primary_theme = max(result.theme_scores.keys(), key=lambda k: result.theme_scores[k]) if result.theme_scores else None
            article.primary_theme = primary_theme
            article.secondary_themes = list(result.theme_scores.keys())
            article.actionability_score = min(100, result.composite_score / 5)  # Scale to 0-100
            article.insight_quality = result.confidence * 100  # Scale to 0-100
            
            # Determine content depth
            if result.quality_indicators.get('roi_data_present') and result.quality_indicators.get('methodology_present'):
                article.content_depth = "deep"
            elif result.quality_indicators.get('methodology_present') or result.quality_indicators.get('case_study_present'):
                article.content_depth = "medium"
            else:
                article.content_depth = "shallow"
            
            scored_count += 1
            insights_extracted += len(result.insights)
        
        session.commit()
        
        return {
            "status": "success",
            "scored_articles": scored_count,
            "excluded_articles": excluded_count,
            "insights_extracted": insights_extracted,
            "message": f"Successfully scored {scored_count} articles, excluded {excluded_count}, extracted {insights_extracted} insights"
        }
        
    except Exception as e:
        session.rollback()
        return {
            "status": "error",
            "message": f"Error running scoring: {str(e)}"
        }
    finally:
        session.close()
