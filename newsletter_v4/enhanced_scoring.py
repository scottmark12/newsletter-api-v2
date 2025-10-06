"""
Enhanced Scoring System for Newsletter API v4
Focus on narrative signals, transformative language, and actionable insights
Rather than rigid keyword matching
"""

import re
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ScoringResult:
    """Enhanced scoring result with narrative analysis"""
    total_score: float
    theme_scores: Dict[str, float]
    narrative_signals: Dict[str, float]
    narrative_signal: float  # Single value for API compatibility
    insight_quality: float
    actionability: float
    transformation_potential: float
    source_credibility: float  # Add missing field
    scoring_details: Dict[str, any]  # Renamed for API compatibility


class NarrativeSignalDetector:
    """Detects narrative signals that indicate high-value content"""
    
    def __init__(self):
        # Transformative Language Patterns
        self.transformative_patterns = [
            r'\bturned into\b', r'\bgrew from\b', r'\bscaled up\b', r'\btransformed\b',
            r'\bconverted\b', r'\breinvented\b', r'\brevolutionized\b', r'\bdisrupted\b',
            r'\bfrom.*to.*\b', r'\bevolved into\b', r'\bexpanded into\b', r'\bmorphed into\b'
        ]
        
        # Impact/ROI Language Patterns  
        self.impact_patterns = [
            r'\breturn on\b', r'\bover time\b', r'\bled to growth\b', r'\bboosted productivity\b',
            r'\bincreased.*by.*%', r'\bgrew.*by.*%', r'\bROI\b', r'\byield\b', r'\bprofit\b',
            r'\brevenue.*growth\b', r'\bperformance.*improved\b', r'\befficiency.*gained\b'
        ]
        
        # Prescriptive/Insight Language Patterns
        self.prescriptive_patterns = [
            r'\blessons\b', r'\binsights\b', r'\bhow.to\b', r'\bframework\b', r'\broadmap\b',
            r'\bstrategy\b', r'\bapproach\b', r'\bmethodology\b', r'\bbest practices\b',
            r'\bcase study\b', r'\banalysis\b', r'\bstudy shows\b', r'\bresearch indicates\b'
        ]
        
        # Opportunity Language Patterns
        self.opportunity_patterns = [
            r'\bemerging\b', r'\buntapped\b', r'\bpotential\b', r'\bopportunity\b',
            r'\bmarket.*gap\b', r'\bunderserved\b', r'\binnovative.*approach\b',
            r'\bcreative.*solution\b', r'\bbreakthrough\b', r'\bgame.changer\b',
            r'\bmodular\b', r'\bprefab\b', r'\btimber\b', r'\bmass.*timber\b',
            r'\baffordable.*housing\b', r'\bsmart.*city\b', r'\beco.*smart\b',
            r'\bgreen.*building\b', r'\bsustainable.*construction\b', r'\bconstruction.*growth\b',
            r'\bmarket.*growth\b', r'\binvestment.*growth\b', r'\bdevelopment.*growth\b',
            r'\bproject.*growth\b', r'\bbuilding.*growth\b', r'\bconstruction.*project\b',
            r'\bdevelopment.*project\b', r'\bbuilding.*project\b', r'\bconstruction.*opportunity\b',
            r'\bdevelopment.*opportunity\b', r'\bbuilding.*opportunity\b', r'\bconstruction.*potential\b',
            r'\bdevelopment.*potential\b', r'\bbuilding.*potential\b', r'\bconstruction.*market\b',
            r'\bdevelopment.*market\b', r'\bbuilding.*market\b', r'\bconstruction.*industry\b',
            r'\bdevelopment.*industry\b', r'\bbuilding.*industry\b', r'\breal.*estate.*market\b',
            r'\bproperty.*market\b', r'\bmarket.*analysis\b', r'\bmarket.*report\b',
            r'\bmarket.*value\b', r'\bproperty.*value\b', r'\basset.*value\b',
            r'\bmillion\b', r'\bbillion\b', r'\b\$.*[mb]\b', r'\b\$.*million\b', r'\b\$.*billion\b',
            r'\brevenue.*growth\b', r'\bprofit.*growth\b', r'\bROI\b', r'\breturn.*on.*investment\b',
            r'\bgrowth.*potential\b', r'\bgrowth.*opportunity\b', r'\bgrowth.*analysis\b',
            r'\bexpansion.*project\b', r'\bexpansion.*opportunity\b', r'\bexpansion.*plan\b',
            r'\bscaling.*up\b', r'\bscaling.*opportunity\b', r'\bscaling.*potential\b',
            r'\binnovative.*approach\b', r'\binnovative.*solution\b', r'\binnovative.*method\b',
            r'\bbreakthrough.*technology\b', r'\bbreakthrough.*method\b', r'\bbreakthrough.*approach\b',
            r'\bcutting.*edge\b', r'\bstate.*of.*the.*art\b', r'\bnext.*generation\b',
            r'\brevival\b', r'\brevitalization\b', r'\bredevelopment\b', r'\brenovation\b',
            r'\btransformation\b', r'\bconversion\b', r'\badaptive.*reuse\b'
        ]
        
        # Compile patterns for efficiency
        self.transformative_regex = re.compile('|'.join(self.transformative_patterns), re.IGNORECASE)
        self.impact_regex = re.compile('|'.join(self.impact_patterns), re.IGNORECASE)
        self.prescriptive_regex = re.compile('|'.join(self.prescriptive_patterns), re.IGNORECASE)
        self.opportunity_regex = re.compile('|'.join(self.opportunity_patterns), re.IGNORECASE)
    
    def detect_narrative_signals(self, text: str) -> Dict[str, float]:
        """Detect narrative signals in text"""
        text_lower = text.lower()
        
        signals = {
            'transformative': len(self.transformative_regex.findall(text_lower)) / max(len(text.split()), 100),
            'impact_roi': len(self.impact_regex.findall(text_lower)) / max(len(text.split()), 100),
            'prescriptive': len(self.prescriptive_regex.findall(text_lower)) / max(len(text.split()), 100),
            'opportunity': len(self.opportunity_regex.findall(text_lower)) / max(len(text.split()), 100)
        }
        
        # Normalize to 0-1 range
        for key in signals:
            signals[key] = min(signals[key] * 10, 1.0)  # Scale up and cap at 1
        
        return signals


class InsightQualityAnalyzer:
    """Analyzes the quality and actionability of insights"""
    
    def __init__(self):
        # High-value content indicators
        self.metrics_patterns = [
            r'\$\d+[bm]?\b',  # Money amounts
            r'\d+%',  # Percentages
            r'\d+\.\d+x\b',  # Multipliers (2.5x, etc.)
            r'\byear.over.year\b', r'\byoy\b',  # Growth metrics
            r'\bquarterly\b', r'\bmonthly\b'  # Time-based metrics
        ]
        
        # Methodology indicators
        self.methodology_patterns = [
            r'\bstudy\b', r'\bresearch\b', r'\banalysis\b', r'\bsurvey\b',
            r'\bdata.*shows\b', r'\bfindings\b', r'\bevidence\b', r'\bresults\b'
        ]
        
        # Actionable content indicators
        self.actionable_patterns = [
            r'\bimplement\b', r'\badopt\b', r'\bapply\b', r'\bexecute\b',
            r'\bstrategy\b', r'\bplan\b', r'\bapproach\b', r'\bframework\b',
            r'\bstep.by.step\b', r'\bprocess\b', r'\bworkflow\b'
        ]
        
        # Compile patterns
        self.metrics_regex = re.compile('|'.join(self.metrics_patterns), re.IGNORECASE)
        self.methodology_regex = re.compile('|'.join(self.methodology_patterns), re.IGNORECASE)
        self.actionable_regex = re.compile('|'.join(self.actionable_patterns), re.IGNORECASE)
    
    def analyze_insight_quality(self, text: str) -> Dict[str, float]:
        """Analyze the quality of insights in the text"""
        text_lower = text.lower()
        
        # Metrics density (financial/performance data)
        metrics_count = len(self.metrics_regex.findall(text_lower))
        metrics_density = metrics_count / max(len(text.split()), 100)
        
        # Methodology strength (research/analysis backing)
        methodology_count = len(self.methodology_regex.findall(text_lower))
        methodology_strength = methodology_count / max(len(text.split()), 100)
        
        # Actionability (how implementable the insights are)
        actionable_count = len(self.actionable_regex.findall(text_lower))
        actionability = actionable_count / max(len(text.split()), 100)
        
        return {
            'metrics_density': min(metrics_density * 20, 1.0),
            'methodology_strength': min(methodology_strength * 15, 1.0),
            'actionability': min(actionability * 15, 1.0)
        }


class EnhancedThemeDetector:
    """Enhanced theme detection based on narrative context, not just keywords"""
    
    def __init__(self):
        # Opportunity Theme: Stories of transformation, wealth creation, scaling, and market opportunities
        self.opportunity_indicators = [
            # Wealth creation patterns
            r'\bwealth.*creation\b', r'\bbuild.*wealth\b', r'\bwealth.*building\b',
            r'\bportfolio.*growth\b', r'\binvestment.*returns\b', r'\basset.*appreciation\b',
            
            # Scaling/growth patterns
            r'\bscaled.*from.*to\b', r'\bgrew.*from.*to\b', r'\bexpanded.*from.*to\b',
            r'\bstarted.*with.*now\b', r'\bbegan.*as.*became\b',
            
            # Success stories
            r'\bsuccess.*story\b', r'\bcase.*study.*success\b', r'\bhow.*achieved\b',
            r'\bturned.*around\b', r'\btransformed.*into\b',
            
            # Market opportunities
            r'\bemerging.*market\b', r'\buntapped.*potential\b', r'\bmarket.*gap\b',
            r'\bunderserved.*market\b', r'\bnew.*opportunity\b',
            
            # Construction and development opportunities
            r'\bmodular.*construction\b', r'\bprefab.*construction\b', r'\bprefabricated\b',
            r'\bmass.*timber\b', r'\btimber.*construction\b', r'\bwood.*construction\b',
            r'\baffordable.*housing\b', r'\baffordable.*homes\b', r'\bhousing.*development\b',
            r'\bsmart.*city\b', r'\beco.*smart\b', r'\bgreen.*building\b',
            r'\bsustainable.*construction\b', r'\bgreen.*construction\b',
            
            # Market and investment terms
            r'\bmarket.*growth\b', r'\bmarket.*analysis\b', r'\bmarket.*report\b',
            r'\binvestment.*opportunity\b', r'\binvestment.*potential\b', r'\binvestment.*growth\b',
            r'\bdevelopment.*project\b', r'\bdevelopment.*opportunity\b', r'\bdevelopment.*potential\b',
            r'\bconstruction.*project\b', r'\bconstruction.*opportunity\b', r'\bconstruction.*growth\b',
            r'\bbuilding.*project\b', r'\bbuilding.*development\b', r'\bbuilding.*opportunity\b',
            
            # Financial and business terms
            r'\bmillion\b', r'\bbillion\b', r'\b\$.*[mb]\b', r'\b\$.*million\b', r'\b\$.*billion\b',
            r'\brevenue.*growth\b', r'\bprofit.*growth\b', r'\bROI\b', r'\breturn.*on.*investment\b',
            r'\bmarket.*value\b', r'\bproperty.*value\b', r'\basset.*value\b',
            
            # Growth and expansion terms
            r'\bgrowth.*potential\b', r'\bgrowth.*opportunity\b', r'\bgrowth.*analysis\b',
            r'\bexpansion.*project\b', r'\bexpansion.*opportunity\b', r'\bexpansion.*plan\b',
            r'\bscaling.*up\b', r'\bscaling.*opportunity\b', r'\bscaling.*potential\b',
            
            # Innovation and breakthrough terms
            r'\binnovative.*approach\b', r'\binnovative.*solution\b', r'\binnovative.*method\b',
            r'\bbreakthrough.*technology\b', r'\bbreakthrough.*method\b', r'\bbreakthrough.*approach\b',
            r'\bcutting.*edge\b', r'\bstate.*of.*the.*art\b', r'\bnext.*generation\b',
            
            # Revival and transformation terms
            r'\brevival\b', r'\brevitalization\b', r'\bredevelopment\b', r'\brenovation\b',
            r'\btransformation\b', r'\bconversion\b', r'\badaptive.*reuse\b',
            
            # Industry-specific opportunities
            r'\bconstruction.*industry\b', r'\breal.*estate.*market\b', r'\bproperty.*market\b',
            r'\bdevelopment.*market\b', r'\bconstruction.*market\b', r'\bbuilding.*market\b'
        ]
        
        # Practices Theme: Methods, techniques, productivity improvements, and building practices
        self.practices_indicators = [
            # Methodology/process
            r'\bhow.*to.*\b', r'\bstep.*by.*step\b', r'\bprocess.*improvement\b',
            r'\bworkflow.*optimization\b', r'\befficiency.*gains\b',
            
            # Innovation in methods
            r'\binnovative.*approach\b', r'\bnew.*method\b', r'\bbreakthrough.*technique\b',
            r'\badvanced.*process\b', r'\bcutting.*edge.*method\b',
            
            # Productivity/performance
            r'\bproductivity.*improvement\b', r'\bperformance.*boost\b', r'\befficiency.*increase\b',
            r'\btime.*savings\b', r'\bcost.*reduction\b',
            
            # Best practices
            r'\bbest.*practices\b', r'\blearned.*lessons\b', r'\bproven.*methods\b',
            r'\btested.*approach\b', r'\bvalidated.*process\b',
            
            # Building and construction practices
            r'\bbuilding.*practices\b', r'\bconstruction.*practices\b', r'\bconstruction.*methods\b',
            r'\bbuilding.*methods\b', r'\bconstruction.*techniques\b', r'\bbuilding.*techniques\b',
            r'\bconstruction.*technology\b', r'\bbuilding.*technology\b', r'\bconstruction.*innovation\b',
            r'\bbuilding.*innovation\b', r'\bconstruction.*advancement\b', r'\bbuilding.*advancement\b',
            
            # Design and architecture practices
            r'\bdesign.*principles\b', r'\barchitecture.*design\b', r'\bdesign.*approach\b',
            r'\barchitectural.*practice\b', r'\bdesign.*methodology\b', r'\barchitectural.*methodology\b',
            r'\bdesign.*innovation\b', r'\barchitectural.*innovation\b', r'\bdesign.*solution\b',
            r'\barchitectural.*solution\b',
            
            # Technology and tools
            r'\btechnology.*implementation\b', r'\btech.*integration\b', r'\bdigital.*tools\b',
            r'\bsoftware.*solution\b', r'\bautomation\b', r'\bAI.*implementation\b',
            r'\bmachine.*learning\b', r'\bdata.*analytics\b', r'\bIoT.*implementation\b',
            
            # Sustainability practices
            r'\bsustainable.*practices\b', r'\bgreen.*practices\b', r'\benvironmental.*practices\b',
            r'\bsustainability.*approach\b', r'\bgreen.*building.*practices\b', r'\bLEED\b',
            r'\benergy.*efficiency\b', r'\benergy.*savings\b', r'\bcarbon.*reduction\b',
            
            # Quality and standards
            r'\bquality.*improvement\b', r'\bquality.*standards\b', r'\bquality.*control\b',
            r'\bstandards.*compliance\b', r'\bcode.*compliance\b', r'\bregulatory.*compliance\b',
            r'\bsafety.*practices\b', r'\bsafety.*standards\b', r'\bsafety.*improvement\b'
        ]
        
        # Systems & Codes Theme: Policy, regulation, frameworks that enable new building
        self.systems_indicators = [
            # Regulatory changes
            r'\bcode.*update\b', r'\bregulation.*change\b', r'\bpolicy.*reform\b',
            r'\bnew.*standards\b', r'\bupdated.*requirements\b',
            
            # Enabling frameworks
            r'\bunlock.*new\b', r'\benable.*construction\b', r'\bfacilitate.*development\b',
            r'\bstreamline.*process\b', r'\bsimplify.*approval\b',
            
            # Building innovations enabled by policy
            r'\btimber.*construction\b', r'\bmass.*timber\b', r'\bgreen.*building\b',
            r'\bsustainable.*materials\b', r'\benergy.*efficient\b',
            
            # Infrastructure/system changes
            r'\binfrastructure.*investment\b', r'\bpublic.*works\b', r'\bdevelopment.*incentives\b'
        ]
        
        # Vision Theme: Future trends, smart cities, community development, and visionary concepts
        self.vision_indicators = [
            # Future trends
            r'\bfuture.*of\b', r'\btrends.*shaping\b', r'\bwhat.*lies.*ahead\b',
            r'\bnext.*generation\b', r'\bemerging.*trends\b',
            
            # Smart cities/technology
            r'\bsmart.*city\b', r'\bdigital.*transformation\b', r'\btech.*integration\b',
            r'\bIoT.*implementation\b', r'\bdata.*driven\b',
            
            # Community/placemaking
            r'\bplacemaking\b', r'\bcommunity.*development\b', r'\blive.*work.*play\b',
            r'\bwalkable.*communities\b', r'\bsustainable.*living\b',
            
            # Innovation in design
            r'\binnovative.*design\b', r'\bfuturistic.*architecture\b', r'\bnext.*gen.*buildings\b',
            r'\brevolutionary.*concept\b', r'\bparadigm.*shift\b',
            
            # Future of cities and urban development
            r'\bfuture.*cities\b', r'\burban.*future\b', r'\bcity.*of.*tomorrow\b',
            r'\bfuture.*urban\b', r'\burban.*innovation\b', r'\bcity.*transformation\b',
            r'\burban.*development\b', r'\bcity.*planning\b', r'\burban.*planning\b',
            
            # Technology and innovation
            r'\btechnology.*trends\b', r'\binnovation.*trends\b', r'\btech.*trends\b',
            r'\bdigital.*innovation\b', r'\bAI.*trends\b', r'\bmachine.*learning\b',
            r'\bautomation.*trends\b', r'\bIoT.*trends\b', r'\bdata.*trends\b',
            
            # Sustainability and green future
            r'\bsustainable.*future\b', r'\bgreen.*future\b', r'\benvironmental.*future\b',
            r'\bclimate.*solutions\b', r'\bcarbon.*neutral\b', r'\bnet.*zero\b',
            r'\bcircular.*economy\b', r'\bgreen.*economy\b', r'\bsustainable.*development\b',
            
            # Architecture and design vision
            r'\barchitecture.*of.*the.*future\b', r'\bfuture.*architecture\b', r'\bvisionary.*design\b',
            r'\bfuturistic.*design\b', r'\bnext.*generation.*design\b', r'\binnovative.*architecture\b',
            r'\bcutting.*edge.*design\b', r'\bstate.*of.*the.*art.*design\b',
            
            # Community and lifestyle vision
            r'\bfuture.*living\b', r'\bfuture.*lifestyle\b', r'\bfuture.*communities\b',
            r'\bnew.*urbanism\b', r'\btransit.*oriented\b', r'\bmixed.*use.*development\b',
            r'\bpedestrian.*friendly\b', r'\bcyclist.*friendly\b', r'\bgreen.*infrastructure\b'
        ]
        
        # Compile all patterns
        self.opportunity_regex = re.compile('|'.join(self.opportunity_indicators), re.IGNORECASE)
        self.practices_regex = re.compile('|'.join(self.practices_indicators), re.IGNORECASE)
        self.systems_regex = re.compile('|'.join(self.systems_indicators), re.IGNORECASE)
        self.vision_regex = re.compile('|'.join(self.vision_indicators), re.IGNORECASE)
    
    def detect_themes(self, text: str) -> Dict[str, float]:
        """Detect themes based on narrative context and patterns"""
        text_lower = text.lower()
        word_count = len(text.split())
        
        # Count pattern matches for each theme
        opportunity_matches = len(self.opportunity_regex.findall(text_lower))
        practices_matches = len(self.practices_regex.findall(text_lower))
        systems_matches = len(self.systems_regex.findall(text_lower))
        vision_matches = len(self.vision_regex.findall(text_lower))
        
        # Calculate theme scores (normalized by text length)
        theme_scores = {
            'opportunities': min(opportunity_matches / max(word_count / 100, 1), 1.0),
            'practices': min(practices_matches / max(word_count / 100, 1), 1.0),
            'systems_codes': min(systems_matches / max(word_count / 100, 1), 1.0),
            'vision': min(vision_matches / max(word_count / 100, 1), 1.0)
        }
        
        return theme_scores


class EnhancedScorer:
    """Enhanced scoring system focusing on insights and opportunities"""
    
    def __init__(self):
        self.narrative_detector = NarrativeSignalDetector()
        self.insight_analyzer = InsightQualityAnalyzer()
        self.theme_detector = EnhancedThemeDetector()
        
        # Source credibility weights
        self.source_credibility = {
            'yardi matrix': 0.9,
            'cbre': 0.9,
            'jll': 0.9,
            'colliers': 0.9,
            'brookfield': 0.9,
            'goldman sachs': 0.9,
            'morgan stanley': 0.9,
            'construction dive': 0.8,
            'enr': 0.8,
            'commercial observer': 0.8,
            'google news': 0.6,
            'researchgate': 0.7,
            'nature': 0.8,
            'wiley': 0.7
        }
    
    def score_article(self, title: str, content: str, source: str, url: str) -> ScoringResult:
        """Score an article using enhanced narrative-based approach"""
        full_text = f"{title} {content}".lower()
        source_lower = source.lower()
        
        # 1. Detect narrative signals
        narrative_signals = self.narrative_detector.detect_narrative_signals(full_text)
        
        # 2. Analyze insight quality
        insight_quality = self.insight_analyzer.analyze_insight_quality(full_text)
        
        # 3. Detect themes using enhanced approach
        theme_scores = self.theme_detector.detect_themes(full_text)
        
        # 4. Calculate source credibility
        source_credibility = self._get_source_credibility(source_lower)
        
        # 5. Calculate transformation potential (stories of growth/success)
        transformation_potential = self._calculate_transformation_potential(full_text)
        
        # 6. Calculate actionability (how useful is this for practitioners)
        actionability = self._calculate_actionability(full_text)
        
        # 7. Calculate total score with enhanced weighting
        total_score = self._calculate_total_score(
            narrative_signals,
            insight_quality,
            theme_scores,
            source_credibility,
            transformation_potential,
            actionability
        )
        
        # 8. Compile details
        details = {
            'narrative_signals': narrative_signals,
            'insight_quality': insight_quality,
            'transformation_potential': transformation_potential,
            'actionability': actionability,
            'source_credibility': source_credibility,
            'word_count': len(full_text.split()),
            'scoring_method': 'enhanced_narrative_based'
        }
        
        return ScoringResult(
            total_score=total_score,
            theme_scores=theme_scores,
            narrative_signals=narrative_signals,
            narrative_signal=sum(narrative_signals.values()) / len(narrative_signals),
            insight_quality=sum(insight_quality.values()) / len(insight_quality),
            actionability=actionability,
            transformation_potential=transformation_potential,
            source_credibility=source_credibility,
            scoring_details=details
        )
    
    def _get_source_credibility(self, source: str) -> float:
        """Get source credibility score"""
        for source_key, credibility in self.source_credibility.items():
            if source_key in source:
                return credibility
        return 0.5  # Default for unknown sources
    
    def _calculate_transformation_potential(self, text: str) -> float:
        """Calculate potential for transformation/success stories"""
        transformation_patterns = [
            r'\bturned.*into\b', r'\bgrew.*from.*to\b', r'\bscaled.*up\b',
            r'\btransformed.*into\b', r'\bconverted.*into\b', r'\breinvented\b',
            r'\bsuccess.*story\b', r'\bcase.*study\b', r'\bwealth.*creation\b',
            r'\bportfolio.*growth\b', r'\binvestment.*success\b'
        ]
        
        pattern_count = 0
        for pattern in transformation_patterns:
            pattern_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(pattern_count / max(len(text.split()) / 200, 1), 1.0)
    
    def _calculate_actionability(self, text: str) -> float:
        """Calculate how actionable/practical the content is"""
        actionable_patterns = [
            r'\bhow.*to\b', r'\bstep.*by.*step\b', r'\bframework\b', r'\bstrategy\b',
            r'\bapproach\b', r'\bmethodology\b', r'\bbest.*practices\b', r'\blessons.*learned\b',
            r'\bimplementation\b', r'\badoption\b', r'\bexecution\b', r'\bprocess\b'
        ]
        
        pattern_count = 0
        for pattern in actionable_patterns:
            pattern_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        return min(pattern_count / max(len(text.split()) / 150, 1), 1.0)
    
    def _calculate_total_score(self, narrative_signals, insight_quality, theme_scores, 
                              source_credibility, transformation_potential, actionability) -> float:
        """Calculate total score with enhanced weighting"""
        
        # Weight the components for high-value content
        weights = {
            'narrative_signals': 0.25,      # 25% - how the story is told
            'insight_quality': 0.20,        # 20% - quality of insights
            'theme_scores': 0.20,           # 20% - thematic relevance
            'transformation_potential': 0.15, # 15% - success/growth stories
            'actionability': 0.15,          # 15% - practical value
            'source_credibility': 0.05      # 5% - source trust
        }
        
        # Calculate weighted scores
        narrative_score = sum(narrative_signals.values()) / len(narrative_signals)
        insight_score = sum(insight_quality.values()) / len(insight_quality)
        theme_score = max(theme_scores.values()) if theme_scores.values() else 0
        
        total_score = (
            narrative_score * weights['narrative_signals'] +
            insight_score * weights['insight_quality'] +
            theme_score * weights['theme_scores'] +
            transformation_potential * weights['transformation_potential'] +
            actionability * weights['actionability'] +
            source_credibility * weights['source_credibility']
        )
        
        return min(total_score, 1.0)


# Main scoring function
def score_article_enhanced(title: str, content: str, source: str, url: str) -> ScoringResult:
    """Enhanced article scoring function"""
    scorer = EnhancedScorer()
    return scorer.score_article(title, content, source, url)
