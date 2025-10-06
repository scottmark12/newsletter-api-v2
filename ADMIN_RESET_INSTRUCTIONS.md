# Database Reset Instructions - Newsletter API v4

## 🎯 **Purpose**
Reset the database and collect fresh articles using the enhanced narrative-based scoring system for high-value insights and opportunities.

## 🚀 **Quick Reset**

### **Option 1: Run Reset Script**
```bash
python3 reset_database.py
```

This script will:
1. ✅ Clear all existing articles and scores
2. ✅ Collect fresh articles from all 53 RSS feeds
3. ✅ Apply enhanced narrative-based scoring
4. ✅ Store only high-quality, relevant content
5. ✅ Show summary of results

### **Option 2: Manual API Calls**
```bash
# Clear existing articles (if endpoint is available)
curl -X DELETE https://newsletter-api-v2.onrender.com/api/v4/admin/clear-articles

# Collect fresh articles with enhanced scoring
curl -X POST https://newsletter-api-v2.onrender.com/api/v4/admin/collect
```

## 🧠 **Enhanced Scoring System Features**

### **Narrative-Based Analysis**
- **Transformative Language**: "turned into", "grew from", "scaled up"
- **Impact Indicators**: ROI, growth metrics, performance data
- **Prescriptive Insights**: "how to", "framework", "best practices"
- **Opportunity Signals**: "emerging", "untapped", "breakthrough"

### **Quality Filtering**
- **Minimum content length**: 200+ words
- **Quality threshold**: 0.4+ total score
- **Source credibility**: Premium sources weighted higher
- **Actionability**: Practical implementation value

### **Theme Detection**
- **Opportunities**: Wealth creation, scaling stories, market gaps
- **Practices**: Methodologies, innovation, efficiency gains
- **Systems & Codes**: Policy changes, enabling frameworks
- **Vision**: Future trends, smart cities, community development

## 📊 **Expected Results**

### **Before Reset**
- Generic news articles
- Basic keyword matching
- Low relevance filtering
- Mixed quality content

### **After Reset**
- High-value insights and opportunities
- Narrative-based scoring
- Strict relevance filtering
- Actionable content only

## 🔍 **Verification**

After reset, test the enhanced endpoints:

```bash
# High-quality opportunities
curl "https://newsletter-api-v2.onrender.com/api/v4/opportunities?min_score=0.4&limit=5"

# Actionable practices
curl "https://newsletter-api-v2.onrender.com/api/v4/practices?min_score=0.4&limit=5"

# System stats
curl "https://newsletter-api-v2.onrender.com/api/v4/admin/stats"
```

## 🎯 **Success Criteria**

✅ **Content Quality**: Articles focus on insights, not just news
✅ **Relevance**: High transformation potential and actionability
✅ **Scoring**: Enhanced narrative-based analysis
✅ **Filtering**: Only premium, relevant content surfaces
✅ **Ranking**: Best articles appear first based on total score

The platform will now deliver exactly what you want: **actionable insights for staying ahead of the industry** rather than generic news!
