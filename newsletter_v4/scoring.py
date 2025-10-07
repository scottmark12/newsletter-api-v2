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
        # New scoring system with three distinct categories
        self.theme_keywords = {
            "development_deals": {
                # ROI, case study, "scaled up," investment, incentives, market entry, redevelopment
                # Entrepreneurial success stories and wealth creation
                "roi", "return on investment", "case study", "scaled up", "grew from", "turned into",
                "success story", "wealth creation", "small investor", "bootstrap", "family office",
                "airbnb portfolio", "exit strategy", "from.*to.*", "startup", "entrepreneur", "founder", 
                "portfolio", "investment returns", "profit", "revenue growth", "expansion", "acquisition",
                "funding round", "venture capital", "private equity", "angel investor", "seed funding",
                "series a", "series b", "unicorn", "valuation", "market cap", "ipo", "exit",
                "wealth building", "financial success", "business growth", "scaling", "growth strategy",
                "market opportunity", "emerging market", "untapped market", "blue ocean", "disruption",
                
                # Real estate development and investment
                "real estate development", "property development", "development project", "construction project",
                "new development", "mixed use", "commercial development", "residential development",
                "adaptive reuse", "redevelopment", "infill development", "transit oriented development",
                "smart growth", "sustainable development", "green development", "market entry",
                
                # Investment and financial terms
                "investment opportunity", "investment returns", "cash flow", "cap rate", "net operating income",
                "property value", "appreciation", "equity", "debt", "leverage", "refinancing",
                "1031 exchange", "opportunity zone", "tax incentive", "tax credit", "incentive program",
                "incentives", "market entry", "redevelopment",
                
                # Development process and methodology
                "development process", "project management", "construction management", "development strategy",
                "market analysis", "feasibility study", "due diligence", "risk assessment", "project timeline",
                "budget", "cost control", "value engineering", "design build", "design bid build",
                "public private partnership", "ppp", "joint venture", "partnership", "collaboration",
                
                # Market trends and opportunities
                "market trend", "industry trend", "emerging trend", "future trend", "market shift",
                "demographic shift", "lifestyle change", "work from home", "remote work", "hybrid work",
                "urban migration", "suburban growth", "city center", "downtown", "urban core",
                "gentrification", "revitalization", "renewal", "transformation", "renaissance"
            },
            "building_better": {
                # prefab, modular, mass timber, automation, BIM, process, cost savings, safety, efficiency
                # Prefabrication and modular construction
                "prefab", "prefabricated", "prefabrication", "off site construction", "offsite construction",
                "factory built", "manufactured", "modular", "modular construction", "modular building",
                "panelized", "panelized construction", "system built", "volumetric", "containerized",
                "shipping container", "container home", "tiny home", "micro housing", "accessory dwelling unit",
                "adu", "granny flat", "in law suite", "backyard cottage", "laneway house",
                
                # Mass timber and wood construction
                "mass timber", "cross laminated timber", "clt", "glulam", "glued laminated timber",
                "engineered wood", "wood construction", "timber construction", "timber skyscraper",
                "wood skyscraper", "tall wood", "mass timber tower", "wood tower", "timber high rise",
                "wood high rise", "tall timber", "tall wood building", "wood building",
                "engineered wood", "structural wood", "wood frame", "timber frame", "post and beam",
                "heavy timber", "light frame", "platform frame", "balloon frame", "stick built",
                
                # Construction technology and automation
                "automation", "robotics", "ai", "artificial intelligence", "machine learning", "predictive analytics",
                "construction technology", "building technology", "construction innovation", "building innovation",
                "construction tech", "proptech", "contech", "construction software", "building software",
                "bim", "building information modeling", "cad", "computer aided design", "3d modeling",
                "virtual reality", "vr", "augmented reality", "ar", "mixed reality", "mr",
                "drone", "uav", "unmanned aerial vehicle", "surveying", "mapping", "scanning",
                
                # Construction methodology and processes
                "construction methodology", "construction method", "building method", "construction technique",
                "construction process", "building process", "assembly process", "installation process",
                "construction sequence", "construction phasing", "construction scheduling", "project scheduling",
                "critical path", "gantt chart", "project management", "construction management", "cm",
                "general contractor", "subcontractor", "trade contractor", "specialty contractor",
                "process", "cost savings", "safety", "efficiency",
                
                # Quality control and assurance
                "quality control", "quality assurance", "qa", "qc", "testing", "inspection",
                "defect", "rework", "waste", "waste reduction", "material efficiency", "resource efficiency",
                "sustainability", "sustainable construction", "green construction", "eco friendly",
                "environmental impact", "carbon footprint", "embodied carbon", "operational carbon",
                "energy efficiency", "water efficiency", "material efficiency", "waste efficiency"
            },
            "forces_frameworks": {
                # zoning, migration, policy, infrastructure, demand, regulation, regional trend, demographic shift, technology adoption
                # Zoning and land use
                "zoning", "zoning reform", "zoning update", "zoning change", "zoning amendment", "rezoning",
                "upzoning", "downzoning", "zoning variance", "special permit", "conditional use",
                "land use", "land use policy", "comprehensive plan", "master plan", "general plan",
                "development plan", "area plan", "neighborhood plan", "transit plan", "transportation plan",
                
                # Migration and demographic trends
                "migration", "demographic shift", "population shift", "urban migration", "suburban growth",
                "city center", "downtown", "urban core", "gentrification", "revitalization", "renewal",
                "transformation", "renaissance", "demographic trend", "population trend", "regional trend",
                "lifestyle change", "work from home", "remote work", "hybrid work",
                
                # Policy and regulation
                "policy", "regulation", "regulatory", "building code", "construction code", "fire code",
                "electrical code", "plumbing code", "mechanical code", "energy code", "green code",
                "sustainable code", "resilience code", "building code update", "code change", "code revision",
                "code amendment", "code modification", "code update", "new code", "updated code",
                "revised code", "amended code", "construction regulation", "building regulation",
                "development regulation", "permit process", "approval process", "review process",
                "inspection", "building inspection", "code enforcement",
                
                # Infrastructure and demand
                "infrastructure", "infrastructure investment", "transit oriented development", "smart growth",
                "public private partnership", "ppp", "infrastructure spending", "transportation infrastructure",
                "demand", "market demand", "housing demand", "commercial demand", "industrial demand",
                "demand curve", "supply and demand", "market supply", "demand growth", "demand shift",
                
                # Regional trends and technology adoption
                "regional trend", "regional development", "regional growth", "regional planning",
                "technology adoption", "digital transformation", "smart city", "smart building",
                "smart infrastructure", "iot", "internet of things", "sensors", "data collection",
                "analytics", "big data", "building automation", "energy management", "smart grid",
                "renewable energy", "solar", "wind", "geothermal", "energy storage", "battery storage",
                "microgrid", "distributed energy", "clean energy"
            }
        }
    
    def detect_themes(self, content: str) -> Dict[str, float]:
        """Detect theme relevance scores using comprehensive keyword matching"""
        if not content:
            return {
                "development_deals": 0.0, 
                "building_better": 0.0, 
                "forces_frameworks": 0.0
            }
        
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
        
        # Map new categories to API-compatible names
        api_theme_scores = {
            "opportunities": weighted_theme_scores.get("development_deals", 0.0),
            "practices": weighted_theme_scores.get("building_better", 0.0),
            "vision": weighted_theme_scores.get("forces_frameworks", 0.0)
        }
        
        return ScoringResult(
            total_score=min(total_score, 10.0),  # Cap at 10.0
            theme_scores=api_theme_scores,
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
# Test deployment fix
