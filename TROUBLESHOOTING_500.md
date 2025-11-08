# Troubleshooting 500 Internal Server Error on Vercel

## 🔍 Common Causes

### 1. Missing Environment Variables

**Most Common Issue**: `DATABASE_URL` is not set in Vercel

**How to Fix**:
1. Go to your Vercel project → **Settings** → **Environment Variables**
2. Make sure `DATABASE_URL` is set
3. Value should be your Supabase connection string
4. **Important**: Make sure `@` in password is URL-encoded as `%40`

**Example**:
```
postgresql://postgres.xxx:password%40with@at@aws-1-us-east-2.pooler.supabase.com:6543/postgres
```

### 2. Incorrect DATABASE_URL Format

**Check**:
- Starts with `postgresql://`
- Has correct hostname
- Port is correct (6543 for pooler, 5432 for direct)
- Password is URL-encoded

### 3. Database Connection Issues

**Test Database Connection**:
1. Visit: `https://your-backend-url.vercel.app/health`
   - Should return: `{"status":"ok","version":"1.0.0"}`
   - This doesn't require database

2. Visit: `https://your-backend-url.vercel.app/health/db`
   - Should return: `{"status":"ok","database":"connected"}`
   - This tests database connection

### 4. Missing Dependencies

**Check**:
- Make sure `requirements.txt` exists in `backend/` directory
- All dependencies are listed

### 5. Import Errors

**Check Vercel Build Logs**:
- Look for "ModuleNotFoundError"
- Make sure all imports are correct

## 🔧 Step-by-Step Debugging

### Step 1: Check Environment Variables

1. Go to Vercel Dashboard
2. Select your backend project
3. Go to **Settings** → **Environment Variables**
4. Verify these are set:
   - `DATABASE_URL` ✅
   - `LISTENNOTES_API_KEY` ✅

### Step 2: Test Health Endpoints

```bash
# Test basic health (no database)
curl https://your-backend-url.vercel.app/health

# Test database health
curl https://your-backend-url.vercel.app/health/db
```

### Step 3: Check Vercel Logs

1. Go to Vercel Dashboard
2. Select your backend project
3. Go to **Deployments** → Click on latest deployment
4. Click **"View Function Logs"** or **"View Build Logs"**
5. Look for error messages

### Step 4: Verify DATABASE_URL Format

**Correct Format**:
```
postgresql://postgres.xxx:password%40with@at@host:6543/dbname
```

**Common Mistakes**:
- ❌ `@` in password not encoded → `password@with@at`
- ✅ Should be: `password%40with%40at`
- ❌ Wrong port (using 5432 instead of 6543 for pooler)
- ✅ Use 6543 for Supabase pooler

### Step 5: Test Database Connection

If `/health/db` fails, check:
1. Supabase project is not paused
2. DATABASE_URL is correct
3. Password is URL-encoded
4. Using correct port (6543 for pooler)

## 🚨 Quick Fixes

### Fix 1: Add Missing Environment Variable

1. Vercel Dashboard → Your Project → Settings → Environment Variables
2. Add `DATABASE_URL` with your Supabase connection string
3. **Redeploy** the project

### Fix 2: URL-Encode Password

If your password contains `@`, replace it with `%40`:

**Before**:
```
postgresql://postgres.xxx:password@with@at@host:6543/db
```

**After**:
```
postgresql://postgres.xxx:password%40with%40at@host:6543/db
```

### Fix 3: Use Correct Port

For Supabase pooler, use port **6543**:
```
postgresql://postgres.xxx:password@host:6543/db
```

For direct connection, use port **5432**:
```
postgresql://postgres.xxx:password@host:5432/db
```

## 📋 Checklist

- [ ] `DATABASE_URL` is set in Vercel environment variables
- [ ] Password is URL-encoded (`@` → `%40`)
- [ ] Using correct port (6543 for pooler)
- [ ] Supabase project is not paused
- [ ] `/health` endpoint works
- [ ] `/health/db` endpoint works
- [ ] Checked Vercel function logs for errors

## 🔗 Useful Links

- Vercel Function Logs: https://vercel.com/dashboard → Your Project → Deployments → View Logs
- Supabase Dashboard: https://supabase.com/dashboard
- Test Database: `https://your-backend-url.vercel.app/health/db`

