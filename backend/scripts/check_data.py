"""Check what data is in the database."""
from __future__ import annotations

import os
from datetime import date
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

with connect(os.environ.get("DATABASE_URL")) as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        # Check podcasts
        cur.execute("SELECT COUNT(*) as count FROM podcasts")
        podcasts_count = cur.fetchone()["count"]
        print(f"📊 Total podcasts: {podcasts_count}")
        
        # Check ranks
        cur.execute("SELECT COUNT(*) as count FROM ranks_daily")
        ranks_count = cur.fetchone()["count"]
        print(f"📊 Total rank records: {ranks_count}")
        
        # Check metrics
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily")
        metrics_count = cur.fetchone()["count"]
        print(f"📊 Total metrics records: {metrics_count}")
        
        # Check dates
        cur.execute("SELECT DISTINCT captured_on FROM ranks_daily ORDER BY captured_on DESC LIMIT 5")
        dates = [row["captured_on"] for row in cur.fetchall()]
        print(f"\n📅 Dates with data: {dates}")
        
        # Check today's data
        today = date.today()
        cur.execute("SELECT COUNT(*) as count FROM ranks_daily WHERE captured_on = %s", (today,))
        today_ranks = cur.fetchone()["count"]
        print(f"\n📅 Today ({today}) rank records: {today_ranks}")
        
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (today,))
        today_metrics = cur.fetchone()["count"]
        print(f"📅 Today ({today}) metrics records: {today_metrics}")
        
        # Show sample data
        if today_metrics > 0:
            cur.execute("""
                SELECT p.title, p.category, m.rank, m.delta_7d, m.delta_30d, m.momentum_score
                FROM metrics_daily m
                JOIN podcasts p ON p.id = m.podcast_id
                WHERE m.captured_on = %s
                ORDER BY m.rank ASC
                LIMIT 10
            """, (today,))
            print(f"\n🏆 Top 10 Podcasts (today):")
            for i, row in enumerate(cur.fetchall(), 1):
                delta_7d = f"Δ7d: {row['delta_7d']}" if row['delta_7d'] is not None else "Δ7d: —"
                momentum = f"M: {row['momentum_score']:.2f}" if row['momentum_score'] is not None else "M: —"
                print(f"   {i}. {row['title'][:50]} (Rank: {row['rank']}, {delta_7d}, {momentum})")
        else:
            # Check if there's any data at all
            cur.execute("""
                SELECT p.title, p.category, m.rank, m.captured_on
                FROM metrics_daily m
                JOIN podcasts p ON p.id = m.podcast_id
                ORDER BY m.captured_on DESC, m.rank ASC
                LIMIT 10
            """)
            rows = cur.fetchall()
            if rows:
                print(f"\n📊 Latest data (not today):")
                for i, row in enumerate(rows, 1):
                    print(f"   {i}. {row['title'][:50]} (Rank: {row['rank']}, Date: {row['captured_on']})")
            else:
                print("\n⚠️  No data found in database")

