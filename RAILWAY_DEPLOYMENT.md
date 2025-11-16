# Analytics Microservice v3 - Railway Deployment Guide

Complete guide to deploy Analytics Microservice to Railway.

---

## 📋 Prerequisites

- Railway account (https://railway.app)
- GitHub account
- OpenAI API key
- Supabase project (for chart storage)

---

## 🚀 Deployment Steps

### Step 1: Prepare Git Repository

```bash
cd /Users/pk1980/Documents/Software/deckster-backend/deckster-w-content-strategist/agents/analytics_microservice_v3

# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Analytics Microservice v3 with interactive chart editor"

# Create GitHub repository (via GitHub UI or CLI)
# Then add remote:
git remote add origin https://github.com/YOUR_USERNAME/analytics-microservice-v3.git

# Push to GitHub
git push -u origin main
```

### Step 2: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository: `analytics-microservice-v3`
4. Railway will auto-detect Python and create the service

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

**Required:**
```
OPENAI_API_KEY=sk-...your-key...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=analytics-charts
```

**Optional (with defaults):**
```
API_PORT=8080
LOG_LEVEL=INFO
APP_ENV=production
```

### Step 4: Deploy

Railway will automatically deploy when you push to GitHub.

**First deployment:**
- Railway reads `railway.toml`
- Installs dependencies from `requirements.txt`
- Runs health check at `/health`
- Assigns a public URL

### Step 5: Get Your Service URL

After deployment:
1. Go to your Railway project
2. Click on the service
3. Go to "Settings" → "Networking"
4. Copy the public URL (e.g., `https://analytics-microservice-production-xxxx.up.railway.app`)

---

## 🔄 Update Chart Generator to Use Railway URL

After getting your Railway URL, update the test script:

**File:** `test_interactive_chart_via_layout_builder.py`

```python
# Change line 36:
api_url = "https://analytics-microservice-production-xxxx.up.railway.app/api/charts"
```

Or pass it dynamically when Layout Builder calls your service.

---

## 🧪 Testing Deployment

### Test Health Check:
```bash
curl https://your-railway-url.up.railway.app/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "service": "analytics_microservice_v3",
  "jobs": {...}
}
```

### Test Chart Data API:
```bash
curl -X POST https://your-railway-url.up.railway.app/api/charts/update-data \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "test-chart",
    "presentation_id": "test-presentation",
    "labels": ["Q1", "Q2", "Q3"],
    "values": [100, 200, 300]
  }'
```

**Expected response:**
```json
{
  "success": true,
  "message": "Chart data updated successfully",
  "chart_id": "test-chart",
  "presentation_id": "test-presentation",
  "labels_count": 3,
  "values_count": 3
}
```

---

## 📁 Files Prepared for Deployment

✅ **railway.toml** - Railway deployment configuration
✅ **requirements.txt** - Python dependencies
✅ **.env.example** - Environment variable template
✅ **.gitignore** - Git ignore rules
✅ **main.py** - Application entry point
✅ **rest_server.py** - FastAPI REST server with chart data endpoints

---

## 🔌 Integration with Layout Builder

Once deployed, Layout Builder can:

### Option 1: Direct Calls (No Proxy Needed)
Layout Builder generates charts with:
```python
chart_html = generator.generate_line_chart(
    data={...},
    enable_editor=True,
    presentation_id=presentation_id,
    api_base_url="https://your-analytics.railway.app/api/charts"  # Your Railway URL
)
```

### Option 2: Proxy (If Layout Builder Adds It)
If Layout Builder adds proxy at `/api/charts/` → your Railway URL:
```python
chart_html = generator.generate_line_chart(
    data={...},
    enable_editor=True,
    presentation_id=presentation_id,
    api_base_url="/api/charts"  # Relative URL (proxied)
)
```

---

## 🔍 Monitoring

### View Logs:
Railway dashboard → Your service → Deployments → View logs

### Check Health:
```bash
curl https://your-railway-url.up.railway.app/health
```

### View Stats:
```bash
curl https://your-railway-url.up.railway.app/stats
```

---

## 🐛 Troubleshooting

### Deployment Fails:
1. Check Railway build logs
2. Verify all environment variables are set
3. Check `requirements.txt` has all dependencies

### Health Check Fails:
1. Verify `API_PORT=8080` is set
2. Check if Supabase credentials are correct
3. View logs for errors

### CORS Errors:
Already configured! CORS middleware allows all origins:
```python
# In rest_server.py lines 31-37
allow_origins=["*"]
```

### Chart Editor Save Fails:
1. Verify Railway URL is HTTPS
2. Check browser console for errors
3. Test API endpoint directly with curl

---

## 📊 API Endpoints Available

Once deployed:

```
GET  /                           # Service info
GET  /health                     # Health check
GET  /stats                      # Job statistics
POST /generate                   # Legacy chart generation
GET  /status/{job_id}           # Job status
POST /api/v1/analytics/{layout}/{type}  # Analytics generation
POST /api/v1/analytics/batch    # Batch analytics
POST /api/charts/update-data    # ✨ Interactive editor save
GET  /api/charts/get-data/{id}  # ✨ Interactive editor load
```

---

## 🎉 Success Checklist

After deployment:

- [ ] Railway service is running (green status)
- [ ] Health check returns `200 OK`
- [ ] Public URL is accessible
- [ ] Environment variables are set
- [ ] Test API endpoints work
- [ ] Updated chart generator with Railway URL
- [ ] Generated test presentation
- [ ] Interactive chart editor works
- [ ] Chart data saves successfully

---

## 🔄 Future Updates

To update your deployment:

```bash
# Make changes to code
git add .
git commit -m "Your update message"
git push

# Railway auto-deploys on push!
```

---

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test endpoints with curl
4. Check browser console for errors

**Status**: Ready for deployment! 🚀
