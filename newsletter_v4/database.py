"""
Database utilities for Newsletter API v4
Clean database initialization and management
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import get_config
from .models import Base

def create_database():
    """Create database tables"""
    config = get_config()
    engine = create_engine(config.database.url, echo=config.database.echo)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully")
    return engine

def get_database_session():
    """Get database session"""
    config = get_config()
    engine = create_engine(config.database.url, echo=config.database.echo)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

if __name__ == "__main__":
    create_database()
