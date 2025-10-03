from urllib.parse import urljoin, urlparse
import json
import pathlib
import re
import time
from typing import Optional
from datetime import datetime, timezone, timedelta

import httpx
import feedparser
from bs4 import BeautifulSoup
from dateutil import parser as dp
from langdetect import detect
from readability import Document
from trafilatura import extract as t_extract
from sqlalchemy import text

from .config import USER_AGENT, MAX_ARTICLES_PER_RUN
from .db import SessionLocal
from .utils import canonicalize_url, sha1
from .cse_client import search_construction_news

HEADERS = {"User-Agent": USER_AGENT}

# Limits
TOP_K = 8                              # per seed page/feed
FRESH_WINDOW = timedelta(hours=72)     # widen now; tighten later if you want
MAX_PER_DOMAIN_PER_RUN = 8             # hard cap per registrable domain per ingest run

# Optional dependency for robust domain normalization
try:
    import tldextract  # type: ignore
except Exception:
    tldextract = None

def _registrable_domain(host: str) -> str:
    host = (host or "").lower().strip()
    for pfx in ("www.", "amp.", "m.", "mobile.", "news.", "beta."):
        if host.startswith(pfx):
            host = host[len(pfx):]
    if tldextract:
        try:
            ext = tldextract.extract(host)
            if ext.registered_domain:
                return ext.registered_domain.lower()
        except Exception:
            pass
    parts = host.split(".")
    if len(parts) >= 2:
        return ".".join(parts[-2:]).lower()
    return host

SITE_LINK_PATTERNS = {
    "archdaily.com": re.compile(r"/\d{6,}/"),
    "dezeen.com": re.compile(r"/20\d{2}/\d{2}/"),
    "constructiondive.com": re.compile(r"/news/"),
    "smartcitiesdive.com": re.compile(r"/news/"),
    "bdcnetwork.com": re.compile(r"/(news|architecture|building|blog)/"),
    "therealdeal.com": re.compile(r"/20\d{2}/\d{2}/\d{2}/"),
    "redfin.com": re.compile(r"/news/"),
    "zillow.com": re.compile(r"/research/"),
    "brookings.edu": re.compile(r"/\d{4}/\d{2}/\d{2}/"),
    "urban.org": re.compile(r"/\d{4}/\d{2}/\d{2}/"),
    "rmi.org": re.compile(r"/(insight|blog)/"),
}

SKIP_HOSTS = {
    "facebook.com", "twitter.com", "x.com", "instagram.com", "pinterest.com",
    "vimeo.com", "tiktok.com"
}
SKIP_SUBSTRINGS = {
    "/login", "/signup", "/contact", "/advertise", "/privacy", "/terms",
    "/imprint", "/jobs", "/search", "/tag/", "/category/", "/videos", "/images",
    "/products", "/professionals", "/events", "/competitions", "/publications",
    "/subscribe", "/feed", "utm_", "ad_source=", "ad_name="
}
STOP_TAILS = {
    "about", "about-us", "contact", "privacy-policy", "privacy",
    "terms", "imprint", "jobs", "advertise", "subscribe", "cookies",
    "cookie-policy", "sitemap"
}

def _first_k_unique(urls, k: int):
    out, seen = [], set()
    for u in urls:
        if u in seen:
            continue
        seen.add(u)
        out.append(u)
        if len(out) >= k:
            break
    return out

def _likely_article(u: str) -> bool:
    p = urlparse(u)
    host = p.netloc.lower()
    if any(h in host for h in SKIP_HOSTS):
        return False
    
    # Special handling for YouTube videos
    if "youtube.com" in host and "/watch" in p.path:
        return True
    if "youtu.be" in host:
        return True
        
    path = p.path.lower()
    if any(s in u.lower() for s in SKIP_SUBSTRINGS):
        return False
    segs = [s for s in path.strip("/").split("/") if s]
    if not segs:
        return False
    if segs[-1] in STOP_TAILS:
        return False
    if len(segs) < 2:
        return False
    if path.endswith((".xml", ".rss", ".atom", ".json")):
        return False
    return True

def _extract_html(url: str, html: str) -> tuple[str, str]:
    doc = Document(html)
    title = (doc.short_title() or "").strip()
    body = t_extract(filecontent=html, include_links=False, url=url) or ""
    if not body:
        soup = BeautifulSoup(html, "lxml")
        title = title or (soup.title.string.strip() if soup.title else "")
        p_tags = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        body = "\n".join(p_tags)
    return (title or url, body)

def _detect_published(soup: BeautifulSoup) -> Optional[str]:
    for key in ("article:published_time", "og:pubdate", "pubdate", "date", "timestamp"):
        tag = soup.find("meta", {"property": key}) or soup.find("meta", {"name": key})
        if tag and tag.get("content"):
            try:
                return dp.parse(tag["content"]).isoformat()
            except Exception:
                pass
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            raw = s.string or s.get_text() or ""
            if not raw.strip():
                continue
            data = json.loads(raw)
            def _scan(obj):
                if isinstance(obj, dict):
                    for k in ("datePublished", "dateModified", "uploadDate", "dateCreated"):
                        v = obj.get(k)
                        if isinstance(v, str):
                            try:
                                return dp.parse(v).isoformat()
                            except Exception:
                                pass
                    for v in obj.values():
                        res = _scan(v)
                        if res:
                            return res
                elif isinstance(obj, list):
                    for item in obj:
                        res = _scan(item)
                        if res:
                            return res
                return None
            found = _scan(data)
            if found:
                return found
        except Exception:
            continue
    return None

def _is_article_by_meta(soup: BeautifulSoup) -> bool:
    og_type = soup.find("meta", {"property": "og:type"})
    if og_type and isinstance(og_type.get("content"), str):
        content_type = og_type["content"].strip().lower()
        if content_type in {"article", "news", "news:article", "blog", "blogposting", "blogpost", "video", "video.other"}:
            return True
    if soup.find("meta", {"property": "article:author"}) or soup.find("meta", {"property": "article:published_time"}):
        return True
    for s in soup.find_all("script", {"type": "application/ld+json"}):
        try:
            raw = s.string or s.get_text() or ""
            if not raw.strip():
                continue
            data = json.loads(raw)
            def _has_article(obj) -> bool:
                if isinstance(obj, dict):
                    t = obj.get("@type")
                    types = [t.lower()] if isinstance(t, str) else [str(x).lower() for x in t] if isinstance(t, list) else []
                    if any(x in {"article", "newsarticle", "blogposting"} for x in types):
                        return True
                    for v in obj.values():
                        if isinstance(v, (dict, list)) and _has_article(v):
                            return True
                elif isinstance(obj, list):
                    return any(_has_article(x) for x in obj)
                return False
            if _has_article(data):
                return True
        except Exception:
            continue
    return False

def _path_articleish(u: str) -> bool:
    path = urlparse(u).path.lower()
    segs = [s for s in path.strip("/").split("/") if s]
    if not segs:
        return False
    if segs[-1] in STOP_TAILS:
        return False
    if any(token in path for token in ("/news", "/article", "/articles", "/architecture-news", "/stories", "/story/")):
        return True
    if re.search(r"/20\d{2}/", path):
        return True
    if len(segs) >= 3 and "-" in segs[-1]:
        return True
    return False

def _is_fresh(published_iso: Optional[str], now_utc: datetime) -> bool:
    if not published_iso:
        return False
    try:
        dt = dp.parse(published_iso)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        if dt > now_utc + timedelta(minutes=5):
            return False
        return (now_utc - dt) <= FRESH_WINDOW
    except Exception:
           return False

def maybe_insert_article(url: str, client: httpx.Client, db, inserted_counter, attempts_counter, domain_counts, cap, now_utc, fallback_published_iso: Optional[str] = None):
    """Helper function to insert an article if it meets criteria"""
    if inserted_counter[0] >= cap:
        return False

    u = canonicalize_url(url)
    host_raw = urlparse(u).netloc
    host = _registrable_domain(host_raw)

    if domain_counts.get(host, 0) >= MAX_PER_DOMAIN_PER_RUN:
        print(f"[crawler] domain-cap reached for {host}; skipping {u}")
        return False

    attempts_counter[0] += 1
    try:
        r = client.get(u, follow_redirects=True)
        r.raise_for_status()
        
        # Use readability to extract main content
        doc = Document(r.text)
        title = doc.title()
        body_html = doc.summary()
        
        # Fallback to trafilatura for content if readability fails or is empty
        if not body_html or len(body_html) < 100: # Arbitrary length check
            body_text = t_extract(r.text, include_comments=False, include_tables=False, no_fallback=False)
        else:
            body_text = BeautifulSoup(body_html, "lxml").get_text(separator="\n")

        if not body_text:
            print(f"[crawler] no content for {u}; skipping")
            return False

        # Language detection
        lang = "en"
        try:
            lang = detect(body_text[:1000]) # Detect language from first 1000 chars
        except Exception:
            pass # Default to 'en' if detection fails

        # Published date extraction
        published_iso = fallback_published_iso
        if not published_iso:
            # Try to get from meta tags
            soup = BeautifulSoup(r.text, "lxml")
            pub_time_tag = soup.find("meta", {"property": "article:published_time"}) or \
                           soup.find("meta", {"name": "date"})
            if pub_time_tag and pub_time_tag.get("content"):
                try:
                    published_iso = dp.parse(pub_time_tag["content"]).isoformat()
                except Exception:
                    pass
        
        if not published_iso:
            # Fallback to current time if no published date found
            published_iso = now_utc.isoformat()

        # Check freshness
        if not _is_fresh(dp.parse(published_iso), now_utc):
            print(f"[crawler] stale {u}; skipping")
            return False

        sql = text("""
            INSERT INTO articles
              (url, source, title, summary_raw, content, published_at, canonical_hash, lang)
            VALUES
              (:url, :source, :title, :summary_raw, :content, :published_at, :canonical_hash, :lang)
            ON CONFLICT (url) DO NOTHING
            RETURNING id
        """)
        res = db.execute(sql, {
            "url": u,
            "source": (soup.find("meta", {"property": "og:site_name"}) or {}).get("content")
                      or (urlparse(u).netloc),
            "title": (title or "")[:500],
            "summary_raw": ((soup.find("meta", {"name": "description"}) or {}).get("content", ""))[:1000],
            "content": body_text[:50000],
            "published_at": published_iso,
            "canonical_hash": sha1(u),
            "lang": lang,
        })
        row = res.fetchone()
        if row:
            inserted_counter[0] += 1
            domain_counts[host] = domain_counts.get(host, 0) + 1
            print(f"[crawler] INSERTED {u} (domain {host}: {domain_counts[host]}/{MAX_PER_DOMAIN_PER_RUN})")
            return True
        else:
            print(f"[crawler] duplicate/no-op {u}")
            return False

    except Exception as e:
        print(f"[crawler] error for {u}: {e}")
        return False

def crawl_google_searches(limit: int, db, inserted_counter, attempts_counter, domain_counts, cap, now_utc) -> int:
    """Crawl articles using Google search queries for innovation and opportunities"""
    print(f"[google] Starting Google search crawl, limit={limit}")
    
    # Innovation/Engineering search queries
    innovation_queries = [
        "3d printed home",
        "straw homes", 
        "rammed earth homes",
        "engineering construction news"
    ]
    
    # Opportunities search queries
    opportunity_queries = [
        "Real Estate Opportunities News",
        "3d printed home News",
        "straw homes News", 
        "rammed earth homes News",
        "engineering construction news"
    ]
    
    all_queries = innovation_queries + opportunity_queries
    
    with httpx.Client(headers=HEADERS, timeout=30.0, follow_redirects=True) as client:
        for query in all_queries:
            if inserted_counter[0] >= limit:
                break
                
            try:
                print(f"[google] Searching: {query}")
                results = search_construction_news(query, num=5)
                
                for result in results:
                    if inserted_counter[0] >= limit:
                        break
                    try:
                        maybe_insert_article(result["url"], client, db, inserted_counter, attempts_counter, domain_counts, cap, now_utc)
                        if inserted_counter[0] % 10 == 0:
                            print(f"[google] Inserted {inserted_counter[0]} articles so far")
                    except Exception as e:
                        print(f"[google] Error processing {result['url']}: {e}")
                        
            except Exception as e:
                print(f"[google] Error searching '{query}': {e}")
                
    print(f"[google] Google search crawl complete: {inserted_counter[0]} articles inserted")
    return inserted_counter[0]

def ingest_run(limit: Optional[int] = None) -> int:
    cap = int(limit or MAX_ARTICLES_PER_RUN)
    now_utc = datetime.now(timezone.utc)

    db = SessionLocal()
    db.execute(text("SELECT 1"))

    seeds_path = pathlib.Path(__file__).with_name("seeds.json")
    with seeds_path.open() as f:
        seed_cfg = json.load(f)

    print(f"[crawler] cap={cap}, seeds={sum(len(v) for v in seed_cfg.values())} lists")
    
    # Split the limit between RSS feeds and Google searches
    rss_limit = int(cap * 0.8)  # 80% RSS feeds
    google_limit = cap - rss_limit  # 20% Google searches
    
    print(f"[crawler] RSS limit: {rss_limit}, Google limit: {google_limit}")

    inserted_counter = [0]  # Use list to allow modification in nested functions
    attempts_counter = [0]
    domain_counts: dict[str, int] = {}

    def maybe_insert(url: str, client: httpx.Client, fallback_published_iso: Optional[str] = None):
        if inserted_counter[0] >= cap:
            return

        u = canonicalize_url(url)
        host_raw = urlparse(u).netloc
        host = _registrable_domain(host_raw)

        if domain_counts.get(host, 0) >= MAX_PER_DOMAIN_PER_RUN:
            print(f"[crawler] domain-cap reached for {host}; skipping {u}")
            return

        if not _likely_article(u):
            print(f"[crawler] skip non-article-url {u}")
            return

        attempts_counter[0] += 1
        try:
            r = client.get(u, follow_redirects=True, timeout=20)
            if r.status_code >= 400 or not r.text:
                print(f"[crawler] skip fetch-failed {u} status={r.status_code}")
                return

            html = r.text
            soup = BeautifulSoup(html, "lxml")

            if not _is_article_by_meta(soup) and not _path_articleish(u):
                print(f"[crawler] skip not-article-by-meta {u}")
                return

            published_iso = _detect_published(soup) or fallback_published_iso
            if not _is_fresh(published_iso, now_utc):
                print(f"[crawler] skip stale-or-undated {u} published={published_iso}")
                return

            title, body_text = _extract_html(u, html)
            if not body_text or len(body_text.split()) < 180:
                print(f"[crawler] skip too-short {u}")
                return

            try:
                lang = detect(body_text)
            except Exception:
                lang = "unknown"
            if lang != "en":
                print(f"[crawler] skip non-en {u} lang={lang}")
                return

            sql = text("""
                INSERT INTO articles
                  (url, source, title, summary_raw, content, published_at, canonical_hash, lang)
                VALUES
                  (:url, :source, :title, :summary_raw, :content, :published_at, :canonical_hash, :lang)
                ON CONFLICT (url) DO NOTHING
                RETURNING id
            """)
            res = db.execute(sql, {
                "url": u,
                "source": (soup.find("meta", {"property": "og:site_name"}) or {}).get("content")
                          or (urlparse(u).netloc),
                "title": (title or "")[:500],
                "summary_raw": ((soup.find("meta", {"name": "description"}) or {}).get("content", ""))[:1000],
                "content": body_text[:50000],
                "published_at": published_iso,
                "canonical_hash": sha1(u),
                "lang": lang,
            })
        row = res.fetchone()
        if row:
            inserted_counter[0] += 1
            domain_counts[host] = domain_counts.get(host, 0) + 1
            print(f"[crawler] INSERTED {u} (domain {host}: {domain_counts[host]}/{MAX_PER_DOMAIN_PER_RUN})")
        else:
            print(f"[crawler] duplicate/no-op {u}")

        except Exception as e:
            print(f"[crawler] error for {u}: {e}")
            return

    with httpx.Client(headers=HEADERS, timeout=20) as client:
        # Prioritize tier_1_sources and new high-quality categories first
        priority_categories = ["tier_1_sources", "innovation_engineering", "insights_sources", "economy_news"]
        other_categories = [k for k in seed_cfg.keys() if k not in priority_categories]
        
        # Process priority categories first
        for category in priority_categories:
            if category in seed_cfg:
                print(f"[crawler] Processing priority category: {category}")
                for base in seed_cfg[category]:
                    if inserted_counter[0] >= cap:
                        break
                try:
                    fp = feedparser.parse(base)

                    if fp.bozo or not getattr(fp, "entries", None):
                        r = client.get(base, follow_redirects=True)
                        if r.status_code < 400 and r.text:
                            soup = BeautifulSoup(r.text, "lxml")
                            base_host = _registrable_domain(urlparse(base).netloc.lower())

                            candidates = []
                            pat = SITE_LINK_PATTERNS.get(base_host)

                            for a in soup.select("a[href]"):
                                href = a.get("href")
                                if not href:
                                    continue
                                absolute = href if href.startswith("http") else urljoin(base, href)
                                u_abs = canonicalize_url(absolute)
                                if not _likely_article(u_abs):
                                    continue

                                cand_host = _registrable_domain(urlparse(u_abs).netloc)

                                # **CRITICAL**: stay on same registrable domain as seed
                                if cand_host != base_host:
                                    continue

                                if domain_counts.get(cand_host, 0) >= MAX_PER_DOMAIN_PER_RUN:
                                    continue

                                if pat:
                                    path = urlparse(u_abs).path
                                    if pat.search(u_abs) or pat.search(path):
                                        candidates.append(u_abs)
                                else:
                                    if _path_articleish(u_abs):
                                        candidates.append(u_abs)

                            for u_abs in _first_k_unique(candidates, TOP_K):
                                maybe_insert(u_abs, client)
                                if inserted >= cap:
                                    break

                    else:
                        for e in fp.entries[:TOP_K]:
                            link = e.get("link")
                            if not link:
                                continue

                            fb = e.get("published") or e.get("updated") or e.get("pubDate")
                            fb_iso = None
                            try:
                                if fb:
                                    fb_iso = dp.parse(fb).isoformat()
                                else:
                                    tp = e.get("published_parsed") or e.get("updated_parsed")
                                    if tp:
                                        fb_iso = datetime.fromtimestamp(
                                            time.mktime(tp), tz=timezone.utc
                                        ).isoformat()
                            except Exception:
                                fb_iso = None

                            host_check = _registrable_domain(urlparse(link).netloc)
                            if domain_counts.get(host_check, 0) >= MAX_PER_DOMAIN_PER_RUN:
                                continue

                            maybe_insert(link, client, fallback_published_iso=fb_iso)
                            if inserted >= cap:
                                break

                       except Exception as e:
                           print(f"[crawler] seed error for {base}: {e}")
                           continue

           # Run Google searches if we haven't reached the RSS limit
           if inserted_counter[0] < rss_limit:
               google_inserted = crawl_google_searches(min(google_limit, cap - inserted_counter[0]), db, inserted_counter, attempts_counter, domain_counts, cap, now_utc)

           db.commit()
           print(f"[crawler] done: attempts={attempts_counter[0]}, inserted={inserted_counter[0]}, per-domain={domain_counts}")
           db.close()
           return inserted_counter[0]

def run(limit: Optional[int] = None):
    count = ingest_run(limit)
    return {"ok": True, "ingested": int(count or 0)}
