# How to Run PodCharts

## Quick Start

### Step 1: Start the Backend API

Open a terminal and run:

```bash
cd backend
conda activate podcharts-backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this terminal open!** The backend needs to keep running.

### Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
cd frontend
npm run dev
```

You should see:
```
  ▲ Next.js 14.2.5
  - Local:        http://localhost:3000
  - Ready in 2.3s
```

**Keep this terminal open too!**

### Step 3: Open the App

Open your browser and go to:
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## Verify Everything Works

### Test the Backend

In a new terminal, test the API:

```bash
# Health check
curl http://localhost:8000/health

# Should return: {"status":"ok"}

# Get leaderboard
curl http://localhost:8000/leaderboard

# Should return JSON with podcast data
```

### Test the Frontend

1. Open http://localhost:3000 in your browser
2. Click "View Leaderboard" or go to http://localhost:3000/leaderboard
3. You should see a table with podcasts
4. Click on any podcast to see details and charts

## Troubleshooting

### Backend won't start

**Error: `conda: command not found`**
- Make sure conda is installed and in your PATH
- Or use: `source ~/miniconda3/etc/profile.d/conda.sh` (adjust path as needed)

**Error: `DATABASE_URL is required`**
- Make sure you have a `.env` file in the `backend/` directory
- Copy from `env.example`: `cp env.example .env`
- Edit `.env` and add your Supabase `DATABASE_URL` and `LISTENNOTES_API_KEY`

**Error: Connection refused**
- Make sure your Supabase database is accessible
- Check that the `DATABASE_URL` in `.env` is correct
- Make sure the password in the URL is URL-encoded (use `%40` instead of `@`)

**Error: Module not found**
- Make sure you're in the conda environment: `conda activate podcharts-backend`
- Install dependencies: `pip install -r requirements.txt` or use the conda environment

### Frontend won't start

**Error: `npm: command not found`**
- Make sure Node.js is installed: `node --version` (should be 18+)
- Install Node.js from https://nodejs.org/

**Error: Port 3000 already in use**
- Kill the process using port 3000: `lsof -ti:3000 | xargs kill -9`
- Or use a different port: `npm run dev -- -p 3001`

**Error: Cannot connect to API**
- Make sure the backend is running on port 8000
- Check `NEXT_PUBLIC_API_BASE_URL` in `frontend/.env.local` (defaults to `http://localhost:8000`)
- Or create `frontend/.env.local` with: `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000`

**No data showing**
- Make sure you've run the ingestion script: `cd backend && python scripts/ingest.py`
- Check that the database has data: `python -c "from app.db import get_connection; from psycopg.rows import dict_row; conn = get_connection().__enter__(); cursor = conn.cursor(row_factory=dict_row); cursor.execute('SELECT COUNT(*) as count FROM podcasts'); print(cursor.fetchone())"`

## Running in Production

### Backend (Production)

```bash
cd backend
conda activate podcharts-backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Or use a process manager like `pm2` or `supervisor`.

### Frontend (Production)

```bash
cd frontend
npm run build
npm start
```

Or deploy to Vercel (recommended for Next.js).

## Daily Ingestion

To run the ingestion script manually:

```bash
cd backend
conda activate podcharts-backend
python scripts/ingest.py
```

Or set up the GitHub Actions workflow (`.github/workflows/ingest.yml`) to run automatically.

## Summary

**Two terminals needed:**

1. **Terminal 1 - Backend:**
   ```bash
   cd backend
   conda activate podcharts-backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Terminal 2 - Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

Then visit **http://localhost:3000** in your browser!

