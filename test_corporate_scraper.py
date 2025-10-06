"""
Test corporate scraper to see which sites work
"""
import asyncio
import aiohttp
from newsletter_v4.corporate_scraper import CorporateInsightsScraper

async def test_corporate_sites():
    """Test which corporate sites are accessible"""
    async with CorporateInsightsScraper() as scraper:
        print("Testing corporate sites accessibility...")
        print("=" * 60)
        
        working_sites = []
        blocked_sites = []
        
        for source in scraper.corporate_sources[:10]:  # Test first 10 sites
            try:
                print(f"Testing {source.name}: {source.insights_url}")
                
                async with scraper.session.get(source.insights_url) as response:
                    print(f"   Status: {response.status}")
                    
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Check for common anti-bot indicators
                        if any(indicator in html.lower() for indicator in [
                            'access denied', 'blocked', 'bot detection', 
                            'cloudflare', 'recaptcha', 'captcha'
                        ]):
                            print(f"   ⚠️  Anti-bot protection detected")
                            blocked_sites.append(source.name)
                        else:
                            print(f"   ✅ Accessible")
                            working_sites.append(source.name)
                    else:
                        print(f"   ❌ Blocked (HTTP {response.status})")
                        blocked_sites.append(source.name)
                        
            except Exception as e:
                print(f"   ❌ Error: {e}")
                blocked_sites.append(source.name)
            
            await asyncio.sleep(2)  # Rate limiting
        
        print("\n" + "=" * 60)
        print("RESULTS:")
        print(f"✅ Working sites ({len(working_sites)}): {', '.join(working_sites)}")
        print(f"❌ Blocked sites ({len(blocked_sites)}): {', '.join(blocked_sites)}")

if __name__ == "__main__":
    from bs4 import BeautifulSoup
    asyncio.run(test_corporate_sites())
