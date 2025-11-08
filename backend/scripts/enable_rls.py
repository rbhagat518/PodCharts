"""Enable Row Level Security (RLS) on all tables in Supabase/Postgres."""
from __future__ import annotations

import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect

RLS_FILE = Path(__file__).parent.parent.parent / "backend" / "scripts" / "enable_rls.sql"


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    load_dotenv()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is required")

    if not RLS_FILE.exists():
        raise RuntimeError(f"RLS file not found: {RLS_FILE}")

    rls_sql = RLS_FILE.read_text()
    logging.info("Connecting to database...")

    with connect(database_url) as conn:
        with conn.cursor() as cursor:
            logging.info("Enabling RLS on all tables...")
            cursor.execute(rls_sql)
            conn.commit()
            logging.info("RLS enabled successfully!")

        # Verify RLS is enabled
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT tablename, rowsecurity
                FROM pg_tables
                WHERE schemaname = 'public'
                AND tablename IN ('podcasts', 'ranks_daily', 'metrics_daily', 'users', 'user_watchlists', 'user_alerts', 'api_usage')
                ORDER BY tablename
                """
            )
            tables = cursor.fetchall()
            logging.info("RLS status:")
            for table_name, rls_enabled in tables:
                status = "✅ Enabled" if rls_enabled else "❌ Disabled"
                logging.info(f"  {table_name}: {status}")


if __name__ == "__main__":
    main()

