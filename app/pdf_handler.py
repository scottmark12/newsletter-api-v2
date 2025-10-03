# PDF Handler - Downloads and extracts text from CRE research reports
import re
import tempfile
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import text

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

from .config import USER_AGENT
from .utils import canonicalize_url, sha1

HEADERS = {"User-Agent": USER_AGENT}

RESEARCH_FIRMS = {
    "jll.com": {"name": "JLL", "insights_page": "https://www.jll.com/en/trends-and-insights", "pdf_patterns": [r"\.pdf$"]},
    "cbre.com": {"name": "CBRE", "insights_page": "https://www.cbre.com/insights", "pdf_patterns": [r"\.pdf$"]},
}

def extract_text_from_pdf(pdf_content: bytes) -> Optional[str]:
    if pdfplumber:
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                tmp.write(pdf_content)
                tmp.flush()
                with pdfplumber.open(tmp.name) as pdf:
                    return "\n\n".join(p.extract_text() or "" for p in pdf.pages)
        except Exception as e:
            print(f"[pdf] pdfplumber failed: {e}")
    if PyPDF2:
        try:
            with tempfile.NamedTemporaryFile(suffix='.pdf') as tmp:
                tmp.write(pdf_content)
                tmp.flush()
                with open(tmp.name, 'rb') as f:
                    reader = PyPDF2.PdfReader(f)
                    return "\n\n".join(p.extract_text() or "" for p in reader.pages)
        except Exception as e:
            print(f"[pdf] PyPDF2 failed: {e}")
    return None

def find_pdfs(url: str, html: str, patterns: List[str]) -> List[str]:
    soup = BeautifulSoup(html, "lxml")
    pdfs = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if any(re.search(p, href, re.I) for p in patterns):
            abs_url = href if href.startswith("http") else urljoin(url, href)
            if abs_url.lower().endswith('.pdf'):
                pdfs.append(abs_url)
    return pdfs[:10]

def run(limit: int = 10):
    from .db import SessionLocal
    db = SessionLocal()
    try:
        if not PyPDF2 and not pdfplumber:
            return {"ok": False, "error": "Install PyPDF2 or pdfplumber"}
        count = 0
        now = datetime.now(timezone.utc)
        with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
            for domain, config in RESEARCH_FIRMS.items():
                if count >= limit:
                    break
                try:
                    r = client.get(config["insights_page"])
                    r.raise_for_status()
                    pdfs = find_pdfs(config["insights_page"], r.text, config["pdf_patterns"])
                    for pdf_url in pdfs[:min(5, limit-count)]:
                        try:
                            pr = client.get(pdf_url)
                            pr.raise_for_status()
                            text = extract_text_from_pdf(pr.content)
                            if not text or len(text) < 500:
                                continue
                            title = f"{config['name']} Research Report"
                            sql = text("""INSERT INTO articles (url, source, title, summary_raw, content, published_at, canonical_hash, lang)
                                VALUES (:url, :source, :title, :summary_raw, :content, :published_at, :canonical_hash, :lang)
                                ON CONFLICT (url) DO NOTHING RETURNING id""")
                            res = db.execute(sql, {
                                "url": pdf_url, "source": config['name'], "title": title[:500],
                                "summary_raw": text[:1000], "content": text[:50000],
                                "published_at": now.isoformat(), "canonical_hash": sha1(pdf_url), "lang": "en"
                            })
                            if row := res.fetchone():
                                count += 1
                                print(f"[pdf] Inserted {config['name']} report")
                        except Exception as e:
                            print(f"[pdf] Error processing {pdf_url}: {e}")
                except Exception as e:
                    print(f"[pdf] Error crawling {domain}: {e}")
        db.commit()
        return {"ok": True, "reports_ingested": count}
    finally:
        db.close()
