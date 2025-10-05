"""
Narrative-Focused Google Queries
Targeting specific language patterns that indicate high-opportunity content
Based on V3 thematic scoring logic
"""

# TRANSFORMATION & SCALING QUERIES - Look for growth stories
TRANSFORMATION_QUERIES = [
    # Growth and scaling stories
    "startup grew from construction company",
    "small company scaled up construction",
    "construction firm turned into billion dollar",
    "started with transformed into construction",
    "construction company evolved into tech",
    "local builder became national developer",
    "family business expanded into construction empire",
    
    # ROI and financial success stories
    "construction project ROI return on investment",
    "construction investment boosted productivity",
    "construction project led to growth",
    "construction development profitability increased",
    "construction project revenue growth",
    "construction investment market share",
    
    # Record-breaking and unprecedented projects
    "record-breaking construction project",
    "unprecedented construction development",
    "largest construction project ever",
    "biggest construction development",
    "first-of-its-kind construction",
    "groundbreaking construction project"
]

# MATERIAL SCIENCE BREAKTHROUGHS - Revolutionary technologies
BREAKTHROUGH_QUERIES = [
    # Scientific breakthroughs
    "construction research breakthrough",
    "construction scientific breakthrough",
    "construction laboratory results",
    "construction engineering feat",
    "construction research shows",
    "construction studies demonstrate",
    
    # Revolutionary materials
    "revolutionary construction material",
    "pioneering construction technology",
    "groundbreaking construction material",
    "cutting-edge construction technology",
    "next-generation construction material",
    "state-of-the-art construction technology",
    
    # Future technologies
    "future of construction technology",
    "next wave construction technology",
    "emerging construction technology",
    "promising construction development",
    "construction technology could revolutionize",
    "construction breakthrough potential"
]

# MARKET DISRUPTION QUERIES - Industry transformations
DISRUPTION_QUERIES = [
    # Market disruption
    "construction industry disrupting",
    "construction market transforming",
    "construction industry revolutionizing",
    "construction changing the game",
    "construction industry shaking up",
    "construction redefining industry",
    
    # New opportunities
    "construction opportunity growth market",
    "construction emerging sector",
    "construction untapped market",
    "construction new frontier",
    "construction growth opportunity",
    "construction market potential",
    
    # Regulatory unlocks
    "construction policy change opportunity",
    "construction new regulations opportunity",
    "construction incentive program",
    "construction government support",
    "construction legislative update opportunity",
    "construction zoning reform opportunity"
]

# HIGH-VALUE PROJECT QUERIES - Billion dollar developments
HIGH_VALUE_QUERIES = [
    # Billion dollar projects
    "billion dollar construction project",
    "billion dollar infrastructure development",
    "billion dollar real estate project",
    "billion dollar construction investment",
    "billion dollar construction development",
    "billion dollar construction program",
    
    # Mega projects
    "mega construction project",
    "mega infrastructure development",
    "mega construction investment",
    "mega construction development",
    "mega construction program",
    "mega construction initiative",
    
    # Large-scale developments
    "large-scale construction project",
    "massive construction development",
    "significant construction investment",
    "major construction development",
    "substantial construction project",
    "extensive construction development"
]

# AUTOMATION & INNOVATION QUERIES - Technology breakthroughs
INNOVATION_QUERIES = [
    # Construction automation
    "automated construction breakthrough",
    "robotic construction revolution",
    "AI construction management breakthrough",
    "construction automation breakthrough",
    "construction robotics breakthrough",
    "construction AI breakthrough",
    
    # 3D printing and additive manufacturing
    "3D printing construction breakthrough",
    "additive manufacturing construction breakthrough",
    "3D printed building breakthrough",
    "construction 3D printing revolution",
    "construction additive manufacturing revolution",
    "3D printing construction revolution",
    
    # Smart construction
    "smart construction breakthrough",
    "digital construction breakthrough",
    "BIM construction breakthrough",
    "construction digital twin breakthrough",
    "construction IoT breakthrough",
    "construction sensors breakthrough"
]

# SUSTAINABLE TECHNOLOGY QUERIES - Green breakthroughs
SUSTAINABLE_QUERIES = [
    # Net zero and carbon negative
    "net zero construction breakthrough",
    "carbon negative construction breakthrough",
    "zero emission construction breakthrough",
    "carbon neutral construction breakthrough",
    "green construction breakthrough",
    "sustainable construction breakthrough",
    
    # Renewable energy construction
    "renewable energy construction breakthrough",
    "solar construction breakthrough",
    "wind energy construction breakthrough",
    "energy storage construction breakthrough",
    "smart grid construction breakthrough",
    "microgrid construction breakthrough",
    
    # Mass timber and sustainable materials
    "mass timber construction breakthrough",
    "cross laminated timber breakthrough",
    "engineered wood breakthrough",
    "sustainable materials breakthrough",
    "recycled materials breakthrough",
    "bio-based materials breakthrough"
]

# All narrative-focused queries combined
ALL_NARRATIVE_QUERIES = (
    TRANSFORMATION_QUERIES + 
    BREAKTHROUGH_QUERIES + 
    DISRUPTION_QUERIES + 
    HIGH_VALUE_QUERIES + 
    INNOVATION_QUERIES + 
    SUSTAINABLE_QUERIES
)

# Categories for targeted crawling
NARRATIVE_CATEGORIES = {
    "transformation": TRANSFORMATION_QUERIES,
    "breakthroughs": BREAKTHROUGH_QUERIES,
    "disruption": DISRUPTION_QUERIES,
    "high_value": HIGH_VALUE_QUERIES,
    "innovation": INNOVATION_QUERIES,
    "sustainable": SUSTAINABLE_QUERIES
}
