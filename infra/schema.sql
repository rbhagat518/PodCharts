-- podcasts: unique shows
CREATE TABLE IF NOT EXISTS podcasts (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  publisher TEXT,
  category TEXT,
  rss_url TEXT,
  country TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on podcasts
ALTER TABLE podcasts ENABLE ROW LEVEL SECURITY;

-- Allow public read access to podcasts (for public API)
CREATE POLICY "Allow public read access to podcasts" ON podcasts
  FOR SELECT
  USING (true);

-- ranks_daily: raw daily ranks by source
CREATE TABLE IF NOT EXISTS ranks_daily (
  podcast_id TEXT REFERENCES podcasts(id),
  source TEXT NOT NULL,
  rank INTEGER NOT NULL,
  country TEXT DEFAULT 'global',
  captured_on DATE NOT NULL,
  PRIMARY KEY (podcast_id, source, captured_on, country)
);

-- Enable RLS on ranks_daily
ALTER TABLE ranks_daily ENABLE ROW LEVEL SECURITY;

-- Allow public read access to ranks_daily
CREATE POLICY "Allow public read access to ranks_daily" ON ranks_daily
  FOR SELECT
  USING (true);

-- metrics_daily: derived metrics
CREATE TABLE IF NOT EXISTS metrics_daily (
  podcast_id TEXT REFERENCES podcasts(id),
  captured_on DATE NOT NULL,
  rank INTEGER,
  delta_7d INTEGER,
  delta_30d INTEGER,
  momentum_score DOUBLE PRECISION,
  PRIMARY KEY (podcast_id, captured_on)
);

-- Enable RLS on metrics_daily
ALTER TABLE metrics_daily ENABLE ROW LEVEL SECURITY;

-- Allow public read access to metrics_daily
CREATE POLICY "Allow public read access to metrics_daily" ON metrics_daily
  FOR SELECT
  USING (true);

-- users: user accounts (using Supabase Auth, this is for additional data)
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,  -- Supabase Auth user ID
  email TEXT UNIQUE,
  subscription_tier TEXT DEFAULT 'free',  -- free, pro, enterprise
  subscription_status TEXT DEFAULT 'active',  -- active, cancelled, expired, past_due
  subscription_id TEXT UNIQUE,  -- Stripe subscription ID
  subscription_expires_at TIMESTAMPTZ,
  api_key TEXT UNIQUE,
  api_quota_monthly INTEGER DEFAULT 1000,  -- API calls per month
  api_calls_used INTEGER DEFAULT 0,
  api_reset_date DATE DEFAULT CURRENT_DATE,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on users
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Users can only read/update their own data
CREATE POLICY "Users can view own data" ON users
  FOR SELECT
  USING (auth.uid() = id);

CREATE POLICY "Users can update own data" ON users
  FOR UPDATE
  USING (auth.uid() = id);

-- user_watchlists: podcasts users follow
CREATE TABLE IF NOT EXISTS user_watchlists (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  created_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, podcast_id)
);

-- Enable RLS on user_watchlists
ALTER TABLE user_watchlists ENABLE ROW LEVEL SECURITY;

-- Users can only access their own watchlist
CREATE POLICY "Users can view own watchlist" ON user_watchlists
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own watchlist" ON user_watchlists
  FOR ALL
  USING (auth.uid() = user_id);

-- user_alerts: alerts for rank changes
CREATE TABLE IF NOT EXISTS user_alerts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  alert_type TEXT NOT NULL,  -- rank_change, momentum_spike, new_episode
  threshold INTEGER,  -- e.g., rank drops below this
  enabled BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on user_alerts
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;

-- Users can only access their own alerts
CREATE POLICY "Users can view own alerts" ON user_alerts
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can manage own alerts" ON user_alerts
  FOR ALL
  USING (auth.uid() = user_id);

-- api_usage: track API usage for rate limiting
CREATE TABLE IF NOT EXISTS api_usage (
  api_key TEXT NOT NULL,
  endpoint TEXT NOT NULL,
  called_at TIMESTAMPTZ DEFAULT now(),
  user_id UUID REFERENCES users(id) ON DELETE SET NULL
);

-- Enable RLS on api_usage
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

-- Users can only view their own API usage
CREATE POLICY "Users can view own API usage" ON api_usage
  FOR SELECT
  USING (auth.uid() = user_id);

-- Service role can insert API usage (for backend tracking)
CREATE POLICY "Service role can insert API usage" ON api_usage
  FOR INSERT
  WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_api_usage_key_date ON api_usage(api_key, called_at);
CREATE INDEX IF NOT EXISTS idx_user_watchlists_user ON user_watchlists(user_id);
CREATE INDEX IF NOT EXISTS idx_user_alerts_user ON user_alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_metrics_daily_podcast ON metrics_daily(podcast_id, captured_on);

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
