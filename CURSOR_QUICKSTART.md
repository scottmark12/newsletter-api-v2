# CURSOR: Quick Start Instructions

## The Situation

Your API has 4 new intelligence endpoints that are **live and working**, but your Lovable frontend doesn't call them yet.

## Fastest Path to See Results (3 Steps):

### Step 1: Trigger Ingestion Manually (Do This First)

Open terminal and run:

```bash
# This will populate your database with research PDFs and YouTube videos
curl -X POST "https://newsletter-api-v2.onrender.com/ingest/research?limit=5"
curl -X POST "https://newsletter-api-v2.onrender.com/ingest/videos?limit=10"
```

**What happens:** Research papers from JLL/CBRE and YouTube videos get added to your `articles` table with `media_type='research'` or `'video'`. They'll automatically show up in your existing article feeds since they're scored like regular articles.

### Step 2: Verify It Worked

```bash
# Check if research/videos appeared
curl "https://newsletter-api-v2.onrender.com/api/articles?limit=20"
# You should see some articles with source='JLL' or source='The B1M'
```

### Step 3: Add New UI Components to Lovable

See `LOVABLE_INTEGRATION_INSTRUCTIONS.md` for full React components, but here's the quick version:

**Add to your Lovable project:**

```typescript
// Fetch narrative brief
const { data } = useQuery({
  queryKey: ['brief'],
  queryFn: () => fetch('https://newsletter-api-v2.onrender.com/api/brief/narrative?days_back=1').then(r => r.json())
});

// Fetch recommended video
const { data: video } = useQuery({
  queryKey: ['video'],
  queryFn: () => fetch('https://newsletter-api-v2.onrender.com/api/content/recommended?content_type=video').then(r => r.json())
});
```

## Long-Term: Automate Ingestion

Create `.github/workflows/weekly-ingestion.yml`:

```yaml
name: Weekly Ingestion
on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday 9 AM
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - run: curl -X POST "https://newsletter-api-v2.onrender.com/ingest/research?limit=10"
      - run: curl -X POST "https://newsletter-api-v2.onrender.com/ingest/videos?limit=20"
```

## What You'll Get

After Step 1, your existing Lovable UI will show:
- ✅ Regular news articles (as before)
- ✅ Research reports from JLL, CBRE, Cushman & Wakefield (NEW)
- ✅ YouTube videos from The B1M, Practical Engineering (NEW)

After Step 3, you'll also have:
- ✅ AI-synthesized daily narrative combining all sources
- ✅ Recommended video/podcast of the week

All scored, ranked, and curated automatically.

---

**TL;DR: Run the two curl commands from Step 1 right now. Everything else can wait.**
