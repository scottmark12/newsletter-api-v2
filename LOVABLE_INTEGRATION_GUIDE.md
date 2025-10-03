# Newsletter API - Lovable Integration Guide

## 🚀 API Base URL
```
https://newsletter-api-v2.onrender.com
```

## 📊 Available Data Sources & Endpoints

### 1. **Top Articles by Category** (Recommended for Homepage)
```typescript
// Get top 3 articles for each category
GET /api/categories/top

// Response structure:
{
  "ok": true,
  "categories": {
    "innovation": [...],      // Top 3 innovation articles
    "market_news": [...],     // Top 3 market news articles  
    "insights": [...],        // Top 3 insights articles
    "unique_developments": [...] // Top 3 unique development articles
  }
}
```

### 2. **Category-Specific Feeds**
```typescript
// Get articles by specific category
GET /api/feed/{bucket}?limit=10&days=7

// Available buckets:
// - tech_innovation
// - market_insight  
// - construction_insight
// - unique_development

// Example: Innovation articles
GET /api/feed/tech_innovation?limit=10

// Response structure:
{
  "ok": true,
  "bucket": "tech_innovation",
  "count": 10,
  "articles": [
    {
      "id": "uuid",
      "url": "https://...",
      "source": "Construction Dive",
      "title": "Article title",
      "summary": "Article summary",
      "published_at": "2025-10-02T00:00:00",
      "score": 187.31,
      "topics": ["innovation", "market_news"],
      "project_stage": "breaks_ground",
      "needs_fact_check": false
    }
  ]
}
```

### 3. **Recent Articles Feed**
```typescript
// Get recent articles with scoring data
GET /api/articles?limit=20&since_hours=24

// Response includes all articles with composite scores and topics
```

### 4. **Search Functionality**
```typescript
// Search articles by title or summary
GET /api/search?query=construction&limit=20
```

### 5. **Admin/Debug Endpoints**
```typescript
// Database status
GET /api/admin/db_status

// Configuration info
GET /api/admin/config
```

## 🎯 Lovable Component Examples

### 1. **Homepage with Top Articles**
```typescript
import { useState, useEffect } from 'react';

interface Article {
  id: string;
  url: string;
  source: string;
  title: string;
  summary_raw: string;
  published_at: string;
  composite_score: number;
  topics: string[];
  project_stage?: string;
  needs_fact_check: boolean;
  media_type: string;
}

interface CategoryData {
  innovation: Article[];
  market_news: Article[];
  insights: Article[];
  unique_developments: Article[];
}

export default function HomePage() {
  const [categories, setCategories] = useState<CategoryData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('https://newsletter-api-v2.onrender.com/api/categories/top')
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          setCategories(data.categories);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch articles:', err);
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!categories) return <div>Failed to load articles</div>;

  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8">Building the Future Newsletter</h1>
      
      {/* Innovation Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-blue-600">🚀 Innovation</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {categories.innovation.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      </section>

      {/* Market News Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-green-600">📈 Market News</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {categories.market_news.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      </section>

      {/* Insights Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-purple-600">💡 Insights</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {categories.insights.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      </section>

      {/* Unique Developments Section */}
      <section className="mb-12">
        <h2 className="text-2xl font-semibold mb-4 text-orange-600">🏗️ Unique Developments</h2>
        <div className="grid md:grid-cols-3 gap-6">
          {categories.unique_developments.map(article => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      </section>
    </div>
  );
}

function ArticleCard({ article }: { article: Article }) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getScoreColor = (score: number) => {
    if (score > 150) return 'text-green-600 bg-green-100';
    if (score > 100) return 'text-blue-600 bg-blue-100';
    return 'text-gray-600 bg-gray-100';
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <span className="text-sm text-gray-500">{article.source}</span>
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${getScoreColor(article.composite_score)}`}>
          {article.composite_score.toFixed(0)}
        </span>
      </div>
      
      <h3 className="text-lg font-semibold mb-2 line-clamp-2">
        <a 
          href={article.url} 
          target="_blank" 
          rel="noopener noreferrer"
          className="text-gray-900 hover:text-blue-600"
        >
          {article.title}
        </a>
      </h3>
      
      <p className="text-gray-600 text-sm mb-3 line-clamp-3">
        {article.summary_raw}
      </p>
      
      <div className="flex justify-between items-center text-xs text-gray-500">
        <span>{formatDate(article.published_at)}</span>
        {article.project_stage && (
          <span className="px-2 py-1 bg-gray-100 rounded">
            {article.project_stage}
          </span>
        )}
      </div>
      
      <div className="flex flex-wrap gap-1 mt-2">
        {article.topics.slice(0, 2).map(topic => (
          <span key={topic} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
            {topic.replace('_', ' ')}
          </span>
        ))}
      </div>
    </div>
  );
}
```

### 2. **Category Page Component**
```typescript
interface CategoryPageProps {
  category: 'tech_innovation' | 'market_insight' | 'construction_insight' | 'unique_development';
}

export default function CategoryPage({ category }: CategoryPageProps) {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`https://newsletter-api-v2.onrender.com/api/feed/${category}?limit=20`)
      .then(res => res.json())
      .then(data => {
        if (data.ok) {
          setArticles(data.articles);
        }
        setLoading(false);
      })
      .catch(err => {
        console.error('Failed to fetch articles:', err);
        setLoading(false);
      });
  }, [category]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="max-w-4xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-8 capitalize">
        {category.replace('_', ' ')}
      </h1>
      
      <div className="space-y-6">
        {articles.map(article => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  );
}
```

### 3. **Search Component**
```typescript
export default function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<Article[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async (searchQuery: string) => {
    if (searchQuery.length < 3) return;
    
    setLoading(true);
    try {
      const response = await fetch(
        `https://newsletter-api-v2.onrender.com/api/search?query=${encodeURIComponent(searchQuery)}&limit=20`
      );
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="mb-8">
        <input
          type="text"
          placeholder="Search articles..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full p-3 border rounded-lg"
        />
        <button
          onClick={() => handleSearch(query)}
          disabled={loading}
          className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      <div className="space-y-4">
        {results.map(article => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  );
}
```

## 🎨 CSS Classes for Styling

Add these Tailwind classes to your Lovable project:

```css
/* Line clamp utilities */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Category colors */
.category-innovation { @apply text-blue-600; }
.category-market { @apply text-green-600; }
.category-insights { @apply text-purple-600; }
.category-developments { @apply text-orange-600; }
```

## 📱 Mobile-Responsive Considerations

```typescript
// Responsive grid classes
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
  {/* Articles */}
</div>

// Mobile-friendly card layout
<div className="bg-white rounded-lg shadow-md p-4 md:p-6">
  {/* Card content */}
</div>
```

## 🔄 Data Refresh Strategy

```typescript
// Auto-refresh every 5 minutes
useEffect(() => {
  const interval = setInterval(() => {
    // Refetch data
    fetchArticles();
  }, 5 * 60 * 1000);

  return () => clearInterval(interval);
}, []);

// Manual refresh button
const [refreshing, setRefreshing] = useState(false);

const handleRefresh = async () => {
  setRefreshing(true);
  await fetchArticles();
  setRefreshing(false);
};
```

## 🚨 Error Handling

```typescript
const [error, setError] = useState<string | null>(null);

const fetchArticles = async () => {
  try {
    setError(null);
    const response = await fetch('https://newsletter-api-v2.onrender.com/api/categories/top');
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    if (!data.ok) {
      throw new Error('API returned error status');
    }
    
    setCategories(data.categories);
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to fetch articles');
    console.error('Fetch error:', err);
  }
};
```

## 🎯 Key Data Points to Display

### Article Properties:
- **`title`** - Article headline
- **`summary_raw`** - Article summary/description
- **`source`** - Publication name (Construction Dive, AEC Magazine, etc.)
- **`published_at`** - Publication date
- **`composite_score`** - Quality score (higher = better)
- **`topics`** - Array of categories (innovation, market_news, etc.)
- **`project_stage`** - Development stage (breaks_ground, opens, etc.)
- **`needs_fact_check`** - Flag for fact-checking
- **`media_type`** - article, video, podcast

### Score Interpretation:
- **150+** = Excellent content (green)
- **100-149** = Good content (blue)  
- **<100** = Standard content (gray)

### Topic Categories:
- **innovation** - AI, technology, new methods
- **market_news** - Deals, financing, market trends
- **insights** - Analysis, trends, expert opinions
- **unique_developments** - Groundbreaking projects, first-of-kind

## 🔗 Integration Checklist

- [ ] Set up base URL: `https://newsletter-api-v2.onrender.com`
- [ ] Create homepage with `/api/categories/top`
- [ ] Build category pages with `/api/feed/{bucket}`
- [ ] Implement search with `/api/search`
- [ ] Add error handling and loading states
- [ ] Style with Tailwind CSS
- [ ] Test mobile responsiveness
- [ ] Add auto-refresh functionality
- [ ] Implement proper TypeScript types
- [ ] Add analytics tracking for article clicks

## 🚀 Quick Start

1. Copy the `HomePage` component above
2. Create the `ArticleCard` component
3. Test with the API endpoints
4. Customize styling to match your brand
5. Add additional features (search, filtering, etc.)

The API is fully operational and ready to power your Lovable frontend! 🎉
