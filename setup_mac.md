# V2 Newsletter API - Mac Setup Guide

## Prerequisites

### 1. Python 3.9+ 
```bash
# Check your Python version
python3 --version

# If you need to install Python, use Homebrew:
brew install python@3.11
```

### 2. Required Environment Variables
Create a `.env` file in the project root:

```bash
# Core Database
DATABASE_URL=postgresql://username:password@localhost:5432/newsletter_db

# OpenAI for scoring (required)
OPENAI_API_KEY=your_openai_api_key_here

# Email (optional)
RESEND_API_KEY=your_resend_key
SENDER_EMAIL=newsletter@yourdomain.com
SENDER_NAME=Building the Future

# Google CSE (optional - for backfill)
GOOGLE_CSE_API_KEY=your_google_api_key
GOOGLE_CSE_CX_ID=your_search_engine_id

# FRED API for macro data (optional)
FRED_API_KEY=your_fred_api_key

# App Config
SITE_BASE_URL=http://localhost:10000
USER_AGENT=BuildingTheFutureBot/2.0
MAX_ARTICLES_PER_RUN=1000
```

## Quick Start

### 1. Install Dependencies
```bash
cd /Users/markscott/Downloads/NEWSLETTER-API-main

# Install Python dependencies
pip3 install -r requirements.txt

# Or use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set up Database
```bash
# Install PostgreSQL (if not already installed)
brew install postgresql
brew services start postgresql

# Create database
createdb newsletter_db
```

### 3. Run the API
```bash
# Start the FastAPI server
uvicorn app.main:web_app --reload --port 10000

# Or with Python directly
python -m uvicorn app.main:web_app --reload --port 10000
```

### 4. Test the API
Open your browser to:
- **API Docs**: http://localhost:10000/docs
- **Health Check**: http://localhost:10000/health
- **Daily Brief**: http://localhost:10000/api/brief/daily

## Running the V2 Pipeline

### 1. Ingest Articles
```bash
# Crawl RSS feeds and websites
curl -X POST "http://localhost:10000/ingest/start?limit=100"
```

### 2. Score Articles
```bash
# Run AI scoring on new articles
curl -X POST "http://localhost:10000/score/run?limit=50"
```

### 3. Get V2 Endpoints
```bash
# Daily brief (What moved + Top 3)
curl "http://localhost:10000/api/brief/daily"

# Weekly brief (Best podcast + video)
curl "http://localhost:10000/api/brief/weekly"

# Video of the week
curl "http://localhost:10000/api/video/week"

# Feed by bucket
curl "http://localhost:10000/api/feed/tech_innovation"
```

## Optional: Background Scheduler

To run the pipeline automatically:

```bash
# In a separate terminal
python app/scheduler.py
```

This will run ingestion and scoring on a schedule.

## Troubleshooting

### Common Mac Issues

1. **SSL Certificate Issues**:
```bash
# Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command
```

2. **Permission Errors**:
```bash
# Use --user flag for pip
pip3 install --user -r requirements.txt
```

3. **PostgreSQL Connection**:
```bash
# Check if PostgreSQL is running
brew services list | grep postgresql

# Start if needed
brew services start postgresql
```

4. **Port Already in Use**:
```bash
# Find what's using port 10000
lsof -i :10000

# Use a different port
uvicorn app.main:web_app --reload --port 8000
```

### Dependencies Check

The main dependencies that should work on Mac:
- `fastapi` - ✅ Mac compatible
- `uvicorn` - ✅ Mac compatible  
- `sqlalchemy` - ✅ Mac compatible
- `psycopg2-binary` - ✅ Mac compatible
- `httpx` - ✅ Mac compatible
- `beautifulsoup4` - ✅ Mac compatible
- `feedparser` - ✅ Mac compatible
- `openai` - ✅ Mac compatible

## Production Deployment

For production on Mac (or deploy to cloud):

1. **Use Gunicorn** (more robust than uvicorn alone):
```bash
pip install gunicorn
gunicorn app.main:web_app -w 4 -k uvicorn.workers.UnicornWorker --bind 0.0.0.0:10000
```

2. **Set up proper logging**:
```bash
export PYTHONPATH=/Users/markscott/Downloads/NEWSLETTER-API-main
```

3. **Use environment variables** instead of .env file in production.

## Next Steps

1. **Test the V2 endpoints** - Try the daily/weekly briefs
2. **Add your data sources** - Update the API keys in .env
3. **Customize the voice** - Modify the CEO voice formatting
4. **Monitor quota usage** - Check CSE and OpenAI usage

The system is designed to be lightweight and should run smoothly on Mac with minimal setup!

