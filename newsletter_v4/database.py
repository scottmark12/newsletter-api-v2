"""
Database utilities for Newsletter API v4
PostgreSQL-compatible database operations
"""

import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from .config import get_config

def get_database_url():
    """Get the database URL from environment or config"""
    config = get_config()
    return config.database.url

def create_database_engine():
    """Create database engine with PostgreSQL support"""
    url = get_database_url()
    
    # PostgreSQL-specific engine configuration
    if url.startswith('postgresql'):
        engine = create_engine(
            url,
            echo=False,
            pool_pre_ping=True,
            pool_recycle=300,
            connect_args={
                "options": "-c timezone=utc"
            }
        )
    else:
        # SQLite fallback
        engine = create_engine(url, echo=False)
    
    return engine

def get_session_maker():
    """Get session maker for database operations"""
    engine = create_database_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_database_connection():
    """Test database connection"""
    try:
        engine = create_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        print(f"Database connection error: {e}")
        return False

def create_tables():
    """Create all database tables"""
    try:
        from .models import Base
        engine = create_database_engine()
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False