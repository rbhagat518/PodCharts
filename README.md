## PodCharts

Make the podcast world transparent. PodCharts is the public scoreboard for podcasts: a live, data‑driven dashboard that tracks rankings, growth, and momentum across every category.

### Why PodCharts

Today, creators, fans, and brands have no unified way to see which podcasts are rising, which are consistent, and which are shaping the conversation. Unlike YouTube or Twitch—where public analytics drive discovery—podcasting data is fragmented, hidden across platforms, and difficult to analyze.

PodCharts’ purpose is to become the public scoreboard for podcasts: a transparent, credible, and continuously updating source of truth for podcast performance.

### High‑Level Objectives

- **Aggregate**: Ingest podcast performance data (Spotify, Apple, ListenNotes, etc.).
- **Visualize**: Show daily/weekly rankings in a StreamerCharts-style interface.
- **Compute**: Derive transparent metrics for growth and momentum.
- **Discover**: Filter by category, country, and compare shows.
- **Share**: Create shareable insights and promo assets for creators.
- **Monetize**: Offer premium analytics and B2B data access.

---

## Roadmap

### Phase 1 – Foundation (Week 1–2)

- [ ] Set up repo & environment
  - Initialize monorepo (`frontend/`, `backend/`, `infra/`)
  - Configure `.env`, Python (Poetry/pipenv), and Next.js (npm)
- [ ] Create database schema in Postgres/Supabase (`podcasts`, `ranks_daily`, `metrics_daily`)
- [ ] Implement ingestion scripts
  - Pull top podcasts from ListenNotes / Spotify charts
  - Store title, publisher, category, rank, country, date
  - Schedule daily cron (GitHub Actions or Railway cron)
- [ ] Compute metrics
  - Rank deltas (7d / 30d)
  - Momentum score formula
  - Write to `metrics_daily`

### Phase 2 – Core Backend (Week 2–3)

- [ ] Build FastAPI endpoints
  - `/leaderboard?category=` – list top shows
  - `/podcast/{id}` – details & history
  - `/compare?id1=&id2=` – two‑show comparison
- [ ] Add caching layer (Redis/Upstash)
- [ ] Add logging + error handling
- [ ] Deploy backend (Render/Railway)

### Phase 3 – Frontend MVP (Week 3–4)

- [ ] Scaffold Next.js + Tailwind project
- [ ] Create pages
  - `/leaderboard` – sortable table
  - `/podcast/[id]` – chart of rank history
  - `/compare` – side‑by‑side chart
- [ ] Connect to API, add category filters
- [ ] Implement Recharts/D3.js visuals
- [ ] Optimize for SEO (static metadata per category)
- [ ] Deploy on Vercel

### Phase 4 – Pro Features (Week 5–6)

- [ ] Integrate Supabase Auth (email/social)
- [ ] Add Stripe Checkout (Pro subscriptions)
- [ ] Gate advanced views (longer history, compare, CSV export)
- [ ] Generate shareable PNG rank cards
- [ ] Build "My Dashboard" page for followed shows

### Phase 5 – Launch & Growth (Week 6–8)

- [ ] Populate 5–10 categories (Tech, Comedy, News, Business, Health, …)
- [ ] Landing page copy (“See who’s rising in podcasting”)
- [ ] Publish beta (Reddit / IndieHackers / Twitter)
- [ ] Add analytics (Plausible / PostHog)
- [ ] Collect feedback & bug reports
- [ ] Ship weekly newsletter (“PodCharts Top 10 Risers”)

### Phase 6 – Iteration (Ongoing)

- [ ] Integrate Apple/Spotify reviews & episode frequency
- [ ] Add guest‑graph (shared guest detection)
- [ ] Topic embeddings for “Rising Topics”
- [ ] Offer API access & agency dashboards
- [ ] Automate PDF “Podcast Influence Reports”

---

## Architecture

- **Monorepo**: `frontend/` (Next.js), `backend/` (FastAPI), `infra/` (IaC/CI)
- **Database**: Postgres (Supabase compatible)
- **Cache**: Redis/Upstash
- **Storage**: Postgres tables for historical metrics
- **Deploy**: Vercel (frontend), Render/Railway (backend), GitHub Actions (cron)

### Initial Data Model (draft)

```sql
-- podcasts: unique shows
CREATE TABLE podcasts (
  id TEXT PRIMARY KEY,            -- stable external ID or ULID
  title TEXT NOT NULL,
  publisher TEXT,
  category TEXT,
  rss_url TEXT,
  country TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- ranks_daily: raw daily ranks by source
CREATE TABLE ranks_daily (
  podcast_id TEXT REFERENCES podcasts(id),
  source TEXT NOT NULL,           -- e.g., 'listennotes', 'spotify'
  rank INTEGER NOT NULL,
  country TEXT,
  captured_on DATE NOT NULL,
  PRIMARY KEY (podcast_id, source, captured_on, COALESCE(country, ''))
);

-- metrics_daily: derived metrics
CREATE TABLE metrics_daily (
  podcast_id TEXT REFERENCES podcasts(id),
  captured_on DATE NOT NULL,
  rank INTEGER,                   -- canonicalized rank
  delta_7d INTEGER,
  delta_30d INTEGER,
  momentum_score DOUBLE PRECISION,
  PRIMARY KEY (podcast_id, captured_on)
);
```

### Metrics (draft)

- **Rank Delta (7d/30d)**: difference in canonical rank vs. 7/30 days prior.
- **Momentum Score**: composite of recent improvement and consistency. Example:

```text
momentum = w1 * zscore(-rank_change_7d) + w2 * zscore(-rank_change_30d) + w3 * stability
```

Tune weights and include guardrails for low‑data cases.

---

## API (planned)

Base URL: `https://api.podcharts.xyz` (placeholder)

- `GET /leaderboard?category=&country=&interval=daily`
  - Returns ranked shows with rank, deltas, momentum.

- `GET /podcast/{id}`
  - Returns show details and historical series (`rank`, `delta_7d`, `delta_30d`, `momentum_score`).

- `GET /compare?id1=&id2=`
  - Returns aligned time series for two shows.

---

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- Postgres (or Supabase project)

### Clone

```bash
git clone https://github.com/your-org/podcharts.git
cd podcharts
```

### Monorepo Structure

```text
podcharts/
  backend/
  frontend/
  infra/
```

### Environment

Create `.env` files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.local
```

Populate with Postgres/Supabase, Redis, and API keys (ListenNotes/Spotify, etc.).

### Backend (FastAPI)

```bash
cd backend
poetry install  # or pipenv install
poetry run uvicorn app.main:app --reload  # or equivalent
```

### Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

### Cron / Ingestion

- Add a scheduled workflow in GitHub Actions or Railway cron to run daily ingestion.
- Store raw ranks in `ranks_daily`; compute and persist derived metrics in `metrics_daily`.

---

## Contributing

Issues and PRs are welcome. Please open an issue to discuss significant changes first.

---

## Success Criteria

- First public version online with daily‑updating leaderboards.
- ≥ 100 organic users checking charts weekly.
- ≥ 10 paying Pro creators within 3 months.
- Recognized as the data reference for podcast trends by industry observers.

---

## License

MIT unless noted otherwise.


