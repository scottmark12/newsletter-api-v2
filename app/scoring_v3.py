# app/scoring_v3.py
# Complete v3 Scoring System - Theme-Based Architecture

from typing import List, Dict, Any, Tuple
import re
import uuid
from datetime import datetime, timezone
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal
from .llm import call_llm
from .schema_v3 import ArticleV3, ArticleScoreV3, ArticleInsightV3, ContentSource

# -------- V3 THEME DEFINITIONS --------
THEMES_V3 = {
    "opportunities": {
        "description": "Stories of transformation, small → big investments, creative deals, entrepreneurial case studies, wealth-building examples",
        "keywords": {
            "transformation": ["grew from", "scaled up", "turned into", "transformed", "expanded from", "started with", "evolved into"],
            "scaling": ["scaled up", "expansion", "growth story", "rapid growth", "accelerated development", "portfolio growth"],
            "creative_deals": ["creative financing", "innovative deal", "structured deal", "unique partnership", "joint venture", "recapitalization"],
            "wealth_building": ["wealth creation", "investor returns", "equity growth", "asset appreciation", "value add", "return on investment", "roi"],
            "case_studies": ["case study", "success story", "project spotlight", "lessons learned", "before and after", "implementation example"]
        },
        "multipliers": {
            "case_study": 1.6,
            "roi_data": 1.5,
            "scaling_story": 1.4,
            "creative_financing": 1.3
        }
    },
    "practices": {
        "description": "Building methods, design principles, process improvements, productivity studies, and lessons learned",
        "keywords": {
            "building_methods": ["modular construction", "prefab", "offsite construction", "mass timber", "cross laminated timber", "clt", "design-build", "integrated project delivery", "ipd", "lean construction", "agile construction"],
            "design_principles": ["biophilic design", "human-centered design", "resilient design", "sustainable design", "universal design", "inclusive design", "performance-based design"],
            "process_improvements": ["workflow optimization", "process efficiency", "productivity gains", "streamlined operations", "digital transformation", "automation in construction"],
            "lessons_learned": ["lessons learned", "best practices", "post-mortem analysis", "project review", "risk mitigation strategies", "challenges overcome"]
        },
        "multipliers": {
            "methodology": 1.5,
            "process_improvement": 1.4,
            "best_practices": 1.3,
            "lessons_learned": 1.2
        }
    },
    "systems_codes": {
        "description": "Policy updates, building code changes, zoning reforms, incentives that unlock new development",
        "keywords": {
            "policy_updates": ["policy change", "regulatory update", "government initiative", "new legislation", "incentive program", "tax credit", "opportunity zone"],
            "building_codes": ["building code", "zoning reform", "land use", "entitlements", "permitting process", "density bonus", "affordable housing mandates"],
            "infrastructure_investment": ["infrastructure bill", "public works", "transit-oriented development", "tod", "smart infrastructure", "grid modernization"]
        },
        "multipliers": {
            "policy_change": 1.4,
            "code_update": 1.3,
            "incentive_program": 1.2,
            "regulatory_unlock": 1.5
        }
    },
    "vision": {
        "description": "Smart cities, future-of-living models, community impact, human-centered and biophilic design",
        "keywords": {
            "smart_cities": ["smart city", "urban innovation", "future cities", "connected communities", "digital infrastructure"],
            "future_living": ["future of living", "next-gen housing", "co-living", "micro-apartments", "adaptive reuse", "vertical communities"],
            "community_impact": ["community development", "social impact", "placemaking", "equitable development", "affordable housing", "public realm"],
            "human_centered_design": ["human-centered", "biophilic design", "wellness architecture", "health and well-being", "user experience", "comfort", "accessibility"]
        },
        "multipliers": {
            "smart_city": 1.3,
            "community_impact": 1.2,
            "future_living": 1.4,
            "human_centered": 1.3
        }
    }
}

# -------- NARRATIVE SIGNAL DETECTION --------
NARRATIVE_SIGNALS_V3 = {
    "transformative_language": {
        "keywords": ["grew from", "scaled up", "turned into", "transformed", "evolved into", "pivoted to", "shifted to"],
        "multiplier": 1.4,
        "description": "Language indicating transformation or evolution"
    },
    "impact_language": {
        "keywords": ["return on investment", "roi", "boosted productivity", "led to growth", "increased efficiency", "reduced costs by", "improved margins", "performance data", "metrics show"],
        "multiplier": 1.5,
        "description": "Language indicating measurable impact"
    },
    "prescriptive_language": {
        "keywords": ["insights", "lessons learned", "framework", "how-to guide", "roadmap", "strategy for", "methodology", "best practices", "actionable advice"],
        "multiplier": 1.3,
        "description": "Language indicating actionable guidance"
    }
}

# -------- INSIGHT QUALITY WEIGHTING --------
INSIGHT_QUALITY_V3 = {
    "high_value": {
        "keywords": ["roi", "return on investment", "performance data", "metrics", "methodology", "process", "framework", "case study", "lessons learned", "implementation guide", "how-to"],
        "weight": 2.0,
        "description": "High-value actionable content"
    },
    "medium_value": {
        "keywords": ["visionary", "future of", "concept", "potential", "outlook", "trends", "forecast"],
        "weight": 1.2,
        "description": "Medium-value conceptual content"
    },
    "low_value": {
        "keywords": ["hype", "press release", "announcement", "launch", "grand opening", "award", "celebration"],
        "weight": 0.7,
        "description": "Low-value promotional content"
    }
}

# -------- ENHANCED EXCLUSION KEYWORDS --------
EXCLUDE_KEYWORDS_V3 = {
    "furniture": ["furniture", "chair", "table", "desk", "sofa", "couch", "lamp", "lighting fixture"],
    "interior_design": ["interior design", "decor", "decoration", "aesthetic", "artistic", "conceptual"],
    "art_gallery": ["installation", "exhibition", "museum", "gallery", "art", "sculpture", "painting"],
    "fashion": ["fashion", "clothing", "textile", "fabric", "wallpaper", "paint color", "color scheme"],
    "academic": ["experimental architecture", "avant-garde", "theoretical", "philosophical", "student project", "academic", "research paper", "thesis", "dissertation"]
}

# -------- INSTITUTIONAL SOURCE INDICATORS --------
INSTITUTIONAL_SOURCES_V3 = {
    "tier_1": ["jll", "cbre", "cushman", "colliers", "marcus & millichap", "newmark", "avison young"],
    "tier_2": ["bisnow", "commercial observer", "real estate weekly", "costar", "rejournals", "globe st"],
    "tier_3": ["construction dive", "smart cities dive", "engineering news record", "architectural record"],
    "research": ["mckinsey", "deloitte", "pwc", "kpmg", "boston consulting", "bain", "oliver wyman"]
}

def detect_themes_v3(text_blob: str) -> Dict[str, float]:
    """Detect themes in content using enhanced signal matching"""
    if not text_blob:
        return {}
    
    t = text_blob.lower()
    
    # Check for exclusions first
    if _should_exclude_content_v3(t):
        return {}
    
    theme_scores = {}
    
    for theme_name, theme_data in THEMES_V3.items():
        theme_score = 0
        keyword_groups = theme_data["keywords"]
        
        # Score based on keyword group matches
        for group_name, keywords in keyword_groups.items():
            matches = sum(1 for kw in keywords if kw in t)
            if matches > 0:
                theme_score += matches * 10  # Base score per match
        
        # Apply theme-specific multipliers
        if theme_score > 0:
            theme_scores[theme_name] = theme_score
    
    return theme_scores

def detect_narrative_signals_v3(text_blob: str) -> Dict[str, float]:
    """Detect narrative signals and calculate bonuses"""
    if not text_blob:
        return {}
    
    t = text_blob.lower()
    signals_detected = {}
    
    for signal_type, signal_data in NARRATIVE_SIGNALS_V3.items():
        keywords = signal_data["keywords"]
        matches = sum(1 for kw in keywords if kw in t)
        if matches > 0:
            signals_detected[signal_type] = {
                "matches": matches,
                "multiplier": signal_data["multiplier"],
                "description": signal_data["description"]
            }
    
    return signals_detected

def calculate_insight_quality_v3(text_blob: str) -> Dict[str, Any]:
    """Calculate pragmatic insight weighting and quality metrics"""
    if not text_blob:
        return {"weight": 1.0, "quality_level": "unknown", "metrics": {}}
    
    t = text_blob.lower()
    
    quality_metrics = {
        "roi_data_present": False,
        "performance_metrics_present": False,
        "methodology_present": False,
        "case_study_present": False
    }
    
    # Check for specific quality indicators
    roi_indicators = ["roi", "return on investment", "profit margin", "revenue", "cost savings", "efficiency gains"]
    performance_indicators = ["performance data", "metrics", "kpi", "benchmark", "measurement", "analytics"]
    methodology_indicators = ["methodology", "process", "framework", "approach", "system", "workflow"]
    case_study_indicators = ["case study", "success story", "example", "implementation", "before and after"]
    
    quality_metrics["roi_data_present"] = any(indicator in t for indicator in roi_indicators)
    quality_metrics["performance_metrics_present"] = any(indicator in t for indicator in performance_indicators)
    quality_metrics["methodology_present"] = any(indicator in t for indicator in methodology_indicators)
    quality_metrics["case_study_present"] = any(indicator in t for indicator in case_study_indicators)
    
    # Calculate quality weight
    high_value_matches = sum(1 for kw in INSIGHT_QUALITY_V3["high_value"]["keywords"] if kw in t)
    medium_value_matches = sum(1 for kw in INSIGHT_QUALITY_V3["medium_value"]["keywords"] if kw in t)
    low_value_matches = sum(1 for kw in INSIGHT_QUALITY_V3["low_value"]["keywords"] if kw in t)
    
    weight = 1.0
    if high_value_matches > 0:
        weight *= INSIGHT_QUALITY_V3["high_value"]["weight"]
    if medium_value_matches > 0:
        weight *= INSIGHT_QUALITY_V3["medium_value"]["weight"]
    if low_value_matches > 0:
        weight *= INSIGHT_QUALITY_V3["low_value"]["weight"]
    
    # Determine quality level
    if high_value_matches > 0 or quality_metrics["roi_data_present"]:
        quality_level = "high"
    elif medium_value_matches > 0 or quality_metrics["methodology_present"]:
        quality_level = "medium"
    elif low_value_matches > 0:
        quality_level = "low"
    else:
        quality_level = "neutral"
    
    return {
        "weight": max(0.1, weight),
        "quality_level": quality_level,
        "metrics": quality_metrics
    }

def _should_exclude_content_v3(text: str) -> bool:
    """Check if content should be excluded using word boundaries"""
    for category, keywords in EXCLUDE_KEYWORDS_V3.items():
        for keyword in keywords:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                return True
    return False

def _get_institutional_source_multiplier_v3(source: str) -> float:
    """Get institutional source multiplier"""
    if not source:
        return 1.0
    
    source_lower = source.lower()
    
    for tier, sources in INSTITUTIONAL_SOURCES_V3.items():
        if any(s in source_lower for s in sources):
            if tier == "tier_1":
                return 1.5
            elif tier == "tier_2":
                return 1.3
            elif tier == "tier_3":
                return 1.2
            elif tier == "research":
                return 1.4
    
    return 1.0

def extract_insights_v3(text_blob: str, title: str) -> List[Dict[str, Any]]:
    """Extract actionable insights from article content"""
    insights = []
    
    if not text_blob or not title:
        return insights
    
    t = text_blob.lower()
    
    # Look for ROI data
    roi_patterns = [
        r"roi of (\d+(?:\.\d+)?%)",
        r"return on investment.*?(\d+(?:\.\d+)?%)",
        r"(\d+(?:\.\d+)?%)\s*(?:increase|improvement|gain|boost)",
        r"cost.*?reduced by (\d+(?:\.\d+)?%)",
        r"efficiency.*?improved by (\d+(?:\.\d+)?%)"
    ]
    
    for pattern in roi_patterns:
        matches = re.findall(pattern, t)
        for match in matches:
            insights.append({
                "insight_type": "roi_data",
                "insight_title": "ROI/Performance Data",
                "insight_content": f"Found ROI/performance metric: {match}",
                "insight_value": match,
                "is_actionable": True,
                "confidence_score": 85.0
            })
    
    # Look for methodologies
    methodology_patterns = [
        r"methodology.*?([^.]{20,100})",
        r"process.*?([^.]{20,100})",
        r"framework.*?([^.]{20,100})",
        r"approach.*?([^.]{20,100})"
    ]
    
    for pattern in methodology_patterns:
        matches = re.findall(pattern, t)
        for match in matches:
            if len(match.strip()) > 20:  # Ensure substantial content
                insights.append({
                    "insight_type": "methodology",
                    "insight_title": "Implementation Methodology",
                    "insight_content": match.strip(),
                    "insight_value": "Methodology identified",
                    "is_actionable": True,
                    "confidence_score": 75.0
                })
    
    # Look for case studies
    if "case study" in t or "success story" in t or "before and after" in t:
        insights.append({
            "insight_type": "case_study",
            "insight_title": "Case Study Analysis",
            "insight_content": "Article contains case study or success story elements",
            "insight_value": "Case study identified",
            "is_actionable": True,
            "confidence_score": 80.0
        })
    
    return insights

def score_article_v3(article_data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    """Score an article using the v3 theme-based system"""
    
    # Extract text content
    title = article_data.get('title', '')
    content = article_data.get('content', '') or article_data.get('summary_raw', '')
    source = article_data.get('source', '')
    url = article_data.get('url', '')
    
    text_blob = f"{title} {content}"
    
    # Detect themes
    theme_scores = detect_themes_v3(text_blob)
    
    # Detect narrative signals
    narrative_signals = detect_narrative_signals_v3(text_blob)
    
    # Calculate insight quality
    insight_quality = calculate_insight_quality_v3(text_blob)
    
    # Extract insights
    insights = extract_insights_v3(text_blob, title)
    
    # Get institutional source multiplier
    institutional_multiplier = _get_institutional_source_multiplier_v3(source)
    
    # Calculate theme scores
    opportunities_score = theme_scores.get('opportunities', 0)
    practices_score = theme_scores.get('practices', 0)
    systems_codes_score = theme_scores.get('systems_codes', 0)
    vision_score = theme_scores.get('vision', 0)
    
    # Apply narrative signal multipliers
    transformative_multiplier = 1.0
    impact_multiplier = 1.0
    prescriptive_multiplier = 1.0
    
    if 'transformative_language' in narrative_signals:
        transformative_multiplier = narrative_signals['transformative_language']['multiplier']
    if 'impact_language' in narrative_signals:
        impact_multiplier = narrative_signals['impact_language']['multiplier']
    if 'prescriptive_language' in narrative_signals:
        prescriptive_multiplier = narrative_signals['prescriptive_language']['multiplier']
    
    # Calculate multipliers based on content quality
    case_study_multiplier = 1.6 if insight_quality['metrics']['case_study_present'] else 1.0
    scalable_process_multiplier = 1.5 if insight_quality['metrics']['methodology_present'] else 1.0
    policy_shift_multiplier = 1.4 if 'systems_codes' in theme_scores else 1.0
    thought_leadership_multiplier = 1.3 if institutional_multiplier > 1.0 else 1.0
    
    # Apply insight quality weight
    insight_weight = insight_quality['weight']
    
    # Calculate final scores
    final_opportunities = opportunities_score * transformative_multiplier * insight_weight
    final_practices = practices_score * prescriptive_multiplier * insight_weight
    final_systems_codes = systems_codes_score * policy_shift_multiplier * insight_weight
    final_vision = vision_score * impact_multiplier * insight_weight
    
    # Calculate composite score
    composite_score = (final_opportunities + final_practices + final_systems_codes + final_vision) * institutional_multiplier
    
    # Determine primary theme
    primary_theme = max(theme_scores.keys(), key=lambda k: theme_scores[k]) if theme_scores else None
    
    # Determine content depth
    if insight_quality['metrics']['roi_data_present'] and insight_quality['metrics']['methodology_present']:
        content_depth = "deep"
    elif insight_quality['metrics']['methodology_present'] or insight_quality['metrics']['case_study_present']:
        content_depth = "medium"
    else:
        content_depth = "shallow"
    
    # Calculate actionability score
    actionability_score = 0
    if insight_quality['metrics']['roi_data_present']:
        actionability_score += 30
    if insight_quality['metrics']['methodology_present']:
        actionability_score += 25
    if insight_quality['metrics']['case_study_present']:
        actionability_score += 25
    if insight_quality['metrics']['performance_metrics_present']:
        actionability_score += 20
    
    # Calculate insight quality score
    insight_quality_score = min(100, composite_score / 10)
    
    # Create score record
    score_data = {
        "opportunities_score": final_opportunities,
        "practices_score": final_practices,
        "systems_codes_score": final_systems_codes,
        "vision_score": final_vision,
        "transformative_language_score": narrative_signals.get('transformative_language', {}).get('matches', 0),
        "impact_language_score": narrative_signals.get('impact_language', {}).get('matches', 0),
        "prescriptive_language_score": narrative_signals.get('prescriptive_language', {}).get('matches', 0),
        "roi_data_present": insight_quality['metrics']['roi_data_present'],
        "performance_metrics_present": insight_quality['metrics']['performance_metrics_present'],
        "methodology_present": insight_quality['metrics']['methodology_present'],
        "case_study_present": insight_quality['metrics']['case_study_present'],
        "case_study_multiplier": case_study_multiplier,
        "scalable_process_multiplier": scalable_process_multiplier,
        "policy_shift_multiplier": policy_shift_multiplier,
        "thought_leadership_multiplier": thought_leadership_multiplier,
        "composite_score": composite_score,
        "institutional_source_bonus": institutional_multiplier,
        "dollar_amount_multiplier": 1.0  # Placeholder for future enhancement
    }
    
    # Create article data
    article_data_v3 = {
        "primary_theme": primary_theme,
        "secondary_themes": list(theme_scores.keys()),
        "content_depth": content_depth,
        "actionability_score": actionability_score,
        "insight_quality": insight_quality_score,
        "media_type": article_data.get('media_type', 'article'),
        "project_stage": article_data.get('project_stage', 'unknown'),
        "needs_fact_check": insight_quality['quality_level'] == 'low'
    }
    
    return score_data, article_data_v3, insights

def run_scoring_v3(limit: int = 100) -> Dict[str, Any]:
    """Run the v3 scoring system on new articles"""
    db = SessionLocal()
    try:
        # Get unscored articles
        unscored_articles = db.execute(text("""
            SELECT a.id, a.url, a.title, a.content, a.summary_raw, a.source, a.media_type, a.project_stage
            FROM articles a
            LEFT JOIN article_scores_v3 s ON s.article_id = a.id
            WHERE s.id IS NULL
              AND a.status != 'discarded'
              AND a.content IS NOT NULL
              AND LENGTH(a.content) > 100
            ORDER BY a.fetched_at DESC
            LIMIT :limit
        """), {"limit": limit}).fetchall()
        
        scored_count = 0
        excluded_count = 0
        insights_extracted = 0
        
        for row in unscored_articles:
            article_dict = dict(row._mapping)
            
            try:
                # Score the article
                score_data, article_data_v3, insights = score_article_v3(article_dict)
                
                # Skip if no themes detected (likely excluded content)
                if not article_data_v3['primary_theme']:
                    excluded_count += 1
                    continue
                
                # Update article with v3 data
                db.execute(text("""
                    UPDATE articles_v3 
                    SET primary_theme = :primary_theme,
                        secondary_themes = :secondary_themes,
                        content_depth = :content_depth,
                        actionability_score = :actionability_score,
                        insight_quality = :insight_quality,
                        media_type = :media_type,
                        project_stage = :project_stage,
                        needs_fact_check = :needs_fact_check
                    WHERE id = :article_id
                """), {
                    "article_id": article_dict['id'],
                    **article_data_v3
                })
                
                # Insert score record
                db.execute(text("""
                    INSERT INTO article_scores_v3 (
                        article_id, opportunities_score, practices_score, systems_codes_score, vision_score,
                        transformative_language_score, impact_language_score, prescriptive_language_score,
                        roi_data_present, performance_metrics_present, methodology_present, case_study_present,
                        case_study_multiplier, scalable_process_multiplier, policy_shift_multiplier, thought_leadership_multiplier,
                        composite_score, institutional_source_bonus, dollar_amount_multiplier
                    ) VALUES (
                        :article_id, :opportunities_score, :practices_score, :systems_codes_score, :vision_score,
                        :transformative_language_score, :impact_language_score, :prescriptive_language_score,
                        :roi_data_present, :performance_metrics_present, :methodology_present, :case_study_present,
                        :case_study_multiplier, :scalable_process_multiplier, :policy_shift_multiplier, :thought_leadership_multiplier,
                        :composite_score, :institutional_source_bonus, :dollar_amount_multiplier
                    )
                """), {
                    "article_id": article_dict['id'],
                    **score_data
                })
                
                # Insert insights
                for insight in insights:
                    db.execute(text("""
                        INSERT INTO article_insights_v3 (
                            article_id, insight_type, insight_title, insight_content, insight_value,
                            is_actionable, confidence_score
                        ) VALUES (
                            :article_id, :insight_type, :insight_title, :insight_content, :insight_value,
                            :is_actionable, :confidence_score
                        )
                    """), {
                        "article_id": article_dict['id'],
                        **insight
                    })
                    insights_extracted += 1
                
                scored_count += 1
                
            except Exception as e:
                print(f"Error scoring article {article_dict['id']}: {str(e)}")
                continue
        
        db.commit()
        
        return {
            "status": "success",
            "scored_articles": scored_count,
            "excluded_articles": excluded_count,
            "insights_extracted": insights_extracted,
            "message": f"Successfully scored {scored_count} articles, excluded {excluded_count}, extracted {insights_extracted} insights"
        }
        
    except Exception as e:
        db.rollback()
        return {
            "status": "error",
            "message": f"Error running v3 scoring: {str(e)}"
        }
    finally:
        db.close()
