from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterable

import httpx
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row


LISTENNOTES_BASE_URL = "https://listen-api.listennotes.com/api/v2"
DEFAULT_CATEGORIES: list[tuple[int | None, str]] = [
    (None, "top"),
    (93, "technology"),
    (99, "news"),
    (67, "comedy"),
    (68, "business"),
    (88, "health"),
    (140, "education"),
]


@dataclass
class RankedPodcast:
    podcast_id: str
    title: str
    publisher: str | None
    category: str | None
    rss_url: str | None
    country: str
    rank: int
    captured_on: date
    source: str = "listennotes"


def load_settings() -> dict[str, Any]:
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

    categories = DEFAULT_CATEGORIES
    return {
        "database_url": database_url,
        "api_key": api_key,
        "limit": max(1, min(limit, 50)),
        "regions": regions,
        "categories": categories,
    }


def fetch_category(
    client: httpx.Client,
    *,
    genre_id: int | None,
    category_slug: str,
    region: str,
    limit: int,
    captured_on: date,
) -> list[RankedPodcast]:
    params: dict[str, Any] = {
        "page": 1,
        "region": region.upper(),
        "page_size": limit,
        "safe_mode": 0,
    }
    if genre_id is not None:
        params["genre_id"] = genre_id

    response = client.get("/best_podcasts", params=params, timeout=30.0)
    response.raise_for_status()
    payload = response.json()
    podcasts = payload.get("podcasts", [])

    ranked: list[RankedPodcast] = []
    for idx, item in enumerate(podcasts, start=1):
        ranked.append(
            RankedPodcast(
                podcast_id=item.get("id"),
                title=item.get("title", "Untitled"),
                publisher=item.get("publisher"),
                category=category_slug,
                rss_url=item.get("rss"),
                country=region.lower() if region else "global",
                rank=idx,
                captured_on=captured_on,
            )
        )
    return ranked


def upsert_podcasts(cursor, records: Iterable[RankedPodcast]) -> None:
    tuples = [
        (
            r.podcast_id,
            r.title,
            r.publisher,
            r.category,
            r.rss_url,
            r.country,
        )
        for r in records
    ]
    if not tuples:
        return

    cursor.executemany(
        """
        INSERT INTO podcasts (id, title, publisher, category, rss_url, country)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET title = EXCLUDED.title,
            publisher = EXCLUDED.publisher,
            category = EXCLUDED.category,
            rss_url = EXCLUDED.rss_url,
            country = EXCLUDED.country
        """,
        tuples,
    )


def upsert_ranks(cursor, records: Iterable[RankedPodcast]) -> None:
    tuples = [
        (
            r.podcast_id,
            r.source,
            r.rank,
            r.country,
            r.captured_on,
        )
        for r in records
    ]
    if not tuples:
        return

    cursor.executemany(
        """
        INSERT INTO ranks_daily (podcast_id, source, rank, country, captured_on)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (podcast_id, source, captured_on, country) DO UPDATE
        SET rank = EXCLUDED.rank
        """,
        tuples,
    )


def compute_metrics(conn, captured_on: date) -> None:
    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(
            """
            SELECT podcast_id, rank
            FROM ranks_daily
            WHERE source = 'listennotes' AND captured_on = %s
            """,
            (captured_on,),
        )
        today_rows = cursor.fetchall()
        if not today_rows:
            logging.info("No ranks to compute metrics for %s", captured_on)
            return

        def fetch_reference(day: date) -> dict[str, int]:
            cursor.execute(
                "SELECT podcast_id, rank FROM metrics_daily WHERE captured_on = %s",
                (day,),
            )
            return {row["podcast_id"]: row["rank"] for row in cursor.fetchall()}

        prev7 = fetch_reference(captured_on - timedelta(days=7))
        prev30 = fetch_reference(captured_on - timedelta(days=30))

        entries: list[tuple[Any, ...]] = []
        for row in today_rows:
            podcast_id = row["podcast_id"]
            rank = row["rank"]
            delta_7d = prev7.get(podcast_id)
            delta_30d = prev30.get(podcast_id)

            delta_7d_val = delta_7d - rank if delta_7d is not None else None
            delta_30d_val = delta_30d - rank if delta_30d is not None else None

            momentum_score: float | None = None
            weights = []
            values = []
            if delta_7d_val is not None:
                weights.append(0.7)
                values.append(delta_7d_val)
            if delta_30d_val is not None:
                weights.append(0.3)
                values.append(delta_30d_val)
            if values:
                momentum_score = sum(w * v for w, v in zip(weights, values))

            entries.append(
                (podcast_id, captured_on, rank, delta_7d_val, delta_30d_val, momentum_score)
            )

        cursor.executemany(
            """
            INSERT INTO metrics_daily (podcast_id, captured_on, rank, delta_7d, delta_30d, momentum_score)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (podcast_id, captured_on) DO UPDATE
            SET rank = EXCLUDED.rank,
                delta_7d = EXCLUDED.delta_7d,
                delta_30d = EXCLUDED.delta_30d,
                momentum_score = EXCLUDED.momentum_score
            """,
            entries,
        )


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    settings = load_settings()
    captured_on = date.today()

    logging.info("Starting ListenNotes ingestion for %s", captured_on)

    with httpx.Client(
        base_url=LISTENNOTES_BASE_URL,
        headers={
            "X-ListenAPI-Key": settings["api_key"],
            "User-Agent": "PodCharts/0.1 (+https://podcharts.xyz)",
        },
    ) as client, connect(settings["database_url"]) as conn:
        conn.autocommit = False
        total_inserted = 0

        with conn.cursor() as cursor:
            for region in settings["regions"]:
                for genre_id, slug in settings["categories"]:
                    try:
                        records = fetch_category(
                            client,
                            genre_id=genre_id,
                            category_slug=slug,
                            region=region,
                            limit=settings["limit"],
                            captured_on=captured_on,
                        )
                    except httpx.HTTPStatusError as exc:
                        logging.error("Failed to fetch %s (%s): %s", slug, region, exc)
                        continue

                    if not records:
                        logging.warning("No podcasts returned for %s (%s)", slug, region)
                        continue

                    upsert_podcasts(cursor, records)
                    upsert_ranks(cursor, records)
                    total_inserted += len(records)
                    logging.info("Fetched %s records for %s (%s)", len(records), slug, region)

            compute_metrics(conn, captured_on)
            conn.commit()

        logging.info("Ingestion complete: %s rank rows processed", total_inserted)


if __name__ == "__main__":
    main()


