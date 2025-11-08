# Enabling Row Level Security (RLS) on Supabase

Supabase requires Row Level Security (RLS) to be enabled on all public tables for security best practices.

## ✅ What I've Done

I've updated the schema to include RLS policies for all tables:

1. **Public Tables** (public read access):
   - `podcasts` - Public read access
   - `ranks_daily` - Public read access
   - `metrics_daily` - Public read access

2. **User Tables** (users can only access their own data):
   - `users` - Users can only view/update their own data
   - `user_watchlists` - Users can only access their own watchlist
   - `user_alerts` - Users can only access their own alerts
   - `api_usage` - Users can only view their own usage, service role can insert

## 🚀 How to Enable RLS

You have **3 options** to enable RLS:

### Option 1: Run SQL Script in Supabase Dashboard (Recommended)

1. Go to your Supabase Dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `backend/scripts/enable_rls.sql`
4. Click **Run**

This will enable RLS on all tables with the appropriate policies.

### Option 2: Run Python Script

```bash
cd backend
conda activate podcharts-backend
python scripts/enable_rls.py
```

This will:
- Connect to your database
- Enable RLS on all tables
- Create the appropriate policies
- Show you the status of RLS on each table

### Option 3: Run Updated Schema

If you want to recreate the tables with RLS enabled:

```bash
cd backend
conda activate podcharts-backend
python scripts/setup_db.py
```

**Note:** This will only work if tables don't exist yet, or if you're okay with recreating them.

## 📋 RLS Policies Summary

### Public Read Access (for public API endpoints)
- `podcasts` - Anyone can read
- `ranks_daily` - Anyone can read
- `metrics_daily` - Anyone can read

### User-Scoped Access
- `users` - Users can only read/update their own records
- `user_watchlists` - Users can only access their own watchlist
- `user_alerts` - Users can only access their own alerts
- `api_usage` - Users can view their own usage, service role can insert

## 🔒 Security Notes

- **Service Role**: Your backend uses the service role key, which bypasses RLS. This is correct for backend operations.
- **Public Access**: Public tables allow read access to anyone, which is needed for your public API endpoints.
- **User Data**: User-specific tables are protected so users can only access their own data.

## ✅ Verification

After enabling RLS, you can verify it's working:

```sql
SELECT tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public'
AND tablename IN ('podcasts', 'ranks_daily', 'metrics_daily', 'users', 'user_watchlists', 'user_alerts', 'api_usage')
ORDER BY tablename;
```

All tables should show `rowsecurity = true`.

## 🎯 Next Steps

1. **Enable RLS** using one of the methods above
2. **Test your API** to ensure everything still works
3. **Verify** in Supabase Dashboard that the warning is gone

The RLS policies are designed to:
- ✅ Allow public read access to podcast data (for your public API)
- ✅ Protect user data (users can only see their own)
- ✅ Allow service role to insert API usage (for backend tracking)

Your backend will continue to work because it uses the service role key, which bypasses RLS.

