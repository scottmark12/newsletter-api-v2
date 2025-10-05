"""
Enhanced Google search queries for construction and real estate intelligence
"""

# High-impact construction technology queries
INNOVATION_QUERIES = [
    # Advanced Materials & Construction Methods
    "mass timber construction 2025",
    "cross laminated timber CLT projects",
    "3D printed concrete buildings",
    "prefabricated modular construction",
    "self-healing concrete technology",
    "carbon fiber construction materials",
    "aerogel insulation buildings",
    "smart glass electrochromic windows",
    
    # Construction Technology & Automation
    "robotic construction automation",
    "drone surveying construction",
    "BIM building information modeling",
    "digital twin construction projects",
    "augmented reality construction",
    "autonomous construction vehicles",
    "AI construction management",
    "IoT sensors smart buildings",
    
    # Sustainable Building Technologies
    "net zero energy buildings",
    "passive house construction",
    "carbon negative buildings",
    "living building challenge",
    "green building certification",
    "renewable energy integration",
    "energy storage buildings",
    "microgrid smart buildings"
]

# Market opportunity and investment queries
OPPORTUNITY_QUERIES = [
    # Real Estate Development Opportunities
    "affordable housing development projects",
    "mixed-use development opportunities",
    "transit-oriented development TOD",
    "urban infill development",
    "brownfield redevelopment projects",
    "adaptive reuse construction",
    "senior housing development",
    "student housing construction",
    
    # Investment & Financing
    "real estate investment opportunities",
    "construction financing deals",
    "public private partnerships PPP",
    "opportunity zone investments",
    "tax credit housing projects",
    "construction lending trends",
    "real estate crowdfunding",
    "infrastructure investment opportunities",
    
    # Market Trends & Analysis
    "construction market outlook 2025",
    "real estate market trends",
    "housing supply shortage solutions",
    "commercial real estate recovery",
    "industrial real estate growth",
    "data center construction boom",
    "healthcare facility construction",
    "education facility development"
]

# Policy and regulatory queries
SYSTEMS_QUERIES = [
    # Building Codes & Standards
    "building code updates 2025",
    "fire safety building regulations",
    "accessibility ADA compliance",
    "energy efficiency standards",
    "seismic building codes",
    "zoning reform updates",
    "building permit processes",
    "construction safety regulations",
    
    # Policy & Incentives
    "housing policy reforms",
    "construction tax incentives",
    "green building mandates",
    "affordable housing policies",
    "infrastructure spending bills",
    "construction labor policies",
    "immigration construction workers",
    "environmental regulations construction"
]

# Future vision and smart city queries
VISION_QUERIES = [
    # Smart Cities & Technology
    "smart city infrastructure",
    "connected buildings IoT",
    "autonomous vehicle infrastructure",
    "5G network construction",
    "electric vehicle charging stations",
    "smart grid integration",
    "urban planning technology",
    "digital city platforms",
    
    # Future Living & Community
    "future of housing design",
    "community resilience planning",
    "aging in place design",
    "multigenerational housing",
    "co-living spaces design",
    "biophilic design buildings",
    "wellness building design",
    "sustainable community development"
]

# High-value project queries
PROJECT_QUERIES = [
    # Mega Infrastructure Projects
    "airport terminal construction",
    "stadium arena construction",
    "hospital medical center construction",
    "university campus expansion",
    "data center construction projects",
    "transportation hub development",
    "convention center construction",
    "sports complex development",
    
    # Innovation Showcase Projects
    "world's tallest timber building",
    "largest mass timber project",
    "first 3D printed building",
    "most sustainable building",
    "smartest building technology",
    "greenest building design",
    "most innovative construction",
    "breakthrough building project"
]

# All queries combined
ALL_QUERIES = (
    INNOVATION_QUERIES + 
    OPPORTUNITY_QUERIES + 
    SYSTEMS_QUERIES + 
    VISION_QUERIES + 
    PROJECT_QUERIES
)

# Query categories for targeted crawling
QUERY_CATEGORIES = {
    "innovation": INNOVATION_QUERIES,
    "opportunities": OPPORTUNITY_QUERIES,
    "systems": SYSTEMS_QUERIES,
    "vision": VISION_QUERIES,
    "projects": PROJECT_QUERIES
}
