from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SCHEMA_SQL = """
-- SQLite-compatible schema (no UUID extension needed)

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
  status TEXT DEFAULT 'new' -- new, scored, selected, discarded
);

CREATE TABLE IF NOT EXISTS article_scores (
  article_id TEXT PRIMARY KEY REFERENCES articles(id) ON DELETE CASCADE,
  rel_building_practices INT,
  rel_market INT,
  rel_design_business INT,
  importance_multiplier REAL,
  freshness_bonus REAL,
  composite_score REAL,
  topics TEXT, -- JSON string instead of PostgreSQL array
  geography TEXT, -- JSON string instead of PostgreSQL array
  macro_flag BOOLEAN,
  summary2 TEXT,
  why1 TEXT,
  project_stage TEXT,        -- v2: approved, breaks_ground, tops_out, opens
  needs_fact_check BOOLEAN DEFAULT FALSE,  -- v2: AI confidence flag
  media_type TEXT DEFAULT 'article'           -- v2: podcast, video, article
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

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_articles_published_at ON articles(published_at);
CREATE INDEX IF NOT EXISTS idx_articles_status ON articles(status);
CREATE INDEX IF NOT EXISTS idx_article_scores_composite ON article_scores(composite_score);
"""

def init_db():
    """Initialize database with schema"""
    try:
        with engine.connect() as conn:
            # Execute each statement separately for SQLite compatibility
            statements = SCHEMA_SQL.strip().split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    conn.execute(text(statement))
            conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
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