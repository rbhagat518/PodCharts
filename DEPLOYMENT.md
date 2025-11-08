# PodCharts Deployment Guide

## 🚀 Quick Overview

Deploying PodCharts is **not a big task**! Here's what you need:

- **Frontend (Next.js)**: Deploy to Vercel (free tier available)
- **Backend (FastAPI)**: Deploy to Vercel, Railway, or Render (all have free tiers)
- **Database**: Already on Supabase (cloud-hosted) ✅
- **Ingestion**: Already on GitHub Actions (automated) ✅

## 📋 Pre-Deployment Checklist

- [ ] Push your code to GitHub (already done ✅)
- [ ] Set up environment variables in deployment platform
- [ ] Configure CORS for production API URL
- [ ] Update frontend API URL to production backend
- [ ] Test the deployment

## 🎯 Option 1: Vercel (Recommended - Easiest)

Vercel can host both your Next.js frontend AND FastAPI backend!

### Step 1: Deploy Frontend to Vercel

1. **Go to Vercel**: https://vercel.com
2. **Sign up/Login** with GitHub
3. **Import Project**:
   - Click "Add New Project"
   - Select your `PodCharts` repository
   - **Root Directory**: Select `frontend`
   - Framework Preset: **Next.js** (auto-detected)
4. **Environment Variables**:
   - Add: `NEXT_PUBLIC_API_BASE_URL` = `https://your-backend-url.vercel.app` (we'll get this after backend deploy)
   - Or use: `https://podcharts-api.vercel.app` (if you name it that)
5. **Deploy**!

### Step 2: Deploy Backend to Vercel

1. **Add another project** in Vercel
2. **Import Project**:
   - Select same `PodCharts` repository
   - **Root Directory**: Select `backend`
   - Framework Preset: **Other** (or Python)
3. **Configure Build Settings**:
   - Build Command: `pip install -r requirements.txt` (or use Poetry)
   - Output Directory: Leave empty (not needed for API)
   - Install Command: `pip install fastapi uvicorn psycopg[binary] psycopg-pool httpx python-dotenv`
4. **Create `vercel.json`** in `backend/`:
   ```json
   {
     "version": 2,
     "builds": [
       {
         "src": "app/main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app/main.py"
       }
     ]
   }
   ```
5. **Environment Variables**:
   - `DATABASE_URL`: Your Supabase connection string
   - `LISTENNOTES_API_KEY`: Your ListenNotes API key
   - `SUPABASE_URL`: Your Supabase URL (if using auth)
   - `SUPABASE_SERVICE_KEY`: Your Supabase service key (if using auth)
   - `STRIPE_SECRET_KEY`: Your Stripe key (if using subscriptions)
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret (if using webhooks)
   - `FRONTEND_URL`: Your frontend Vercel URL (for CORS)
6. **Deploy**!

### Step 3: Update Frontend API URL

1. Go back to your **Frontend project** in Vercel
2. **Settings** → **Environment Variables**
3. Update `NEXT_PUBLIC_API_BASE_URL` to your backend URL
4. **Redeploy** the frontend

### Step 4: Configure CORS

Make sure your backend allows requests from your frontend domain. Check `backend/app/main.py` - CORS should already be configured, but verify:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-frontend.vercel.app",  # Add your production URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🎯 Option 2: Railway (Alternative for Backend)

If you prefer Railway for the backend:

1. **Go to Railway**: https://railway.app
2. **New Project** → **Deploy from GitHub**
3. **Select your repository**
4. **Configure**:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Same as Vercel
6. **Deploy**!

## 🎯 Option 3: Render (Alternative)

1. **Go to Render**: https://render.com
2. **New** → **Web Service**
3. **Connect GitHub** and select your repo
4. **Configure**:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. **Environment Variables**: Same as above
6. **Deploy**!

## 📝 Required Files for Deployment

### For Vercel Backend: `backend/vercel.json`

```json
{
  "version": 2,
  "builds": [
    {
      "src": "app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "app/main.py"
    }
  ]
}
```

### For Railway/Render: `backend/requirements.txt`

Create this file if it doesn't exist:

```txt
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
python-dotenv>=1.0.1
psycopg[binary]>=3.2.1
psycopg-pool>=3.2.1
httpx>=0.27.2
supabase>=2.0.0
stripe>=10.0.0
python-jose[cryptography]>=3.3.0
python-multipart>=0.0.9
```

## 🔧 Environment Variables Needed

### Frontend (Vercel)
- `NEXT_PUBLIC_API_BASE_URL`: Your backend API URL

### Backend (Vercel/Railway/Render)
- `DATABASE_URL`: Supabase connection string
- `LISTENNOTES_API_KEY`: ListenNotes API key
- `SUPABASE_URL`: Supabase URL (optional, for auth)
- `SUPABASE_SERVICE_KEY`: Supabase service key (optional, for auth)
- `STRIPE_SECRET_KEY`: Stripe key (optional, for subscriptions)
- `STRIPE_WEBHOOK_SECRET`: Stripe webhook secret (optional)
- `FRONTEND_URL`: Frontend URL (for CORS)

## ✅ Post-Deployment Checklist

- [ ] Test frontend: Visit your Vercel frontend URL
- [ ] Test backend: Visit `https://your-backend.vercel.app/health`
- [ ] Test API: Visit `https://your-backend.vercel.app/docs`
- [ ] Verify CORS: Frontend should be able to call backend
- [ ] Check database: Data should be accessible
- [ ] Test ingestion: GitHub Actions should still work

## 🆓 Free Tier Limits

### Vercel
- ✅ Unlimited deployments
- ✅ 100 GB bandwidth/month
- ✅ Serverless functions (100 GB-hours/month)
- ✅ Perfect for Next.js and Python APIs

### Railway
- ✅ $5 free credit/month
- ✅ Enough for small projects

### Render
- ✅ Free tier available
- ✅ Spins down after inactivity (adds cold start delay)

## 🚨 Common Issues

### CORS Errors
- Make sure `FRONTEND_URL` is set correctly in backend
- Update CORS origins in `backend/app/main.py`

### Database Connection Errors
- Verify `DATABASE_URL` is correct
- Make sure password is URL-encoded (`@` → `%40`)
- Check Supabase project is not paused

### API Not Found
- Verify `NEXT_PUBLIC_API_BASE_URL` is set correctly
- Check backend is deployed and running
- Test backend URL directly: `https://your-backend.vercel.app/health`

## 📚 Next Steps

1. **Custom Domain**: Add your own domain in Vercel settings
2. **Analytics**: Add Vercel Analytics to track usage
3. **Monitoring**: Set up error tracking (Sentry, etc.)
4. **SEO**: Add meta tags and Open Graph images

## 🎉 You're Done!

Once deployed, your site will be live at:
- Frontend: `https://your-project.vercel.app`
- Backend: `https://your-backend.vercel.app`
- API Docs: `https://your-backend.vercel.app/docs`

