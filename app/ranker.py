from sqlalchemy import text
from .db import SessionLocal
from datetime import datetime, timezone

ALT_TAGS = {"rammed","straw","hempcrete","bamboo","mycelium","adaptive reuse","passive","geopolymer","low-carbon","net-zero"}

def _has_alt(topics):
    return any(any(tag in (t or "").lower() for tag in ALT_TAGS) for t in (topics or []))

def select_top5():
    db = SessionLocal()
    rows = db.execute(text("""
      SELECT a.id, a.url, a.title, a.source, s.composite_score, s.topics, s.summary2, s.why1, a.published_at
      FROM article_scores s
      JOIN articles a ON a.id = s.article_id
      WHERE a.status IN ('scored','selected')
      ORDER BY s.composite_score DESC
      LIMIT 60
    """)).fetchall()
    if not rows:
        db.close(); return []

    # Section balance targets
    market = []
    build = []
    deal = []
    alt_candidates = []

    for r in rows:
        t = [ (x or "").lower() for x in (r.topics or []) ]
        score = float(r.composite_score or 0)
        rec = {"id": str(r.id), "url": r.url, "title": r.title, "source": r.source, "score": score,
               "topics": t, "summary2": r.summary2, "why1": r.why1}
        if any(x in t for x in ["rates","inflation","fed","cpi","permits","policy","rents","cap rate","m&a"]):
            market.append(rec)
        if any(x in t for x in ["3d","modular","timber","rammed","straw","hempcrete","bamboo","mycelium","geopolymer","adaptive reuse","net-zero"]):
            build.append(rec)
        if any(x in t for x in ["development","lawsuit","case study","entitlement","design","feasibility"]):
            deal.append(rec)
        if _has_alt(t):
            alt_candidates.append(rec)

    # assemble with guardrails
    selected = []
    selected.extend(market[:2])        # 1–2 market
    selected.extend(build[:2])         # 1–2 build-tech
    if not alt_candidates and build:
        pass  # if none, will still have build-tech
    else:
        # ensure at least one alt if not already present
        if not any(_has_alt(x["topics"]) for x in selected):
            if alt_candidates:
                selected.append(alt_candidates[0])

    # fill remaining slots by best remaining
    used_ids = {x["id"] for x in selected}
    remaining = [r for r in rows if str(r.id) not in used_ids]
    remaining_sorted = sorted(
        [{"id":str(r.id),"url":r.url,"title":r.title,"source":r.source,"score":float(r.composite_score or 0),
          "topics":[(x or "").lower() for x in (r.topics or [])], "summary2":r.summary2, "why1":r.why1} for r in remaining],
        key=lambda x: -x["score"]
    )
    for r in remaining_sorted:
        if len(selected) >= 5: break
        selected.append(r)

    # clip to 5
    selected = selected[:5]
    db.close()
    return selected
