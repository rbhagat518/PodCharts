# Episode Tracking & Most Watched Feature

## Overview

This feature adds episode-level tracking and "most watched" podcast metrics to PodCharts. Since watch/listen time data is not publicly available from ListenNotes, Spotify, or Apple Podcasts APIs, we use **proxy metrics** based on episode data that is available.

## What's Implemented

### 1. Database Schema (`infra/schema_episodes.sql`)

Three new tables:

- **`episodes`**: Stores individual podcast episodes
  - Episode ID, title, description, audio URL
  - Audio length (duration in seconds)
  - Publication date
  
- **`episode_metrics_daily`**: Daily episode-level metrics
  - Listen time metrics (placeholders for future real data)
  - Episode age (days since publication)
  - New episode flag (published within last 7 days)

- **`podcast_listen_metrics_daily`**: Aggregated podcast-level metrics
  - Total listen time (sum of all episodes)
  - Total unique listeners
  - New episodes count
  - Engagement score (composite metric)

### 2. Episode Ingestion Script (`backend/scripts/ingest_episodes.py`)

Fetches episode data from ListenNotes API and computes metrics:
- Fetches episodes for each podcast
- Tracks episode publication dates
- Computes episode age and new episode flags
- Aggregates to podcast-level metrics

### 3. API Endpoint (`/most-watched`)

New endpoint to get most watched podcasts for a specific time period:

```
GET /most-watched?start_date=2024-11-01&end_date=2024-11-07&sort_by=listen_time&limit=50
```

**Query Parameters:**
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)
- `category` (optional): Filter by category
- `country` (optional): Filter by country
- `limit` (optional): Number of results (default: 50)
- `sort_by` (optional): Sort by `listen_time`, `listeners`, `engagement_score`, or `new_episodes` (default: `listen_time`)

**Response:**
```json
{
  "start_date": "2024-11-01",
  "end_date": "2024-11-07",
  "sort_by": "listen_time",
  "items": [
    {
      "id": "podcast_id",
      "title": "Podcast Title",
      "publisher": "Publisher Name",
      "category": "technology",
      "country": "us",
      "total_listen_time_seconds": 1234567,
      "total_listen_time_hours": 342.94,
      "total_unique_listeners": 5000,
      "avg_completion_rate": 0.75,
      "total_new_episodes": 3,
      "total_active_episodes": 10,
      "avg_engagement_score": 0.85,
      "days_tracked": 7
    }
  ]
}
```

## Setup Instructions

### 1. Create Episode Tables

Run the episode schema migration:

```bash
cd backend
python scripts/setup_db.py  # This will need to be updated to include episode tables
# OR manually run:
psql $DATABASE_URL -f ../infra/schema_episodes.sql
```

### 2. Run Episode Ingestion

Ingest episodes for existing podcasts:

```bash
cd backend
python scripts/ingest_episodes.py
```

This will:
- Fetch episodes for all podcasts in your database
- Compute episode metrics
- Aggregate to podcast-level metrics

### 3. Schedule Daily Episode Ingestion

Add to your cron job or GitHub Actions workflow:

```yaml
# .github/workflows/ingest_episodes.yml
name: Ingest Episodes
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  ingest:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Ingest episodes
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          LISTENNOTES_API_KEY: ${{ secrets.LISTENNOTES_API_KEY }}
        run: |
          cd backend
          python scripts/ingest_episodes.py
```

## Example: Most Watched Podcasts (First Week of November)

To get the most watched podcasts for the first week of November 2024:

```bash
curl "http://localhost:8000/most-watched?start_date=2024-11-01&end_date=2024-11-07&sort_by=engagement_score&limit=20"
```

This will return podcasts sorted by engagement score, which combines:
- New episodes (30% weight)
- Active episodes (40% weight)
- Completion rate (30% weight)

## Current Limitations

1. **No Real Listen Time Data**: Since listen time is not publicly available, we use:
   - Episode count and recency as proxies
   - Engagement score based on episode activity
   - Placeholders for real listen time (will be populated when we get access)

2. **ListenNotes API Limits**: 
   - Free tier: 10,000 requests/month
   - Episode fetching requires one API call per podcast
   - Consider rate limiting and caching

3. **Episode Data Availability**:
   - Not all podcasts may have episode data in ListenNotes
   - Some podcasts may not have recent episodes

## Future Enhancements

1. **Real Listen Time Integration**:
   - If you get access to Spotify/Apple Podcasts APIs with listen time data
   - Update `episode_metrics_daily.total_listen_time_seconds` with real values
   - The endpoint will automatically use real data

2. **Additional Metrics**:
   - Episode download counts (if available)
   - Episode ratings/reviews
   - Social media engagement (shares, mentions)

3. **Frontend Integration**:
   - Add "Most Watched" page to frontend
   - Display listen time charts
   - Show episode-level details

## Notes

- The engagement score is a composite metric that can be adjusted based on your needs
- Currently, `total_listen_time_seconds` will be 0 until we have real data
- The endpoint still works and will sort by engagement score, new episodes, or listeners
- When real listen time data becomes available, just update the `episode_metrics_daily` table and the endpoint will automatically use it

