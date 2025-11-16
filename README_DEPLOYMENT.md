# Analytics Microservice v3 - Quick Deployment Guide

Fast-track guide to deploy this service to Railway and enable interactive chart editing.

---

## 🚀 What This Service Does

Generates **Chart.js charts** with an **interactive editor** that allows users to click an "Edit Data" button and modify chart values in real-time, right in the presentation.

**Key Feature**: Self-contained interactive charts - no changes needed from Layout Builder team!

---

## ⚡ Quick Deploy to Railway

### 1. Push to GitHub

```bash
# In this directory
git init
git add .
git commit -m "Analytics Microservice v3 with interactive charts"

# Create repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/analytics-microservice-v3.git
git push -u origin main
```

### 2. Deploy on Railway

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `analytics-microservice-v3`
4. Railway auto-deploys!

### 3. Set Environment Variables

In Railway dashboard, add:

```
OPENAI_API_KEY=sk-...your-openai-key...
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=your-service-role-key
SUPABASE_BUCKET=analytics-charts
```

### 4. Get Your URL

After deployment:
- Railway assigns a URL like: `https://analytics-production-xxxx.up.railway.app`
- Copy this URL - you'll need it!

---

## 🔌 Use the Deployed Service

### Update Test Script

In `test_interactive_chart_via_layout_builder.py`, line 36:

```python
# Change from:
api_url = "http://localhost:8080/api/charts"

# To:
api_url = "https://analytics-production-xxxx.up.railway.app/api/charts"
```

### Generate Test Presentation

```bash
python3 test_interactive_chart_via_layout_builder.py
```

Now the interactive editor will work because both services are HTTPS on Railway!

---

## ✅ Files Ready for Deployment

All files are already prepared:

- ✅ `railway.toml` - Railway configuration
- ✅ `requirements.txt` - Python dependencies
- ✅ `.env.example` - Environment template
- ✅ `.gitignore` - Git exclusions
- ✅ `main.py` - Entry point
- ✅ `rest_server.py` - FastAPI server with `/api/charts/` endpoints

---

## 🧪 Test Your Deployment

### Health Check
```bash
curl https://your-railway-url.up.railway.app/health
```

### Test Interactive Editor API
```bash
curl -X POST https://your-railway-url.up.railway.app/api/charts/update-data \
  -H "Content-Type: application/json" \
  -d '{
    "chart_id": "test",
    "presentation_id": "test",
    "labels": ["A", "B"],
    "values": [100, 200]
  }'
```

Expected: `{"success": true, ...}`

---

## 📝 Next Steps

1. **Deploy to Railway** (5 minutes)
2. **Get Railway URL** (1 minute)
3. **Update test script** with Railway URL (1 minute)
4. **Test interactive charts** (2 minutes)
5. **Celebrate!** 🎉

**Total time**: ~10 minutes to have working interactive charts!

---

See **RAILWAY_DEPLOYMENT.md** for detailed documentation.
