-- episodes: individual podcast episodes
CREATE TABLE IF NOT EXISTS episodes (
  id TEXT PRIMARY KEY,  -- ListenNotes episode ID
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  audio_url TEXT,
  audio_length_seconds INTEGER,  -- Episode duration in seconds
  published_at TIMESTAMPTZ,  -- When episode was published
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on episodes
ALTER TABLE episodes ENABLE ROW LEVEL SECURITY;

-- Allow public read access to episodes
CREATE POLICY "Allow public read access to episodes" ON episodes
  FOR SELECT
  USING (true);

-- episode_metrics_daily: daily episode-level metrics
CREATE TABLE IF NOT EXISTS episode_metrics_daily (
  episode_id TEXT REFERENCES episodes(id) ON DELETE CASCADE,
  captured_on DATE NOT NULL,
  -- Listen time metrics (if available from future APIs)
  total_listen_time_seconds BIGINT DEFAULT 0,  -- Total seconds listened across all users
  unique_listeners INTEGER DEFAULT 0,  -- Number of unique listeners
  completion_rate DOUBLE PRECISION,  -- Average completion rate (0-1)
  -- Proxy metrics (available now)
  episode_age_days INTEGER,  -- Days since publication
  is_new_episode BOOLEAN DEFAULT false,  -- Published within last 7 days
  PRIMARY KEY (episode_id, captured_on)
);

-- Enable RLS on episode_metrics_daily
ALTER TABLE episode_metrics_daily ENABLE ROW LEVEL SECURITY;

-- Allow public read access to episode_metrics_daily
CREATE POLICY "Allow public read access to episode_metrics_daily" ON episode_metrics_daily
  FOR SELECT
  USING (true);

-- podcast_listen_metrics_daily: aggregated podcast-level listen metrics
CREATE TABLE IF NOT EXISTS podcast_listen_metrics_daily (
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  captured_on DATE NOT NULL,
  -- Aggregated listen time
  total_listen_time_seconds BIGINT DEFAULT 0,  -- Sum of all episode listen times
  total_unique_listeners INTEGER DEFAULT 0,  -- Sum of unique listeners across episodes
  average_completion_rate DOUBLE PRECISION,  -- Average completion rate
  -- Episode activity metrics
  new_episodes_count INTEGER DEFAULT 0,  -- Episodes published in last 7 days
  total_episodes_count INTEGER DEFAULT 0,  -- Total episodes for podcast
  active_episodes_count INTEGER DEFAULT 0,  -- Episodes with listen activity
  -- Engagement score (composite metric)
  engagement_score DOUBLE PRECISION,  -- Composite score based on listen time, listeners, new episodes
  PRIMARY KEY (podcast_id, captured_on)
);

-- Enable RLS on podcast_listen_metrics_daily
ALTER TABLE podcast_listen_metrics_daily ENABLE ROW LEVEL SECURITY;

-- Allow public read access to podcast_listen_metrics_daily
CREATE POLICY "Allow public read access to podcast_listen_metrics_daily" ON podcast_listen_metrics_daily
  FOR SELECT
  USING (true);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_episodes_podcast ON episodes(podcast_id);
CREATE INDEX IF NOT EXISTS idx_episodes_published ON episodes(published_at);
CREATE INDEX IF NOT EXISTS idx_episode_metrics_date ON episode_metrics_daily(captured_on);
CREATE INDEX IF NOT EXISTS idx_episode_metrics_episode ON episode_metrics_daily(episode_id, captured_on);
CREATE INDEX IF NOT EXISTS idx_podcast_listen_metrics_date ON podcast_listen_metrics_daily(captured_on);
CREATE INDEX IF NOT EXISTS idx_podcast_listen_metrics_podcast ON podcast_listen_metrics_daily(podcast_id, captured_on);

