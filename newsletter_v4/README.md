# Newsletter API v4

A clean, modern, and intelligent newsletter platform for construction and real estate professionals. This v4 platform provides comprehensive article scoring, video processing, and an accessible web interface.

## 🚀 Features

### Core Functionality
- **Intelligent Scoring System**: Advanced theme detection with comprehensive keyword sets
- **Multi-Source Data Collection**: RSS feeds, Google search, and web scraping
- **Video Processing**: YouTube integration with transcript analysis and scoring
- **Modern Web Interface**: Responsive design with 4 theme categories
- **Admin Dashboard**: Real-time scoring visualization and configuration management

### Theme Categories
1. **Opportunities** - Market growth, investments, and emerging trends
2. **Practices** - Best practices, technology, and methodologies  
3. **Systems & Codes** - Infrastructure, regulations, and compliance
4. **Vision** - Smart cities, future trends, and transformative insights

### API Endpoints

#### Main Content
- `GET /api/v4/home` - Homepage with featured content and video
- `GET /api/v4/top-stories` - Top stories across all categories
- `GET /api/v4/opportunities` - Opportunities category articles
- `GET /api/v4/practices` - Practices category articles
- `GET /api/v4/systems-codes` - Systems & Codes category articles
- `GET /api/v4/vision` - Vision category articles

#### Intelligence & Insights
- `GET /api/v4/insights/high-impact` - High-impact insights
- `GET /api/v4/insights/methodology` - Methodology insights
- `GET /api/v4/synthesis/daily-brief` - AI-synthesized daily brief

#### Admin & Management
- `POST /api/v4/admin/collect` - Collect articles from all sources
- `POST /api/v4/admin/score` - Run scoring on articles
- `POST /api/v4/admin/process-videos` - Process YouTube videos
- `GET /api/v4/admin/stats` - System statistics

#### Web Interfaces
- `GET /website` - Main website interface
- `GET /dashboard` - Admin scoring dashboard

## 🛠️ Installation

### Prerequisites
- Python 3.9+
- SQLite or PostgreSQL database

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd newsletter-api-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (optional)
   ```bash
   export GOOGLE_API_KEY="your-google-api-key"
   export GOOGLE_CSE_ID="your-custom-search-engine-id"
   export YOUTUBE_API_KEY="your-youtube-api-key"
   export DATABASE_URL="sqlite:///./newsletter_v4.db"
   ```

4. **Run the application**
   ```bash
   python newsletter_v4/main.py
   ```

## 📊 Scoring System

The v4 scoring system uses comprehensive keyword sets and configurable weights to score articles across four themes:

### Theme Detection
- **Keyword Matching**: 200+ keywords per theme category
- **Weighted Scoring**: Multi-word phrases weighted more heavily
- **Density Analysis**: Content density and keyword frequency analysis
- **Normalization**: Scores normalized to 0-1 range

### Quality Factors
- **Insight Quality**: Analysis of research indicators and data-driven content
- **Narrative Signal**: Storytelling quality and narrative structure
- **Source Credibility**: Premium and institutional source bonuses

### Configuration
Scoring parameters can be adjusted through:
- Environment variables
- Admin dashboard interface
- Configuration API endpoints

## 🎥 Video Processing

### YouTube Integration
- **Metadata Extraction**: Title, channel, duration, view count
- **Transcript Analysis**: Automatic transcript extraction and scoring
- **Content Scoring**: Relevance and quality assessment
- **Featured Video**: Top-scoring video displayed on homepage

### Video Scoring
- **Content Relevance**: Theme-based content analysis
- **Engagement Metrics**: View count and duration scoring
- **Channel Authority**: Construction/real estate channel recognition

## 🌐 Web Interface

### Main Website (`/website`)
- **Responsive Design**: Mobile-first approach
- **Theme Navigation**: Easy switching between categories
- **Featured Content**: Top articles and videos
- **Real-time Data**: Live API integration

### Admin Dashboard (`/dashboard`)
- **Scoring Visualization**: Real-time score monitoring
- **Configuration Management**: Easy parameter adjustment
- **Data Collection Control**: Manual collection triggers
- **System Statistics**: Performance and usage metrics

## 📡 Data Sources

### RSS Feeds (50+ sources)
- Construction Dive, ENR, Commercial Observer
- ArchDaily, Dezeen, Smart Cities Dive
- Real Estate publications and industry blogs
- Government and institutional sources

### Google Custom Search
- Recent article discovery (last 7 days)
- Site-specific searches on premium sources
- Construction and real estate queries

### Web Scraping
- Direct article extraction
- Content parsing and metadata extraction
- Error handling and rate limiting

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=sqlite:///./newsletter_v4.db
DATABASE_ECHO=false

# API Configuration
DEBUG=false
PORT=8000

# Scoring Weights
OPPORTUNITIES_WEIGHT=1.0
PRACTICES_WEIGHT=1.0
SYSTEMS_WEIGHT=1.0
VISION_WEIGHT=1.0
INSIGHT_QUALITY_WEIGHT=1.5
NARRATIVE_SIGNAL_WEIGHT=1.2
INSTITUTIONAL_BONUS=1.3
PREMIUM_BONUS=1.2

# Data Sources
GOOGLE_API_KEY=your-key
GOOGLE_CSE_ID=your-search-engine-id
YOUTUBE_API_KEY=your-youtube-key
MAX_ARTICLES_PER_SOURCE=50
REQUEST_DELAY=1.0
```

## 🚀 Deployment

### Local Development
```bash
python newsletter_v4/main.py
```

### Production Deployment
```bash
# Using uvicorn directly
uvicorn newsletter_v4.api:app --host 0.0.0.0 --port 8000

# With gunicorn
gunicorn newsletter_v4.api:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "newsletter_v4/main.py"]
```

## 📈 Performance

### Optimizations
- **Async Operations**: Non-blocking data collection
- **Connection Pooling**: Efficient database connections
- **Caching**: In-memory caching for frequent queries
- **Rate Limiting**: Respectful API usage

### Monitoring
- **Health Checks**: `/health` endpoint
- **Statistics**: Real-time system metrics
- **Error Handling**: Comprehensive error logging
- **Performance Metrics**: Response time monitoring

## 🔍 Testing

### Run Tests
```bash
python test_v4.py
```

### Test Coverage
- ✅ Module imports
- ✅ Configuration loading
- ✅ Scoring system
- ✅ API endpoints
- ✅ Database operations

## 📝 API Documentation

### Request/Response Examples

#### Get Homepage Content
```bash
curl -X GET "http://localhost:8000/api/v4/home?limit=10"
```

#### Collect Articles
```bash
curl -X POST "http://localhost:8000/api/v4/admin/collect"
```

#### Get Theme Articles
```bash
curl -X GET "http://localhost:8000/api/v4/opportunities?limit=20"
```

## 🛡️ Security

### Best Practices
- **Input Validation**: All inputs sanitized
- **SQL Injection Protection**: Parameterized queries
- **Rate Limiting**: API request throttling
- **CORS Configuration**: Configurable origins

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Add docstrings to functions
- Include error handling

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Documentation
- API documentation available at `/docs` (Swagger UI)
- Configuration examples in `config.py`
- Test examples in `test_v4.py`

### Issues
- Report bugs via GitHub issues
- Feature requests welcome
- Pull requests appreciated

---

**Newsletter API v4** - Intelligent construction and real estate platform
Built with ❤️ for the building industry
