# 🚀 Newsletter API v4

A completely fresh, modern newsletter platform for construction and real estate intelligence.

## ✨ Features

### 🎯 **Intelligent Categorization**
- **Opportunities**: Market growth, investments, emerging trends
- **Practices**: Best practices, technology, methodologies  
- **Systems & Codes**: Infrastructure, regulations, compliance
- **Vision**: Future trends, strategy, industry outlook

### 🧠 **Smart Scoring System**
- Theme-based content analysis
- Insight quality assessment
- Narrative signal detection
- Source credibility evaluation
- Configurable scoring weights

### 📊 **Data Sources**
- RSS feed aggregation
- Google Custom Search integration
- Web scraping and crawling
- YouTube video processing

### 🎥 **Video Integration**
- YouTube transcript extraction
- Video content scoring
- Featured video on homepage
- Construction-specific video discovery

## 🏗️ Architecture

### Clean Module Structure
```
newsletter_v4/
├── __init__.py          # Package initialization
├── config.py            # Configuration management
├── models.py            # Database models
├── scoring.py           # Intelligent scoring system
├── data_collectors.py   # Data collection modules
├── video_processor.py   # Video processing
├── api.py              # FastAPI application
└── database.py         # Database utilities
```

### Modern Tech Stack
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Advanced ORM with async support
- **Pydantic** - Data validation and settings
- **aiohttp** - Async HTTP client
- **BeautifulSoup** - Web scraping
- **feedparser** - RSS feed processing

## 🚀 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Configuration
Set environment variables:
```bash
# Optional: Google Search API
export GOOGLE_API_KEY="your_google_api_key"
export GOOGLE_CSE_ID="your_custom_search_engine_id"

# Optional: YouTube API
export YOUTUBE_API_KEY="your_youtube_api_key"

# Optional: Database (defaults to SQLite)
export DATABASE_URL="postgresql://user:pass@host:port/db"
```

### 3. Initialize Database
```bash
python -c "from newsletter_v4.database import create_database; create_database()"
```

### 4. Run Application
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Theme Categories
- `GET /api/v4/opportunities` - Opportunities articles
- `GET /api/v4/practices` - Practices articles  
- `GET /api/v4/systems-codes` - Systems & Codes articles
- `GET /api/v4/vision` - Vision articles

### Main Endpoints
- `GET /api/v4/home` - Homepage with featured content
- `GET /api/v4/top-stories` - Top stories across categories

### Intelligence
- `GET /api/v4/insights/high-impact` - High-impact insights
- `GET /api/v4/insights/methodology` - Methodology insights
- `GET /api/v4/synthesis/daily-brief` - AI daily brief

### Developer
- `GET /api/v4/developer/opportunities` - Tech opportunities

### Admin
- `POST /api/v4/admin/collect` - Collect articles
- `POST /api/v4/admin/score` - Run scoring
- `POST /api/v4/admin/process-videos` - Process videos
- `GET /api/v4/admin/stats` - System statistics

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /website` - Web interface

## 🎯 Scoring System

### Theme Detection
Automatically categorizes content into 4 themes using pattern matching:
- **Opportunities**: Investment, growth, expansion keywords
- **Practices**: Technology, methodology, process keywords  
- **Systems**: Infrastructure, regulation, compliance keywords
- **Vision**: Future, strategy, innovation keywords

### Quality Factors
- **Insight Quality**: Depth of analysis and evidence
- **Narrative Signal**: Storytelling and coherence
- **Source Credibility**: Authority and reputation

### Configurable Weights
All scoring parameters can be adjusted via environment variables:
```bash
OPPORTUNITIES_WEIGHT=1.0
PRACTICES_WEIGHT=1.2
SYSTEMS_WEIGHT=0.8
VISION_WEIGHT=1.1
INSIGHT_QUALITY_WEIGHT=1.5
NARRATIVE_SIGNAL_WEIGHT=1.2
```

## 🔧 Development

### Running Tests
```bash
# Test scoring system
python -c "from newsletter_v4.scoring import score_article_v4; print(score_article_v4('Construction Innovation', 'New technology in construction...', 'ENR', 'https://enr.com'))"

# Test data collection
python -c "import asyncio; from newsletter_v4.data_collectors import collect_rss_articles; print(asyncio.run(collect_rss_articles()))"
```

### Database Management
```bash
# Initialize database
python -c "from newsletter_v4.database import create_database; create_database()"

# View stats
curl http://localhost:8000/api/v4/admin/stats
```

## 🚀 Deployment

### Render.com
1. Push code to GitHub
2. Connect repository to Render
3. Use provided `render.yaml` configuration
4. Set environment variables in Render dashboard

### Docker (Optional)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
```

## 📊 Monitoring

### Health Checks
- `GET /health` - Basic health status
- `GET /api/v4/admin/stats` - Detailed statistics

### Metrics
- Total articles collected
- Scoring coverage percentage
- Recent activity (24h)
- Video processing status

## 🔮 Future Enhancements

- [ ] AI-powered content summarization
- [ ] Advanced video transcript analysis
- [ ] Real-time notifications
- [ ] Mobile app integration
- [ ] Advanced analytics dashboard
- [ ] Multi-language support

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built with ❤️ for the construction and real estate industry**# Force deployment update
# Force rebuild Mon Oct  6 14:46:49 EDT 2025
# Test deployment
