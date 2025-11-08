"""Ingest episode data from ListenNotes API and compute listen metrics."""
from __future__ import annotations

import logging
import os
from datetime import date, timedelta
from typing import Any

import httpx
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row


LISTENNOTES_BASE_URL = "https://listen-api.listennotes.com/api/v2"


def load_settings() -> dict[str, Any]:
    load_dotenv()
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    api_key = os.environ.get("LISTENNOTES_API_KEY")
    if not api_key:
        raise RuntimeError("LISTENNOTES_API_KEY is required")

    return {
        "database_url": database_url,
        "api_key": api_key,
    }


def fetch_podcast_episodes(
    client: httpx.Client,
    podcast_id: str,
    *,
    next_episode_pub_date: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch episodes for a podcast from ListenNotes API."""
    # Use the /podcasts/{id} endpoint which returns podcast info with episodes
    params: dict[str, Any] = {
        "sort": "recent_first",
    }
    if next_episode_pub_date:
        params["next_episode_pub_date"] = next_episode_pub_date

    try:
        response = client.get(
            f"/podcasts/{podcast_id}",
            params=params,
            timeout=30.0,
        )
        response.raise_for_status()
        payload = response.json()
        
        # Get episodes from the response
        # ListenNotes API returns episodes in the response
        episodes = payload.get("episodes", [])
        
        # If no episodes in direct response, try fetching from episodes endpoint
        if not episodes:
            # Try the episodes endpoint directly
            episodes_response = client.get(
                f"/podcasts/{podcast_id}/episodes",
                params={"sort": "recent_first", "page_size": 10},
                timeout=30.0,
            )
            if episodes_response.status_code == 200:
                episodes_payload = episodes_response.json()
                episodes = episodes_payload.get("episodes", [])
        
        return episodes
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            logging.warning("Podcast %s not found", podcast_id)
            return []
        raise


def upsert_episodes(cursor, episodes: list[dict[str, Any]], podcast_id: str) -> None:
    """Upsert episodes into the database."""
    if not episodes:
        return

    tuples = []
    for ep in episodes:
        ep_id = ep.get("id")
        if not ep_id:
            continue

        published_at = None
        if ep.get("pub_date_ms"):
            try:
                from datetime import datetime
                published_at = datetime.fromtimestamp(ep["pub_date_ms"] / 1000)
            except (ValueError, TypeError):
                pass

        tuples.append((
            ep_id,
            podcast_id,
            ep.get("title", "Untitled Episode"),
            ep.get("description", ""),
            ep.get("audio", ""),
            ep.get("audio_length_sec"),
            published_at,
        ))

    if not tuples:
        return

    cursor.executemany(
        """
        INSERT INTO episodes (id, podcast_id, title, description, audio_url, audio_length_seconds, published_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET title = EXCLUDED.title,
            description = EXCLUDED.description,
            audio_url = EXCLUDED.audio_url,
            audio_length_seconds = EXCLUDED.audio_length_seconds,
            published_at = EXCLUDED.published_at,
            updated_at = now()
        """,
        tuples,
    )


def compute_episode_metrics(conn, captured_on: date) -> None:
    """Compute episode-level metrics based on available data."""
    with conn.cursor(row_factory=dict_row) as cursor:
        # Get all episodes published in the last 30 days
        cutoff_date = captured_on - timedelta(days=30)
        
        cursor.execute(
            """
            SELECT 
                e.id as episode_id,
                e.podcast_id,
                e.published_at,
                e.audio_length_seconds,
                CASE 
                    WHEN e.published_at >= %s - INTERVAL '7 days' THEN true
                    ELSE false
                END as is_new_episode,
                EXTRACT(EPOCH FROM (%s - e.published_at)) / 86400 as episode_age_days
            FROM episodes e
            WHERE e.published_at IS NOT NULL
            AND e.published_at >= %s
            """,
            (captured_on, captured_on, cutoff_date),
        )
        
        episodes = cursor.fetchall()
        
        if not episodes:
            logging.info("No episodes to compute metrics for %s", captured_on)
            return

        entries = []
        for ep in episodes:
            entries.append((
                ep["episode_id"],
                captured_on,
                0,  # total_listen_time_seconds (placeholder - will be populated when we have real data)
                0,  # unique_listeners (placeholder)
                None,  # completion_rate (placeholder)
                int(ep["episode_age_days"]) if ep["episode_age_days"] else None,
                ep["is_new_episode"],
            ))

        cursor.executemany(
            """
            INSERT INTO episode_metrics_daily (
                episode_id, captured_on, total_listen_time_seconds, unique_listeners,
                completion_rate, episode_age_days, is_new_episode
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (episode_id, captured_on) DO UPDATE
            SET episode_age_days = EXCLUDED.episode_age_days,
                is_new_episode = EXCLUDED.is_new_episode
            """,
            entries,
        )


def compute_podcast_listen_metrics(conn, captured_on: date) -> None:
    """Aggregate episode metrics to podcast level."""
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            WITH episode_stats AS (
                SELECT 
                    e.podcast_id,
                    COUNT(DISTINCT e.id) as total_episodes,
                    COUNT(DISTINCT CASE WHEN em.is_new_episode THEN e.id END) as new_episodes,
                    COUNT(DISTINCT CASE WHEN em.total_listen_time_seconds > 0 THEN e.id END) as active_episodes,
                    COALESCE(SUM(em.total_listen_time_seconds), 0) as total_listen_time,
                    COALESCE(SUM(em.unique_listeners), 0) as total_listeners,
                    AVG(em.completion_rate) as avg_completion_rate
                FROM episodes e
                LEFT JOIN episode_metrics_daily em ON em.episode_id = e.id AND em.captured_on = %s
                WHERE e.published_at IS NOT NULL
                AND e.published_at >= %s - INTERVAL '30 days'
                GROUP BY e.podcast_id
            )
            INSERT INTO podcast_listen_metrics_daily (
                podcast_id, captured_on, total_listen_time_seconds, total_unique_listeners,
                average_completion_rate, new_episodes_count, total_episodes_count,
                active_episodes_count, engagement_score
            )
            SELECT 
                podcast_id,
                %s as captured_on,
                total_listen_time as total_listen_time_seconds,
                total_listeners as total_unique_listeners,
                avg_completion_rate as average_completion_rate,
                new_episodes as new_episodes_count,
                total_episodes as total_episodes_count,
                active_episodes as active_episodes_count,
                -- Engagement score: weighted combination of metrics
                CASE 
                    WHEN total_episodes > 0 THEN
                        (COALESCE(new_episodes::DOUBLE PRECISION / NULLIF(total_episodes, 0), 0) * 0.3) +
                        (COALESCE(active_episodes::DOUBLE PRECISION / NULLIF(total_episodes, 0), 0) * 0.4) +
                        (COALESCE(avg_completion_rate, 0) * 0.3)
                    ELSE 0
                END as engagement_score
            FROM episode_stats
            ON CONFLICT (podcast_id, captured_on) DO UPDATE
            SET total_listen_time_seconds = EXCLUDED.total_listen_time_seconds,
                total_unique_listeners = EXCLUDED.total_unique_listeners,
                average_completion_rate = EXCLUDED.average_completion_rate,
                new_episodes_count = EXCLUDED.new_episodes_count,
                total_episodes_count = EXCLUDED.total_episodes_count,
                active_episodes_count = EXCLUDED.active_episodes_count,
                engagement_score = EXCLUDED.engagement_score
            """,
            (captured_on, captured_on, captured_on),
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()
    captured_on = date.today()

    logging.info("Starting episode ingestion for %s", captured_on)

    with httpx.Client(
        base_url=LISTENNOTES_BASE_URL,
        headers={
            "X-ListenAPI-Key": settings["api_key"],
            "User-Agent": "PodCharts/0.1 (+https://podcharts.xyz)",
        },
    ) as client, connect(settings["database_url"]) as conn:
        conn.autocommit = False

        with conn.cursor(row_factory=dict_row) as cursor:
            # Get all podcasts
            cursor.execute("SELECT id FROM podcasts LIMIT 100")  # Limit for testing
            podcasts = cursor.fetchall()

            total_episodes = 0
            for pod in podcasts:
                podcast_id = pod["id"]
                try:
                    episodes = fetch_podcast_episodes(client, podcast_id)
                    if episodes:
                        upsert_episodes(cursor, episodes, podcast_id)
                        total_episodes += len(episodes)
                        logging.info("Fetched %s episodes for podcast %s", len(episodes), podcast_id)
                except Exception as e:
                    logging.error("Failed to fetch episodes for podcast %s: %s", podcast_id, e)
                    continue

            # Compute metrics
            compute_episode_metrics(conn, captured_on)
            compute_podcast_listen_metrics(conn, captured_on)
            conn.commit()

        logging.info("Episode ingestion complete: %s episodes processed", total_episodes)


if __name__ == "__main__":
    main()

