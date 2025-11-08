"""Setup episode tables in database."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect

# Load environment variables
load_dotenv()

EPISODE_SCHEMA = """
-- episodes: individual podcast episodes
CREATE TABLE IF NOT EXISTS episodes (
  id TEXT PRIMARY KEY,
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  description TEXT,
  audio_url TEXT,
  audio_length_seconds INTEGER,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Enable RLS on episodes
DO $$ BEGIN
  ALTER TABLE episodes ENABLE ROW LEVEL SECURITY;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- Allow public read access to episodes
DO $$ BEGIN
  CREATE POLICY "Allow public read access to episodes" ON episodes
    FOR SELECT
    USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- episode_metrics_daily: daily episode-level metrics
CREATE TABLE IF NOT EXISTS episode_metrics_daily (
  episode_id TEXT REFERENCES episodes(id) ON DELETE CASCADE,
  captured_on DATE NOT NULL,
  total_listen_time_seconds BIGINT DEFAULT 0,
  unique_listeners INTEGER DEFAULT 0,
  completion_rate DOUBLE PRECISION,
  episode_age_days INTEGER,
  is_new_episode BOOLEAN DEFAULT false,
  PRIMARY KEY (episode_id, captured_on)
);

-- Enable RLS on episode_metrics_daily
DO $$ BEGIN
  ALTER TABLE episode_metrics_daily ENABLE ROW LEVEL SECURITY;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- Allow public read access to episode_metrics_daily
DO $$ BEGIN
  CREATE POLICY "Allow public read access to episode_metrics_daily" ON episode_metrics_daily
    FOR SELECT
    USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- podcast_listen_metrics_daily: aggregated podcast-level listen metrics
CREATE TABLE IF NOT EXISTS podcast_listen_metrics_daily (
  podcast_id TEXT REFERENCES podcasts(id) ON DELETE CASCADE,
  captured_on DATE NOT NULL,
  total_listen_time_seconds BIGINT DEFAULT 0,
  total_unique_listeners INTEGER DEFAULT 0,
  average_completion_rate DOUBLE PRECISION,
  new_episodes_count INTEGER DEFAULT 0,
  total_episodes_count INTEGER DEFAULT 0,
  active_episodes_count INTEGER DEFAULT 0,
  engagement_score DOUBLE PRECISION,
  PRIMARY KEY (podcast_id, captured_on)
);

-- Enable RLS on podcast_listen_metrics_daily
DO $$ BEGIN
  ALTER TABLE podcast_listen_metrics_daily ENABLE ROW LEVEL SECURITY;
EXCEPTION WHEN OTHERS THEN NULL;
END $$;

-- Allow public read access to podcast_listen_metrics_daily
DO $$ BEGIN
  CREATE POLICY "Allow public read access to podcast_listen_metrics_daily" ON podcast_listen_metrics_daily
    FOR SELECT
    USING (true);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_episodes_podcast ON episodes(podcast_id);
CREATE INDEX IF NOT EXISTS idx_episodes_published ON episodes(published_at);
CREATE INDEX IF NOT EXISTS idx_episode_metrics_date ON episode_metrics_daily(captured_on);
CREATE INDEX IF NOT EXISTS idx_episode_metrics_episode ON episode_metrics_daily(episode_id, captured_on);
CREATE INDEX IF NOT EXISTS idx_podcast_listen_metrics_date ON podcast_listen_metrics_daily(captured_on);
CREATE INDEX IF NOT EXISTS idx_podcast_listen_metrics_podcast ON podcast_listen_metrics_daily(podcast_id, captured_on);
"""


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    logging.info("Connecting to database...")
    with connect(database_url) as conn:
        with conn.cursor() as cursor:
            logging.info("Creating episode tables...")
            cursor.execute(EPISODE_SCHEMA)
            conn.commit()
            logging.info("Episode tables created successfully!")

        # Verify tables exist
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('episodes', 'episode_metrics_daily', 'podcast_listen_metrics_daily')
                ORDER BY table_name
                """
            )
            tables = [row[0] for row in cursor.fetchall()]
            logging.info("Created tables: %s", ", ".join(tables) if tables else "none")


if __name__ == "__main__":
    main()

