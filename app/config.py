# app/config.py
import os

def _required(name: str) -> str:
    v = os.environ.get(name)
    if not v:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return v

OPENAI_API_KEY = _required("OPENAI_API_KEY")
DATABASE_URL   = _required("DATABASE_URL")

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
SENDER_EMAIL   = os.environ.get("SENDER_EMAIL", "no-reply@example.com")
SENDER_NAME    = os.environ.get("SENDER_NAME", "Building the Future")
SITE_BASE_URL  = os.environ.get("SITE_BASE_URL", "http://localhost:10000")
TIMEZONE       = os.environ.get("TIMEZONE", "America/New_York")
USER_AGENT     = os.environ.get("USER_AGENT", "BuildingTheFutureBot/1.0")
MAX_ARTICLES_PER_RUN = int(os.environ.get("MAX_ARTICLES_PER_RUN", "100"))
