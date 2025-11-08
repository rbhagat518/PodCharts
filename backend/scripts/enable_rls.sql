-- Enable Row Level Security (RLS) on all tables
-- This script can be run directly in Supabase SQL Editor

-- Enable RLS on podcasts (public read access)
ALTER TABLE podcasts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access to podcasts" ON podcasts;
CREATE POLICY "Allow public read access to podcasts" ON podcasts
  FOR SELECT
  USING (true);

-- Enable RLS on ranks_daily (public read access)
ALTER TABLE ranks_daily ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access to ranks_daily" ON ranks_daily;
CREATE POLICY "Allow public read access to ranks_daily" ON ranks_daily
  FOR SELECT
  USING (true);

-- Enable RLS on metrics_daily (public read access)
ALTER TABLE metrics_daily ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Allow public read access to metrics_daily" ON metrics_daily;
CREATE POLICY "Allow public read access to metrics_daily" ON metrics_daily
  FOR SELECT
  USING (true);

-- Enable RLS on users (users can only access their own data)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own data" ON users;
CREATE POLICY "Users can view own data" ON users
  FOR SELECT
  USING (auth.uid() = id);

DROP POLICY IF EXISTS "Users can update own data" ON users;
CREATE POLICY "Users can update own data" ON users
  FOR UPDATE
  USING (auth.uid() = id);

-- Enable RLS on user_watchlists (users can only access their own watchlist)
ALTER TABLE user_watchlists ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own watchlist" ON user_watchlists;
CREATE POLICY "Users can view own watchlist" ON user_watchlists
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own watchlist" ON user_watchlists;
CREATE POLICY "Users can manage own watchlist" ON user_watchlists
  FOR ALL
  USING (auth.uid() = user_id);

-- Enable RLS on user_alerts (users can only access their own alerts)
ALTER TABLE user_alerts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own alerts" ON user_alerts;
CREATE POLICY "Users can view own alerts" ON user_alerts
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Users can manage own alerts" ON user_alerts;
CREATE POLICY "Users can manage own alerts" ON user_alerts
  FOR ALL
  USING (auth.uid() = user_id);

-- Enable RLS on api_usage (users can only view their own usage)
ALTER TABLE api_usage ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Users can view own API usage" ON api_usage;
CREATE POLICY "Users can view own API usage" ON api_usage
  FOR SELECT
  USING (auth.uid() = user_id);

DROP POLICY IF EXISTS "Service role can insert API usage" ON api_usage;
CREATE POLICY "Service role can insert API usage" ON api_usage
  FOR INSERT
  WITH CHECK (true);

