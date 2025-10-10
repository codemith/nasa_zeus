# Production Deployment Checklist - NASA ZEUS

This document contains all the critical fixes and configurations needed for a successful production deployment. Follow these steps to avoid common issues.

## 🔧 Critical Configuration Fixes

### 1. Frontend Environment Variables (MOST IMPORTANT)

**❌ WRONG Configuration:**
```bash
NEXT_PUBLIC_API_URL=https://www.nasazeus.org/api  # DO NOT include /api suffix!
```

**✅ CORRECT Configuration:**
```bash
# In frontend/.env.local
NEXT_PUBLIC_API_URL=https://www.nasazeus.org  # No /api suffix
NEXT_PUBLIC_GEMINI_URL=https://www.nasazeus.org/gemini
NEXT_PUBLIC_SITE_URL=https://www.nasazeus.org
```

**Why?** The frontend code already adds `/api/` prefix in the fetch calls:
```typescript
const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;
fetch(`${apiBaseUrl}/api/tempo_json`);  // Results in: https://www.nasazeus.org/api/tempo_json
```

If you set `NEXT_PUBLIC_API_URL=https://www.nasazeus.org/api`, it becomes:
`https://www.nasazeus.org/api/api/tempo_json` ❌ (Double /api/ causes 405 errors)

### 2. Backend .env Configuration

```bash
# Backend .env file
DATABASE_URL=sqlite:///./nasa_zeus.db
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENWEATHER_API_KEY=your_key_here
OPENAQ_API_KEY=your_key_here
GEMINI_API_KEY=your_gemini_key_here
NOAA_API_BASE=https://api.weather.gov
FRONTEND_URL=https://nasazeus.org
```

### 3. Caddy Reverse Proxy Configuration

**Location:** `/etc/caddy/Caddyfile`

```caddy
www.nasazeus.org {
    # Backend API routes - DO NOT strip /api prefix
    handle /api/* {
        reverse_proxy localhost:8000
    }
    
    # Gemini service - STRIP /gemini prefix
    handle /gemini/* {
        uri strip_prefix /gemini
        reverse_proxy localhost:8001
    }
    
    # Frontend for all other routes
    handle {
        reverse_proxy localhost:3000
    }
}

nasazeus.org {
    redir https://www.nasazeus.org{uri}
}
```

**Key Points:**
- ✅ `/api/*` routes pass through to backend WITH the `/api` prefix
- ✅ `/gemini/*` routes strip `/gemini` prefix before forwarding to port 8001
- ❌ DO NOT use `uri strip_prefix /api` - this causes the double /api bug

### 4. PM2 Process Manager Setup

```bash
# Start all services
cd ~/nasa_zeus

# Backend
pm2 start "venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000" --name backend

# Frontend
cd frontend
pm2 start "npm start" --name frontend

# Gemini service
cd ..
pm2 start "venv/bin/python gemini_server.py" --name gemini

# Save PM2 configuration
pm2 save
pm2 startup
```

## 🚀 Deployment Steps

### Step 1: Update Server Code

```bash
# SSH into server
ssh -i deployment/nasa-zeus-key.pem ubuntu@98.80.14.227

# Pull latest code
cd nasa_zeus
git pull origin main

# Update Python dependencies
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Configure Environment

```bash
# Create/update backend .env
cat > .env << 'EOF'
DATABASE_URL=sqlite:///./nasa_zeus.db
SECRET_KEY=$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENWEATHER_API_KEY=your_key
OPENAQ_API_KEY=your_key
GEMINI_API_KEY=your_gemini_key
NOAA_API_BASE=https://api.weather.gov
FRONTEND_URL=https://nasazeus.org
EOF

# Create frontend environment (NO /api suffix!)
cat > frontend/.env.local << 'EOF'
NEXT_PUBLIC_API_URL=https://www.nasazeus.org
NEXT_PUBLIC_GEMINI_URL=https://www.nasazeus.org/gemini
NEXT_PUBLIC_SITE_URL=https://www.nasazeus.org
EOF
```

### Step 3: Build Frontend

```bash
cd frontend
npm install
npm run build  # This bakes environment variables into the build
cd ..
```

### Step 4: Restart Services

```bash
pm2 restart all
pm2 logs --lines 50  # Check for errors
```

### Step 5: Verify Endpoints

```bash
# Test TEMPO endpoint
curl https://www.nasazeus.org/api/tempo_json

# Test OpenAQ endpoint
curl 'https://www.nasazeus.org/api/openaq-latest?lat=40.7128&lon=-74.006&radius=25000'

# Test Gemini endpoint
curl 'https://www.nasazeus.org/gemini/atmospheric-data?location=New%20York%20City'
```

## 🐛 Common Issues & Solutions

### Issue 1: "405 Method Not Allowed" on API calls

**Symptom:** Browser logs show requests to `/api/api/tempo_json`

**Cause:** Double `/api` prefix due to wrong NEXT_PUBLIC_API_URL

**Fix:**
```bash
# On server
cd nasa_zeus/frontend
echo "NEXT_PUBLIC_API_URL=https://www.nasazeus.org" > .env.local
npm run build
pm2 restart frontend
```

### Issue 2: TEMPO timeout errors

**Symptom:** "httpx.ReadTimeout" in backend logs

**Fix:** Already implemented in main.py:
```python
async with httpx.AsyncClient(timeout=30.0) as client:
    response = await client.get(image_server_url, ...)
```

### Issue 3: Gemini API quota exceeded

**Symptom:** "429 You exceeded your current quota"

**Solutions:**
1. Wait 24 hours for quota reset
2. Use a different Gemini API key
3. Upgrade to Gemini paid plan

### Issue 4: CORS errors

**Fix:** Already configured in main.py with wildcard origins and all necessary headers.

## 📝 Pre-Deployment Verification

Run this checklist before every deployment:

- [ ] Frontend `.env.local` has NO `/api` suffix in `NEXT_PUBLIC_API_URL`
- [ ] Backend `.env` has valid API keys
- [ ] Caddy config does NOT strip `/api` prefix
- [ ] Frontend is built with `npm run build`
- [ ] All PM2 services restart successfully
- [ ] Test all endpoints with curl
- [ ] Check PM2 logs for errors: `pm2 logs --lines 100`

## 🔄 Quick Redeploy Script

```bash
#!/bin/bash
# Save as: deployment/quick-redeploy.sh

ssh -i deployment/nasa-zeus-key.pem ubuntu@98.80.14.227 << 'ENDSSH'
cd nasa_zeus
git pull origin main
source venv/bin/activate
pip install -r requirements.txt

# Ensure correct frontend env
echo "NEXT_PUBLIC_API_URL=https://www.nasazeus.org" > frontend/.env.local
echo "NEXT_PUBLIC_GEMINI_URL=https://www.nasazeus.org/gemini" >> frontend/.env.local
echo "NEXT_PUBLIC_SITE_URL=https://www.nasazeus.org" >> frontend/.env.local

cd frontend
npm install
npm run build
cd ..

pm2 restart all
pm2 logs --lines 30 --nostream
ENDSSH

echo "✅ Deployment complete! Check https://www.nasazeus.org"
```

Make executable: `chmod +x deployment/quick-redeploy.sh`

## 🎯 Testing After Deployment

1. **Open browser:** https://www.nasazeus.org
2. **Check browser console:** Should see NO 405 or CORS errors
3. **Verify map data:** Should see:
   - TEMPO NO2 satellite data points
   - OpenAQ ground station markers
   - Heatmap visualization
4. **Test O3 prediction:** May fail if Gemini quota exhausted (expected)
5. **Check backend logs:** `ssh ... "pm2 logs backend --lines 50"`

## 📊 Success Indicators

- ✅ All API calls return 200 status
- ✅ Map shows air quality data from multiple sources
- ✅ No `/api/api/` paths in browser network tab
- ✅ PM2 shows all services online
- ✅ No CORS errors in browser console

## 🆘 Emergency Rollback

If deployment fails:

```bash
ssh -i deployment/nasa-zeus-key.pem ubuntu@98.80.14.227
cd nasa_zeus
git reset --hard HEAD~1  # Rollback code
pm2 restart all
```

---

**Last Updated:** October 9, 2025
**Tested On:** Ubuntu 22.04, AWS EC2 t3.small
**Domain:** nasazeus.org / www.nasazeus.org
