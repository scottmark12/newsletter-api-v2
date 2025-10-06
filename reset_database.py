#!/usr/bin/env python3
"""
Database Reset Script for Newsletter API v4
Clears all articles and scores to start fresh with enhanced scoring
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from newsletter_v4.database import create_database_engine, get_session_maker, create_tables
from newsletter_v4.models import Article, ArticleScore, ArticleInsight
from newsletter_v4.data_collectors import collect_all_articles
from newsletter_v4.enhanced_scoring import score_article_enhanced
from newsletter_v4.config import get_config
import json

async def reset_database():
    """Reset the database and collect fresh articles with enhanced scoring"""
    
    print("🔄 Starting database reset and fresh data collection...")
    print("=" * 60)
    
    # Initialize database
    config = get_config()
    engine = create_database_engine(config.database.url)
    SessionLocal = get_session_maker(engine)
    
    # Create tables
    create_tables(engine)
    print("✅ Database tables created/verified")
    
    # Clear existing data
    print("🗑️  Clearing existing articles and scores...")
    db = SessionLocal()
    
    try:
        # Delete in correct order due to foreign key constraints
        deleted_insights = db.query(ArticleInsight).delete()
        deleted_scores = db.query(ArticleScore).delete()
        deleted_articles = db.query(Article).delete()
        
        db.commit()
        print(f"   Deleted {deleted_insights} insights, {deleted_scores} scores, {deleted_articles} articles")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")
        db.rollback()
        return
    finally:
        db.close()
    
    # Collect fresh articles
    print("📡 Collecting fresh articles from all sources...")
    try:
        articles = await collect_all_articles()
        print(f"✅ Collected {len(articles)} articles from all sources")
        
        if not articles:
            print("⚠️  No articles collected. Check your RSS feeds and network connection.")
            return
            
    except Exception as e:
        print(f"❌ Error collecting articles: {e}")
        return
    
    # Store articles with enhanced scoring
    print("🧠 Processing articles with enhanced scoring system...")
    db = SessionLocal()
    stored_count = 0
    
    try:
        for i, article_data in enumerate(articles):
            try:
                # Check if article already exists (shouldn't happen after clear, but safety check)
                existing = db.query(Article).filter(Article.url == article_data.url).first()
                if existing:
                    continue
                
                # Create new article
                article = Article(
                    title=article_data.title,
                    url=article_data.url,
                    content=article_data.content or "",
                    summary=article_data.summary or "",
                    source=article_data.source,
                    author=article_data.author,
                    published_at=article_data.published_at,
                    word_count=len((article_data.content or "").split()),
                    reading_time=len((article_data.content or "").split()) // 200,
                    themes=json.dumps(getattr(article_data, 'tags', []) or [])
                )
                
                db.add(article)
                db.flush()  # Get the ID
                
                # Score with enhanced system
                scoring_result = score_article_enhanced(
                    article_data.title,
                    article_data.content or "",
                    article_data.source,
                    article_data.url
                )
                
                # Store enhanced score
                score = ArticleScore(
                    article_id=article.id,
                    total_score=scoring_result.total_score,
                    opportunities_score=scoring_result.theme_scores.get('opportunities', 0),
                    practices_score=scoring_result.theme_scores.get('practices', 0),
                    systems_score=scoring_result.theme_scores.get('systems_codes', 0),
                    vision_score=scoring_result.theme_scores.get('vision', 0),
                    insight_quality_score=scoring_result.insight_quality,
                    narrative_signal_score=sum(scoring_result.narrative_signals.values()) / len(scoring_result.narrative_signals),
                    source_credibility_score=scoring_result.details.get('source_credibility', 0.5),
                    scoring_details=json.dumps(scoring_result.details)
                )
                
                db.add(score)
                stored_count += 1
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"   Processed {i + 1}/{len(articles)} articles...")
                    
            except Exception as e:
                print(f"   ⚠️  Error processing article '{article_data.title[:50]}...': {e}")
                continue
        
        db.commit()
        print(f"✅ Successfully stored and scored {stored_count} articles")
        
    except Exception as e:
        print(f"❌ Error storing articles: {e}")
        db.rollback()
        return
    finally:
        db.close()
    
    # Show summary
    print("\n" + "=" * 60)
    print("🎉 Database reset and fresh collection complete!")
    print(f"📊 Total articles: {stored_count}")
    print("🧠 Enhanced scoring system applied")
    print("🔍 High-relevance filtering active")
    print("=" * 60)
    
    # Show sample of high-scoring articles
    db = SessionLocal()
    try:
        high_score_articles = db.query(Article, ArticleScore).join(
            ArticleScore, Article.id == ArticleScore.article_id
        ).filter(
            ArticleScore.total_score >= 0.6
        ).order_by(
            ArticleScore.total_score.desc()
        ).limit(5).all()
        
        if high_score_articles:
            print("\n🏆 Top 5 High-Scoring Articles:")
            for article, score in high_score_articles:
                print(f"   • {article.title[:80]}... (Score: {score.total_score:.3f})")
                
    except Exception as e:
        print(f"⚠️  Could not fetch sample articles: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(reset_database())
