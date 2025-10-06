# 🤖 Gemini Weather Agent - Quick Start Guide

## ✅ What We Just Built

A complete AI-powered atmospheric data fetcher that uses Google's Gemini AI to search the web and extract real-time weather parameters for your O3 prediction model!

---

## 📋 Files Created

1. **`gemini_weather_agent.py`** - Core AI agent with web search
2. **`gemini_api.py`** - FastAPI backend server
3. **`frontend/src/app/components/GeminiWeatherWidget.js`** - Frontend UI widget
4. Updated **`frontend/src/app/dashboard/page.js`** - Integrated widget into dashboard

---

## 🚀 Setup Instructions

### Step 1: Set Your API Key

```bash
# In the nasa-zeus directory
export GEMINI_API_KEY='your-api-key-here'
```

**OR** create a `.env` file:

```bash
echo "GEMINI_API_KEY=your-api-key-here" > .env
```

### Step 2: Install Python Dependencies

```bash
# Already installed! ✅
# google-generativeai has been added to your environment
```

### Step 3: Start the Gemini API Server

Open a new terminal and run:

```bash
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus
export GEMINI_API_KEY='your-api-key-here'
/Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/.venv/bin/python gemini_api.py
```

You should see:
```
🚀 Starting Gemini Weather Agent API...
📍 API will be available at: http://localhost:8001
📚 Docs available at: http://localhost:8001/docs
```

### Step 4: View Your Dashboard

Your frontend is already running! Just refresh the page:

```
http://localhost:3000/dashboard
```

You'll see the new **"🤖 AI Weather Agent"** widget on the bottom-right!

---

## 🎯 How to Use

1. **Click "🔍 Fetch Data"** on the Gemini widget
2. Wait 10-15 seconds (Gemini is searching the web!)
3. See atmospheric parameters appear:
   - ✅ TS (Temperature)
   - ✅ PS (Surface Pressure)
   - ✅ CLDPRS (Cloud Pressure)
   - ✅ Q250 (Humidity at 250 hPa)
   - ✅ TO3 (Total Ozone)
   - ✅ TOX (Odd Oxygen)

4. **Click any parameter box** to see detailed info:
   - Data sources
   - Timestamps
   - Confidence levels

---

## 🧪 Test the Agent Standalone

Want to test just the Python agent?

```bash
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus
export GEMINI_API_KEY='your-api-key-here'
/Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/.venv/bin/python gemini_weather_agent.py
```

It will prompt you for location and show results in the terminal!

---

## 📊 API Endpoints

### Get Atmospheric Data
```bash
GET http://localhost:8001/atmospheric-data?location=New%20York%20City
```

Response:
```json
{
  "success": true,
  "data": {
    "location": "New York City",
    "parameters": {
      "TS": {"value": 288.5, "unit": "K", "source": "NOAA", "confidence": "high"},
      "PS": {"value": 101325, "unit": "Pa", "source": "Weather.gov", "confidence": "high"},
      ...
    }
  }
}
```

### Health Check
```bash
GET http://localhost:8001/health
```

### API Documentation
```
http://localhost:8001/docs
```

---

## 🎨 What It Looks Like

The widget matches your dashboard's glassmorphism aesthetic:
- **Ultra-transparent background**: `bg-gray-900/20`
- **Subtle blur**: `backdrop-blur-sm`
- **White border**: `border-white/10`
- **Grid layout** for all 6 parameters
- **Confidence indicators**: ✅ (high), ⚠️ (medium), ❓ (low)

---

## 🔧 Customization

### Change Location

Edit `dashboard/page.js`:
```javascript
<GeminiWeatherWidget location="Los Angeles" />
```

### Adjust Update Frequency

The data is fetched on-demand (click button). To auto-refresh, add in `GeminiWeatherWidget.js`:

```javascript
useEffect(() => {
  const interval = setInterval(() => {
    fetchWeatherData();
  }, 300000); // Every 5 minutes
  
  return () => clearInterval(interval);
}, []);
```

### Modify Parameters

Edit the prompt in `gemini_weather_agent.py` (line 28) to add/remove parameters!

---

## 💡 Pro Tips

1. **Free Tier Limits**: 15 requests/minute, 1M tokens/day
   - Perfect for your use case!
   - Each request uses ~5000 tokens
   
2. **Caching**: Consider caching results for 5-10 minutes to save API calls

3. **Fallback**: If Gemini is down, fall back to your MERRA-2 CSV:
   ```python
   import pandas as pd
   df = pd.read_csv('MACHINE_LEARNING/merra2_nyc_final_dataset.csv')
   ```

4. **Map Integration**: Next step - display these values as map layers!

---

## 🐛 Troubleshooting

### "GEMINI_API_KEY not configured"
- Make sure you exported the key: `export GEMINI_API_KEY='your-key'`
- Restart the API server after setting the key

### "Failed to fetch atmospheric data"
- Check if API server is running on port 8001
- Check CORS settings in `gemini_api.py` (already configured for localhost:3000)

### Widget not showing
- Make sure frontend dev server is running: `npm run dev`
- Check browser console for errors
- Verify the import path in `dashboard/page.js`

---

## 📈 Next Steps

1. ✅ **DONE**: Gemini agent fetching atmospheric data
2. **TODO**: Add map layers for each parameter
3. **TODO**: Connect to your O3 prediction model
4. **TODO**: Display predictions on the map
5. **TODO**: Add time-series charts for parameters

---

## 🎉 You're Ready!

Just run:
```bash
# Terminal 1: Start Gemini API
export GEMINI_API_KEY='your-key'
/Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/.venv/bin/python gemini_api.py

# Terminal 2: Already running!
# cd frontend && npm run dev
```

Then visit: **http://localhost:3000/dashboard**

Click **"🔍 Fetch Data"** and watch the magic happen! 🎊

---

**Built in under 30 minutes! 🚀**
