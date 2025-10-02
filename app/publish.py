# app/publish.py
from jinja2 import Environment, BaseLoader
import httpx
from sqlalchemy import text
from datetime import date
from .config import RESEND_API_KEY, SENDER_EMAIL, SENDER_NAME, SITE_BASE_URL
from .db import SessionLocal

TEMPLATE = """
<h1>Building the Future — {{ issue_date }}</h1>
<p>Curated market + building-tech intel, with an architect–developer lens.</p>
{% for it in items %}
  <h3>{{ it.title }}</h3>
  <p>{{ it.summary2 }}</p>
  <p><strong>Why it matters:</strong> {{ it.why1 }}</p>
  <p><em>My take:</em> {{ it.opinion }}</p>
  <p><a href="{{ it.url }}">Read →</a></p>
{% endfor %}
"""

def save_issue(issue_date: str, items: list, slug: str) -> str:
    """Render and persist the issue HTML. Creates the table if it's missing."""
    env = Environment(loader=BaseLoader())
    html = env.from_string(TEMPLATE).render(issue_date=issue_date, items=items)

    db = SessionLocal()
    # 1) Ensure table exists (safe to run every time)
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS issues (
          id          bigserial PRIMARY KEY,
          issue_date  date UNIQUE NOT NULL,
          slug        text,
          html        text NOT NULL,
          created_at  timestamptz NOT NULL DEFAULT now()
        )
    """))

    # 2) Upsert the HTML
    db.execute(
        text("""INSERT INTO issues (issue_date, slug, html)
                VALUES (:d, :s, :h)
                ON CONFLICT (issue_date)
                DO UPDATE SET html = EXCLUDED.html, slug = EXCLUDED.slug"""),
        {"d": issue_date, "s": f"building-the-future-{issue_date}", "h": html}
    )
    db.commit()
    db.close()
    return html

def send_email(issue_date: str, html: str, to_list: list[str]) -> bool:
    if not RESEND_API_KEY:
        return False
    payload = {
        "from": f"{SENDER_NAME} <{SENDER_EMAIL}>",
        "to": to_list,
        "subject": f"Building the Future — {issue_date}",
        "html": html
    }
    r = httpx.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json=payload,
        timeout=20
    )
    return r.status_code in (200, 201)

def dryrun(limit: int = 10) -> str:
    """
    Build a preview issue HTML from the most recent articles (with scores if available).
    Robust: if saving fails, still return the rendered HTML so the endpoint never 502s.
    """
    db = SessionLocal()
    rows = db.execute(text("""
        SELECT
          a.id,
          a.url,
          a.title,
          COALESCE(s.summary2, '') AS summary2,
          COALESCE(s.why1, '')     AS why1,
          ''::text                 AS opinion
        FROM articles a
        LEFT JOIN article_scores s ON s.article_id = a.id
        ORDER BY COALESCE(a.published_at, now()) DESC, a.id DESC
        LIMIT :limit
    """), {"limit": limit}).mappings().all()
    db.close()

    items = [dict(r) for r in rows]

    # Render HTML
    env = Environment(loader=BaseLoader())
    html = env.from_string(TEMPLATE).render(issue_date=date.today().isoformat(), items=items)

    # Try to persist, but don't fail the response if DB writes error
    try:
        _ = save_issue(date.today().isoformat(), items, slug="dryrun")
        return html  # we already rendered the same HTML above
    except Exception as e:
        print(f"[publish.dryrun] save_issue failed: {e}")
        return html
