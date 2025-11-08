"""Create synthetic historical data for testing momentum computation."""
from __future__ import annotations

import os
import random
from datetime import date, timedelta
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

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
                SELECT podcast_id, rank, delta_7d, delta_30d, momentum_score
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
                
                entries = []
                for metric in latest_metrics:
                    # Create synthetic rank by adding some variation
                    # Rank should be between 1 and ~200 (reasonable range)
                    base_rank = metric["rank"]
                    # Add random variation: -5 to +5, but keep rank >= 1
                    variation = random.randint(-5, 5)
                    synthetic_rank = max(1, base_rank + variation)
                    
                    # For synthetic data, we don't compute deltas yet (they'll be computed when we have more data)
                    entries.append((
                        metric["podcast_id"],
                        synthetic_date,
                        synthetic_rank,
                        None,  # delta_7d
                        None,  # delta_30d
                        None,  # momentum_score
                    ))
                
                # Insert synthetic data using a single VALUES clause
                if entries:
                    values_str = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s)", entry).decode() for entry in entries)
                    cur.execute(f"""
                        INSERT INTO metrics_daily (podcast_id, captured_on, rank, delta_7d, delta_30d, momentum_score)
                        VALUES {values_str}
                        ON CONFLICT (podcast_id, captured_on) DO UPDATE
                        SET rank = EXCLUDED.rank
                    """)
                
                print(f"   ✅ Created {len(entries)} records for {synthetic_date}")
            
            conn.commit()
            
            # Now recompute metrics for the latest date (so it can calculate deltas)
            print(f"\n🔄 Recomputing metrics for {latest}...")
            cur.execute("""
                SELECT podcast_id, rank
                FROM ranks_daily
                WHERE source = 'listennotes' AND captured_on = %s
            """, (latest,))
            today_rows = cur.fetchall()
            
            if not today_rows:
                print("   ⚠️  No ranks found for latest date")
                return
            
            def fetch_reference(day: date) -> dict[str, int]:
                cur.execute(
                    "SELECT podcast_id, rank FROM metrics_daily WHERE captured_on = %s",
                    (day,),
                )
                return {row["podcast_id"]: row["rank"] for row in cur.fetchall()}
            
            prev7 = fetch_reference(latest - timedelta(days=7))
            prev30 = fetch_reference(latest - timedelta(days=30))
            
            entries = []
            for row in today_rows:
                podcast_id = row["podcast_id"]
                rank = row["rank"]
                delta_7d = prev7.get(podcast_id)
                delta_30d = prev30.get(podcast_id)
                
                delta_7d_val = delta_7d - rank if delta_7d is not None else None
                delta_30d_val = delta_30d - rank if delta_30d is not None else None
                
                momentum_score = None
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
                
                entries.append((
                    podcast_id, latest, rank, delta_7d_val, delta_30d_val, momentum_score
                ))
            
            # Update metrics using a single VALUES clause
            if entries:
                values_str = ','.join(cur.mogrify("(%s,%s,%s,%s,%s,%s)", entry).decode() for entry in entries)
                cur.execute(f"""
                    INSERT INTO metrics_daily (podcast_id, captured_on, rank, delta_7d, delta_30d, momentum_score)
                    VALUES {values_str}
                    ON CONFLICT (podcast_id, captured_on) DO UPDATE
                    SET rank = EXCLUDED.rank,
                        delta_7d = EXCLUDED.delta_7d,
                        delta_30d = EXCLUDED.delta_30d,
                        momentum_score = EXCLUDED.momentum_score
                """)
            
            conn.commit()
            print(f"   ✅ Recomputed metrics for {len(entries)} podcasts")
            
            # Check results
            cur.execute("""
                SELECT 
                    COUNT(*) as total,
                    COUNT(momentum_score) as with_momentum,
                    AVG(momentum_score) as avg_momentum
                FROM metrics_daily
                WHERE captured_on = %s
            """, (latest,))
            stats = cur.fetchone()
            
            print(f"\n✅ Synthetic history created!")
            print(f"   Total records: {stats['total']}")
            print(f"   With momentum: {stats['with_momentum']}")
            if stats['avg_momentum']:
                print(f"   Avg momentum: {stats['avg_momentum']:.2f}")


if __name__ == "__main__":
    import sys
    days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
    create_synthetic_history(days)

