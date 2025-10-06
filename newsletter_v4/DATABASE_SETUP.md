# Database Setup Guide - Newsletter API v4

## PostgreSQL Configuration

The Newsletter API v4 is configured to work with PostgreSQL by default. Here's how to set it up:

### 1. Install PostgreSQL

#### macOS (using Homebrew):
```bash
brew install postgresql
brew services start postgresql
```

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Docker:
```bash
docker run --name newsletter-postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=newsletter_v4 \
  -p 5432:5432 \
  -d postgres:15
```

### 2. Create Database

Connect to PostgreSQL and create the database:

```bash
psql -U postgres
```

```sql
CREATE DATABASE newsletter_v4;
CREATE USER newsletter_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE newsletter_v4 TO newsletter_user;
\q
```

### 3. Environment Configuration

Set your database URL as an environment variable:

```bash
export DATABASE_URL="postgresql://newsletter_user:your_password@localhost:5432/newsletter_v4"
```

Or create a `.env` file:
```
DATABASE_URL=postgresql://newsletter_user:your_password@localhost:5432/newsletter_v4
DATABASE_ECHO=false
DEBUG=false
PORT=8000
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python app.py
```

The application will automatically:
- Connect to PostgreSQL
- Create all necessary tables
- Set up the database schema

## Database Schema

The v4 platform creates the following tables:

### Articles Table (`articles_v4`)
- `id` - Primary key
- `title` - Article title
- `url` - Article URL (unique)
- `content` - Full article content
- `summary` - Article summary
- `source` - Source name
- `author` - Article author
- `published_at` - Publication timestamp
- `word_count` - Word count
- `reading_time` - Reading time in minutes
- `themes` - Detected themes (JSON)
- `keywords` - Extracted keywords (JSON)

### Article Scores Table (`article_scores_v4`)
- `id` - Primary key
- `article_id` - Foreign key to articles
- `total_score` - Overall score
- `opportunities_score` - Opportunities theme score
- `practices_score` - Practices theme score
- `systems_score` - Systems theme score
- `vision_score` - Vision theme score
- `insight_quality_score` - Insight quality score
- `narrative_signal_score` - Narrative signal score
- `source_credibility_score` - Source credibility score
- `scoring_details` - Detailed scoring breakdown (JSON)

### Videos Table (`videos_v4`)
- `id` - Primary key
- `title` - Video title
- `youtube_id` - YouTube video ID (unique)
- `url` - Video URL
- `channel_name` - YouTube channel name
- `duration` - Video duration in seconds
- `view_count` - View count
- `published_at` - Publication timestamp
- `transcript` - Video transcript
- `summary` - Video summary
- `relevance_score` - Relevance score
- `quality_score` - Quality score
- `total_score` - Overall score

### Article Insights Table (`article_insights_v4`)
- `id` - Primary key
- `article_id` - Foreign key to articles
- `insight_text` - Insight content
- `insight_type` - Type of insight (opportunity, practice, system, vision)
- `confidence_score` - Confidence score
- `supporting_evidence` - Supporting evidence
- `related_keywords` - Related keywords (JSON)

## Connection Testing

Test your database connection:

```python
from newsletter_v4.database import test_database_connection

if test_database_connection():
    print("✅ Database connection successful")
else:
    print("❌ Database connection failed")
```

## Troubleshooting

### Common Issues:

1. **Connection Refused**:
   - Ensure PostgreSQL is running
   - Check if the port (5432) is accessible
   - Verify the database exists

2. **Authentication Failed**:
   - Check username and password
   - Ensure user has proper permissions
   - Verify database name is correct

3. **Module Not Found**:
   - Install psycopg2-binary: `pip install psycopg2-binary`
   - Ensure all dependencies are installed

4. **Table Creation Errors**:
   - Check database permissions
   - Ensure the database is empty or use a new database
   - Check for conflicting table names

### Environment Variables:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/database_name
DATABASE_ECHO=false

# API
DEBUG=false
PORT=8000

# Scoring Configuration
OPPORTUNITIES_WEIGHT=1.0
PRACTICES_WEIGHT=1.0
SYSTEMS_WEIGHT=1.0
VISION_WEIGHT=1.0

# Data Sources
GOOGLE_API_KEY=your_google_api_key
GOOGLE_CSE_ID=your_custom_search_engine_id
YOUTUBE_API_KEY=your_youtube_api_key
```

## Production Deployment

For production deployment:

1. Use a managed PostgreSQL service (AWS RDS, Google Cloud SQL, etc.)
2. Set strong passwords and use SSL connections
3. Configure connection pooling
4. Set up database backups
5. Monitor database performance

Example production DATABASE_URL:
```
DATABASE_URL=postgresql://user:strong_password@db.example.com:5432/newsletter_v4?sslmode=require
```
