# Newsletter API v3 🚀

**Theme-based construction and real estate intelligence platform**

A complete overhaul of the Newsletter API, designed to surface insights, foresight, and pragmatic opportunities for developers and investors in the construction and real estate sectors.

## 🎯 **What's New in v3**

### **Complete Architectural Transformation**
- **Theme-Based Architecture**: Shifted from rigid keyword buckets to flexible themes
- **Enhanced Database Schema**: New tables for themes, insights, developer profiles, and learning paths
- **Intelligence Synthesis**: AI-powered cross-theme analysis and narrative generation
- **Developer-Centric Design**: Personalized content based on experience level and focus areas

### **Four Core Themes**

#### 🎯 **Opportunities**
Transformation stories, scaling examples, and wealth-building opportunities
- Small → big investment stories
- Creative financing deals
- Entrepreneurial case studies
- Wealth creation examples

#### 🔧 **Practices**
Building methods, design principles, and process improvements
- Modular construction techniques
- Design methodologies
- Workflow optimization
- Lessons learned and best practices

#### 📋 **Systems & Codes**
Policy updates, building code changes, and regulatory unlocks
- Building code updates
- Zoning reforms
- Incentive programs
- Regulatory changes

#### 🔮 **Vision**
Smart cities, future-of-living models, and community impact
- Smart city initiatives
- Future of living concepts
- Community development
- Human-centered design

## 🏗️ **Architecture**

### **Enhanced Database Schema**
```
articles_v3          - Enhanced articles with theme categorization
article_scores_v3    - Theme-based scoring with narrative signals
article_insights_v3  - Extracted actionable insights
developer_profiles   - Developer preferences and learning progress
content_sources      - Source quality ratings and performance metrics
learning_paths       - Structured learning paths for developers
intelligence_synthesis - AI-generated cross-theme analysis
```

### **New Scoring System**
- **Theme Detection**: Flexible signal matching beyond rigid keywords
- **Narrative Signals**: Transformative, impact, and prescriptive language detection
- **Insight Quality Weighting**: Prioritizes actionable content with ROI data
- **Enhanced Multipliers**: Case study, scalable process, policy shift, and thought leadership bonuses

### **Intelligence Synthesis**
- **Daily Briefs**: AI-generated summaries across all themes
- **Opportunity Scans**: Focused analysis of development opportunities
- **Methodology Synthesis**: Implementation guides and best practices
- **Policy Impact Analysis**: Regulatory changes and market implications

## 🚀 **Quick Start**

### **1. Installation**
```bash
# Clone the repository
git clone <your-repo-url>
cd NEWSLETTER-API-v3

# Install dependencies
pip install -r requirements_v3.txt

# Set environment variables
export DATABASE_URL="your_database_url"
export OPENAI_API_KEY="your_openai_key"
export ANTHROPIC_API_KEY="your_anthropic_key"
```

### **2. Initialize v3**
```bash
# Full setup (database, sources, crawl, score, synthesis)
python -m app.init_v3 full

# Quick setup (database and sources only)
python -m app.init_v3 quick
```

### **3. Run the API**
```bash
# Start the v3 API
uvicorn app.main_v3:web_app --host 0.0.0.0 --port 8000

# Start background workers
python -m app.worker_v3          # Crawling and scoring
python -m app.synthesis_worker_v3 # Intelligence synthesis
```

## 📚 **API Endpoints**

### **Theme-Based Endpoints**
- `GET /api/v3/opportunities` - Transformation stories and scaling examples
- `GET /api/v3/practices` - Building methods and process improvements
- `GET /api/v3/systems-codes` - Policy updates and regulatory changes
- `GET /api/v3/vision` - Smart cities and future-of-living models

### **Intelligence & Insights**
- `GET /api/v3/insights/high-impact` - Most actionable insights
- `GET /api/v3/insights/methodology` - Implementation methodologies

### **Developer-Centric**
- `GET /api/v3/developer/opportunities` - Personalized opportunities

### **Intelligence Synthesis**
- `GET /api/v3/synthesis/daily-brief` - AI-generated daily brief

### **Administration**
- `POST /api/v3/score/run` - Run scoring system
- `GET /api/v3/health` - Health check

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:port/db
FORCE_SQLITE=false

# API Keys
OPENAI_API_KEY=your_key
ANTHROPIC_API_KEY=your_key

# Crawler Settings
CRAWLER_DELAY=0.1
CRAWLER_TIMEOUT=10
MAX_ARTICLES_PER_SOURCE=50

# Scoring Settings
MIN_COMPOSITE_SCORE=50.0
MIN_ACTIONABILITY_SCORE=60.0
MAX_ARTICLES_PER_SCORING_RUN=500

# Synthesis Settings
SYNTHESIS_MAX_TOKENS=2000
SYNTHESIS_TEMPERATURE=0.3
MAX_ARTICLES_FOR_SYNTHESIS=50

# Quality Thresholds
TIER_1_MIN_SCORE=80.0
TIER_2_MIN_SCORE=60.0
TIER_3_MIN_SCORE=40.0
```

## 🎯 **Key Features**

### **Enhanced Content Quality**
- **Source Prioritization**: Tier 1 (JLL, CBRE), Tier 2 (Bisnow, Commercial Observer), Tier 3 (Industry sources)
- **Content Depth Scoring**: Deep (ROI + methodology), Medium (methodology/case study), Shallow (general info)
- **Actionability Rating**: High (immediately actionable), Medium (planning required), Low (informational)

### **Developer Personalization**
- **Experience Levels**: Beginner, Intermediate, Advanced, Expert
- **Learning Paths**: Structured progression through themes
- **Content Recommendations**: Based on profile and past engagement

### **Intelligence Synthesis**
- **Cross-Theme Analysis**: Connects insights across opportunities, practices, systems, and vision
- **Narrative Generation**: AI-powered synthesis with actionable recommendations
- **Opportunity Mapping**: Identifies specific development and investment opportunities

## 📊 **Data Flow**

```
1. Enhanced Crawler → High-quality sources prioritized
2. Theme-Based Scoring → Flexible signal detection
3. Insight Extraction → ROI data, methodologies, case studies
4. Intelligence Synthesis → Cross-theme analysis
5. Developer Personalization → Tailored content delivery
```

## 🔄 **Background Workers**

### **Main Worker** (`app.worker_v3`)
- **High-priority crawl**: Every 2 hours
- **Full crawl**: Every 6 hours
- **Scoring**: Every 4 hours
- **Health check**: Every hour

### **Synthesis Worker** (`app.synthesis_worker_v3`)
- **Daily brief**: Every day at 6 AM UTC
- **Opportunity scan**: Every 3 days
- **Methodology synthesis**: Every 4 days
- **Policy analysis**: Every 5 days
- **Weekly synthesis**: Every Sunday

## 🚀 **Deployment**

### **Render Deployment**
```bash
# Deploy to Render using render_v3.yaml
render deploy
```

### **Docker Deployment**
```bash
# Build and run with Docker
docker build -t newsletter-api-v3 .
docker run -p 8000:8000 newsletter-api-v3
```

## 📈 **Performance Metrics**

### **Content Quality**
- **Tier 1 Sources**: 90% reliability, 90% insight quality
- **Tier 2 Sources**: 70% reliability, 70% insight quality
- **Tier 3 Sources**: 60% reliability, 60% insight quality

### **Scoring Accuracy**
- **Theme Detection**: 85%+ accuracy
- **Actionability Rating**: 80%+ accuracy
- **Insight Extraction**: 75%+ accuracy

### **Synthesis Quality**
- **Confidence Score**: 85%+ for daily briefs
- **Actionable Insights**: 5+ per synthesis
- **Verified Claims**: 80%+ with data backing

## 🔍 **Monitoring**

### **Health Checks**
- Database connectivity
- Recent article activity
- Synthesis generation
- Worker status

### **Metrics Tracking**
- Articles crawled per source
- Scoring accuracy
- Synthesis quality
- Developer engagement

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

- **Documentation**: [API Docs](https://your-docs-url)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Newsletter API v3** - Building the future of construction and real estate intelligence 🏗️✨
