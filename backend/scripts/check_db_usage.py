"""Check database usage and estimate when you'll hit Supabase free tier limits."""
from __future__ import annotations

import os
from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

load_dotenv()

with connect(os.environ.get("DATABASE_URL")) as conn:
    with conn.cursor(row_factory=dict_row) as cur:
        # Check database size
        cur.execute("""
            SELECT 
                pg_size_pretty(pg_database_size(current_database())) as db_size,
                pg_database_size(current_database()) as db_size_bytes
        """)
        size = cur.fetchone()
        
        # Check table sizes
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
                pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)
        tables = cur.fetchall()
        
        # Count records
        cur.execute("SELECT COUNT(*) as count FROM podcasts")
        podcasts = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) as count FROM metrics_daily")
        metrics = cur.fetchone()["count"]
        
        cur.execute("SELECT COUNT(*) as count FROM ranks_daily")
        ranks = cur.fetchone()["count"]
        
        print(f"📊 Current Database Usage:")
        print(f"   Total database size: {size['db_size']}")
        print(f"   Database size (bytes): {size['db_size_bytes']:,}")
        print(f"")
        print(f"📈 Current Data:")
        print(f"   Podcasts: {podcasts:,}")
        print(f"   Metrics records: {metrics:,}")
        print(f"   Rank records: {ranks:,}")
        print(f"")
        print(f"📋 Table Sizes:")
        for table in tables:
            print(f"   {table['tablename']}: {table['size']}")
        
        # Estimate growth
        db_size_mb = size["db_size_bytes"] / (1024 * 1024)
        free_limit_mb = 500
        remaining_mb = free_limit_mb - db_size_mb
        
        print(f"")
        print(f"💾 Storage Analysis:")
        print(f"   Current usage: {db_size_mb:.2f} MB")
        print(f"   Free tier limit: 500 MB")
        print(f"   Remaining: {remaining_mb:.2f} MB ({remaining_mb/free_limit_mb*100:.1f}% left)")
        
        # Estimate how long until limit
        if metrics > 0:
            avg_record_size = size["db_size_bytes"] / metrics if metrics > 0 else 0
            records_per_day = 116  # Current ingestion rate
            growth_per_day_mb = (records_per_day * avg_record_size) / (1024 * 1024)
            
            if growth_per_day_mb > 0:
                days_until_limit = remaining_mb / growth_per_day_mb
                print(f"")
                print(f"📅 Growth Estimate:")
                print(f"   Records per day: ~{records_per_day}")
                print(f"   Growth rate: ~{growth_per_day_mb:.4f} MB/day")
                print(f"   Days until 500 MB limit: ~{days_until_limit:.0f} days")
                print(f"   That's ~{days_until_limit/365:.1f} years at current rate")
        
        print(f"")
        print(f"💰 Supabase Free Tier Limits:")
        print(f"   ✅ 500 MB database storage")
        print(f"   ✅ 2 GB bandwidth per month")
        print(f"   ✅ 2 million API requests per month")
        print(f"   ✅ 50,000 monthly active users")
        print(f"")
        print(f"💡 When you'll need to pay:")
        print(f"   - Database storage > 500 MB")
        print(f"   - Bandwidth > 2 GB/month")
        print(f"   - API requests > 2 million/month")
        print(f"")
        print(f"📈 Check your usage:")
        print(f"   https://supabase.com/dashboard/project/YOUR_PROJECT_ID/settings/billing")

