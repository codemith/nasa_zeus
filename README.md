<div align="center">

# NASA Zeus Air Quality Monitoring System

### *Real-time Air Quality Intelligence with AI-Powered Predictions*

## Data Sources

| Source | Type | Usage |
|--------|------|-------|
| **OpenAQ** | Ground Stations | Real-time PM2.5, PM10, O3, NO2, SO2, CO |
| **NASA TEMPO** | Satellite | Tropospheric air quality observations |
| **NASA MERRA-2** | Reanalysis | Historical atmospheric data (15,552 records) |
| **NOAA GFS** | Model | Weather forecasts and atmospheric parameters |
| **NOAA METAR** | Ground Stations | Surface temperature and pressure |

---

## Overview

**NASA Zeus** is an enterprise-grade air quality monitoring platform that combines real-time ground station data, satellite observations, and machine learning to provide actionable air quality intelligence. Developed for the NASA Space Apps Challenge, it addresses critical environmental monitoring needs through innovative data integration and AI-powered analytics.

### Key Capabilities

- **Real-Time Monitoring**: Interactive heat maps with live air quality data from 10,000+ stations worldwide
- **Satellite Integration**: NASA TEMPO and MERRA-2 satellite data for comprehensive atmospheric analysis
- **AI Weather Agent**: Google Gemini-powered intelligent assistant for atmospheric data retrieval and analysis
- **Predictive Analytics**: XGBoost-based machine learning model for O3 (ozone) concentration predictions
- **Multi-Source Fusion**: Seamless integration of ground stations, satellite data, and weather forecasts
- **Enterprise Security**: JWT-based authentication with role-based access control
- **Historical Analysis**: Time-series visualization and trend analysis for pollution patterns
- **Real-Time Alerts**: Configurable threshold-based notifications for air quality events

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Client Layer                              │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │         Next.js Frontend (React + TailwindCSS)            │   │
│  │  • Interactive Maps (Leaflet) • Real-time Dashboard       │   │
│  │  • User Authentication • AI Chat Interface                │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Application Layer                            │
│  ┌─────────────────────┐  ┌──────────────────────────────────┐  │
│  │   FastAPI Backend   │  │   Gemini AI Service              │  │
│  │   • REST API        │  │   • Atmospheric Data Retrieval   │  │
│  │   • Authentication  │  │   • O3 Prediction Engine         │  │
│  │   • Data Aggregation│  │   • XGBoost ML Model             │  │
│  │   Port: 8000        │  │   Port: 8001                     │  │
│  └─────────────────────┘  └──────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Layer                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │ OpenAQ   │  │   NASA   │  │  NOAA    │  │ Weather  │        │
│  │   API    │  │  TEMPO   │  │   GFS    │  │   APIs   │        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
│       Ground Stations    Satellite Data    Atmospheric Models   │
└─────────────────────────────────────────────────────────────────┘
```

---

## Features

### User Interface
- **Responsive Design**: Mobile-first approach with TailwindCSS
- **Interactive Maps**: Leaflet-based heat maps with real-time data overlay
- **Dark/Light Mode**: Customizable theme preferences
- **Accessibility**: WCAG 2.1 AA compliant

### Data & Analytics
- **Multi-Pollutant Tracking**: PM2.5, PM10, O3, NO2, SO2, CO monitoring
- **Historical Data**: Access to years of archived measurements
- **Trend Analysis**: Statistical analysis and visualization
- **Data Export**: CSV, JSON formats for research use

### AI & Machine Learning
- **Gemini Integration**: Natural language queries for atmospheric data
- **O3 Prediction Model**: 
  - XGBoost regression model
  - Input features: PS, TS, CLDPRS, Q250, TO3
  - Trained on 15,552 NYC MERRA-2 records
  - Prediction accuracy: RMSE < 15 ppb

### Security & Authentication
- **JWT Tokens**: Secure stateless authentication
- **Password Hashing**: bcrypt with salt rounds
- **CORS Protection**: Configurable cross-origin policies
- **Rate Limiting**: API throttling to prevent abuse

---

## API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create new user account |
| POST | `/auth/login` | Login and receive JWT token |
| GET | `/auth/me` | Get current user info |

### Air Quality Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/air-quality` | Get real-time air quality data |
| GET | `/api/stations` | List all monitoring stations |
| GET | `/api/historical/{location}` | Get historical data |

### Gemini AI Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/atmospheric-data?location={city}` | Get atmospheric parameters |
| GET | `/predict-o3?location={city}` | Predict O3 concentration |

**Interactive API Documentation**: Visit http://localhost:8000/docs after starting the backend

---
## Technology Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Styling**: TailwindCSS
- **Maps**: Leaflet + React-Leaflet
- **State Management**: React Hooks
- **HTTP Client**: Axios

### Backend
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLAlchemy + SQLite
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt
- **Validation**: Pydantic

### AI & Machine Learning
- **LLM**: Google Gemini 1.5 Flash
- **ML Framework**: XGBoost 1.7.6
- **Data Processing**: Pandas, NumPy
- **Scientific**: SciPy, scikit-learn

### DevOps
- **Cloud**: AWS EC2 (t3.small)
- **CI/CD**: GitHub Actions (optional)
- **Monitoring**: CloudWatch (optional)
- **Containerization**: Docker (optional)

---
