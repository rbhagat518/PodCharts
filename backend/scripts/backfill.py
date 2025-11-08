"""Backfill historical data by running ingestion for past dates."""
from __future__ import annotations

import logging
import os
import sys
from datetime import date, timedelta

import httpx
from dotenv import load_dotenv
from psycopg import connect

# Import the ingestion functions
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.ingest import (
    DEFAULT_CATEGORIES,
    fetch_category,
    upsert_podcasts,
    upsert_ranks,
    compute_metrics,
)


def backfill_days(days: int = 7) -> None:
    """Backfill data for the past N days."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    api_key = os.environ.get("LISTENNOTES_API_KEY")
    if not api_key:
        raise RuntimeError("LISTENNOTES_API_KEY is required")

    limit = int(os.environ.get("LISTENNOTES_LIMIT", "50"))
    regions = os.environ.get("LISTENNOTES_REGIONS", "us").split(",")
    regions = [r.strip().lower() for r in regions if r.strip()]
    if not regions:
        regions = ["us"]

    today = date.today()

    with httpx.Client(
        base_url=LISTENNOTES_BASE_URL,
        headers={
            "X-ListenAPI-Key": api_key,
            "User-Agent": "PodCharts/0.1 (+https://podcharts.xyz)",
        },
    ) as client, connect(database_url) as conn:
        conn.autocommit = False

        # Backfill for each day
        for day_offset in range(days, 0, -1):
            captured_on = today - timedelta(days=day_offset)
            logging.info("Backfilling data for %s", captured_on)

            total_inserted = 0
            with conn.cursor() as cursor:
                for region in regions:
                    for genre_id, slug in DEFAULT_CATEGORIES:
                        try:
                            records = fetch_category(
                                client,
                                genre_id=genre_id,
                                category_slug=slug,
                                region=region,
                                limit=limit,
                                captured_on=captured_on,
                            )
                        except httpx.HTTPStatusError as exc:
                            logging.error("Failed to fetch %s (%s) for %s: %s", slug, region, captured_on, exc)
                            continue

                        if not records:
                            logging.warning("No podcasts returned for %s (%s) on %s", slug, region, captured_on)
                            continue

                        upsert_podcasts(cursor, records)
                        upsert_ranks(cursor, records)
                        total_inserted += len(records)
                        logging.info("Fetched %s records for %s (%s) on %s", len(records), slug, region, captured_on)

                # Compute metrics for this day
                compute_metrics(conn, captured_on)
                conn.commit()

            logging.info("Backfilled %s records for %s", total_inserted, captured_on)

        logging.info("Backfill complete!")


if __name__ == "__main__":
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    logging.info("Starting backfill for the past %s days", days)
    backfill_days(days)

