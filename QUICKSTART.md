# 🚀 QUICK START - 3 STEPS TO LAUNCH!

## Step 1: Add Your API Key

Open the `.env` file and replace `your-api-key-here` with your actual Gemini API key:

```bash
# Edit .env file
GEMINI_API_KEY=AIzaSyC_your_actual_key_here
```

**Get your API key from:** https://aistudio.google.com/app/apikey

---

## Step 2: Start the Gemini API Server

Open a **NEW TERMINAL** and run:

```bash
cd /Users/mithileshbiradar/Desktop/Lockin_Repository/nasa-zeus/nasa-zeus
./start_gemini_server.sh
```

You should see:
```
🤖 Starting Gemini Weather Agent API Server...
📄 Loading .env file...
✅ Environment variables loaded
✅ API Key is set
🚀 Starting server on http://localhost:8001
```

---

## Step 3: View Your Dashboard

Your frontend is already running! Just refresh:

**http://localhost:3000/dashboard**

You'll see the new **🤖 AI Weather Agent** widget on the bottom-right corner!

---

## 🎯 Test It!

1. Click **"🔍 Fetch Data"** button
2. Wait 10-15 seconds (Gemini searches the web!)
3. See all atmospheric parameters appear:
   - ✅ TS (Temperature)
   - ✅ PS (Surface Pressure)
   - ✅ CLDPRS (Cloud Pressure)
   - ✅ Q250 (Humidity)
   - ✅ TO3 (Total Ozone)
   - ✅ TOX (Odd Oxygen)

4. Click any parameter to see details (source, timestamp, confidence)

---

## ✅ That's It!

**Total Time:** Under 5 minutes! 🎊

### Your Running Services:
- ✅ Frontend: http://localhost:3000
- ✅ Gemini API: http://localhost:8001
- ✅ API Docs: http://localhost:8001/docs

---

## 🔧 Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you edited `.env` and added your real API key
- Restart the server: `Ctrl+C` then `./start_gemini_server.sh` again

### Widget not showing
- Make sure frontend is running: `npm run dev` in `/frontend` directory
- Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+R` (Windows)

### Port 8001 already in use
- Kill existing process: `lsof -ti:8001 | xargs kill -9`
- Then restart server

---

## 📖 Full Documentation

See **GEMINI_SETUP_GUIDE.md** for complete details, API endpoints, and advanced features!

---

**🎉 BUILT IN 30 MINUTES! NOW GO FETCH SOME WEATHER DATA! 🌍**
