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
        # New comprehensive keyword sets focused on insights, case studies, and actionable content
        self.theme_keywords = {
            "creative_opportunities": {
                # Entrepreneurial success stories and wealth creation
                "airbnb portfolio", "bootstrap", "family office", "wealth creation", "small investor", 
                "case study", "exit strategy", "from.*to.*", "scaled up", "grew from", "turned into",
                "success story", "startup", "entrepreneur", "founder", "portfolio", "investment returns",
                "roi", "return on investment", "profit", "revenue growth", "expansion", "acquisition",
                "funding round", "venture capital", "private equity", "angel investor", "seed funding",
                "series a", "series b", "unicorn", "valuation", "market cap", "ipo", "exit",
                "wealth building", "financial success", "business growth", "scaling", "growth strategy",
                "market opportunity", "emerging market", "untapped market", "blue ocean", "disruption",
                
                # Real estate development and investment
                "real estate development", "property development", "development project", "construction project",
                "new development", "mixed use", "commercial development", "residential development",
                "adaptive reuse", "redevelopment", "infill development", "transit oriented development",
                "smart growth", "sustainable development", "green development", "leed certification",
                "energy efficient", "net zero", "carbon neutral", "sustainable building",
                
                # Investment and financial terms
                "investment opportunity", "investment returns", "cash flow", "cap rate", "net operating income",
                "property value", "appreciation", "equity", "debt", "leverage", "refinancing",
                "1031 exchange", "opportunity zone", "tax incentive", "tax credit", "incentive program",
                
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
            "smart_cities_productivity": {
                # Human-centered design and wellness
                "human centered design", "human-centred design", "user experience", "ux design",
                "biophilic", "biophilic design", "nature inspired", "natural elements", "green space",
                "wellness design", "healthy building", "well building standard", "fitwel",
                "indoor air quality", "natural light", "daylighting", "ventilation", "thermal comfort",
                "acoustic design", "sound design", "noise reduction", "quiet space", "peaceful",
                
                # Placemaking and community impact
                "placemaking", "place making", "public realm", "public space", "civic space",
                "community space", "social space", "gathering space", "activation", "programming",
                "community engagement", "stakeholder engagement", "public participation", "community input",
                "social impact", "community impact", "neighborhood", "local community", "sense of place",
                "place identity", "cultural identity", "local culture", "authentic", "character",
                
                # Productivity and performance studies
                "productivity study", "productivity research", "performance study", "efficiency study",
                "workplace productivity", "office productivity", "employee productivity", "worker productivity",
                "productivity metrics", "performance metrics", "efficiency metrics", "kpi", "key performance indicator",
                "productivity improvement", "efficiency improvement", "performance improvement", "optimization",
                "workplace wellness", "employee wellness", "worker wellness", "health and wellness",
                "stress reduction", "mental health", "cognitive performance", "focus", "concentration",
                
                # Urban wellness and peaceful architecture
                "urban wellness", "city wellness", "urban health", "city health", "public health",
                "peaceful architecture", "calming design", "serene", "tranquil", "meditation space",
                "mindfulness", "wellness center", "health center", "medical facility", "hospital design",
                "healing environment", "therapeutic environment", "restorative", "rejuvenating",
                
                # Smart city and technology integration
                "smart city", "smart building", "smart infrastructure", "iot", "internet of things",
                "sensors", "data collection", "analytics", "big data", "predictive analytics",
                "artificial intelligence", "machine learning", "automation", "building automation",
                "energy management", "smart grid", "renewable energy", "solar", "wind", "geothermal",
                "energy storage", "battery storage", "microgrid", "distributed energy", "clean energy",
                
                # Accessibility and inclusive design
                "accessibility", "accessible design", "universal design", "inclusive design",
                "ada compliance", "barrier free", "mobility", "wheelchair accessible", "assistive technology",
                "aging in place", "senior housing", "multigenerational", "intergenerational", "diversity",
                "equity", "inclusion", "social equity", "environmental justice", "climate justice"
            },
            "policy_code_evolution": {
                # Building codes and regulations
                "mass timber code", "timber code", "wood code", "cross laminated timber", "clt",
                "glulam", "glued laminated timber", "engineered wood", "wood construction", "timber construction",
                "fire rating", "fire resistance", "fire safety", "fire protection", "fire suppression",
                "sprinkler system", "fire alarm", "egress", "exit", "life safety", "building safety",
                "building code", "construction code", "fire code", "electrical code", "plumbing code",
                "mechanical code", "energy code", "green code", "sustainable code", "resilience code",
                
                # Zoning and land use
                "zoning reform", "zoning update", "zoning change", "zoning amendment", "rezoning",
                "upzoning", "downzoning", "zoning variance", "special permit", "conditional use",
                "land use", "land use policy", "comprehensive plan", "master plan", "general plan",
                "development plan", "area plan", "neighborhood plan", "transit plan", "transportation plan",
                
                # Incentives and policy programs
                "incentive expansion", "tax incentive", "development incentive", "construction incentive",
                "green incentive", "sustainability incentive", "energy incentive", "renewable incentive",
                "solar incentive", "wind incentive", "geothermal incentive", "efficiency incentive",
                "tax credit", "development tax credit", "historic tax credit", "low income tax credit",
                "new markets tax credit", "opportunity zone", "enterprise zone", "empowerment zone",
                "brownfield", "brownfield redevelopment", "contaminated site", "environmental cleanup",
                "remediation", "environmental remediation", "site cleanup", "landfill", "superfund",
                
                # Building code updates and changes
                "building code update", "code change", "code revision", "code amendment", "code modification",
                "code update", "new code", "updated code", "revised code", "amended code",
                "construction regulation", "building regulation", "development regulation", "permit process",
                "approval process", "review process", "inspection", "building inspection", "code enforcement",
                
                # Sustainability and green building codes
                "sustainable building code", "green building code", "energy code", "energy efficiency code",
                "renewable energy code", "solar code", "wind code", "geothermal code", "efficiency standard",
                "performance standard", "green standard", "sustainable standard", "resilience standard",
                "climate adaptation", "climate mitigation", "carbon reduction", "net zero", "carbon neutral",
                "leed", "green globes", "living building challenge", "well building standard", "fitwel",
                
                # Timber and wood construction updates
                "timber skyscraper", "wood skyscraper", "tall wood", "mass timber tower", "wood tower",
                "timber high rise", "wood high rise", "tall timber", "tall wood building", "wood building",
                "engineered wood", "structural wood", "wood frame", "timber frame", "post and beam",
                "heavy timber", "light frame", "platform frame", "balloon frame", "stick built",
                "prefabricated", "prefab", "modular", "panelized", "system built", "factory built"
            },
            "building_practices_efficiency": {
                # Prefabrication and modular construction
                "prefab", "prefabricated", "prefabrication", "off site construction", "offsite construction",
                "factory built", "manufactured", "modular", "modular construction", "modular building",
                "panelized", "panelized construction", "system built", "volumetric", "containerized",
                "shipping container", "container home", "tiny home", "micro housing", "accessory dwelling unit",
                "adu", "granny flat", "in law suite", "backyard cottage", "laneway house",
                
                # Construction methodology and processes
                "construction methodology", "construction method", "building method", "construction technique",
                "construction process", "building process", "assembly process", "installation process",
                "construction sequence", "construction phasing", "construction scheduling", "project scheduling",
                "critical path", "gantt chart", "project management", "construction management", "cm",
                "general contractor", "subcontractor", "trade contractor", "specialty contractor",
                
                # ROI case studies and financial performance
                "roi case study", "return on investment", "roi", "financial performance", "cost benefit",
                "cost effectiveness", "value engineering", "life cycle cost", "total cost of ownership",
                "payback period", "net present value", "npv", "internal rate of return", "irr",
                "profit margin", "gross margin", "operating margin", "ebitda", "cash flow",
                "net operating income", "noi", "cap rate", "capitalization rate", "yield",
                
                # Repeatable models and standardization
                "repeatable model", "standardized", "standardization", "prototype", "template",
                "best practice", "proven method", "established practice", "industry standard",
                "quality standard", "performance standard", "efficiency standard", "benchmark",
                "benchmarking", "comparison", "competitive analysis", "market analysis",
                
                # Process improvement and optimization
                "process improvement", "continuous improvement", "lean construction", "lean building",
                "six sigma", "quality improvement", "efficiency improvement", "productivity improvement",
                "optimization", "optimize", "streamline", "automation", "robotics", "ai", "artificial intelligence",
                "machine learning", "predictive analytics", "data analytics", "performance analytics",
                "kpi", "key performance indicator", "metrics", "measurement", "monitoring",
                
                # Construction technology and innovation
                "construction technology", "building technology", "construction innovation", "building innovation",
                "construction tech", "proptech", "contech", "construction software", "building software",
                "bim", "building information modeling", "cad", "computer aided design", "3d modeling",
                "virtual reality", "vr", "augmented reality", "ar", "mixed reality", "mr",
                "drone", "uav", "unmanned aerial vehicle", "surveying", "mapping", "scanning",
                
                # Quality control and assurance
                "quality control", "quality assurance", "qa", "qc", "testing", "inspection",
                "defect", "rework", "waste", "waste reduction", "material efficiency", "resource efficiency",
                "sustainability", "sustainable construction", "green construction", "eco friendly",
                "environmental impact", "carbon footprint", "embodied carbon", "operational carbon",
                "energy efficiency", "water efficiency", "material efficiency", "waste efficiency"
            }
        }
    
    def detect_themes(self, content: str) -> Dict[str, float]:
        """Detect theme relevance scores using comprehensive keyword matching"""
        if not content:
            return {
                "creative_opportunities": 0.0, 
                "smart_cities_productivity": 0.0, 
                "policy_code_evolution": 0.0, 
                "building_practices_efficiency": 0.0
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
            "opportunities": weighted_theme_scores.get("creative_opportunities", 0.0),
            "practices": weighted_theme_scores.get("building_practices_efficiency", 0.0),
            "systems": weighted_theme_scores.get("policy_code_evolution", 0.0),
            "vision": weighted_theme_scores.get("smart_cities_productivity", 0.0)
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
