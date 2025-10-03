import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment, with FORCE_SQLITE override
def _get_database_url():
    """Get the actual database URL, respecting FORCE_SQLITE"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///newsletter.db")
    force_sqlite = os.getenv("FORCE_SQLITE", "").lower() in ("true", "1", "yes")
    
    if force_sqlite:
        # Force SQLite even if DATABASE_URL looks like PostgreSQL
        return "sqlite:///newsletter.db"
    else:
        # Convert postgres:// to postgresql+psycopg:// for Python 3.13 compatibility
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql+psycopg://', 1)
        elif db_url.startswith('postgresql://'):
            db_url = db_url.replace('postgresql://', 'postgresql+psycopg://', 1)
        return db_url

# Get the actual database URL
actual_db_url = _get_database_url()
is_postgres = actual_db_url.startswith('postgresql') or actual_db_url.startswith('postgres')

# Create engine with the actual database URL
engine = create_engine(actual_db_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# PostgreSQL schema
POSTGRES_SCHEMA_SQL = """
-- Enable UUID extension for PostgreSQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS articles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  url TEXT UNIQUE,
  source TEXT,
  title TEXT,
  summary_raw TEXT,
  content TEXT,
  published_at TIMESTAMPTZ,
  fetched_at TIMESTAMPTZ DEFAULT NOW(),
  canonical_hash TEXT,
  embedding BYTEA,
  lang TEXT,
  paywalled BOOLEAN DEFAULT FALSE,
  status TEXT DEFAULT 'new' -- new, scored, selected, discarded
);

CREATE TABLE IF NOT EXISTS article_scores (
  article_id UUID PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
  rel_building_practices INT,
  rel_market INT,
  rel_design_business INT,
  importance_multiplier REAL,
  freshness_bonus REAL,
  composite_score REAL,
  topics TEXT[], -- PostgreSQL array
  geography TEXT[], -- PostgreSQL array
  macro_flag BOOLEAN,
  summary2 TEXT,
  why1 TEXT,
  project_stage TEXT,        -- v2: approved, breaks_ground, tops_out, opens
  needs_fact_check BOOLEAN DEFAULT FALSE,  -- v2: AI confidence flag
  media_type TEXT DEFAULT 'article'           -- v2: podcast, video, article
);

CREATE TABLE IF NOT EXISTS issues (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  issue_date TIMESTAMPTZ UNIQUE,
  slug TEXT UNIQUE,
  html TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS issue_items (
  issue_id UUID REFERENCES issues(id) ON DELETE CASCADE,
  article_id UUID REFERENCES articles(id) ON DELETE CASCADE,
  rank INT,
  section TEXT,
  PRIMARY KEY (issue_id, article_id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_article_scores_composite ON article_scores(composite_score);
"""

# SQLite schema (fallback)
SQLITE_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS articles (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  url TEXT UNIQUE,
  source TEXT,
  title TEXT,
  summary_raw TEXT,
  content TEXT,
  published_at TEXT,
  fetched_at TEXT DEFAULT (datetime('now')),
  canonical_hash TEXT,
  embedding BLOB,
  lang TEXT,
  paywalled BOOLEAN DEFAULT FALSE,
  status TEXT DEFAULT 'new'
);

CREATE TABLE IF NOT EXISTS article_scores (
  article_id TEXT PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
  rel_building_practices INT,
  rel_market INT,
  rel_design_business INT,
  importance_multiplier REAL,
  freshness_bonus REAL,
  composite_score REAL,
  topics TEXT,
  geography TEXT,
  macro_flag BOOLEAN,
  summary2 TEXT,
  why1 TEXT,
  project_stage TEXT,
  needs_fact_check BOOLEAN DEFAULT FALSE,
  media_type TEXT DEFAULT 'article'
);

CREATE TABLE IF NOT EXISTS issues (
  id TEXT PRIMARY KEY DEFAULT (lower(hex(randomblob(16)))),
  issue_date TEXT UNIQUE,
  slug TEXT UNIQUE,
  html TEXT,
  created_at TEXT DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS issue_items (
  issue_id TEXT REFERENCES issues(id) ON DELETE CASCADE,
  article_id TEXT REFERENCES articles(id) ON DELETE CASCADE,
  rank INT,
  section TEXT,
  PRIMARY KEY (issue_id, article_id)
);

CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_article_scores_composite ON article_scores(composite_score);
"""

def init_db():
    """Initialize database with schema"""
    try:
        with engine.connect() as conn:
            if is_postgres:
                # For PostgreSQL, we can execute the whole script at once
                conn.execute(text(POSTGRES_SCHEMA_SQL))
            else:
                # For SQLite, execute each statement separately
                statements = SQLITE_SCHEMA_SQL.strip().split(';')
                for statement in statements:
                    statement = statement.strip()
                    if statement:
                        conn.execute(text(statement))
            conn.commit()
        print(f"Database initialized successfully ({'PostgreSQL' if is_postgres else 'SQLite'})")
    except Exception as e:
        print(f"Error initializing database: {e}")
        # Don't re-raise if it's just about existing tables/extensions
        if "already exists" not in str(e).lower():
            raise

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on import
init_db()