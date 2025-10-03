from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

# Detect if we're using PostgreSQL or SQLite
is_postgres = DATABASE_URL.startswith('postgresql') or DATABASE_URL.startswith('postgres')

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
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
  published_at TIMESTAMP,
  fetched_at TIMESTAMP DEFAULT NOW(),
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
  topics TEXT, -- JSON string
  geography TEXT, -- JSON string
  macro_flag BOOLEAN,
  summary2 TEXT,
  why1 TEXT,
  project_stage TEXT,        -- v2: approved, breaks_ground, tops_out, opens
  needs_fact_check BOOLEAN DEFAULT FALSE,  -- v2: AI confidence flag
  media_type TEXT DEFAULT 'article'           -- v2: podcast, video, article
);

CREATE TABLE IF NOT EXISTS issues (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  issue_date DATE UNIQUE,
  slug TEXT UNIQUE,
  html TEXT,
  created_at TIMESTAMP DEFAULT NOW()
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