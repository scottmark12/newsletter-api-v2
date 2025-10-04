# app/config_v3_fix.py
# Quick fix to make v3 work with existing SQLite setup

import os

def get_database_url():
    """Get database URL - force SQLite for compatibility"""
    # Always use SQLite for now to match existing setup
    return "sqlite:///./newsletter.db"  # Use existing database file

def force_sqlite():
    """Force SQLite usage"""
    return True
