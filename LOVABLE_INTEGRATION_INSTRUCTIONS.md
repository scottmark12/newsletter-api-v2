# LOVABLE INTEGRATION INSTRUCTIONS

## Why Your Lovable Site Hasn't Changed

The intelligence synthesis endpoints are **live in the API** but Lovable doesn't know to call them yet. The API is just the backend - Lovable (your frontend) needs to be updated to use the new features.

## What's Available in the API (Already Working):

✅ `POST /ingest/research?limit=10` - Scrapes PDFs from JLL, CBRE, etc.
✅ `POST /ingest/videos?limit=20` - Gets YouTube video transcripts
✅ `GET /api/brief/narrative?days_back=1` - AI-synthesized narrative brief
✅ `GET /api/content/recommended?content_type=video` - Top video/podcast

## Option 1: Quick Test (Recommended First Step)

**Manually trigger ingestion once to populate your database with research + videos:**

```bash
# Run these commands once
curl -X POST "https://newsletter-api-v2.onrender.com/ingest/research?limit=5"
curl -X POST "https://newsletter-api-v2.onrender.com/ingest/videos?limit=10"
```

Then check your existing Lovable UI - research papers and videos should now appear mixed in with regular articles (they all go in the same `articles` table and get scored).

## Option 2: Add New UI Sections in Lovable

### A. Add "Daily Intelligence Brief" Section

Create a new component in Lovable:

```typescript
// components/IntelligenceBrief.tsx
import { useQuery } from '@tanstack/react-query';

export function IntelligenceBrief() {
  const { data } = useQuery({
    queryKey: ['narrative-brief'],
    queryFn: async () => {
      const res = await fetch('https://newsletter-api-v2.onrender.com/api/brief/narrative?days_back=1');
      return res.json();
    }
  });

  if (!data?.ok) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">Today's Intelligence Brief</h2>
      
      <div className="prose">
        <p className="text-lg">{data.narrative.opening}</p>
        
        <div className="mt-6">
          <h3 className="font-semibold">Key Themes:</h3>
          {data.narrative.themes.map((theme, i) => (
            <div key={i} className="mt-4">
              <h4 className="font-medium">{theme.name}</h4>
              <p className="text-gray-700">{theme.insight}</p>
            </div>
          ))}
        </div>

        <div className="mt-6 bg-blue-50 p-4 rounded">
          <h3 className="font-semibold">Bottom Line:</h3>
          <p>{data.narrative.recommendations}</p>
        </div>
      </div>
    </div>
  );
}
```

### B. Add "Video of the Week" Section

```typescript
// components/VideoOfWeek.tsx
import { useQuery } from '@tanstack/react-query';

export function VideoOfWeek() {
  const { data } = useQuery({
    queryKey: ['video-of-week'],
    queryFn: async () => {
      const res = await fetch('https://newsletter-api-v2.onrender.com/api/content/recommended?content_type=video');
      return res.json();
    }
  });

  if (!data?.ok || !data?.recommended) return null;

  const video = data.recommended;

  return (
    <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg shadow p-6">
      <h2 className="text-2xl font-bold mb-4">📹 Video of the Week</h2>
      
      <div className="space-y-3">
        <h3 className="text-xl font-semibold">{video.title}</h3>
        <p className="text-gray-700">{video.summary}</p>
        
        <div className="bg-white p-3 rounded">
          <p className="text-sm font-medium text-gray-600">Why it matters:</p>
          <p className="text-gray-800">{video.why_relevant}</p>
        </div>

        <a 
          href={video.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
        >
          Watch Now →
        </a>
      </div>
    </div>
  );
}
```

### C. Add to Your Main Page

```typescript
// pages/index.tsx
import { IntelligenceBrief } from '@/components/IntelligenceBrief';
import { VideoOfWeek } from '@/components/VideoOfWeek';

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Add at the top of your page */}
      <IntelligenceBrief />
      
      <div className="mt-8">
        <VideoOfWeek />
      </div>

      {/* Your existing article feed */}
      <ArticleFeed />
    </div>
  );
}
```

## Option 3: Automate Weekly Ingestion (Best for Production)

Set up GitHub Actions to run ingestion weekly:

Create `.github/workflows/weekly-ingestion.yml`:

```yaml
name: Weekly Intelligence Ingestion

on:
  schedule:
    - cron: '0 9 * * 1'  # Every Monday at 9 AM UTC
  workflow_dispatch:  # Allow manual trigger

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - name: Ingest Research PDFs
        run: |
          curl -X POST "https://newsletter-api-v2.onrender.com/ingest/research?limit=10"
      
      - name: Ingest YouTube Videos
        run: |
          curl -X POST "https://newsletter-api-v2.onrender.com/ingest/videos?limit=20"
      
      - name: Verify Ingestion
        run: |
          curl "https://newsletter-api-v2.onrender.com/admin/table/articles?limit=5"
```

## What Gets Added to Your Database:

When you run ingestion, these get added as regular articles with special flags:

**Research PDFs:**
- `media_type = 'research'`
- `source = 'JLL'` or `'CBRE'` or `'Cushman & Wakefield'`
- Full text extracted from PDF
- Scored like regular articles

**YouTube Videos:**
- `media_type = 'video'`
- `source = 'The B1M'` or `'Practical Engineering'`
- Full transcript as content
- Scored like regular articles

**They automatically appear in your existing feeds** because they're in the `articles` table!

## Testing the Integration

1. **Trigger ingestion manually:**
   ```bash
   curl -X POST "https://newsletter-api-v2.onrender.com/ingest/research?limit=5"
   curl -X POST "https://newsletter-api-v2.onrender.com/ingest/videos?limit=10"
   ```

2. **Check if content appears:**
   ```bash
   curl "https://newsletter-api-v2.onrender.com/api/articles?limit=20"
   # Look for articles with media_type='research' or 'video'
   ```

3. **Test narrative brief:**
   ```bash
   curl "https://newsletter-api-v2.onrender.com/api/brief/narrative?days_back=1"
   ```

4. **Test recommended content:**
   ```bash
   curl "https://newsletter-api-v2.onrender.com/api/content/recommended?content_type=video"
   ```

## Recommended Implementation Path

1. ✅ **Start with Option 1** - Manually trigger ingestion once to test
2. ✅ **Check existing Lovable UI** - Research/videos should appear in article feeds
3. ✅ **Add Option 2** - Create new UI components for narrative brief and video of week
4. ✅ **Set up Option 3** - Automate weekly ingestion with GitHub Actions

## The Result

Your Lovable site will show:
- Regular news articles (as before)
- Research reports from major CRE firms (NEW)
- Technical YouTube videos with transcripts (NEW)
- AI-synthesized daily narrative combining all sources (NEW)
- Recommended video/podcast of the week (NEW)

All scored, ranked, and curated automatically. 🚀
