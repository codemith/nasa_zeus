# 🎨 NASA ZEUS Deployment Architecture

## 🏗️ Infrastructure Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     INTERNET                                │
│                  (Users & Browsers)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTPS (443)
                           │ HTTP (80) → redirects to HTTPS
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                    nasazeus.org                             │
│                  www.nasazeus.org                           │
│                   (DNS A Records)                           │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Points to →
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              AWS EC2 t3.small Instance                      │
│              Ubuntu 22.04 LTS                               │
│              Public IP: XXX.XXX.XXX.XXX                     │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Caddy Web Server (Port 80/443)            │  │
│  │  • Automatic HTTPS/SSL (Let's Encrypt)              │  │
│  │  • Reverse Proxy                                     │  │
│  │  • Security Headers                                  │  │
│  │  • Request Routing                                   │  │
│  └────────────┬─────────────────────┬───────────────────┘  │
│               │                     │                       │
│               │                     │                       │
│    ┌──────────▼────────┐  ┌────────▼────────┐             │
│    │   /api/* routes   │  │  All other routes│             │
│    │   Port 8000       │  │   Port 3000      │             │
│    └──────────┬────────┘  └────────┬─────────┘             │
│               │                     │                       │
│  ┌────────────▼──────────────────────▼───────────────────┐ │
│  │              PM2 Process Manager                      │ │
│  │  • Auto-restart on crash                             │ │
│  │  • Log management                                    │ │
│  │  • Cluster mode support                              │ │
│  │  • Startup on boot                                   │ │
│  └────┬──────────────┬─────────────────┬─────────────────┘ │
│       │              │                 │                   │
│  ┌────▼─────┐  ┌────▼──────┐  ┌──────▼────────┐          │
│  │ Backend  │  │ Frontend  │  │ Gemini Server │          │
│  │ FastAPI  │  │ Next.js   │  │  (Optional)   │          │
│  │ Uvicorn  │  │ Prod Build│  │   Port 8080   │          │
│  │ Port 8000│  │ Port 3000 │  └───────────────┘          │
│  └────┬─────┘  └────┬──────┘                              │
│       │             │                                      │
│  ┌────▼─────────────▼──────────────────────────────────┐  │
│  │      Python Virtual Environment (venv)              │  │
│  │  • FastAPI, Uvicorn, SQLAlchemy                    │  │
│  │  • httpx, pandas, numpy                            │  │
│  │  • XGBoost, scikit-learn                           │  │
│  │  • Google Generative AI                            │  │
│  └──────────────────────┬──────────────────────────────┘  │
│                         │                                  │
│  ┌──────────────────────▼──────────────────────────────┐  │
│  │           SQLite Database                           │  │
│  │  • User accounts                                    │  │
│  │  • User preferences                                 │  │
│  │  • Alerts & notifications                           │  │
│  │  File: nasa_zeus.db                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │           CSV Data Files (data/)                    │  │
│  │  • air_quality_dataset.csv                          │  │
│  │  • tempo_nyc_timeseries.csv                         │  │
│  │  • Analysis outputs                                 │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ External API Calls
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  External Data Sources                      │
├─────────────────────────────────────────────────────────────┤
│  • OpenAQ API (Ground stations)                            │
│  • NASA TEMPO Satellite (NO₂, O₃)                          │
│  • OpenWeatherMap (Forecasts, current weather)             │
│  • NOAA Weather API (Surface pressure)                     │
│  • Google Gemini AI (Chat & insights)                      │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Request Flow

### 1. User Visits Website
```
User Browser → nasazeus.org (DNS lookup) → EC2 Public IP
```

### 2. HTTPS Handling
```
Request → Caddy (Port 443)
         ├─ If HTTP → Redirect to HTTPS
         ├─ SSL/TLS Termination
         └─ Route Decision
```

### 3. Backend API Request
```
/api/openaq-latest → Caddy → Backend (Port 8000)
                              ├─ FastAPI Router
                              ├─ External API Calls
                              ├─ Data Processing
                              └─ JSON Response
```

### 4. Frontend Page Request
```
/ → Caddy → Frontend (Port 3000)
            ├─ Next.js SSR/SSG
            ├─ React Components
            ├─ API Calls to Backend
            └─ Rendered HTML
```

## 📦 Deployment Flow

```
┌─────────────────────┐
│   LOCAL MACHINE     │
│   (Developer)       │
└──────────┬──────────┘
           │
           │ Step 1: Run deployment script
           │ ./deploy-nasazeus-org.sh aws-setup
           ▼
┌─────────────────────────────────────┐
│      AWS CLI Commands               │
│  • Create Security Group            │
│  • Launch EC2 Instance              │
│  • Configure Firewall Rules         │
└──────────┬──────────────────────────┘
           │
           │ Instance Created
           │ Public IP: XXX.XXX.XXX.XXX
           ▼
┌─────────────────────────────────────┐
│   MANUAL STEP: Configure DNS        │
│   A Record: nasazeus.org → IP       │
│   Wait for DNS Propagation          │
└──────────┬──────────────────────────┘
           │
           │ Step 2: Copy script to EC2
           │ scp deploy-nasazeus-org.sh ubuntu@IP:~/
           ▼
┌─────────────────────────────────────┐
│      SSH into EC2 Instance          │
│   ssh -i key.pem ubuntu@IP          │
└──────────┬──────────────────────────┘
           │
           │ Step 3: Run server setup
           │ ./deploy-nasazeus-org.sh server-setup
           ▼
┌─────────────────────────────────────┐
│    Automated Server Setup           │
│  1. Update system packages          │
│  2. Install Python 3 + pip          │
│  3. Install Node.js 18              │
│  4. Install PM2                     │
│  5. Install Caddy                   │
│  6. Clone git repository            │
│  7. Setup Python venv               │
│  8. Install dependencies            │
│  9. Build Next.js                   │
│ 10. Start PM2 processes             │
│ 11. Configure Caddy                 │
│ 12. Enable auto-start               │
└──────────┬──────────────────────────┘
           │
           │ Services Running
           ▼
┌─────────────────────────────────────┐
│    Configure API Keys               │
│   nano .env                         │
│   pm2 restart all                   │
└──────────┬──────────────────────────┘
           │
           │ Deployment Complete!
           ▼
┌─────────────────────────────────────┐
│   Live at https://nasazeus.org      │
│   ✅ Auto HTTPS                     │
│   ✅ Auto restart on crash          │
│   ✅ Production ready                │
└─────────────────────────────────────┘
```

## 🔐 Security Layers

```
┌─────────────────────────────────────────────────────┐
│           Layer 1: AWS Security                     │
│  • EC2 Security Group (Firewall)                   │
│  • Only ports 22, 80, 443 open                     │
│  • SSH key authentication only                     │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│           Layer 2: Caddy Security                   │
│  • Automatic HTTPS/TLS 1.3                         │
│  • Security headers (HSTS, XSS, etc)               │
│  • Rate limiting (configurable)                    │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Layer 3: Application Security               │
│  • JWT authentication                              │
│  • Password hashing (bcrypt)                       │
│  • CORS configuration                              │
│  • Input validation                                │
└────────────────┬────────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────────┐
│         Layer 4: Data Security                      │
│  • API keys in environment variables               │
│  • Database credentials secured                    │
│  • No secrets in code/git                          │
└─────────────────────────────────────────────────────┘
```

## 📊 Resource Allocation

### t3.small Instance (2GB RAM, 2 vCPU)

```
┌─────────────────────────────────────────┐
│         Memory Allocation (2GB)         │
├─────────────────────────────────────────┤
│  System/OS:        400MB  ████          │
│  Caddy:             50MB  █             │
│  Backend:          600MB  ████████████  │
│  Frontend:         600MB  ████████████  │
│  Gemini:           200MB  ████          │
│  Buffer/Cache:     150MB  ███           │
└─────────────────────────────────────────┘
```

### CPU Usage (Typical)
```
Backend:     40% (API requests, data processing)
Frontend:    30% (SSR/SSG rendering)
Caddy:       10% (proxy, SSL)
Gemini:      15% (AI queries)
System:       5% (OS overhead)
```

## 🔄 Data Flow Example

### Air Quality Query Flow
```
1. User clicks "View Air Quality"
   ↓
2. Frontend (React) → API call to /api/openaq-latest
   ↓
3. Caddy → Routes to Backend (Port 8000)
   ↓
4. FastAPI endpoint handler
   ↓
5. httpx client → OpenAQ API (external)
   ↓
6. Data normalization & processing
   ↓
7. Cache in memory (optional)
   ↓
8. JSON response → Caddy → Frontend
   ↓
9. React updates state
   ↓
10. Leaflet map renders markers
```

## 🎯 Deployment Phases

### Phase 1: Infrastructure (5 min)
```
┌─────────────────┐
│  AWS Resources  │  EC2 + Security Group
│   Provisioning  │  ✅ Automated
└─────────────────┘
```

### Phase 2: DNS Configuration (10-60 min)
```
┌─────────────────┐
│  DNS Provider   │  A Record Setup
│  Configuration  │  ⚠️ Manual + Wait Time
└─────────────────┘
```

### Phase 3: Server Setup (10 min)
```
┌─────────────────┐
│  Application    │  Install + Configure
│   Deployment    │  ✅ Automated
└─────────────────┘
```

### Phase 4: Configuration (2 min)
```
┌─────────────────┐
│   API Keys &    │  Environment Variables
│  Final Config   │  ⚠️ Manual
└─────────────────┘
```

## 📈 Scalability Path

### Current: Single t3.small
```
100-200 concurrent users
5,000-10,000 requests/hour
```

### Scale Up: t3.medium
```
200-400 concurrent users
10,000-20,000 requests/hour
Cost: ~$30/month
```

### Scale Out: Load Balancer + Multiple Instances
```
500+ concurrent users
50,000+ requests/hour
Cost: ~$100+/month
```

---

**Diagram Version**: 1.0  
**Last Updated**: October 2025  
**Architecture**: Production Ready
