# app/init_v3.py
# V3 Initialization and Setup Script

import sys
import os
from datetime import datetime, timezone
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

from .schema_v3 import Base, init_db_v3
from .config_v3 import get_v3_config, validate_v3_config
from .scoring_v3 import run_scoring_v3
from .crawler_v3 import run_crawler_v3
from .intelligence_v3 import run_all_synthesis_v3

def initialize_v3_database() -> bool:
    """Initialize the v3 database schema"""
    try:
        print("🔧 Initializing Newsletter API v3 Database...")
        
        # Validate configuration
        validation = validate_v3_config()
        if not validation["valid"]:
            print("❌ Configuration validation failed:")
            for category, results in validation["results"].items():
                for check, passed in results.items():
                    status = "✅" if passed else "❌"
                    print(f"  {status} {category}.{check}")
            return False
        
        print("✅ Configuration validation passed")
        
        # Initialize database schema
        init_db_v3()
        print("✅ Database schema initialized")
        
        return True
        
    except Exception as e:
        print(f"❌ Error initializing v3 database: {str(e)}")
        return False

def setup_v3_sources() -> bool:
    """Set up initial content sources"""
    try:
        print("📂 Setting up v3 content sources...")
        
        config = get_v3_config()
        db_engine = create_engine(config.database_url)
        
        # Insert initial source configurations
        with db_engine.connect() as conn:
            # Check if sources already exist
            result = conn.execute(text("SELECT COUNT(*) FROM content_sources")).scalar()
            if result > 0:
                print("✅ Content sources already configured")
                return True
            
            # Insert tier 1 sources
            tier_1_sources = [
                ("jll.com", "JLL", 0.9, 0.9, 0.8, "research", "top_tier", ["opportunities", "practices", "systems_codes"]),
                ("cbre.com", "CBRE", 0.9, 0.9, 0.8, "research", "top_tier", ["opportunities", "practices", "systems_codes"]),
                ("cushmanwakefield.com", "Cushman & Wakefield", 0.9, 0.9, 0.8, "research", "top_tier", ["opportunities", "practices", "systems_codes"]),
                ("colliers.com", "Colliers", 0.8, 0.8, 0.7, "research", "top_tier", ["opportunities", "practices"]),
                ("marcusmillichap.com", "Marcus & Millichap", 0.8, 0.8, 0.7, "research", "top_tier", ["opportunities"])
            ]
            
            for domain, name, reliability, insight_quality, actionability, source_type, institutional_level, themes in tier_1_sources:
                conn.execute(text("""
                    INSERT INTO content_sources (
                        domain, name, reliability_score, insight_quality_score, actionability_score,
                        source_type, institutional_level, primary_themes, is_active
                    ) VALUES (
                        :domain, :name, :reliability, :insight_quality, :actionability,
                        :source_type, :institutional_level, :themes, true
                    )
                """), {
                    "domain": domain,
                    "name": name,
                    "reliability": reliability,
                    "insight_quality": insight_quality,
                    "actionability": actionability,
                    "source_type": source_type,
                    "institutional_level": institutional_level,
                    "themes": themes
                })
            
            # Insert tier 2 sources
            tier_2_sources = [
                ("bisnow.com", "Bisnow", 0.7, 0.7, 0.6, "news", "high", ["opportunities", "market_news"]),
                ("commercialobserver.com", "Commercial Observer", 0.7, 0.7, 0.6, "news", "high", ["opportunities", "market_news"]),
                ("rejournals.com", "Real Estate Journals", 0.7, 0.6, 0.6, "news", "high", ["opportunities"]),
                ("globest.com", "GlobeSt", 0.7, 0.6, 0.6, "news", "high", ["opportunities", "market_news"])
            ]
            
            for domain, name, reliability, insight_quality, actionability, source_type, institutional_level, themes in tier_2_sources:
                conn.execute(text("""
                    INSERT INTO content_sources (
                        domain, name, reliability_score, insight_quality_score, actionability_score,
                        source_type, institutional_level, primary_themes, is_active
                    ) VALUES (
                        :domain, :name, :reliability, :insight_quality, :actionability,
                        :source_type, :institutional_level, :themes, true
                    )
                """), {
                    "domain": domain,
                    "name": name,
                    "reliability": reliability,
                    "insight_quality": insight_quality,
                    "actionability": actionability,
                    "source_type": source_type,
                    "institutional_level": institutional_level,
                    "themes": themes
                })
            
            # Insert tier 3 sources
            tier_3_sources = [
                ("constructiondive.com", "Construction Dive", 0.6, 0.6, 0.5, "industry_news", "medium", ["practices", "vision", "systems_codes"]),
                ("smartcitiesdive.com", "Smart Cities Dive", 0.6, 0.6, 0.5, "industry_news", "medium", ["practices", "vision", "systems_codes"]),
                ("engineeringnewsrecord.com", "Engineering News Record", 0.6, 0.6, 0.5, "industry_news", "medium", ["practices", "systems_codes"]),
                ("architecturalrecord.com", "Architectural Record", 0.6, 0.5, 0.5, "industry_news", "medium", ["practices", "vision"])
            ]
            
            for domain, name, reliability, insight_quality, actionability, source_type, institutional_level, themes in tier_3_sources:
                conn.execute(text("""
                    INSERT INTO content_sources (
                        domain, name, reliability_score, insight_quality_score, actionability_score,
                        source_type, institutional_level, primary_themes, is_active
                    ) VALUES (
                        :domain, :name, :reliability, :insight_quality, :actionability,
                        :source_type, :institutional_level, :themes, true
                    )
                """), {
                    "domain": domain,
                    "name": name,
                    "reliability": reliability,
                    "insight_quality": insight_quality,
                    "actionability": actionability,
                    "source_type": source_type,
                    "institutional_level": institutional_level,
                    "themes": themes
                })
            
            conn.commit()
        
        print("✅ Content sources configured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up v3 sources: {str(e)}")
        return False

def setup_v3_learning_paths() -> bool:
    """Set up initial learning paths"""
    try:
        print("🎓 Setting up v3 learning paths...")
        
        config = get_v3_config()
        db_engine = create_engine(config.database_url)
        
        with db_engine.connect() as conn:
            # Check if learning paths already exist
            result = conn.execute(text("SELECT COUNT(*) FROM learning_paths")).scalar()
            if result > 0:
                print("✅ Learning paths already configured")
                return True
            
            # Insert learning paths
            learning_paths = [
                ("Beginner Developer Path", "Learn the fundamentals of construction and real estate development", "beginner", "3-6 months", "easy", [], [], [], []),
                ("Intermediate Developer Path", "Scale your operations with proven methodologies and best practices", "intermediate", "6-12 months", "medium", [], [], [], []),
                ("Advanced Developer Path", "Identify and capitalize on market opportunities", "advanced", "12+ months", "hard", [], [], [], []),
                ("Expert Developer Path", "Shape industry direction and identify emerging trends", "expert", "Ongoing", "hard", [], [], [], [])
            ]
            
            for name, description, target_audience, estimated_duration, difficulty_level, modules, prerequisites, featured_articles, case_studies in learning_paths:
                conn.execute(text("""
                    INSERT INTO learning_paths (
                        name, description, target_audience, estimated_duration, difficulty_level,
                        modules, prerequisites, featured_articles, case_studies
                    ) VALUES (
                        :name, :description, :target_audience, :estimated_duration, :difficulty_level,
                        :modules, :prerequisites, :featured_articles, :case_studies
                    )
                """), {
                    "name": name,
                    "description": description,
                    "target_audience": target_audience,
                    "estimated_duration": estimated_duration,
                    "difficulty_level": difficulty_level,
                    "modules": modules,
                    "prerequisites": prerequisites,
                    "featured_articles": featured_articles,
                    "case_studies": case_studies
                })
            
            conn.commit()
        
        print("✅ Learning paths configured successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up v3 learning paths: {str(e)}")
        return False

def run_initial_v3_crawl() -> bool:
    """Run initial crawl to populate database"""
    try:
        print("🕷️  Running initial v3 crawl...")
        
        result = run_crawler_v3(limit_per_source=10)  # Small initial crawl
        
        if result["status"] == "success":
            print(f"✅ Initial crawl completed: {result['total_articles_saved']} articles saved")
            return True
        else:
            print(f"❌ Initial crawl failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error running initial crawl: {str(e)}")
        return False

def run_initial_v3_scoring() -> bool:
    """Run initial scoring on crawled articles"""
    try:
        print("📊 Running initial v3 scoring...")
        
        result = run_scoring_v3(limit=100)
        
        if result["status"] == "success":
            print(f"✅ Initial scoring completed: {result['scored_articles']} articles scored")
            return True
        else:
            print(f"❌ Initial scoring failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error running initial scoring: {str(e)}")
        return False

def run_initial_v3_synthesis() -> bool:
    """Run initial intelligence synthesis"""
    try:
        print("🧠 Running initial v3 synthesis...")
        
        result = run_all_synthesis_v3()
        
        if result["status"] == "success":
            print("✅ Initial synthesis completed successfully")
            return True
        else:
            print(f"❌ Initial synthesis failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Error running initial synthesis: {str(e)}")
        return False

def full_v3_setup() -> bool:
    """Run complete v3 setup process"""
    try:
        print("🚀 Starting Newsletter API v3 Full Setup")
        print("=" * 50)
        
        # Step 1: Initialize database
        if not initialize_v3_database():
            return False
        
        # Step 2: Setup sources
        if not setup_v3_sources():
            return False
        
        # Step 3: Setup learning paths
        if not setup_v3_learning_paths():
            return False
        
        # Step 4: Run initial crawl
        if not run_initial_v3_crawl():
            return False
        
        # Step 5: Run initial scoring
        if not run_initial_v3_scoring():
            return False
        
        # Step 6: Run initial synthesis
        if not run_initial_v3_synthesis():
            return False
        
        print("=" * 50)
        print("🎉 Newsletter API v3 Setup Complete!")
        print("\n📋 Setup Summary:")
        print("✅ Database schema initialized")
        print("✅ Content sources configured")
        print("✅ Learning paths created")
        print("✅ Initial articles crawled")
        print("✅ Initial scoring completed")
        print("✅ Initial synthesis generated")
        print("\n🚀 Your v3 API is ready to use!")
        print("\n📚 Available endpoints:")
        print("  - /api/v3/opportunities")
        print("  - /api/v3/practices")
        print("  - /api/v3/systems-codes")
        print("  - /api/v3/vision")
        print("  - /api/v3/insights/high-impact")
        print("  - /api/v3/developer/opportunities")
        print("  - /api/v3/synthesis/daily-brief")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in full v3 setup: {str(e)}")
        return False

def quick_v3_setup() -> bool:
    """Run quick v3 setup (database and sources only)"""
    try:
        print("⚡ Starting Newsletter API v3 Quick Setup")
        print("=" * 40)
        
        # Step 1: Initialize database
        if not initialize_v3_database():
            return False
        
        # Step 2: Setup sources
        if not setup_v3_sources():
            return False
        
        # Step 3: Setup learning paths
        if not setup_v3_learning_paths():
            return False
        
        print("=" * 40)
        print("✅ Newsletter API v3 Quick Setup Complete!")
        print("\n📋 Setup Summary:")
        print("✅ Database schema initialized")
        print("✅ Content sources configured")
        print("✅ Learning paths created")
        print("\n🚀 Ready for crawling and scoring!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in quick v3 setup: {str(e)}")
        return False

if __name__ == "__main__":
    """Command line interface for v3 setup"""
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "full":
            success = full_v3_setup()
        elif command == "quick":
            success = quick_v3_setup()
        elif command == "database":
            success = initialize_v3_database()
        elif command == "sources":
            success = setup_v3_sources()
        elif command == "crawl":
            success = run_initial_v3_crawl()
        elif command == "score":
            success = run_initial_v3_scoring()
        elif command == "synthesis":
            success = run_initial_v3_synthesis()
        else:
            print("❌ Unknown command. Available commands:")
            print("  full      - Complete setup (database, sources, crawl, score, synthesis)")
            print("  quick     - Quick setup (database, sources, learning paths)")
            print("  database  - Initialize database schema only")
            print("  sources   - Setup content sources only")
            print("  crawl     - Run initial crawl only")
            print("  score     - Run initial scoring only")
            print("  synthesis - Run initial synthesis only")
            success = False
    else:
        print("🚀 Newsletter API v3 Setup")
        print("Usage: python -m app.init_v3 [command]")
        print("\nAvailable commands:")
        print("  full      - Complete setup")
        print("  quick     - Quick setup")
        print("  database  - Database only")
        print("  sources   - Sources only")
        print("  crawl     - Crawl only")
        print("  score     - Score only")
        print("  synthesis - Synthesis only")
        success = False
    
    sys.exit(0 if success else 1)
