# Newsletter API v4 - Intelligent Construction Platform

## 🚀 Overview

Newsletter API v4 is a complete rewrite and modernization of the construction intelligence platform. It features a clean, modular architecture with video support, AI-powered scoring, and comprehensive data collection from multiple sources.

## ✨ Key Features

### 🎯 Core Functionality
- **RSS Feed Collection** - Automated collection from construction and real estate RSS feeds
- **Google Custom Search** - Intelligent search for relevant articles using Google's API
- **YouTube Video Analysis** - Extract and score video content from construction channels
- **Web Scraping** - Advanced content extraction using trafilatura
- **AI-Powered Scoring** - Flexible, configurable scoring system with easy adjustment
- **Theme-Based Categorization** - Four core themes: Opportunities, Practices, Systems & Codes, Vision

### 🎥 Video Support
- **YouTube Integration** - Automatic video discovery and processing
- **Transcript Analysis** - Extract and analyze video transcripts
- **Video Scoring** - Apply the same scoring system to video content
- **Featured Videos** - Best videos displayed on homepage and theme pages

### 🧠 Intelligent Features
- **Flexible Scoring System** - Easily adjustable weights and multipliers
- **Narrative Signal Detection** - Identify transformative, impact, and prescriptive language
- **Quality Indicators** - Detect ROI data, methodologies, and case studies
- **Insight Extraction** - Automatically extract actionable insights
- **Source Quality Tiers** - Tier-based source reliability scoring

### 🌐 Modern Web Interface
- **Responsive Design** - Beautiful, modern UI that works on all devices
- **Real-time Updates** - Live scoring and content updates
- **Video Integration** - Featured videos with thumbnails and metadata
- **Theme Navigation** - Easy navigation between content categories
- **Score Visualization** - Visual representation of article and video scores

## 🏗️ Architecture

### Clean Separation of Concerns
```
app_v4/
├── config.py          # Environment-based configuration
├── models.py          # SQLAlchemy database models
├── scoring.py         # Flexible scoring engine
├── data_collectors.py # RSS, Google, web scraping
├── video_processor.py # YouTube video processing
├── api.py            # FastAPI endpoints
├── worker.py         # Background data collection
├── video_worker.py   # Background video processing
└── init_db.py        # Database initialization
```

### Five Main API Endpoints
1. **`/api/v4/home`** - Homepage with theme overview and featured video
2. **`/api/v4/top-stories`** - Highest scoring articles across all themes
3. **`/api/v4/opportunities`** - Transformation stories and wealth-building examples
4. **`/api/v4/practices`** - Building methods and process improvements
5. **`/api/v4/systems-codes`** - Policy updates and regulatory changes
6. **`/api/v4/vision`** - Smart cities and future-of-living models

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**
   ```bash
   pip install -r requirements_v4.txt
   ```

2. **Set Environment Variables**
   ```bash
   export DATABASE_URL="sqlite:///./newsletter_v4.db"
   export ENVIRONMENT="development"
   export ENABLE_VIDEO_SUPPORT="true"
   ```

3. **Initialize Database**
   ```bash
   python -m app_v4.init_db
   ```

4. **Start API Server**
   ```bash
   python -m uvicorn app_v4.api:app --reload --host 0.0.0.0 --port 8000
   ```

5. **Start Background Worker** (in another terminal)
   ```bash
   python -m app_v4.worker
   ```

6. **Start Website** (in another terminal)
   ```bash
   cd website_v4
   python server.py
   ```

### Access the Platform
- **API Documentation**: http://localhost:8000/docs
- **Website**: http://localhost:8082
- **API Base**: http://localhost:8000

## 🔧 Configuration

### Environment Variables

#### Core Configuration
- `DATABASE_URL` - Database connection string
- `ENVIRONMENT` - development/staging/production
- `ENABLE_VIDEO_SUPPORT` - Enable/disable video processing
- `ENABLE_AI_SYNTHESIS` - Enable/disable AI synthesis features

#### Scoring Configuration
- `MIN_COMPOSITE_SCORE` - Minimum score threshold (default: 50.0)
- `MIN_ACTIONABILITY_SCORE` - Minimum actionability score (default: 60.0)
- `ROI_BONUS` - ROI data multiplier (default: 1.5)
- `METHODOLOGY_BONUS` - Methodology multiplier (default: 1.4)
- `CASE_STUDY_BONUS` - Case study multiplier (default: 1.6)

#### Data Collection
- `CRAWLER_DELAY` - Delay between requests (default: 0.1s)
- `CRAWLER_TIMEOUT` - Request timeout (default: 10s)
- `MAX_ARTICLES_PER_SOURCE` - Max articles per source (default: 50)
- `REQUESTS_PER_MINUTE` - Rate limiting (default: 60)

#### API Keys (Optional)
- `GOOGLE_API_KEY` - Google Custom Search API key
- `GOOGLE_CSE_ID` - Google Custom Search Engine ID
- `YOUTUBE_API_KEY` - YouTube Data API key
- `OPENAI_API_KEY` - OpenAI API key for AI features

## 📊 Scoring System

### Theme Detection
The scoring system uses keyword-based theme detection with configurable weights:
- **Opportunities** (1.2x weight) - Transformation stories, scaling examples
- **Practices** (1.0x weight) - Building methods, process improvements
- **Systems & Codes** (1.1x weight) - Policy updates, regulatory changes
- **Vision** (0.9x weight) - Smart cities, future-of-living models

### Narrative Signals
- **Transformative Language** (1.4x bonus) - "grew from", "scaled up", "transformed"
- **Impact Language** (1.5x bonus) - "ROI", "reduced costs", "performance data"
- **Prescriptive Language** (1.3x bonus) - "methodology", "framework", "how-to"

### Quality Indicators
- **ROI Data Present** (1.5x bonus) - Financial performance metrics
- **Methodology Present** (1.4x bonus) - Implementation processes
- **Case Study Present** (1.6x bonus) - Success stories and examples
- **Performance Metrics** (1.2x bonus) - Measurable outcomes

### Source Quality Tiers
- **Tier 1** (1.5x bonus) - Premium sources (JLL, CBRE, McKinsey)
- **Tier 2** (1.3x bonus) - High quality (Bisnow, Commercial Observer)
- **Tier 3** (1.2x bonus) - Standard sources (Construction Dive, ENR)

## 🎥 Video Processing

### YouTube Integration
- **Channel Monitoring** - Track specific construction channels
- **Video Discovery** - Find relevant videos using keywords
- **Transcript Extraction** - Get video transcripts when available
- **Content Analysis** - Apply same scoring system to video content
- **Article Creation** - Convert high-quality videos to articles

### Video Scoring Factors
- **Content Quality** - Transcript and description analysis
- **Engagement Metrics** - View count, like ratio
- **Duration Bonus** - Longer videos often have more depth
- **Transcript Availability** - Bonus for videos with transcripts

## 🌐 Web Interface

### Modern Design
- **Responsive Layout** - Works on desktop, tablet, and mobile
- **Glass Morphism** - Modern UI with backdrop blur effects
- **Smooth Animations** - Fade-in effects and hover animations
- **Theme-Based Colors** - Each theme has its own color scheme

### Features
- **Homepage Overview** - Theme cards with article counts
- **Featured Video** - Best video displayed prominently
- **Article Cards** - Rich article display with scores and insights
- **Navigation** - Easy switching between themes and top stories
- **Real-time Updates** - Live data from the API

## 🚀 Deployment

### Render Deployment

The platform is configured for easy deployment on Render:

1. **Connect Repository** - Connect your GitHub repository to Render
2. **Set Environment Variables** - Add API keys and configuration
3. **Deploy Services** - Deploy API, workers, and website
4. **Configure Database** - Set up PostgreSQL database

### Services
- **Main API** - FastAPI application with auto-scaling
- **Background Worker** - Data collection and scoring
- **Video Worker** - Video processing and analysis
- **Website** - Static site serving the web interface
- **Database** - PostgreSQL with automated backups

## 📈 Performance

### Optimizations
- **Database Indexing** - Optimized queries with proper indexes
- **Connection Pooling** - Efficient database connections
- **Rate Limiting** - Respectful API usage
- **Caching** - Redis caching for frequently accessed data
- **Background Processing** - Non-blocking data collection

### Monitoring
- **Health Checks** - Built-in health monitoring
- **Logging** - Comprehensive logging with structured logs
- **Metrics** - Performance and usage metrics
- **Error Tracking** - Automatic error reporting

## 🔮 Future Enhancements

### Phase 2: Advanced AI
- **Machine Learning Scoring** - ML-based content scoring
- **Sentiment Analysis** - Content sentiment and tone analysis
- **Topic Modeling** - Automatic topic discovery
- **Recommendation Engine** - Personalized content recommendations

### Phase 3: Community Features
- **User Profiles** - Developer and investor profiles
- **Social Features** - Comments, likes, and sharing
- **Expert Q&A** - Direct access to industry experts
- **Collaboration Tools** - Team features and project sharing

### Phase 4: Integration Ecosystem
- **CRM Integration** - Connect with Salesforce, HubSpot
- **Project Management** - Integrate with Asana, Monday.com
- **Financial Modeling** - Connect with Excel, Google Sheets
- **Market Data** - Real-time market feeds and analytics

## 📚 API Documentation

### Main Endpoints

#### Homepage Data
```http
GET /api/v4/home?include_videos=true&limit=10
```

#### Top Stories
```http
GET /api/v4/top-stories?min_score=70&include_insights=true
```

#### Theme Articles
```http
GET /api/v4/opportunities?days=7&min_score=50&include_videos=true
GET /api/v4/practices?days=7&min_score=50&include_videos=true
GET /api/v4/systems-codes?days=7&min_score=50&include_videos=true
GET /api/v4/vision?days=7&min_score=50&include_videos=true
```

#### Admin Endpoints
```http
POST /api/v4/admin/collect      # Trigger data collection
POST /api/v4/admin/score        # Run scoring
POST /api/v4/admin/process-videos # Process videos
GET  /api/v4/health            # Health check
```

### Response Format
```json
{
  "ok": true,
  "endpoint": "homepage",
  "last_updated": "2024-01-15T10:30:00Z",
  "stats": {
    "total_articles": 1250,
    "high_quality_articles": 340,
    "video_content": {
      "total_videos": 150,
      "processed_videos": 120
    }
  },
  "themes": {
    "opportunities": {
      "theme": {...},
      "articles": [...],
      "count": 45
    }
  },
  "featured_video": {
    "video_id": "abc123",
    "title": "Construction Innovation 2024",
    "video_url": "https://youtube.com/watch?v=abc123",
    "actionability_score": 85.5,
    "insight_quality": 78.2
  }
}
```

## 🛠️ Development

### Adding New Data Sources

1. **Create Collector Class**
   ```python
   class NewSourceCollector:
       async def collect_articles(self) -> List[Dict[str, Any]]:
           # Implementation
   ```

2. **Add to Orchestrator**
   ```python
   # In data_collectors.py
   async def collect_all_data(self):
       # Add new collector
   ```

3. **Update Configuration**
   ```python
   # In config.py
   new_source_urls: List[str] = [...]
   ```

### Customizing Scoring

1. **Adjust Theme Weights**
   ```python
   # In config.py
   theme_weights = {
       "opportunities": 1.3,  # Increase weight
       "practices": 1.0,
       "systems_codes": 1.1,
       "vision": 0.8  # Decrease weight
   }
   ```

2. **Add New Keywords**
   ```python
   # In config.py
   THEMES["opportunities"]["keywords"].append("new_keyword")
   ```

3. **Modify Multipliers**
   ```python
   # In config.py
   roi_bonus = 1.8  # Increase ROI bonus
   methodology_bonus = 1.2  # Decrease methodology bonus
   ```

## 📞 Support

For questions, issues, or contributions:

1. **Check Documentation** - Review this README and API docs
2. **GitHub Issues** - Report bugs and request features
3. **Discussions** - Ask questions and share ideas
4. **Pull Requests** - Contribute improvements

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Newsletter API v4** - Building the future of construction intelligence, one article at a time. 🏗️✨
