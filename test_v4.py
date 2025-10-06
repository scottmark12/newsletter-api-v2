"""
Test script for Newsletter API v4
Tests core functionality without external dependencies
"""

def test_imports():
    """Test that all modules can be imported"""
    try:
        from newsletter_v4.config import get_config
        print("✅ Config module imported successfully")
        
        from newsletter_v4.models import Article, ArticleScore
        print("✅ Models module imported successfully")
        
        from newsletter_v4.scoring import score_article_v4
        print("✅ Scoring module imported successfully")
        
        config = get_config()
        print(f"✅ Config loaded: {config.api.title}")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_scoring():
    """Test the scoring system"""
    try:
        from newsletter_v4.scoring import score_article_v4
        
        # Test article scoring
        result = score_article_v4(
            title="Construction Technology Innovation in 2024",
            content="New AI-powered construction management systems are revolutionizing the industry with advanced automation and data analytics capabilities.",
            source="Construction Dive",
            url="https://constructiondive.com/news/ai-construction-2024"
        )
        
        print(f"✅ Scoring test passed")
        print(f"   Total Score: {result.total_score:.2f}")
        print(f"   Theme Scores: {result.theme_scores}")
        print(f"   Insight Quality: {result.insight_quality:.2f}")
        
        return True
    except Exception as e:
        print(f"❌ Scoring test failed: {e}")
        return False

def test_config():
    """Test configuration system"""
    try:
        from newsletter_v4.config import get_config
        
        config = get_config()
        
        print(f"✅ Configuration test passed")
        print(f"   API Title: {config.api.title}")
        print(f"   Database URL: {config.database.url}")
        print(f"   Opportunities Weight: {config.scoring.opportunities_weight}")
        print(f"   RSS Feeds Count: {len(config.data_sources.rss_feeds)}")
        
        return True
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Newsletter API v4 Core Functionality\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Configuration Test", test_config),
        ("Scoring Test", test_scoring),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
        print()
    
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Newsletter API v4 is ready for deployment.")
    else:
        print("⚠️  Some tests failed. Please review the errors above.")
