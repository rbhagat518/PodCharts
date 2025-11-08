"""Setup database schema in Supabase/Postgres."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect

SCHEMA_FILE = Path(__file__).parent.parent.parent / "infra" / "schema.sql"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    if not SCHEMA_FILE.exists():
        raise RuntimeError(f"Schema file not found: {SCHEMA_FILE}")

    schema_sql = SCHEMA_FILE.read_text()
    logging.info("Connecting to database...")

    with connect(database_url) as conn:
        with conn.cursor() as cursor:
            logging.info("Executing schema SQL...")
            cursor.execute(schema_sql)
            conn.commit()
            logging.info("Schema created successfully!")

        # Verify tables exist
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('podcasts', 'ranks_daily', 'metrics_daily')
                ORDER BY table_name
                """
            )
            tables = [row[0] for row in cursor.fetchall()]
            logging.info("Created tables: %s", ", ".join(tables) if tables else "none")


if __name__ == "__main__":
    main()

