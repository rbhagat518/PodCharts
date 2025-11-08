"""Check momentum computation."""
from __future__ import annotations

import os
from datetime import date, timedelta
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

with connect(os.environ.get("DATABASE_URL")) as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        # Check latest date
        cur.execute("SELECT MAX(captured_on) as latest FROM metrics_daily")
        latest = cur.fetchone()["latest"]
        print(f"📅 Latest data date: {latest}")
        
        # Check if we have historical data
        today = date.today()
        seven_days_ago = latest - timedelta(days=7)
        thirty_days_ago = latest - timedelta(days=30)
        
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (seven_days_ago,))
        seven_days_data = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (thirty_days_ago,))
        thirty_days_data = cur.fetchone()["count"]
        
        print(f"\n📊 Historical Data Check:")
        print(f"   7 days ago ({seven_days_ago}): {seven_days_data} records")
        print(f"   30 days ago ({thirty_days_ago}): {thirty_days_data} records")
        
        # Check momentum statistics
        cur.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(momentum_score) as with_momentum,
                COUNT(*) FILTER (WHERE momentum_score IS NULL) as null_momentum,
                AVG(momentum_score) as avg_momentum,
                MIN(momentum_score) as min_momentum,
                MAX(momentum_score) as max_momentum
            FROM metrics_daily
            WHERE captured_on = %s
        """, (latest,))
        stats = cur.fetchone()
        print(f"\n📈 Momentum Statistics (for {latest}):")
        print(f"   Total records: {stats['total']}")
        print(f"   With momentum: {stats['with_momentum']}")
        print(f"   Null momentum: {stats['null_momentum']}")
        if stats['avg_momentum']:
            print(f"   Avg momentum: {stats['avg_momentum']:.2f}")
            print(f"   Min momentum: {stats['min_momentum']:.2f}")
            print(f"   Max momentum: {stats['max_momentum']:.2f}")
        
        # Check deltas
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE delta_7d IS NOT NULL) as has_delta_7d,
                COUNT(*) FILTER (WHERE delta_30d IS NOT NULL) as has_delta_30d,
                COUNT(*) FILTER (WHERE delta_7d IS NULL AND delta_30d IS NULL) as no_deltas
            FROM metrics_daily
            WHERE captured_on = %s
        """, (latest,))
        delta_stats = cur.fetchone()
        print(f"\n📊 Delta Statistics:")
        print(f"   Has delta_7d: {delta_stats['has_delta_7d']}")
        print(f"   Has delta_30d: {delta_stats['has_delta_30d']}")
        print(f"   No deltas: {delta_stats['no_deltas']}")
        
        # Show sample records
        cur.execute("""
            SELECT 
                p.title,
                m.rank,
                m.delta_7d,
                m.delta_30d,
                m.momentum_score
            FROM metrics_daily m
            JOIN podcasts p ON p.id = m.podcast_id
            WHERE m.captured_on = %s
            ORDER BY m.rank ASC
            LIMIT 5
        """, (latest,))
        print(f"\n📋 Sample Records:")
        for row in cur.fetchall():
            delta_7d = f"Δ7d: {row['delta_7d']}" if row['delta_7d'] is not None else "Δ7d: null"
            delta_30d = f"Δ30d: {row['delta_30d']}" if row['delta_30d'] is not None else "Δ30d: null"
            momentum = f"M: {row['momentum_score']:.2f}" if row['momentum_score'] is not None else "M: null"
            print(f"   {row['title'][:45]}")
            print(f"      Rank: {row['rank']}, {delta_7d}, {delta_30d}, {momentum}")
        
        # Check all dates
        cur.execute("SELECT DISTINCT captured_on FROM metrics_daily ORDER BY captured_on")
        dates = [row['captured_on'] for row in cur.fetchall()]
        print(f"\n📅 All dates with data: {dates}")
        print(f"   Number of days: {len(dates)}")
        
        # Explain why momentum is null
        if len(dates) < 2:
            print(f"\n💡 Why momentum is null:")
            print(f"   - Momentum requires historical data (7d and/or 30d ago)")
            print(f"   - You only have {len(dates)} day(s) of data")
            print(f"   - After 7+ days of ingestion, momentum will populate automatically")
        elif stats['null_momentum'] > 0:
            print(f"\n💡 Momentum computation:")
            print(f"   - Formula: momentum = 0.7 * delta_7d + 0.3 * delta_30d")
            print(f"   - Requires at least one delta (7d or 30d)")
            print(f"   - {stats['null_momentum']} records have null momentum (no historical data)")
            print(f"   - {stats['with_momentum']} records have momentum scores")

