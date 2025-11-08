# What Does Ingestion Mean?

## Overview

When the ingestion script succeeds, it means your PodCharts database has been updated with the latest podcast rankings and metrics from ListenNotes API.

## What Happens During Ingestion

### 1. Fetches Podcast Rankings
- Connects to ListenNotes API
- Gets top podcasts across multiple categories:
  - Top (overall)
  - Technology
  - News
  - Comedy
  - Business
  - Health
  - Education
- Fetches rankings for US region (configurable)

### 2. Stores Podcast Data
- **`podcasts` table**: Stores podcast information
  - ID, title, publisher, category, country
  - RSS feed URL
  - Created/updated timestamps

### 3. Stores Daily Rankings
- **`ranks_daily` table**: Stores daily rank snapshots
  - Podcast ID
  - Rank position
  - Date captured
  - Source (ListenNotes)
  - Country

### 4. Computes Metrics
- **`metrics_daily` table**: Calculates derived metrics
  - **Rank**: Current rank position
  - **Delta 7d**: Change in rank vs. 7 days ago
    - Positive = moved up (better rank)
    - Negative = moved down (worse rank)
  - **Delta 30d**: Change in rank vs. 30 days ago
  - **Momentum Score**: Composite metric showing growth
    - Higher = more momentum/rising
    - Lower = declining

## What "Success" Means

✅ **Ingestion succeeded** means:
- Podcast data was fetched from ListenNotes API
- Rankings were stored in the database
- Metrics were calculated
- Your database now has fresh data for today

## How to Verify the Results

### 1. Check the Database
```bash
# Check how many podcasts are in the database
# Check today's rankings
# Check today's metrics
```

### 2. Check the API
```bash
# View leaderboard
curl http://localhost:8000/leaderboard?limit=10

# View trending podcasts
curl http://localhost:8000/trending?limit=10

# View a specific podcast
curl http://localhost:8000/podcast/{podcast_id}
```

### 3. Check the Frontend
- Visit: http://localhost:3000/leaderboard
- You should see today's rankings
- Metrics (deltas, momentum) should be displayed

## What Data Gets Updated

### Daily Updates
- **New rankings**: Today's rank positions
- **New metrics**: Calculated deltas and momentum scores
- **Historical tracking**: Builds a history of rank changes over time

### Metrics Explained

**Delta 7d (7-day change)**:
- `+5` = Moved up 5 positions (improved)
- `-3` = Moved down 3 positions (declined)
- `null` = No data from 7 days ago

**Delta 30d (30-day change)**:
- `+10` = Moved up 10 positions (big improvement)
- `-5` = Moved down 5 positions (decline)
- `null` = No data from 30 days ago

**Momentum Score**:
- Composite metric combining 7d and 30d changes
- Higher score = more momentum/rising popularity
- Used to identify trending podcasts

## When Does Ingestion Run?

### Automated (GitHub Actions)
- **Schedule**: Daily at 3:00 AM UTC
- **Trigger**: Automatic via cron job
- **Manual**: Can be triggered from Actions tab

### Manual (Local)
```bash
cd backend
python scripts/ingest.py
```

## What to Expect After Ingestion

1. **Leaderboard**: Shows current rankings
2. **Trending**: Identifies podcasts with momentum
3. **Insights**: Historical data for monthly/weekly insights
4. **Compare**: Can compare podcasts over time
5. **Most Watched**: Episode data (if episode ingestion runs)

## Troubleshooting

### If ingestion succeeds but no data appears:
- Check if data exists in database
- Verify the date matches today
- Check API endpoints are working
- Verify frontend is connected to backend

### If metrics show `null`:
- This is normal for the first few days
- Deltas require historical data (7d/30d ago)
- After running for 7+ days, deltas will populate

## Next Steps

After successful ingestion:
1. ✅ Check the leaderboard page
2. ✅ View trending podcasts
3. ✅ Explore podcast detail pages
4. ✅ Check insights for historical data
5. ✅ Run episode ingestion (separate script)

