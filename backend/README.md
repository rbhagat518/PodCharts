# PodCharts Backend

FastAPI backend for PodCharts podcast analytics.

## Setup

### Using Conda (Recommended)

1. Create the conda environment:
   ```bash
   conda env create -f environment.yml
   ```

2. Activate the environment:
   ```bash
   conda activate podcharts-backend
   ```

3. Copy and configure environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your Supabase DATABASE_URL and LISTENNOTES_API_KEY
   ```

4. Set up the database schema:
   ```bash
   python scripts/setup_db.py
   ```

5. Run ingestion (optional, to populate data):
   ```bash
   python scripts/ingest.py
   ```

## Running the API

### Development Server

```bash
# Using conda
conda activate podcharts-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using conda run
conda run -n podcharts-backend uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

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

## Database Schema

See `../infra/schema.sql` for the database schema.

## Ingestion

The ingestion script fetches podcast data from ListenNotes API and stores it in the database.

Run manually:
```bash
python scripts/ingest.py
```

Or set up the GitHub Actions workflow (`.github/workflows/ingest.yml`) to run daily.

