"""Check how many days of data we have."""
from __future__ import annotations

import os
from datetime import date
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

with connect(os.environ.get("DATABASE_URL")) as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        # Check all dates in ranks_daily
        cur.execute("SELECT DISTINCT captured_on FROM ranks_daily ORDER BY captured_on")
        rank_dates = [row['captured_on'] for row in cur.fetchall()]
        
        # Check all dates in metrics_daily
        cur.execute("SELECT DISTINCT captured_on FROM metrics_daily ORDER BY captured_on")
        metric_dates = [row['captured_on'] for row in cur.fetchall()]
        
        print(f"📅 Dates in ranks_daily: {rank_dates}")
        print(f"📅 Dates in metrics_daily: {metric_dates}")
        print(f"\n📊 Summary:")
        print(f"   Ranks data: {len(rank_dates)} day(s)")
        print(f"   Metrics data: {len(metric_dates)} day(s)")
        
        # Check today
        today = date.today()
        cur.execute("SELECT COUNT(*) as count FROM ranks_daily WHERE captured_on = %s", (today,))
        today_ranks = cur.fetchone()['count']
        
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (today,))
        today_metrics = cur.fetchone()['count']
        
        print(f"\n📅 Today ({today}):")
        print(f"   Ranks: {today_ranks} records")
        print(f"   Metrics: {today_metrics} records")
        
        if today_ranks == 0 and today_metrics == 0:
            print(f"\n💡 No data for today yet. The GitHub Actions workflow may not have run yet.")
        
        # Show counts for each date
        print(f"\n📋 Records per date:")
        for d in metric_dates:
            cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (d,))
            count = cur.fetchone()['count']
            print(f"   {d}: {count} records")

