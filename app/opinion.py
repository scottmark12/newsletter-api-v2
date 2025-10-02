from openai import OpenAI
from .config import OPENAI_API_KEY

CLIENT = OpenAI(api_key=OPENAI_API_KEY)

VOICE = """
You are the author—an aspiring architect–developer.
Write a 1–2 sentence opinion for each article that ties design to cost/constructability/entitlement/resilience.
Tone: concise, practical, optimistic but clear-eyed.
"""

def generate_opinion(title, summary, why):
    prompt = f"Title: {title}\nSummary: {summary}\nWhy it matters: {why}\n\nWrite the opinion:"
    rsp = CLIENT.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role":"system","content":VOICE},
                  {"role":"user","content":prompt}],
        temperature=0.4
    )
    return rsp.choices[0].message.content.strip()
