"""Create synthetic historical data for testing momentum computation."""
from __future__ import annotations

import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

# Import compute_metrics from ingest
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.ingest import compute_metrics

load_dotenv()

def create_synthetic_history(days: int = 7) -> None:
    """Create synthetic historical data by copying existing data to previous dates."""
    with connect(os.environ.get("DATABASE_URL")) as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            # Get the latest date with data
            cur.execute("SELECT MAX(captured_on) as latest FROM metrics_daily")
            latest = cur.fetchone()["latest"]
            
            if not latest:
                print("❌ No existing data found. Please run ingest.py first.")
                return
            
            print(f"📅 Latest data date: {latest}")
            print(f"📊 Creating synthetic history for {days} days...")
            
            # Get all metrics from the latest date
            cur.execute("""
                SELECT podcast_id, rank
                FROM metrics_daily
                WHERE captured_on = %s
                ORDER BY rank
            """, (latest,))
            latest_metrics = cur.fetchall()
            
            if not latest_metrics:
                print("❌ No metrics found for latest date.")
                return
            
            print(f"   Found {len(latest_metrics)} podcasts")
            
            # Create synthetic data for each previous day
            for day_offset in range(1, days + 1):
                synthetic_date = latest - timedelta(days=day_offset)
                
                # Check if data already exists for this date
                cur.execute("SELECT COUNT(*) as count FROM metrics_daily WHERE captured_on = %s", (synthetic_date,))
                existing = cur.fetchone()["count"]
                
                if existing > 0:
                    print(f"   ⚠️  Data already exists for {synthetic_date}, skipping...")
                    continue
                
                # Create synthetic ranks with some variation
                entries = []
                for metric in latest_metrics:
                    base_rank = metric["rank"]
                    # Add random variation: -5 to +5, but keep rank >= 1
                    variation = random.randint(-5, 5)
                    synthetic_rank = max(1, base_rank + variation)
                    
                    entries.append((
                        metric["podcast_id"],
                        synthetic_date,
                        synthetic_rank,
                        None,  # delta_7d
                        None,  # delta_30d
                        None,  # momentum_score
                    ))
                
                # Insert using executemany with a fresh cursor
                with conn.cursor() as insert_cur:
                    insert_cur.executemany("""
                        INSERT INTO metrics_daily (podcast_id, captured_on, rank, delta_7d, delta_30d, momentum_score)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        ON CONFLICT (podcast_id, captured_on) DO UPDATE
                        SET rank = EXCLUDED.rank
                    """, entries)
                
                conn.commit()
                print(f"   ✅ Created {len(entries)} records for {synthetic_date}")
            
            # Now recompute metrics for the latest date using the existing function
            print(f"\n🔄 Recomputing metrics for {latest}...")
            compute_metrics(conn, latest)
            conn.commit()
            print(f"   ✅ Recomputed metrics")
            
            # Check results
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(momentum_score) as with_momentum,
                    AVG(momentum_score) as avg_momentum,
                    MIN(momentum_score) as min_momentum,
                    MAX(momentum_score) as max_momentum
                FROM metrics_daily
                WHERE captured_on = %s
            """, (latest,))
            stats = cur.fetchone()
            
            print(f"\n✅ Synthetic history created!")
            print(f"   Total records: {stats['total']}")
            print(f"   With momentum: {stats['with_momentum']}")
            if stats['avg_momentum']:
                print(f"   Avg momentum: {stats['avg_momentum']:.2f}")
                print(f"   Min momentum: {stats['min_momentum']:.2f}")
                print(f"   Max momentum: {stats['max_momentum']:.2f}")
            
            # Show sample records with momentum
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
                AND m.momentum_score IS NOT NULL
                ORDER BY m.momentum_score DESC
                LIMIT 5
            """, (latest,))
            print(f"\n📋 Top 5 by Momentum:")
            for row in cur.fetchall():
                delta_7d = f"Δ7d: {row['delta_7d']}" if row['delta_7d'] is not None else "Δ7d: null"
                delta_30d = f"Δ30d: {row['delta_30d']}" if row['delta_30d'] is not None else "Δ30d: null"
                momentum = f"M: {row['momentum_score']:.2f}" if row['momentum_score'] is not None else "M: null"
                print(f"   {row['title'][:45]}")
                print(f"      Rank: {row['rank']}, {delta_7d}, {delta_30d}, {momentum}")


if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    create_synthetic_history(days)

