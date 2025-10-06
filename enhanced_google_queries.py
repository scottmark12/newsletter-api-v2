"""
Enhanced Google Search Queries for Newsletter API v4
More comprehensive query strategy for better article coverage
"""

# Current queries (working well)
CURRENT_QUERIES = [
    "construction industry news",
    "real estate development", 
    "construction technology innovation",
    "sustainable construction practices",
    "construction market trends"
]

# Enhanced query sets for better coverage
ENHANCED_QUERIES = {
    "market_intelligence": [
        "construction market outlook 2024",
        "real estate investment trends",
        "construction spending forecast",
        "commercial real estate market",
        "construction industry growth"
    ],
    
    "technology_innovation": [
        "construction technology trends",
        "building technology innovation", 
        "construction automation",
        "smart building technology",
        "construction software solutions"
    ],
    
    "sustainability_green": [
        "green building trends",
        "sustainable construction methods",
        "LEED construction projects",
        "carbon neutral buildings",
        "renewable energy construction"
    ],
    
    "infrastructure_development": [
        "infrastructure investment",
        "public works construction",
        "transportation construction",
        "utility construction projects",
        "infrastructure funding"
    ],
    
    "regulatory_policy": [
        "construction regulations 2024",
        "building code updates",
        "construction safety standards",
        "environmental regulations construction",
        "construction labor laws"
    ],
    
    "materials_construction": [
        "construction materials innovation",
        "prefab construction trends",
        "mass timber construction",
        "concrete technology advances",
        "steel construction methods"
    ],
    
    "financial_investment": [
        "construction financing trends",
        "real estate investment opportunities",
        "construction project funding",
        "construction industry investment",
        "commercial real estate finance"
    ],
    
    "workforce_labor": [
        "construction workforce shortage",
        "construction labor trends",
        "construction training programs",
        "construction worker safety",
        "construction industry employment"
    ]
}

# Premium source targeting
PREMIUM_SOURCES = [
    "constructiondive.com",
    "enr.com", 
    "bisnow.com",
    "commercialobserver.com",
    "therealdeal.com",
    "archdaily.com",
    "dezeen.com",
    "smartcitiesdive.com",
    "builtworlds.com",
    "construction.com"
]

# Alternative source targeting for different query types
SOURCE_TARGETING = {
    "market_intelligence": "constructiondive.com OR enr.com OR commercialobserver.com",
    "technology_innovation": "constructiondive.com OR builtworlds.com OR smartcitiesdive.com",
    "sustainability_green": "constructiondive.com OR buildinggreen.com OR usgbc.org",
    "infrastructure_development": "enr.com OR constructiondive.com OR infrastructure.com",
    "regulatory_policy": "enr.com OR constructiondive.com OR aia.org",
    "materials_construction": "constructiondive.com OR enr.com OR mass-timber.com",
    "financial_investment": "commercialobserver.com OR therealdeal.com OR bisnow.com",
    "workforce_labor": "constructiondive.com OR enr.com OR construction.com"
}

# Suggested enhanced query strategy
ENHANCED_STRATEGY = {
    "daily_queries": [
        # Core industry coverage (5 queries)
        "construction industry news",
        "real estate development",
        "construction market trends",
        "construction technology innovation", 
        "sustainable construction practices",
        
        # Market intelligence (3 queries)
        "construction market outlook 2024",
        "commercial real estate trends",
        "construction spending forecast",
        
        # Technology focus (2 queries)
        "building technology innovation",
        "construction automation trends"
    ],
    
    "weekly_queries": [
        # Infrastructure focus (3 queries)
        "infrastructure investment projects",
        "public works construction",
        "transportation infrastructure",
        
        # Regulatory updates (2 queries)
        "construction regulations 2024",
        "building code updates",
        
        # Materials innovation (2 queries)
        "construction materials innovation",
        "prefab construction trends"
    ],
    
    "monthly_queries": [
        # Workforce and labor (3 queries)
        "construction workforce trends",
        "construction labor shortage",
        "construction training programs",
        
        # Financial and investment (2 queries)
        "construction financing trends",
        "real estate investment opportunities"
    ]
}

def get_enhanced_queries_for_day():
    """Get daily query set with enhanced coverage"""
    return ENHANCED_STRATEGY["daily_queries"]

def get_enhanced_queries_for_week():
    """Get weekly query set for broader coverage"""
    return ENHANCED_STRATEGY["weekly_queries"]

def get_enhanced_queries_for_month():
    """Get monthly query set for comprehensive coverage"""
    return ENHANCED_STRATEGY["monthly_queries"]

def get_source_targeting_for_query_type(query_type):
    """Get appropriate source targeting for query type"""
    return SOURCE_TARGETING.get(query_type, "constructiondive.com OR enr.com OR bisnow.com OR commercialobserver.com")

# Example usage
if __name__ == "__main__":
    print("Current Google Queries:")
    for i, query in enumerate(CURRENT_QUERIES, 1):
        print(f"{i}. {query}")
    
    print(f"\nEnhanced Daily Queries ({len(ENHANCED_STRATEGY['daily_queries'])}):")
    for i, query in enumerate(ENHANCED_STRATEGY['daily_queries'], 1):
        print(f"{i}. {query}")
    
    print(f"\nExpected daily article volume: {len(ENHANCED_STRATEGY['daily_queries']) * 5} articles")
    print(f"Premium sources: {len(PREMIUM_SOURCES)} targeted sites")
