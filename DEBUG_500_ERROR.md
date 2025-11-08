# Debugging 500 Error on /health/db

## 🔍 Step-by-Step Debugging

### Step 1: Check Vercel Function Logs

1. Go to **Vercel Dashboard**: https://vercel.com/dashboard
2. Select your **backend project**
3. Go to **Deployments** tab
4. Click on the **latest deployment**
5. Click **"View Function Logs"** or **"View Logs"**
6. Look for error messages

**What to look for**:
- `DATABASE_URL is required`
- `Failed to create database connection pool`
- Connection timeout errors
- Authentication errors

### Step 2: Check Environment Variables

1. In Vercel Dashboard, go to **Settings** → **Environment Variables**
2. Verify `DATABASE_URL` is set
3. Check the value format

**Correct Format**:
```
postgresql://postgres.xxx:password%40with@at@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

**Common Mistakes**:
- ❌ Missing `DATABASE_URL` entirely
- ❌ Password has `@` not encoded as `%40`
- ❌ Wrong port (should be 6543 for pooler)
- ❌ Missing `postgresql://` prefix

### Step 3: Test Endpoints

```bash
# Test basic health (no database needed)
curl https://your-backend-url.vercel.app/health

# Should return: {"status":"ok","version":"1.0.0"}

# Test database health
curl https://your-backend-url.vercel.app/health/db

# Should return: {"status":"ok","database":"connected"}
# OR error details if connection fails
```

### Step 4: Verify DATABASE_URL

**Get your DATABASE_URL from Supabase**:
1. Go to https://supabase.com/dashboard
2. Select your project
3. Go to **Settings** → **Database**
4. Under **Connection string**, select **"Session mode"** (pooler)
5. Copy the connection string
6. **Important**: Replace `@` in password with `%40`

**Example**:
```
# If password is: mypassword@123
# Connection string should be:
postgresql://postgres.xxx:mypassword%40123@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

### Step 5: Check Supabase Status

1. Go to Supabase Dashboard
2. Check if project is **paused**
3. If paused, **unpause** it
4. Verify database is accessible

## 🚨 Quick Fixes

### Fix 1: Add DATABASE_URL

1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Click **"Add New"**
3. Name: `DATABASE_URL`
4. Value: Your Supabase connection string (with URL-encoded password)
5. Click **"Save"**
6. **Redeploy** the project

### Fix 2: URL-Encode Password

If your password contains `@`, replace it with `%40`:

**Before**:
```
postgresql://postgres.xxx:password@123@host:6543/db
```

**After**:
```
postgresql://postgres.xxx:password%40123@host:6543/db
```

### Fix 3: Use Correct Port

For Supabase **pooler** (recommended), use port **6543**:
```
postgresql://postgres.xxx:password@host:6543/db
```

For **direct** connection, use port **5432**:
```
postgresql://postgres.xxx:password@host:5432/db
```

## 📋 Checklist

- [ ] Checked Vercel function logs for error messages
- [ ] Verified `DATABASE_URL` is set in Vercel environment variables
- [ ] Password is URL-encoded (`@` → `%40`)
- [ ] Using correct port (6543 for pooler)
- [ ] Supabase project is not paused
- [ ] `/health` endpoint works (returns `{"status":"ok"}`)
- [ ] `/health/db` endpoint shows error details

## 🔗 Next Steps

After fixing the issue:
1. **Redeploy** in Vercel
2. Test `/health/db` endpoint again
3. Check logs if still failing
4. Update frontend `NEXT_PUBLIC_API_BASE_URL` once backend works

