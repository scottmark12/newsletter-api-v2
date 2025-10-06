# Newsletter API v4 Deployment Guide

## 🚀 Deploy to GitHub and Render

### Step 1: Push to GitHub

1. **Create a new GitHub repository** (if you haven't already)
2. **Initialize git and push your code**:

```bash
# Initialize git repository
git init

# Add all files
git add .

# Commit the v4 platform
git commit -m "Add Newsletter API v4 - Complete platform with video support"

# Add your GitHub repository as remote
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Push to GitHub
git push -u origin main
```

### Step 2: Deploy to Render

#### 2.1 Create Render Services

You'll need to create **4 services** on Render:

1. **Web Service** (Main API)
2. **Background Worker** (Data Collection)
3. **Video Worker** (Video Processing)
4. **Static Site** (Website)

#### 2.2 Main API Service

**Service Type**: Web Service
**Name**: `newsletter-api-v4`
**Environment**: Python 3
**Build Command**:
```bash
pip install -r requirements_v4.txt && python -m app_v4.init_db
```
**Start Command**:
```bash
python -m uvicorn app_v4.api:app --host 0.0.0.0 --port $PORT
```

**Environment Variables**:
```
PYTHON_VERSION=3.11.0
ENVIRONMENT=production
ENABLE_VIDEO_SUPPORT=true
ENABLE_AI_SYNTHESIS=true
ENABLE_REAL_TIME_SCORING=true
MIN_COMPOSITE_SCORE=50.0
MIN_ACTIONABILITY_SCORE=60.0
CRAWLER_DELAY=0.1
CRAWLER_TIMEOUT=10
MAX_ARTICLES_PER_SOURCE=50
REQUESTS_PER_MINUTE=60
RATE_LIMIT_PER_MINUTE=100
CORS_ORIGINS=*
```

**API Keys** (Set these in Render dashboard):
```
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_google_cse_id
YOUTUBE_API_KEY=your_youtube_api_key
OPENAI_API_KEY=your_openai_api_key
```

#### 2.3 Background Worker Service

**Service Type**: Background Worker
**Name**: `newsletter-v4-worker`
**Environment**: Python 3
**Build Command**:
```bash
pip install -r requirements_v4.txt
```
**Start Command**:
```bash
python -m app_v4.worker
```

**Environment Variables** (same as main API service)

#### 2.4 Video Worker Service

**Service Type**: Background Worker
**Name**: `newsletter-v4-video-worker`
**Environment**: Python 3
**Build Command**:
```bash
pip install -r requirements_v4.txt
```
**Start Command**:
```bash
python -m app_v4.video_worker
```

**Environment Variables** (same as main API service)

#### 2.5 Website Service

**Service Type**: Static Site
**Name**: `newsletter-v4-website`
**Build Command**:
```bash
echo "Static site - no build needed"
```
**Publish Directory**: `website_v4`

### Step 3: Database Setup

1. **Create a PostgreSQL database** on Render
2. **Name**: `newsletter-v4-db`
3. **Plan**: Starter (free tier)
4. **Add the database URL** to all services:
   ```
   DATABASE_URL=postgresql://user:password@host:port/database
   ```

### Step 4: Configure API Keys in Render

In your Render dashboard, add these environment variables to all services:

1. **Google Custom Search**:
   - `GOOGLE_API_KEY` - Your Google API key
   - `GOOGLE_CSE_ID` - Your Custom Search Engine ID

2. **YouTube API**:
   - `YOUTUBE_API_KEY` - Your YouTube Data API key

3. **OpenAI** (optional):
   - `OPENAI_API_KEY` - Your OpenAI API key

### Step 5: Deploy and Test

1. **Deploy all services** on Render
2. **Wait for deployment** to complete
3. **Test the API**:
   - Visit: `https://your-api-service.onrender.com/api/v4/health`
   - Visit: `https://your-website-service.onrender.com`

### Step 6: Initial Data Collection

Once deployed, trigger initial data collection:

```bash
# Trigger data collection
curl -X POST https://your-api-service.onrender.com/api/v4/admin/collect

# Run scoring
curl -X POST https://your-api-service.onrender.com/api/v4/admin/score

# Process videos
curl -X POST https://your-api-service.onrender.com/api/v4/admin/process-videos
```

## 🔧 Troubleshooting

### Common Issues

1. **Build Failures**:
   - Check that `requirements_v4.txt` is in the root directory
   - Verify Python version is 3.11.0

2. **Database Connection Issues**:
   - Ensure PostgreSQL database is created
   - Check DATABASE_URL is set correctly

3. **API Key Issues**:
   - Verify all API keys are set in Render dashboard
   - Check API key permissions and quotas

4. **Service Not Starting**:
   - Check logs in Render dashboard
   - Verify start commands are correct

### Health Check Endpoints

- **API Health**: `https://your-api.onrender.com/api/v4/health`
- **API Docs**: `https://your-api.onrender.com/docs`

## 📊 Monitoring

### Render Dashboard
- Monitor service health and logs
- Check database connections
- View deployment status

### API Endpoints
- Health check: `/api/v4/health`
- Stats: Available in health check response

## 🎯 Next Steps

1. **Set up monitoring** for production use
2. **Configure custom domain** (optional)
3. **Set up automated backups** for database
4. **Monitor API usage** and costs

## 📞 Support

If you encounter issues:
1. Check Render service logs
2. Verify environment variables
3. Test API endpoints
4. Check database connectivity

Your v4 platform should now be running on Render with:
- ✅ Main API service
- ✅ Background data collection worker
- ✅ Video processing worker  
- ✅ Static website
- ✅ PostgreSQL database
- ✅ All API keys configured

The platform will automatically collect data, score articles, and process videos in the background!
