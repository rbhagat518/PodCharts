# Deploy Backend to Vercel - Step by Step

## 🚀 Quick Steps

### Step 1: Add New Project in Vercel

1. Go to your Vercel dashboard: https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Select your **PodCharts** repository from GitHub
4. Click **"Import"**

### Step 2: Configure Project Settings

1. **Project Name**: 
   - Name it something like `podcharts-api` or `podcharts-backend`
   - This will be your backend URL: `https://podcharts-api.vercel.app`

2. **Root Directory**: 
   - Click **"Edit"** next to Root Directory
   - Select **`backend`** (not the root!)
   - Click **"Continue"**

3. **Framework Preset**: 
   - Select **"Other"** (or leave as auto-detected)
   - Vercel should detect Python/FastAPI

4. **Build Settings** (usually auto-detected):
   - **Build Command**: Leave empty (Vercel will use `vercel.json`)
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty (Vercel will use `requirements.txt`)

### Step 3: Add Environment Variables

**Before deploying**, add these environment variables:

1. Click **"Environment Variables"** section
2. Add each variable below:

#### Required Variables:

```
DATABASE_URL
```
- Value: Your Supabase connection string
- Example: `postgresql://postgres.xxx:password%40with@at@aws-1-us-east-2.pooler.supabase.com:6543/postgres`
- **Important**: Make sure `@` in password is URL-encoded as `%40`

```
LISTENNOTES_API_KEY
```
- Value: Your ListenNotes API key
- Get it from: https://www.listennotes.com/api/docs/

#### Optional Variables (if using features):

```
SUPABASE_URL
```
- Value: `https://your-project-id.supabase.co`
- Only needed if using authentication

```
SUPABASE_SERVICE_KEY
```
- Value: Your Supabase service role key
- Only needed if using authentication

```
STRIPE_SECRET_KEY
```
- Value: Your Stripe secret key
- Only needed if using subscriptions

```
STRIPE_WEBHOOK_SECRET
```
- Value: Your Stripe webhook secret
- Only needed if using webhooks

```
FRONTEND_URL
```
- Value: Your frontend Vercel URL
- Example: `https://podcharts-frontend.vercel.app`
- Used for CORS and redirects

### Step 4: Deploy!

1. Click **"Deploy"** button
2. Wait for build to complete (usually 1-2 minutes)
3. Once deployed, you'll get a URL like: `https://podcharts-api.vercel.app`

### Step 5: Test Your Backend

1. Visit: `https://your-backend-url.vercel.app/health`
   - Should return: `{"status":"ok","version":"1.0.0"}`

2. Visit: `https://your-backend-url.vercel.app/docs`
   - Should show FastAPI Swagger documentation

3. Test an endpoint:
   ```bash
   curl https://your-backend-url.vercel.app/leaderboard?limit=5
   ```

### Step 6: Update Frontend to Use Backend

1. Go back to your **Frontend project** in Vercel
2. **Settings** → **Environment Variables**
3. Add/Update: `NEXT_PUBLIC_API_BASE_URL`
   - Value: `https://your-backend-url.vercel.app`
   - Example: `https://podcharts-api.vercel.app`
4. **Redeploy** the frontend

## ✅ Checklist

- [ ] Created new project in Vercel
- [ ] Set root directory to `backend`
- [ ] Added `DATABASE_URL` environment variable
- [ ] Added `LISTENNOTES_API_KEY` environment variable
- [ ] Added optional variables (if needed)
- [ ] Deployed backend
- [ ] Tested `/health` endpoint
- [ ] Tested `/docs` endpoint
- [ ] Updated frontend `NEXT_PUBLIC_API_BASE_URL`
- [ ] Redeployed frontend

## 🔧 Troubleshooting

### Build Fails

**Error: "Module not found"**
- Make sure `requirements.txt` exists in `backend/` directory
- Check that all dependencies are listed

**Error: "DATABASE_URL is required"**
- Make sure you added `DATABASE_URL` environment variable
- Check that the value is correct (password URL-encoded)

### API Returns 500 Errors

**Error: "Connection refused"**
- Check `DATABASE_URL` is correct
- Make sure Supabase project is not paused
- Verify password is URL-encoded (`@` → `%40`)

**Error: "CORS error"**
- CORS is already configured to allow all origins (`allow_origins=["*"]`)
- If issues persist, check `FRONTEND_URL` is set correctly

### Webhook Issues

**Stripe webhooks not working**
- Make sure `STRIPE_WEBHOOK_SECRET` is set
- Update Stripe webhook URL to: `https://your-backend-url.vercel.app/api/subscriptions/webhook`

## 📝 Notes

- **`vercel.json`** is already configured in `backend/vercel.json`
- **`requirements.txt`** is already created in `backend/requirements.txt`
- **CORS** is already configured to allow all origins
- Backend will be available at: `https://your-project-name.vercel.app`

## 🎉 You're Done!

Once deployed:
- Backend: `https://your-backend-url.vercel.app`
- Frontend: `https://your-frontend-url.vercel.app`
- API Docs: `https://your-backend-url.vercel.app/docs`

