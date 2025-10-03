from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal

# -------- Category keyword sets --------
# Developer-focused content: practical, actionable building processes and technologies
# We tag each article with one or more of these:
# "innovation", "market_news", "insights", "unique_developments"

# Keywords that indicate non-developer content (furniture, experimental architecture, etc.)
EXCLUDE_KEYWORDS = {
    "furniture","chair","table","desk","sofa","couch","lamp","lighting fixture",
    "interior design","decor","decoration","aesthetic","artistic","conceptual",
    "installation","exhibition","museum","gallery","art","sculpture","painting",
    "fashion","clothing","textile","fabric","wallpaper","paint color","color scheme",
    "experimental architecture","avant-garde","theoretical","philosophical",
    "student project","academic","research paper","thesis","dissertation"
}

KWS = {
    "innovation": {
        # AI and advanced technology
        "ai campus","ai factory","hyperscale","data center","robotic","robotics",
        "3d printed","3d printing","bim","digital twin","prefab","modular",
        "offsite","automation","computer vision","generative ai","llm","r&d",
        "breakthrough","pilot program","prototype","patent","innovation","innovative",
        "smart building","smart city","iot","sensor","blockchain","vr","ar",
        "machine learning","artificial intelligence","green tech","sustainability",
        "renewable energy","solar","wind","battery","electric vehicle","ev",
        "nanotechnology","biotech","fintech","proptech","contech",
        
        # Advanced construction technologies
        "mass timber","cross laminated timber","clt","glulam","engineered wood",
        "precast concrete","tilt-up","insulated concrete forms","icf",
        "steel frame","structural steel","cold-formed steel","cf steel",
        "building envelope","air barrier","vapor barrier","thermal bridge",
        "heat pump","geothermal","ground source","air source",
        "building automation","hvac controls","energy management","building controls",
        "construction technology","contech","construction tech","building tech",
        
        # Cutting-edge building processes and materials
        "self-healing concrete","carbon fiber","fiber reinforced polymer","frp",
        "aerogel insulation","phase change materials","pcm","smart glass",
        "electrochromic","photovoltaic glass","pv glass","transparent solar",
        "living walls","green roofs","vertical farming","hydroponic",
        "biomimetic","biomimicry","nature-inspired","bio-based materials",
        "recycled materials","circular construction","cradle to cradle",
        "net zero","carbon negative","passive house","passivhaus",
        "zero energy","energy positive","plus energy",
        
        # Advanced construction methods
        "drone surveying","lidar scanning","laser scanning","3d scanning",
        "augmented reality","mixed reality","hololens","construction vr",
        "autonomous vehicles","self-driving","robotic construction","exoskeleton",
        "wearable tech","smart hardhat","construction iot","connected job site",
        "predictive maintenance","condition monitoring","structural health monitoring",
        "digital fabrication","cnc construction","robotic welding","automated bricklaying",
        
        # Emerging building systems
        "microgrid","smart grid","energy storage","battery storage","thermal storage",
        "district energy","thermal networks","heat recovery","waste heat",
        "greywater recycling","rainwater harvesting","water treatment",
        "air purification","indoor air quality","iaq","ventilation systems",
        "acoustic design","sound masking","noise reduction","vibration control",
        
        # Future building concepts
        "floating buildings","underwater construction","space construction",
        "modular construction","volumetric construction","kit of parts",
        "design for manufacturing","dfma","offsite manufacturing",
        "factory-built","prefabricated","panelized construction",
        "structural insulated panels","sip","insulated concrete forms","icf",
        "autoclaved aerated concrete","aac","lightweight concrete",
        "high-performance concrete","ultra-high performance concrete","uhpc"
    },
    "market_news": {
        "refinance","bond","cmbs","term sheet","bridge loan","construction loan",
        "cap rate","dscr","occupancy","vacancy","absorption","pipeline","starts",
        "transaction","deal","acquisition","raises","funding","yoy","qoq",
        "rent growth","foreclosure","construction financing","development loan",
        "mezzanine loan","construction starts","building permits","housing starts",
        "commercial real estate","cre","multifamily","office","retail","industrial",
        "logistics","warehouse","distribution center","data center","hospitality"
    },
    "insights": {
        # Building science and construction insights
        "mass timber","electrification","heat pump","embodied carbon",
        "operational carbon","leed","passive house","energy code","stretch code",
        "upzoning","by-right","inclusionary","office-to-residential","conversion",
        "student housing","life science","industrial","logistics","macro","headwinds",
        # Developer-relevant insights
        "building performance","energy efficiency","water efficiency","indoor air quality",
        "building materials","construction methods","building systems","mep systems",
        "structural engineering","civil engineering","building codes","zoning",
        "development process","entitlement","permitting","construction timeline",
        "cost analysis","construction costs","material costs","labor costs",
        "project delivery","design-build","construction management","general contractor",
        # Institutional research and insights
        "market outlook","market forecast","market analysis","market trends","market intelligence",
        "quarterly report","annual report","market survey","industry survey","market research",
        "investment outlook","capital markets","debt markets","equity markets","fundraising",
        "investment thesis","market dynamics","supply and demand","absorption rates",
        "cap rates","yield","risk assessment","due diligence","underwriting",
        "portfolio strategy","asset allocation","investment strategy","risk management",
        "market commentary","expert opinion","thought leadership","perspective","viewpoint",
        "white paper","case study","best practices","lessons learned","market study",
        "economic impact","economic analysis","demographic trends","population growth",
        "urban planning","city planning","infrastructure investment","public policy",
        "regulatory environment","government policy","tax policy","incentive programs"
    },
    "unique_developments": {
        # Real development projects and construction milestones
        "groundbreaking","opens","topped out","topping out","approved",
        "wins approval","entitled","rezoned","permits issued","milestone",
        "first-of-its-kind","world's first","largest","record-breaking",
        "breaks ground","construction begins","construction started","new development",
        "development project","mixed-use","tower","high-rise","skyscraper",
        "campus","complex","facility","center","hub","district","quarter",
        "master plan","phase","expansion","renovation","redevelopment",
        "affordable housing","luxury","boutique","flagship","headquarters",
        # Developer-relevant project types
        "office building","residential tower","apartment building","condominium",
        "hotel","hospitality","retail center","shopping center","mall",
        "industrial park","warehouse","distribution center","manufacturing facility",
        "data center","research facility","laboratory","medical facility","hospital",
        "school","university","college","transportation hub","transit oriented",
        "infrastructure project","bridge","tunnel","highway","transit","rail"
    },
}

def _tag_categories(text_blob: str) -> list[str]:
    t = (text_blob or "").lower()
    
    # First check if content should be excluded (furniture, experimental architecture, etc.)
    if any(exclude_word in t for exclude_word in EXCLUDE_KEYWORDS):
        return []  # Return empty tags for excluded content
    
    tags = []
    for cat, words in KWS.items():
        if any(w in t for w in words):
            tags.append(cat)
    
    # de-duplicate while preserving order
    seen = set()
    out = []
    for x in tags:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

# If you later wire LLM scoring, import here and merge into composite_score
# from .llm import score_article_with_llm

def fetch_new_articles(limit: int = 50) -> List[Dict[str, Any]]:
    db = SessionLocal()
    try:
        rows = db.execute(
            text("""
                SELECT id, title, summary_raw, content, published_at, fetched_at
                FROM articles
                WHERE status = 'new'
                ORDER BY fetched_at DESC NULLS LAST
                LIMIT :lim
            """),
            {"lim": limit}
        ).mappings().all()
        return [dict(r) for r in rows]
    finally:
        db.close()

def save_scores(article_id: str, scores: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        import json
        from .db import is_postgres
        
        # Convert lists based on database type
        topics = scores.get("topics", [])
        geography = scores.get("geography", [])
        
        if is_postgres:
            # PostgreSQL expects actual arrays, not JSON strings
            topics_data = topics
            geography_data = geography
        else:
            # SQLite expects JSON strings
            topics_data = json.dumps(topics)
            geography_data = json.dumps(geography)
        
        db.execute(text("""
            INSERT INTO article_scores (
                article_id, rel_building_practices, rel_market, rel_design_business,
                importance_multiplier, freshness_bonus, composite_score, topics,
                geography, macro_flag, summary2, why1, project_stage, needs_fact_check, media_type
            )
            VALUES (
                :article_id, :rbp, :rm, :rdb, :imp, :fresh, :comp, :topics,
                :geo, :macro, :summary2, :why1, :project_stage, :needs_fact_check, :media_type
            )
            ON CONFLICT (article_id) DO UPDATE SET
                rel_building_practices = EXCLUDED.rel_building_practices,
                rel_market = EXCLUDED.rel_market,
                rel_design_business = EXCLUDED.rel_design_business,
                importance_multiplier = EXCLUDED.importance_multiplier,
                freshness_bonus = EXCLUDED.freshness_bonus,
                composite_score = EXCLUDED.composite_score,
                topics = EXCLUDED.topics,
                geography = EXCLUDED.geography,
                macro_flag = EXCLUDED.macro_flag,
                summary2 = EXCLUDED.summary2,
                why1 = EXCLUDED.why1,
                project_stage = EXCLUDED.project_stage,
                needs_fact_check = EXCLUDED.needs_fact_check,
                media_type = EXCLUDED.media_type
        """), {
            "article_id": article_id,
            "rbp": scores.get("rel_building_practices", 0),
            "rm": scores.get("rel_market", 0),
            "rdb": scores.get("rel_design_business", 0),
            "imp": scores.get("importance_multiplier", 1.0),
            "fresh": scores.get("freshness_bonus", 0.0),
            "comp": scores.get("composite_score", 0.0),
            "topics": topics_data,
            "geo": geography_data,
            "macro": scores.get("macro_flag", False),
            "summary2": scores.get("summary2", None),
            "why1": scores.get("why1", None),
            "project_stage": scores.get("project_stage", None),
            "needs_fact_check": scores.get("needs_fact_check", False),
            "media_type": scores.get("media_type", "article"),
        })
        db.execute(text("UPDATE articles SET status='scored' WHERE id=:id"), {"id": article_id})
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    finally:
        db.close()

def _detect_project_stage(text_blob: str) -> str:
    """Detect project development stage from article text"""
    t = text_blob.lower()
    
    # Stage detection patterns
    if any(phrase in t for phrase in ["approved", "wins approval", "gets approval", "city approves", "planning approval"]):
        return "approved"
    elif any(phrase in t for phrase in ["breaks ground", "groundbreaking", "construction begins", "starts construction"]):
        return "breaks_ground" 
    elif any(phrase in t for phrase in ["tops out", "topping out", "topped out", "reaches full height"]):
        return "tops_out"
    elif any(phrase in t for phrase in ["opens", "opening", "grand opening", "now open", "officially opened"]):
        return "opens"
    else:
        return None

def _detect_media_type(url: str, title: str, content: str) -> str:
    """Detect if content is podcast, video, or article"""
    # Check URL first for definitive identification
    if "youtube.com" in url or "youtu.be" in url:
        return "video"
    if "vimeo.com" in url:
        return "video"
    
    text = f"{url} {title} {content}".lower()
    
    if any(word in text for word in ["podcast", "episode", "listen", "audio", "spotify", "apple podcasts"]):
        return "podcast"
    elif any(word in text for word in ["video", "watch", "youtube", "vimeo", "webinar"]):
        return "video"
    else:
        return "article"

def _assess_fact_check_need(text_blob: str, composite_score: float) -> bool:
    """Determine if article needs fact checking based on content patterns"""
    t = text_blob.lower()
    
    # High-stakes claims that need verification
    risky_patterns = [
        "breaking:", "exclusive:", "first reported", "sources say", "unnamed source",
        "leaked", "confidential", "insider", "rumor", "alleged", "reportedly",
        "unconfirmed", "developing story"
    ]
    
    # Financial/numerical claims
    financial_patterns = [
        "$", "billion", "million", "percent", "%", "rate", "price", "cost"
    ]
    
    has_risky = any(pattern in t for pattern in risky_patterns)
    has_financial = any(pattern in t for pattern in financial_patterns)
    
    # Need fact check if: risky language OR high-stakes financial claims with low confidence
    return has_risky or (has_financial and composite_score < 3.0)

def developer_focused_score(row: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scoring system optimized for aspiring developer looking for:
    - Tech-enabled repeatable projects
    - Construction innovation opportunities  
    - Market/policy changes creating openings
    - Pragmatic focus on human-centered spaces
    """
    text_blob = " ".join([
        row.get("title") or "",
        row.get("summary_raw") or "",
        row.get("content") or ""
    ])
    t = text_blob.lower()
    
    composite_score = 0.0
    
    # 🚀 TIER 1: CUTTING-EDGE BUILDING TECH (15-25 points) - Highest Priority for Developers
    breakthrough_tech = {
        # Next-gen materials and construction methods
        "self-healing concrete": 25, "carbon fiber": 22, "aerogel": 20, "smart materials": 20,
        "phase change materials": 18, "smart glass": 18, "electrochromic": 18,
        "photovoltaic glass": 20, "transparent solar": 20, "biomimetic materials": 18,
        "bio-based materials": 16, "graphene": 22, "nanotechnology": 20,
        
        # Advanced construction technologies
        "3d printing": 22, "additive manufacturing": 22, "robotic construction": 20,
        "automated bricklaying": 18, "robotic welding": 16, "cnc construction": 16,
        "digital fabrication": 18, "exoskeleton": 15, "autonomous vehicles": 16,
        "predictive maintenance": 14, "structural health monitoring": 16,
        
        # Smart building systems
        "digital twin": 18, "ai-powered": 16, "machine learning": 14, "artificial intelligence": 14,
        "computer vision": 15, "generative ai": 16, "parametric design": 12,
        "smart building": 14, "iot sensors": 12, "connected job site": 12,
        "wearable tech": 10, "smart hardhat": 10, "construction iot": 12,
        
        # Advanced surveying and visualization
        "drone surveying": 15, "lidar scanning": 14, "laser scanning": 12, "3d scanning": 12,
        "augmented reality": 14, "mixed reality": 14, "construction vr": 12, "hololens": 12,
        "virtual reality": 10, "bim": 12, "building information modeling": 12,
        
        # Modular and prefab innovations
        "mass timber": 16, "clt": 16, "cross laminated timber": 16, "glulam": 14,
        "modular construction": 14, "prefab": 12, "offsite construction": 14,
        "volumetric construction": 12, "kit of parts": 10, "factory-built": 12,
        
        # Sustainable building technologies
        "net zero": 16, "carbon negative": 18, "passive house": 14, "passivhaus": 14,
        "energy positive": 16, "embodied carbon": 14, "operational carbon": 12,
        "circular construction": 14, "cradle to cradle": 12, "living materials": 16
    }
    
    # 🏗️ TIER 2: UNIQUE DEVELOPMENTS & REAL PROJECTS (12-30 points) - High Priority for Examples
    project_opportunities = {
        # Innovation showcase projects (20-30 points)
        "first-of-its-kind": 30, "world's first": 28, "pioneering": 25, "breakthrough project": 25,
        "innovative design": 22, "cutting-edge project": 20, "next-generation": 20,
        "revolutionary building": 25, "groundbreaking project": 22, "trailblazing": 20,
        
        # Mega infrastructure projects (18-25 points)
        "stadium": 25, "arena": 22, "convention center": 20, "airport terminal": 22,
        "hospital": 20, "medical center": 18, "university campus": 18, "data center": 22,
        "research facility": 20, "laboratory": 18, "innovation hub": 22, "tech campus": 20,
        
        # Construction milestones and stages (15-20 points)
        "groundbreaking": 20, "breaks ground": 20, "construction begins": 18,
        "topped out": 16, "topping out": 16, "opens": 14, "grand opening": 16,
        "completed": 18, "finished": 16, "delivered": 16, "handed over": 15,
        "fully operational": 14, "tenant ready": 12, "leasing": 10,
        
        # Project leadership and partnerships (15-20 points)
        "construction manager": 20, "general contractor": 18, "cm/gc": 18,
        "joint venture": 18, "jv": 18, "partnership": 15, "consortium": 16,
        "design-build": 16, "epc": 15, "turnkey": 14,
        
        # High-value development types (12-18 points)
        "affordable housing": 16, "mixed-use": 15, "transit-oriented": 18,
        "multifamily": 12, "student housing": 14, "senior housing": 12,
        "industrial park": 14, "logistics hub": 16, "warehouse": 10,
        "life science": 18, "medical office": 16, "research park": 18,
        
        # Innovation and pilot projects (16-22 points)
        "pilot project": 18, "demonstration": 16, "prototype": 16,
        "proof of concept": 15, "test bed": 14, "showcase": 16,
        "case study": 14, "project profile": 12, "feature story": 10,
        
        # Approvals and policy wins (12-18 points)
        "approved": 16, "planning approval": 16, "permits issued": 14,
        "rezoning": 18, "zoning change": 18, "upzoning": 16,
        "entitled": 15, "development rights": 14, "air rights": 12
    }
    
    # 💰 TIER 3: ACTIONABLE MARKET INTELLIGENCE (8-15 points) - High Value for Developers
    financing_deals = {
        # Major financing deals and opportunities (12-15 points)
        "construction loan": 15, "development financing": 14, "bridge loan": 12,
        "mezzanine loan": 13, "term sheet": 12, "financing package": 14,
        "construction financing": 14, "development loan": 14, "acquisition loan": 12,
        
        # Tax incentives and government programs (10-14 points)
        "tax credit": 12, "lihtc": 12, "opportunity zone": 14, "new markets": 12,
        "subsidies": 14, "grants": 11, "incentives": 10, "tax abatement": 11,
        "government funding": 12, "public-private partnership": 14, "ppp": 14,
        
        # Partnership and investment structures (10-13 points)
        "joint venture": 12, "jv": 12, "partnership": 11, "investment partnership": 12,
        "acquisition": 10, "merger": 11, "consortium": 12, "alliance": 10,
        "development rights": 12, "air rights": 10, "land assembly": 11,
        "land acquisition": 10, "site assembly": 11, "portfolio acquisition": 12
    }
    
    # 📊 TIER 4: MARKET INSIGHTS & TRENDS (8-12 points) - Actionable Intelligence
    market_signals = {
        # Construction and development metrics (10-12 points)
        "housing starts": 12, "building permits": 12, "construction spending": 11,
        "construction starts": 12, "development pipeline": 12, "project pipeline": 11,
        "construction activity": 10, "building activity": 10, "development activity": 11,
        
        # Market performance indicators (8-11 points)
        "cap rate": 9, "vacancy": 8, "absorption": 9, "occupancy": 8,
        "rent growth": 10, "rental rates": 9, "market rent": 9, "asking rent": 8,
        "transaction volume": 11, "deal volume": 11, "sales volume": 10,
        
        # Cost and supply factors (9-12 points)
        "material costs": 11, "construction costs": 12, "labor costs": 10,
        "labor shortage": 10, "skilled labor": 9, "supply chain": 10,
        "material shortage": 11, "cost escalation": 10, "price increases": 9,
        
        # Economic and policy signals (7-10 points)
        "interest rates": 8, "fed rate": 8, "inflation": 7, "economic outlook": 9,
        "market forecast": 10, "market outlook": 10, "trend analysis": 9,
        "policy changes": 9, "regulatory changes": 8, "zoning changes": 10,
        
        # Investment and capital markets (9-12 points)
        "investment activity": 11, "capital markets": 10, "debt markets": 9,
        "equity markets": 9, "fundraising": 11, "capital raising": 11,
        "investor sentiment": 9, "market sentiment": 8, "risk assessment": 8
    }
    
    # 🌱 TIER 5: SUSTAINABLE BUILDING SOLUTIONS (8-15 points) - Future-Focused
    sustainability = {
        # Advanced sustainability technologies (12-15 points)
        "net zero": 15, "carbon negative": 15, "zero energy": 14, "plus energy": 14,
        "energy positive": 14, "carbon neutral": 12, "embodied carbon": 12,
        "operational carbon": 10, "life cycle assessment": 12, "lca": 12,
        
        # High-performance building systems (10-13 points)
        "passive house": 12, "passivhaus": 12, "energy efficiency": 10,
        "building performance": 11, "energy management": 10, "smart grid": 11,
        "microgrid": 12, "energy storage": 11, "battery storage": 10,
        
        # Renewable and clean energy (8-12 points)
        "solar": 10, "photovoltaic": 11, "pv": 11, "wind": 9,
        "geothermal": 11, "heat pump": 9, "electrification": 10,
        "renewable energy": 10, "clean energy": 9, "green energy": 9,
        
        # Sustainable materials and practices (9-12 points)
        "circular economy": 12, "circular construction": 12, "cradle to cradle": 11,
        "waste reduction": 9, "recycled materials": 10, "reclaimed materials": 9,
        "sustainable materials": 11, "green materials": 10, "eco-friendly": 9,
        
        # Water and resource management (8-11 points)
        "water efficiency": 10, "water conservation": 9, "rainwater harvesting": 10,
        "greywater": 9, "stormwater": 9, "water treatment": 8,
        "resource efficiency": 9, "resource conservation": 8
    }
    
    # Calculate scores for each category
    for keyword, points in breakthrough_tech.items():
        if keyword in t:
            composite_score += points * (1 + t.count(keyword) * 0.5)  # Bonus for multiple mentions
    
    for keyword, points in project_opportunities.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in financing_deals.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in market_signals.items():
        if keyword in t:
            composite_score += points
    
    for keyword, points in sustainability.items():
        if keyword in t:
            composite_score += points
    
    # ❌ PENALTIES: Filter out irrelevant content
    penalties = {
        "starbucks": -20, "retail chain": -15, "restaurant": -10,
        "layoffs": -10, "earnings": -8, "stock price": -8,
        "celebrity": -15, "entertainment": -10, "sports": -8,
        "fashion": -10, "luxury goods": -8, "automotive": -5,
        "tech stocks": -8, "cryptocurrency": -10, "social media": -8
    }
    
    for keyword, penalty in penalties.items():
        if keyword in t:
            composite_score += penalty
    
    # 🎯 ENHANCED BONUSES: Developer-focused multipliers
    
    # 🏢 INSTITUTIONAL SOURCE BONUS (Enhanced for developer credibility)
    institutional_sources = [
        "blackstone", "cbre", "jll", "cushman", "savills", "colliers",
        "kkr", "apollo", "carlyle", "brookfield", "tpg", "ares",
        "morgan stanley", "goldman sachs", "jpmorgan", "bank of america",
        "wells fargo", "citi", "freddie mac", "fannie mae", "hud",
        "urban land institute", "uli", "nareit", "ncrc", "u.s. green building council",
        "usgbc", "architecture 2030", "carbon leadership forum", "passive house institute",
        "international living future institute", "ilfi", "building green",
        "construction dive", "engineering news record", "enr", "architect magazine",
        "architectural record", "archdaily", "dezeen", "bd+c", "building design construction",
        "turner construction", "skanska", "fluor", "bechtel", "aecom", "jacobs",
        "hunt construction", "pcl construction", "whiting-turner", "suffolk construction"
    ]
    
    if any(source in t for source in institutional_sources):
        composite_score *= 1.7  # 70% bonus for institutional research (increased from 50%)
    
    # 📊 ACTIONABLE RESEARCH & INSIGHTS BONUS (Enhanced)
    research_indicators = [
        "market outlook", "quarterly report", "annual report", "white paper",
        "market analysis", "investment outlook", "market forecast", "case study",
        "market survey", "industry survey", "thought leadership", "expert opinion",
        "market commentary", "perspective", "viewpoint", "market study",
        "economic impact", "economic analysis", "demographic trends", "population growth",
        "urban planning", "city planning", "infrastructure investment", "public policy",
        "regulatory environment", "government policy", "tax policy", "incentive programs",
        "best practices", "lessons learned", "industry trends", "market dynamics",
        "cost analysis", "roi analysis", "feasibility study", "market feasibility"
    ]
    
    if any(indicator in t for indicator in research_indicators):
        composite_score *= 1.5  # 50% bonus for research content (increased from 30%)
    
    # 🚀 CUTTING-EDGE INNOVATION BONUS (Enhanced for tech-forward developers)
    innovation_indicators = [
        "breakthrough", "pilot program", "prototype", "patent", "first-of-its-kind",
        "world's first", "cutting-edge", "next-generation", "revolutionary",
        "groundbreaking", "innovative", "advanced technology", "emerging technology",
        "new technology", "latest technology", "state-of-the-art", "bleeding edge",
        "ai-powered", "machine learning", "artificial intelligence", "generative ai",
        "robotics", "automation", "computer vision", "digital twin", "bim",
        "smart materials", "self-healing", "carbon fiber", "aerogel", "graphene",
        "phase change materials", "electrochromic", "photovoltaic glass", "smart glass",
        "biomimetic", "bio-based", "circular construction", "net zero energy",
        "passive house", "energy positive", "carbon negative", "embodied carbon",
        "drone surveying", "lidar scanning", "augmented reality", "mixed reality",
        "construction vr", "exoskeleton", "wearable tech", "smart hardhat",
        "construction iot", "predictive maintenance", "digital fabrication",
        "cnc construction", "robotic welding", "automated bricklaying", "3d printing",
        "additive manufacturing", "offsite construction", "modular construction"
    ]
    
    if any(indicator in t for indicator in innovation_indicators):
        composite_score *= 1.6  # 60% bonus for innovation content (increased from 40%)
    
    # 🏗️ REAL-WORLD PROJECT BONUS (New - for completed/implemented innovations)
    project_indicators = [
        "completed", "finished", "delivered", "handed over", "opened to public",
        "fully operational", "tenant ready", "leasing", "occupied", "inhabited",
        "construction completed", "final phase", "last phase", "completion",
        "ribbon cutting", "grand opening", "official opening", "public opening",
        "case study", "project profile", "feature story", "project spotlight",
        "development update", "construction update", "progress report",
        "success story", "implementation", "deployed", "installed", "operational"
    ]
    
    if any(indicator in t for indicator in project_indicators):
        composite_score *= 1.4  # 40% bonus for real, completed projects
    
    # 🏢 GENERAL DEVELOPMENT PENALTY (reduce innovation scores for generic development news)
    general_dev_terms = [
        "construction loan", "financing", "refinance", "acquisition", "development project",
        "groundbreaking", "topped out", "opens", "approved", "city council", "planning board",
        "luxury rental", "apartment complex", "mixed-use", "retail center", "office building"
    ]
    
    # If it's tagged as innovation but contains mostly general development terms, reduce the score
    if "innovation" in topics and any(term in t for term in general_dev_terms):
        # Only apply penalty if there are no strong innovation indicators
        strong_innovation = any(indicator in t for indicator in innovation_indicators[:20])  # First 20 are strongest
        if not strong_innovation:
            composite_score *= 0.7  # 30% penalty for generic development news tagged as innovation
    
    # 💰 ENHANCED PROJECT VALUE MULTIPLIER (Increased for major developments)
    import re
    dollar_matches = re.findall(r'\$([0-9]+(?:\.[0-9]+)?)\s*(billion|million|b|m)\b', t)
    if dollar_matches:
        max_value = 0
        for amount, unit in dollar_matches:
            value = float(amount)
            if unit.lower() in ['billion', 'b']:
                value *= 1000  # Convert to millions
            max_value = max(max_value, value)
        
        # Enhanced major project multipliers based on size
        if max_value >= 1000:  # $1B+
            composite_score *= 3.5  # Increased from 2.5
        elif max_value >= 500:  # $500M+
            composite_score *= 2.8  # Increased from 2.0
        elif max_value >= 100:  # $100M+
            composite_score *= 2.2  # Increased from 1.7
        elif max_value >= 50:   # $50M+
            composite_score *= 1.8  # Increased from 1.4
        elif max_value >= 25:   # $25M+ (new threshold)
            composite_score *= 1.5
    
    # 🏗️ PRACTICAL IMPLEMENTATION BONUSES (Enhanced for developers)
    
    # Scalable/repeatable solutions (Higher value for developers)
    if any(word in t for word in ["scalable", "repeatable", "replicable", "standardized", "systematic", "modular", "prefab"]):
        composite_score *= 1.5  # Increased from 1.3
    
    # Cost-effectiveness and ROI (Critical for developers)
    if any(word in t for word in ["cost-effective", "efficient", "practical", "feasible", "viable", "roi", "return on investment", "payback period", "cost savings"]):
        composite_score *= 1.4  # Increased from 1.15
    
    # Human-centered and community impact (Market demand)
    if any(word in t for word in ["community", "placemaking", "human-centered", "social impact", "wellness", "health", "safety", "accessibility", "affordable"]):
        composite_score *= 1.35  # Increased from 1.2
    
    # Geographic opportunity bonus (Emerging markets)
    if any(word in t for word in ["emerging market", "underserved", "opportunity zone", "revitalization", "urban renewal", "gentrification", "infill"]):
        composite_score *= 1.4  # Increased from 1.25
    
    # Collaboration and partnerships (Shows market opportunities)
    if any(word in t for word in ["joint venture", "jv", "partnership", "consortium", "alliance", "collaboration", "team up", "strategic partnership"]):
        composite_score *= 1.3  # Increased from 1.2
    
    # 🎯 NEW DEVELOPER-FOCUSED BONUSES
    
    # Technical depth and specifications (Implementation guidance)
    if any(word in t for word in ["specifications", "technical details", "performance data", "test results", "certification", "compliance", "standards", "codes"]):
        composite_score *= 1.25
    
    # Market timing and trends (Investment timing)
    if any(word in t for word in ["trending", "growing demand", "increasing", "rising", "emerging", "new market", "opportunity", "timing", "market timing"]):
        composite_score *= 1.2
    
    # Implementation guidance (How-to content)
    if any(word in t for word in ["how to", "implementation", "installation", "process", "methodology", "approach", "strategy", "roadmap", "step-by-step"]):
        composite_score *= 1.15
    
    # Risk mitigation (Important for developers)
    if any(word in t for word in ["risk management", "risk mitigation", "insurance", "liability", "warranty", "guarantee", "performance bond"]):
        composite_score *= 1.1
    
    # Ensure minimum score for highly relevant content
    if composite_score < 0:
        composite_score = 0
    
    # Length bonus for substantial content
    word_count = len((row.get("content") or "").split())
    if word_count > 300:
        composite_score += min(word_count / 500.0, 3.0)  # Up to +3 points

    topics = _tag_categories(text_blob)
    
    # If no topics (excluded content like furniture/experimental architecture), return None
    if not topics:
        return None  # This will signal to skip scoring this article
    
    project_stage = _detect_project_stage(text_blob)
    media_type = _detect_media_type(row.get("url", ""), row.get("title", ""), row.get("content", ""))
    needs_fact_check = _assess_fact_check_need(text_blob, composite_score)
    
    # Enhanced scoring for YouTube videos
    if media_type == "video" and ("youtube.com" in row.get("url", "") or "youtu.be" in row.get("url", "")):
        try:
            from .youtube_handler import process_youtube_video
            youtube_data = process_youtube_video(
                row.get("url", ""), 
                row.get("title", ""), 
                row.get("content", ""),
                row.get("published_at")
            )
            if youtube_data:
                composite_score = max(composite_score, youtube_data.get("composite_score", 0))
                needs_fact_check = youtube_data.get("needs_fact_check", needs_fact_check)
        except ImportError:
            pass
    
    return {
        "rel_building_practices": int(composite_score * 0.1),  # Convert to legacy format
        "rel_market": int(composite_score * 0.1),
        "rel_design_business": int(composite_score * 0.1),
        "importance_multiplier": 1.0,
        "freshness_bonus": 0.0,
        "composite_score": float(composite_score),
        "topics": topics,
        "geography": [],
        "macro_flag": any(word in t for word in ["macro", "federal", "policy", "regulation"]),
        "summary2": None,
        "why1": None,
        "project_stage": project_stage,
        "needs_fact_check": needs_fact_check,
        "media_type": media_type,
    }

# Use the new developer-focused scoring
def naive_score(row: Dict[str, Any]) -> Dict[str, Any]:
    return developer_focused_score(row)

def run(limit: int = 50) -> Dict[str, Any]:
    arts = fetch_new_articles(limit=limit)
    scored = 0
    excluded = 0
    
    for a in arts:
        # scores = score_article_with_llm(...)
        scores = naive_score(a)
        
        # If scores is None, the article was excluded (furniture/experimental architecture)
        if scores is None:
            print(f"Excluding non-developer content: {a.get('title', 'No title')[:60]}...")
            # Mark article as discarded
            db = SessionLocal()
            try:
                db.execute(text("UPDATE articles SET status='discarded' WHERE id=:id"), {"id": a["id"]})
                db.commit()
            finally:
                db.close()
            excluded += 1
        else:
            save_scores(a["id"], scores)
            scored += 1
    
    print(f"Scored {scored} developer-relevant articles, excluded {excluded} non-developer articles")
    return {"ok": True, "scored": scored, "excluded": excluded}
