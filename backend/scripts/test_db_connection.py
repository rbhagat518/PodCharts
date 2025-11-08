"""Test database connection."""
from __future__ import annotations

import os
from dotenv import load_dotenv
from psycopg import connect

load_dotenv()

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    print("❌ DATABASE_URL not found in .env")
    exit(1)

print(f"Testing connection with DATABASE_URL...")
print(f"URL (first 60 chars): {database_url[:60]}...")

try:
    conn = connect(database_url, connect_timeout=10)
    print("✅ Connection successful!")
    
    with conn.cursor() as cur:
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL version: {version[:50]}...")
    
    conn.close()
    print("✅ Database connection test passed!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    print("\nTroubleshooting:")
    print("1. Check if your Supabase project is active (not paused)")
    print("2. Verify DATABASE_URL in .env file")
    print("3. Make sure password with @ is URL-encoded as %40")
    print("   Example: postgresql://postgres:password%40with@at@host:5432/db")
    exit(1)

