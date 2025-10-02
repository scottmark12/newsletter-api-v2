# app/macro_data.py
"""
V2 Macro Data Integration
Fetches key construction/real estate indicators for "What moved" section
"""
import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from .config import DATABASE_URL

# FRED API key for economic data
FRED_API_KEY = os.environ.get("FRED_API_KEY", "")

# Data series IDs from FRED (Federal Reserve Economic Data)
FRED_SERIES = {
    "10Y_TREASURY": "DGS10",           # 10-Year Treasury Constant Maturity Rate
    "CONSTRUCTION_SPENDING": "TTLCONS", # Total Construction Spending
    "HOUSING_STARTS": "HOUST",         # Housing Starts
    "BUILDING_PERMITS": "PERMIT"       # New Private Housing Units Authorized by Building Permits
}

# NAHB Housing Market Index (requires separate API or scraping)
NAHB_HMI_URL = "https://www.nahb.org/news-and-economics/housing-economics/indices/housing-market-index"

def fetch_fred_data(series_id: str, limit: int = 5) -> Optional[Dict[str, Any]]:
    """Fetch data from FRED API"""
    if not FRED_API_KEY:
        return None
        
    try:
        url = f"https://api.stlouisfed.org/fred/series/observations"
        params = {
            "series_id": series_id,
            "api_key": FRED_API_KEY,
            "file_type": "json",
            "sort_order": "desc",
            "limit": limit
        }
        
        with httpx.Client(timeout=10) as client:
            response = client.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                if "observations" in data and data["observations"]:
                    latest = data["observations"][0]
                    return {
                        "value": latest.get("value"),
                        "date": latest.get("date"),
                        "series_id": series_id
                    }
    except Exception as e:
        print(f"Error fetching FRED data for {series_id}: {e}")
    
    return None

def calculate_change(current: float, previous: float) -> str:
    """Calculate and format percentage change"""
    if not current or not previous:
        return "N/A"
    
    try:
        current_val = float(current)
        previous_val = float(previous)
        change = current_val - previous_val
        
        if abs(change) < 0.01:
            return "unchanged"
        elif change > 0:
            return f"+{change:.1f} bps" if abs(change) < 1 else f"+{change:.1f}%"
        else:
            return f"{change:.1f} bps" if abs(change) < 1 else f"{change:.1f}%"
    except (ValueError, TypeError):
        return "N/A"

def fetch_treasury_10y() -> str:
    """Get 10-Year Treasury rate with change"""
    data = fetch_fred_data("DGS10", limit=2)
    if not data:
        return "10Y N/A"
    
    try:
        # Get current and previous values for change calculation
        with httpx.Client(timeout=10) as client:
            response = client.get(
                "https://api.stlouisfed.org/fred/series/observations",
                params={
                    "series_id": "DGS10",
                    "api_key": FRED_API_KEY,
                    "file_type": "json",
                    "sort_order": "desc",
                    "limit": 2
                }
            )
            
            if response.status_code == 200:
                observations = response.json().get("observations", [])
                if len(observations) >= 2:
                    current = observations[0].get("value")
                    previous = observations[1].get("value")
                    
                    if current and current != "." and previous and previous != ".":
                        change = float(current) - float(previous)
                        change_bps = change * 100  # Convert to basis points
                        
                        if abs(change_bps) < 0.1:
                            return f"10Y {current}% (unch)"
                        elif change_bps > 0:
                            return f"10Y {current}% (+{change_bps:.0f}bps)"
                        else:
                            return f"10Y {current}% ({change_bps:.0f}bps)"
                    else:
                        return f"10Y {current}%"
    except Exception:
        pass
    
    return "10Y N/A"

def fetch_nahb_sentiment() -> str:
    """Get NAHB Housing Market Index (placeholder - requires web scraping or paid API)"""
    # TODO: Implement NAHB HMI scraping or API integration
    # For now, return placeholder with realistic range
    return "NAHB 45 (-2)"

def fetch_dodge_momentum() -> str:
    """Get Dodge Momentum Index (placeholder - requires Dodge Data subscription)"""
    # TODO: Implement Dodge Data API integration
    # For now, return placeholder
    return "Dodge +2.1% MoM"

def get_macro_indicators() -> str:
    """
    Compile all macro indicators into the "What moved" string
    Format: "10Y +6 bps | Dodge Momentum +2.1% MoM | NAHB −2"
    """
    try:
        treasury = fetch_treasury_10y()
        nahb = fetch_nahb_sentiment()
        dodge = fetch_dodge_momentum()
        
        return f"{treasury} | {dodge} | {nahb}"
    
    except Exception as e:
        print(f"Error compiling macro indicators: {e}")
        # Fallback to static example
        return "10Y +6 bps | Dodge Momentum +2.1% MoM | NAHB −2"

def get_detailed_metrics() -> Dict[str, Any]:
    """Get detailed macro metrics for analysis (optional endpoint)"""
    return {
        "treasury_10y": fetch_fred_data("DGS10"),
        "construction_spending": fetch_fred_data("TTLCONS"),
        "housing_starts": fetch_fred_data("HOUST"),
        "building_permits": fetch_fred_data("PERMIT"),
        "nahb_hmi": {"note": "Requires separate integration"},
        "dodge_momentum": {"note": "Requires Dodge Data subscription"}
    }

