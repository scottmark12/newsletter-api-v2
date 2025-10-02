# app/cse_backfill.py
"""
V2 Google CSE Backfill System
Uses curated search queries to find additional stories when RSS feeds don't provide enough content
"""
import json
import pathlib
from typing import List, Dict, Any
from datetime import datetime, timedelta
from .cse_client import search_construction_news, get_quota_status
from .db import SessionLocal
from sqlalchemy import text

# Load CSE queries
QUERIES_PATH = pathlib.Path(__file__).parent / "cse_queries.json"

def load_cse_queries() -> Dict[str, List[str]]:
    """Load curated CSE search queries"""
    try:
        with QUERIES_PATH.open() as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback queries if file not found
        return {
            "real_estate_opportunities": ["Real Estate Opportunities News"],
            "alternative_construction": ["3d printed home News"],
            "sustainable_materials": ["straw homes News"],
            "earth_construction": ["rammed earth homes News"],
            "engineering_construction": ["engineering construction news"]
        }

def check_content_gaps() -> Dict[str, int]:
    """Check how many articles we have per bucket in the last 24 hours"""
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(hours=24)
        
        # Count articles per topic bucket
        rows = db.execute(text("""
            SELECT 
                UNNEST(s.topics) as topic,
                COUNT(*) as count
            FROM article_scores s
            JOIN articles a ON a.id = s.article_id
            WHERE a.published_at >= :cutoff
            GROUP BY UNNEST(s.topics)
        """), {"cutoff": cutoff.isoformat()}).fetchall()
        
        topic_counts = {row[0]: row[1] for row in rows}
        
        # Map to v2 bucket names
        bucket_counts = {
            "tech_innovation": topic_counts.get("innovation", 0),
            "market_insight": topic_counts.get("market_news", 0),
            "construction_insight": topic_counts.get("insights", 0),
            "unique_development": topic_counts.get("unique_developments", 0)
        }
        
        return bucket_counts
    finally:
        db.close()

def run_cse_backfill(target_per_bucket: int = 5, max_queries_per_run: int = 10) -> Dict[str, Any]:
    """
    Run CSE backfill to supplement RSS content
    Only runs queries for buckets that are below target
    """
    # Check quota first
    quota = get_quota_status()
    if quota["remaining"] < max_queries_per_run:
        return {
            "ok": False,
            "reason": "insufficient_quota",
            "quota": quota
        }
    
    # Check content gaps
    gaps = check_content_gaps()
    queries_to_run = []
    
    # Determine which buckets need more content
    query_mapping = {
        "tech_innovation": ["alternative_construction", "innovation_queries"],
        "market_insight": ["real_estate_opportunities", "market_queries"],
        "construction_insight": ["sustainable_materials", "earth_construction", "engineering_construction"],
        "unique_development": ["policy_queries"]
    }
    
    cse_queries = load_cse_queries()
    
    for bucket, count in gaps.items():
        if count < target_per_bucket:
            # Add queries for this bucket
            for query_category in query_mapping.get(bucket, []):
                if query_category in cse_queries:
                    queries_to_run.extend(cse_queries[query_category])
    
    # Limit total queries to stay within budget
    queries_to_run = queries_to_run[:max_queries_per_run]
    
    if not queries_to_run:
        return {
            "ok": True,
            "reason": "no_gaps_found",
            "gaps": gaps,
            "quota": quota
        }
    
    # Run searches and collect results
    search_results = []
    for query in queries_to_run:
        try:
            results = search_construction_news(query, num=3)
            for result in results:
                result["search_query"] = query
                result["found_via"] = "cse_backfill"
            search_results.extend(results)
        except Exception as e:
            print(f"CSE search failed for '{query}': {e}")
            continue
    
    # TODO: Process search results into articles
    # This would involve:
    # 1. Fetching full content from URLs
    # 2. Running through scoring pipeline
    # 3. Inserting into database
    # For now, just return the raw results
    
    return {
        "ok": True,
        "queries_run": len(queries_to_run),
        "results_found": len(search_results),
        "gaps_before": gaps,
        "quota_after": get_quota_status(),
        "sample_results": search_results[:5]  # First 5 for preview
    }

def get_cse_suggestions(bucket: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get CSE search suggestions for a specific bucket
    Useful for manual review or testing
    """
    query_mapping = {
        "tech_innovation": ["alternative_construction", "innovation_queries"],
        "market_insight": ["real_estate_opportunities", "market_queries"], 
        "construction_insight": ["sustainable_materials", "earth_construction", "engineering_construction"],
        "unique_development": ["policy_queries"]
    }
    
    cse_queries = load_cse_queries()
    bucket_queries = []
    
    for query_category in query_mapping.get(bucket, []):
        if query_category in cse_queries:
            bucket_queries.extend(cse_queries[query_category])
    
    # Run a sample search
    if bucket_queries:
        sample_query = bucket_queries[0]
        try:
            results = search_construction_news(sample_query, num=limit)
            return results
        except Exception as e:
            print(f"Sample CSE search failed: {e}")
    
    return []

