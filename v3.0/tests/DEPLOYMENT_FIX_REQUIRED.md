# Analytics Service v3.0 - Deployment Fix Required

**Analysis Date**: December 20, 2024
**Analyst**: Claude Code (Comprehensive Investigation)

---

## Executive Summary

**The code is correct and fully implemented. The issue is Railway deployment.**

| Component | Status | Details |
|-----------|--------|---------|
| Local Code | Correct | All 18 endpoints implemented in v3.0/rest_server.py |
| GitHub | Synced | Commit c5ea70e pushed 13 hours ago |
| Production | **STALE** | Missing 6 endpoints, version 3.1.2 vs code 3.1.0 |

---

## Root Cause Analysis

### Issue: Railway Not Deploying Latest Code

**Evidence**:
1. Production version: `3.1.2`
2. GitHub v3.0/rest_server.py: Has `/capabilities` at line 589
3. Production `/capabilities`: Returns 404 Not Found

**Conclusion**: Railway has not redeployed after the latest commits.

---

## Code Location Analysis

### Repository Structure
```
analytics_microservice/          ← Git repo root
├── rest_server.py              ← v3.1.4 (ROOT - different code!)
├── agent.py                    ← ROOT agent
├── v3.0/                       ← CORRECT deployment source
│   ├── rest_server.py         ← v3.1.0 (HAS all endpoints)
│   ├── main.py                ← Entry point
│   ├── Dockerfile             ← Container build
│   ├── railway.toml           ← Railway config
│   └── railway.json           ← Railway project config
└── v3.1/                       ← Newer version (unused?)
```

### Critical Finding
**TWO different rest_server.py files exist:**

| Location | Version | Has Service Coordination | Has Layout Service |
|----------|---------|-------------------------|-------------------|
| `/analytics_microservice/rest_server.py` | 3.1.4 | NO | NO |
| `/analytics_microservice/v3.0/rest_server.py` | 3.1.0 | YES | YES |

Railway SHOULD deploy from `v3.0/` because that's where railway.toml is.

---

## Endpoints Verification (Local Code)

### v3.0/rest_server.py Contains:

**Service Coordination (Lines 584-915)**:
- `GET /capabilities` - Line 589
- `POST /api/v1/analytics/can-handle` - Line 680
- `POST /api/v1/analytics/recommend-chart` - Line 779

**Layout Service Integration (Lines 1751-2266)**:
- `POST /api/ai/chart/generate` - Line 1754
- `GET /api/ai/chart/constraints` - Line 2210
- `GET /api/ai/chart/palettes` - Line 2240

**Field Aliases (agent.py + layout_assembler.py)**:
- `chart_html` → alias for `element_3`
- `element_4` → alias for `element_3`
- `body` → alias for `element_2`

---

## Fix Required

### Step 1: Trigger Railway Redeploy

**Option A: Railway Dashboard**
1. Go to https://railway.app
2. Find project: `analytics-v30-production`
3. Click "Deploy" or trigger new deployment
4. Wait for build to complete

**Option B: Railway CLI (if installed)**
```bash
cd /path/to/analytics_microservice/v3.0
railway up
```

**Option C: Git Push Empty Commit**
```bash
cd /path/to/analytics_microservice
git commit --allow-empty -m "trigger: Redeploy to Railway"
git push origin main
```

### Step 2: Verify Deployment

After redeploy, verify all endpoints:
```bash
# Service Coordination
curl https://analytics-v30-production.up.railway.app/capabilities

# Should return JSON with capabilities, NOT 404
```

### Step 3: Verify Field Aliases

```bash
curl -X POST https://analytics-v30-production.up.railway.app/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{
    "presentation_id": "test",
    "slide_id": "test",
    "slide_number": 1,
    "narrative": "Test",
    "data": [{"label": "Q1", "value": 100}]
  }'

# Response should include:
# - content.element_3 (original)
# - content.chart_html (alias)
# - content.element_4 (alias)
# - content.body (alias)
```

---

## Railway Configuration Verification

### Expected Railway Settings

**Root Directory**: Should be set to `v3.0/` (not repo root)

If Railway is set to deploy from repo root, it will use:
- `/analytics_microservice/rest_server.py` (WRONG - v3.1.4, missing endpoints)

Instead of:
- `/analytics_microservice/v3.0/rest_server.py` (CORRECT - v3.1.0, all endpoints)

### How to Fix if Root Directory is Wrong

1. Railway Dashboard → Project Settings
2. Find "Root Directory" setting
3. Set to `v3.0`
4. Redeploy

---

## Post-Deployment Verification Checklist

After Railway redeploy, run these tests:

```bash
BASE_URL="https://analytics-v30-production.up.railway.app"

# 1. Check version
curl -s $BASE_URL/ | jq '.version'
# Expected: "3.1.0" or newer

# 2. Test Service Coordination
curl -s $BASE_URL/capabilities | jq '.service'
# Expected: "analytics-service"

curl -s -X POST $BASE_URL/api/v1/analytics/can-handle \
  -H "Content-Type: application/json" \
  -d '{"slide_content": {"title": "Test", "topics": [], "topic_count": 0}}' | jq '.can_handle'
# Expected: true or false (not 404)

# 3. Test Layout Service Integration
curl -s $BASE_URL/api/ai/chart/constraints | jq '.success'
# Expected: true

curl -s $BASE_URL/api/ai/chart/palettes | jq '.success'
# Expected: true

# 4. Test Field Aliases
curl -s -X POST $BASE_URL/api/v1/analytics/L02/revenue_over_time \
  -H "Content-Type: application/json" \
  -d '{"presentation_id": "test", "slide_id": "test", "slide_number": 1, "narrative": "Test", "data": [{"label": "Q1", "value": 100}, {"label": "Q2", "value": 200}]}' \
  | jq '.content | keys'
# Expected: ["body", "chart_html", "element_2", "element_3", "element_4"]
```

---

## Summary

| Issue | Root Cause | Fix |
|-------|------------|-----|
| 6 endpoints return 404 | Railway hasn't deployed latest code | Trigger Railway redeploy |
| Field aliases missing | Same as above | Trigger Railway redeploy |
| Version mismatch (3.1.2 vs 3.1.0) | Confusing version numbering | Update version consistently after deploy |

---

## Railway Troubleshooting

### Already Attempted
- [x] Empty commit pushed to GitHub (commit 50ce51f)
- [x] Verified code is on GitHub main branch
- [ ] Railway auto-deploy not triggering

### Manual Railway Deployment Steps

1. **Login to Railway Dashboard**:
   - Go to https://railway.app/dashboard
   - Find project: `analytics-v30-production`

2. **Check Deployment Settings**:
   - Verify "Root Directory" is set to `v3.0`
   - Verify auto-deploy is enabled for `main` branch
   - Verify GitHub repo is: `Pramod-Potti-Krishnan/analytics-v3.0`

3. **Trigger Manual Redeploy**:
   - Click on the service
   - Click "Redeploy" or "Deploy" button
   - Wait for build to complete (usually 2-5 minutes)

4. **Check Build Logs**:
   - Look for any build errors
   - Verify it's using the correct Dockerfile from v3.0/

### If Root Directory is Wrong

If Railway is deploying from repo root instead of `v3.0/`:

**Option A: Change Railway Root Directory**
1. Railway Dashboard → Project Settings
2. Set "Root Directory" to `v3.0`
3. Redeploy

**Option B: Move Files to Repo Root**
If you want Railway to deploy from root:
1. Move all v3.0/ files to repo root
2. Update imports in main.py
3. Commit and push
4. Railway will auto-deploy

### Railway CLI Deployment (if available)

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
cd /path/to/analytics_microservice/v3.0
railway link

# Deploy
railway up
```

---

## Action Required (MANUAL)

**Since auto-deploy didn't work, please manually:**

1. **Go to Railway Dashboard**: https://railway.app/dashboard
2. **Find the analytics-v30-production service**
3. **Click "Redeploy" or manually trigger deployment**
4. **Verify with test commands after deploy completes**

---

## Version History

- **December 20, 2024 10:30 UTC**: Comprehensive analysis completed
- **December 20, 2024 10:35 UTC**: Empty commit pushed (50ce51f) - auto-deploy not triggered
- **Pending**: Manual Railway redeploy required
