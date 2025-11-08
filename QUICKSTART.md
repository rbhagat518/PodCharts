# PodCharts Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Conda installed
- Node.js 18+ installed
- Supabase database with schema set up
- ListenNotes API key

### 1. Backend Setup

```bash
cd backend

# Create conda environment
conda env create -f environment.yml
conda activate podcharts-backend

# Copy and configure environment variables
cp env.example .env
# Edit .env with your DATABASE_URL and LISTENNOTES_API_KEY

# Set up database schema
python scripts/setup_db.py

# Run ingestion to populate data
python scripts/ingest.py

# Start the API server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 📊 Testing

### Test the API

```bash
# Run the test script
./test-api.sh

# Or test manually:
curl http://localhost:8000/health
curl "http://localhost:8000/leaderboard"
curl "http://localhost:8000/leaderboard?category=technology"
```

### Test the Frontend

1. Open `http://localhost:3000` in your browser
2. Navigate to `/leaderboard` to see the rankings
3. Click on any podcast to see details and charts
4. Go to `/compare` to compare two podcasts

## 🎯 Available Endpoints

### `GET /health`
Health check endpoint.

### `GET /leaderboard`
Get leaderboard of podcasts with rankings and metrics.

**Query Parameters:**
- `category` (optional): Filter by category (e.g., "technology", "comedy")
- `country` (optional): Filter by country (e.g., "us", "global")
- `interval` (optional): Time interval (default: "daily")

**Example:**
```bash
curl "http://localhost:8000/leaderboard?category=technology&country=us"
```

### `GET /podcast/{podcast_id}`
Get podcast details and historical rank data (last 90 days).

**Example:**
```bash
curl "http://localhost:8000/podcast/4d3fe717742d4963a85562e9f7d74f8e"
```

### `GET /compare?id1={id1}&id2={id2}`
Compare two podcasts side-by-side with historical data.

**Example:**
```bash
curl "http://localhost:8000/compare?id1=4d3fe717742d4963a85562e9f7d74f8e&id2=another-podcast-id"
```

## 📁 Project Structure

```
podcharts/
├── backend/           # FastAPI backend
│   ├── app/          # Application code
│   │   ├── main.py   # API endpoints
│   │   └── db.py     # Database connection
│   └── scripts/      # Utility scripts
│       ├── setup_db.py    # Database schema setup
│       └── ingest.py      # Data ingestion script
├── frontend/         # Next.js frontend
│   └── app/          # Next.js app router pages
├── infra/            # Infrastructure
│   └── schema.sql    # Database schema
└── .github/          # GitHub Actions
    └── workflows/
        └── ingest.yml    # Daily ingestion cron
```

## 🔄 Daily Ingestion

The ingestion script runs daily via GitHub Actions (`.github/workflows/ingest.yml`).

To run manually:
```bash
cd backend
conda activate podcharts-backend
python scripts/ingest.py
```

## 🐛 Troubleshooting

### Backend Issues

**Connection Pool Error:**
- Make sure the database URL is correct in `.env`
- Check that the database schema is set up: `python scripts/setup_db.py`

**API Returns 500 Error:**
- Check backend logs for error messages
- Verify database connection: `python -c "from app.db import get_connection; conn = get_connection().__enter__(); print('Connected!')"`

### Frontend Issues

**Cannot connect to API:**
- Make sure backend is running on port 8000
- Check `NEXT_PUBLIC_API_BASE_URL` in frontend `.env.local` (defaults to `http://localhost:8000`)

**Charts not rendering:**
- Make sure Recharts is installed: `npm install recharts`
- Check browser console for errors

## 📝 Next Steps

1. **Deploy Backend**: Deploy to Render, Railway, or similar
2. **Deploy Frontend**: Deploy to Vercel
3. **Set up GitHub Actions**: Configure secrets for daily ingestion
4. **Add Authentication**: Implement Supabase Auth for Pro features
5. **Add More Data Sources**: Integrate Spotify, Apple Podcasts, etc.

## 🎉 Success!

You should now have:
- ✅ Backend API running on port 8000
- ✅ Frontend app running on port 3000
- ✅ Database with podcast data
- ✅ Working leaderboard, podcast details, and compare pages
- ✅ Charts and visualizations

Visit `http://localhost:3000` to see your PodCharts app!

