# 🏗️ Newsletter API v2 - Developer Intelligence System

A **construction & real estate intelligence API** designed for aspiring developers. Crawls industry sources, scores content with AI, and delivers actionable insights in a "Chill CEO" executive format.

## 🎯 **What It Does**

- **Crawls Tier-1 Sources**: ENR, Dodge, Commercial Observer, Bisnow, ULI, Construction Dive
- **AI-Powered Scoring**: Prioritizes $1B+ projects, tech innovations, and opportunities  
- **Developer-Focused**: Surfaces JVs, financing deals, policy changes, and breakthrough tech
- **Executive Format**: "Why it matters" + "CEO takeaway" for each story
- **YouTube Integration**: Construction tech videos from The B1M, Practical Engineering, etc.

## 🚀 **Live Example**

**Top Story Today**: Cleveland Browns $2.4B Stadium (Score: 187.3)
- **Why it matters**: AECOM Hunt-Turner JV shows major partnership model
- **CEO Takeaway**: Study mixed funding structure ($1.2B private + $1.2B public)

## 📊 **API Endpoints**

```bash
# Daily developer intelligence brief
GET /api/brief/daily

# Weekly summary with best video/podcast
GET /api/brief/weekly  

# Video feed from construction YouTube channels
GET /api/videos/feed

# Trigger article crawling
POST /ingest/start?limit=20

# Run AI scoring on articles
POST /score/run?limit=25
```

## 🛠️ **Quick Start**

### Local Development
```bash
# Clone and setup
git clone <your-repo-url>
cd NEWSLETTER-API-main
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Add your OPENAI_API_KEY

# Run locally
./run_local.sh
# API available at http://localhost:10000
```

### Deploy to Render (Free)
1. Push to GitHub
2. Connect to [Render](https://render.com)
3. Uses `render.yaml` config automatically
4. Set `OPENAI_API_KEY` in environment variables

## 🎨 **Lovable Integration**

Perfect for building construction intelligence dashboards:

```javascript
// Get developer opportunities
const brief = await fetch('https://your-api.onrender.com/api/brief/daily');
const data = await brief.json();

// Display high-scoring projects
data.top_stories.forEach(story => {
  if (story.score > 100) {
    console.log(`🚀 ${story.headline} (${story.score})`);
    console.log(`Action: ${story.ceo_takeaway}`);
  }
});
```

See `lovable-integration.md` for complete integration guide.

## 🏗️ **Scoring Algorithm**

Prioritizes content for aspiring developers:

- **🚀 Breakthrough Tech** (15pts): 3D printing, modular, mass timber, AI design
- **🏗️ Major Projects** (25pts): Stadiums, hospitals, data centers  
- **💰 Big Deals** (2.5x multiplier): $1B+ projects get massive score boost
- **🤝 Partnerships** (1.2x): JVs, consortiums show collaboration opportunities
- **❌ Penalties** (-20pts): Filters out retail/restaurant operational news

## 📁 **Project Structure**

```
app/
├── main.py              # FastAPI app & endpoints
├── crawler.py           # RSS/HTML crawling
├── scoring.py           # Developer-focused AI scoring  
├── db.py               # SQLite database schema
├── ceo_voice.py        # "Chill CEO" formatting
├── youtube_handler.py   # Video processing
├── macro_data.py       # Economic indicators
└── seeds.json          # RSS feeds & YouTube channels

render.yaml             # Deployment configuration
requirements.txt        # Python dependencies
lovable-integration.md  # Frontend integration guide
```

## 🔧 **Tech Stack**

- **Backend**: FastAPI, SQLAlchemy, SQLite
- **AI**: OpenAI GPT for scoring & summaries
- **Crawling**: RSS feeds, HTML parsing
- **Deployment**: Render (free tier)
- **Frontend Ready**: CORS enabled, JSON API

## 📈 **Key Features**

- **Dollar Value Detection**: Automatically scores $2.4B projects higher
- **Project Stage Tracking**: Groundbreaking → Topping Out → Opens
- **Fact-Check Flagging**: Identifies content needing verification
- **Geographic Intelligence**: Tracks opportunity zones and emerging markets
- **Technology Focus**: Prioritizes repeatable, scalable construction methods

## 🎯 **Perfect For**

- **Aspiring Developers**: Find project opportunities and partnership models
- **Construction Tech**: Track innovation adoption and breakthrough methods  
- **Real Estate Intelligence**: Policy changes, financing trends, market signals
- **Executive Dashboards**: "So what, now what" actionable intelligence

---

**Built for developers who want to leverage unhuman tech to create deep human connection through space** 🏗️✨