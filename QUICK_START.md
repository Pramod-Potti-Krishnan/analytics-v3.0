# Quick Start Guide - Analytics Microservice v3

## 🚀 Server is Already Running!

The REST API server is now running at: **http://localhost:8080**

The test UI should be open in your browser. If not, open: `test_ui.html`

---

## ⚠️ Important: Supabase Configuration

The server is running but **will fail to upload charts** because Supabase credentials are placeholders.

### To Enable Full Functionality:

Edit `.env` file and replace these values with your real Supabase credentials:

```bash
# Get these from your Supabase project dashboard
SUPABASE_URL=https://your-actual-project.supabase.co
SUPABASE_KEY=your-actual-service-role-key
```

Then restart the server:
```bash
# Kill current server
lsof -ti:8080 | xargs kill -9

# Restart with new credentials
source venv/bin/activate
python main.py
```

---

## 🧪 Testing Without Supabase (Current State)

The server will:
- ✅ Accept chart generation requests
- ✅ Generate charts using matplotlib
- ❌ Fail to upload to Supabase (placeholder credentials)
- ❌ Return error in the response

### Expected Behavior:

When you submit a chart request via the UI, you'll see:
- Job created successfully with job_id
- Progress updates (processing...)
- **Error**: "Failed to upload chart to storage"

This is expected without real Supabase credentials.

---

## ✅ What's Working

1. **REST API Server** - Running on port 8080
2. **Job Manager** - Tracks async jobs
3. **Chart Generation** - Creates PNG charts using matplotlib
4. **Progress Tracking** - Real-time progress via polling
5. **Test UI** - Interactive web interface

---

## 📋 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service information |
| `/health` | GET | Health check |
| `/stats` | GET | Job statistics |
| `/generate` | POST | Submit chart generation job |
| `/status/{job_id}` | GET | Poll for job status/results |

---

## 🎨 Using the Test UI

1. **Open** `test_ui.html` in your browser (already open)
2. **Modify** the form fields:
   - Chart Description (e.g., "Show Q1-Q4 revenue")
   - Title
   - Chart Type (bar, line, pie, etc.)
   - Theme (professional, dark, colorful, etc.)
3. **Click** "Generate Chart"
4. **Watch** the progress bar update in real-time
5. **View** the result (or error if no Supabase)

---

## 🔧 Manual Testing with cURL

```bash
# Submit job
curl -X POST http://localhost:8080/generate \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Show quarterly revenue",
    "title": "2024 Revenue",
    "chart_type": "bar_vertical",
    "theme": "professional"
  }'

# Get job status (replace JOB_ID with actual ID from above)
curl http://localhost:8080/status/JOB_ID

# Health check
curl http://localhost:8080/health

# Service info
curl http://localhost:8080/
```

---

## 🛠️ Server Management

### View Server Logs
The server is running in background. Check logs:
```bash
# Server output is visible in terminal where it started
# Or check process:
ps aux | grep "python main.py"
```

### Stop Server
```bash
lsof -ti:8080 | xargs kill -9
```

### Restart Server
```bash
source venv/bin/activate
python main.py
```

---

## 📦 What Was Set Up

1. ✅ Virtual environment created (`venv/`)
2. ✅ Dependencies installed (matplotlib, fastapi, supabase, etc.)
3. ✅ .env file configured (needs real Supabase credentials)
4. ✅ Test UI created (`test_ui.html`)
5. ✅ Server running on port 8080

---

## 🎯 Next Steps

### Option 1: Add Real Supabase Credentials
1. Go to https://supabase.com
2. Create a new project (or use existing)
3. Get your project URL and service role key
4. Update `.env` with real credentials
5. Restart server
6. Test chart generation - it should now upload to Supabase!

### Option 2: Test Locally Without Storage
The current setup works for testing the:
- REST API architecture
- Job management system
- Chart generation
- Progress tracking

You just won't get public URLs (will get errors instead).

---

## 🐛 Troubleshooting

### Port 8080 Already in Use
```bash
lsof -ti:8080 | xargs kill -9
```

### Dependencies Missing
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Supabase Errors
This is expected with placeholder credentials. Add real credentials to fix.

### Server Won't Start
Check `.env` file exists and has all required variables.

---

## 📚 Full Documentation

See `README.md` for complete API documentation and all available features.

---

**🎉 You're all set! The test UI is ready to use.**
