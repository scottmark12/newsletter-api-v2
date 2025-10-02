# app/cse_client.py
# Server-side Google Programmable Search (Custom Search JSON API)
# - Caches results locally (sqlite file) for 24h
# - Simple daily quota guard so you don't burn credits

import os, json, time, hashlib, sqlite3, pathlib, requests
from typing import List, Dict, Optional

# FIXED: Environment variable names should match the actual env var names
GOOGLE_API_KEY = os.environ.get("GOOGLE_CSE_API_KEY")        # <-- set in env
DEFAULT_CX = os.environ.get("GOOGLE_CSE_CX_ID")             # your Search engine ID
CSE_DAILY_MAX = int(os.environ.get("CSE_DAILY_MAX_QUERIES", "60"))
CACHE_TTL_SEC = int(os.environ.get("CSE_CACHE_TTL_SEC", "86400"))  # 24h

DATA_DIR = pathlib.Path(os.environ.get("CSE_DATA_DIR", ".cse_store"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "cse_cache.sqlite"

def _open_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS cache (
      key TEXT PRIMARY KEY,
      value TEXT NOT NULL,
      ts INTEGER NOT NULL
    )""")
    conn.execute("""
    CREATE TABLE IF NOT EXISTS quota (
      day TEXT PRIMARY KEY,
      used INTEGER NOT NULL
    )""")
    conn.commit()
    return conn

def _k(cx: str, q: str, num: int, site: Optional[str]) -> str:
    h = hashlib.sha256(f"{cx}|{q}|{num}|{site or ''}".encode()).hexdigest()
    return h

def _today():
    return time.strftime("%Y-%m-%d")

def _quota_try_consume(conn, n=1) -> bool:
    day = _today()
    cur = conn.cursor()
    row = cur.execute("SELECT used FROM quota WHERE day=?", (day,)).fetchone()
    used = row[0] if row else 0
    if used + n > CSE_DAILY_MAX:
        return False
    if row:
        cur.execute("UPDATE quota SET used=? WHERE day=?", (used + n, day))
    else:
        cur.execute("INSERT INTO quota(day, used) VALUES(?,?)", (day, n))
    conn.commit()
    return True

def get_quota_status() -> Dict[str, int]:
    """Get current quota usage for monitoring"""
    conn = _open_db()
    day = _today()
    row = conn.execute("SELECT used FROM quota WHERE day=?", (day,)).fetchone()
    used = row[0] if row else 0
    conn.close()
    return {"used": used, "limit": CSE_DAILY_MAX, "remaining": CSE_DAILY_MAX - used}

def cse_search(q: str, *, cx: Optional[str]=None, num: int=5, site: Optional[str]=None) -> List[Dict]:
    """
    Search using Google Custom Search Engine with caching and quota management
    
    Args:
        q: Search query
        cx: Custom search engine ID (optional, uses default)
        num: Number of results (1-10)
        site: Restrict search to specific site (optional)
    
    Returns:
        List of search results with title, url, snippet
    """
    if not GOOGLE_API_KEY:
        raise RuntimeError("GOOGLE_CSE_API_KEY missing. Set it in your environment.")
    cx = cx or DEFAULT_CX
    if not cx:
        raise RuntimeError("GOOGLE_CSE_CX_ID missing. Set your Programmable Search 'cx' in env.")

    conn = _open_db()
    try:
        key = _k(cx, q, min(max(num,1),10), site)
        now = int(time.time())

        # cache hit?
        row = conn.execute("SELECT value, ts FROM cache WHERE key=?", (key,)).fetchone()
        if row:
            value, ts = row
            if now - ts < CACHE_TTL_SEC:
                conn.close()
                return json.loads(value)

        # quota check
        if not _quota_try_consume(conn, 1):
            # out of budget → return stale cache if any, else empty
            if row:
                conn.close()
                return json.loads(row[0])
            conn.close()
            return []

        params = {
            "key": GOOGLE_API_KEY, 
            "cx": cx, 
            "q": q, 
            "num": min(max(num,1),10)
        }
        if site:
            params["siteSearch"] = site

        try:
            r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=15)
            r.raise_for_status()
            data = r.json()
            
            # Handle API errors
            if "error" in data:
                print(f"CSE API Error: {data['error']}")
                if row:  # Return stale cache if available
                    return json.loads(row[0])
                return []
                
            items = data.get("items", []) or []
            out = [
                {
                    "title": it.get("title", ""),
                    "url": it.get("link", ""),
                    "snippet": it.get("snippet", "")
                } 
                for it in items
            ]

            # Cache the results
            conn.execute("INSERT OR REPLACE INTO cache(key,value,ts) VALUES(?,?,?)", 
                        (key, json.dumps(out), now))
            conn.commit()
            return out
            
        except requests.RequestException as e:
            print(f"CSE Request Error: {e}")
            # Return stale cache if available
            if row:
                return json.loads(row[0])
            return []
    
    finally:
        conn.close()

def search_construction_news(query: str, num: int = 5) -> List[Dict]:
    """
    Search for construction/real estate news with v2 source prioritization
    """
    # Try tier-1 sources first
    tier1_sites = [
        "enr.com",
        "construction.com", 
        "commercialobserver.com",
        "bisnow.com",
        "urbanland.uli.org"
    ]
    
    results = []
    remaining = num
    
    # Search tier-1 sources first
    for site in tier1_sites:
        if remaining <= 0:
            break
        site_results = cse_search(query, site=site, num=min(remaining, 3))
        results.extend(site_results)
        remaining -= len(site_results)
    
    # If we need more results, do a general search
    if remaining > 0:
        general_results = cse_search(query, num=remaining)
        # Filter out duplicates
        existing_urls = {r["url"] for r in results}
        for result in general_results:
            if result["url"] not in existing_urls:
                results.append(result)
                if len(results) >= num:
                    break
    
    return results[:num]

