# app/llm.py
import json
from openai import OpenAI
from .config import OPENAI_API_KEY

CLIENT = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM = """
You score news articles for a weekly newsletter about architecture/development and building tech.
Return ONLY a compact JSON object with keys:
- summary2: 1–2 sentence summary, plain text.
- why1: one short sentence explaining why it matters.
- topics: array of 3–6 lowercase topic tags (e.g., "modular", "prefab", "timber", "zoning", "entitlements",
  "financing", "bamboo", "passive", "geopolymer", "low-carbon", "net-zero").
- composite_score: number from 0 to 100 (float is fine) reflecting overall quality/relevance.
No prose, no markdown — just JSON.
"""

def score_article_with_llm(title: str, content: str, published_at=None, fetched_at=None) -> dict:
    # Keep prompt modest in size to avoid token bloat during testing
    snippet = (content or "")[:4000]
    user = f"Title: {title}\n\nContent:\n{snippet}"

    rsp = CLIENT.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "system", "content": SYSTEM},
                  {"role": "user", "content": user}],
        temperature=0.2,
    )
    text = (rsp.choices[0].message.content or "").strip()

    # Try to parse JSON; if the model returns text, fall back safely
    try:
        data = json.loads(text)
    except Exception:
        data = {
            "summary2": title or "Untitled",
            "why1": "Relevant to building-tech / AEC.",
            "topics": [],
            "composite_score": 60.0,
        }

    # Normalize fields so DB inserts don’t blow up
    data.setdefault("summary2", title or "Untitled")
    data.setdefault("why1", "Relevant to building-tech / AEC.")
    if not isinstance(data.get("topics"), list):
        data["topics"] = []
    try:
        data["composite_score"] = float(data.get("composite_score", 60.0))
    except Exception:
        data["composite_score"] = 60.0

    return data

def call_llm(prompt: str, max_tokens: int = 1000, temperature: float = 0.3) -> str:
    """Generic LLM call function for synthesis tasks"""
    try:
        rsp = CLIENT.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return (rsp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"Error generating content: {str(e)}"
