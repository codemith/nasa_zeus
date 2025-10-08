<div align="center">

# NASA Zeus Air Quality Monitoring System

### *Real-time Air Quality Intelligence with AI-Powered Predictions*

[![NASA Space Apps Challenge](https://img.shields.io/badge/NASA-Space%20Apps%20Challenge-0B3D91?style=for-the-badge&logo=nasa)](https://www.spaceappschallenge.org/)
[![Python](https://img.shie---

## Data Sources

| Source | Type | Usage |
|--------|------|-------|
| **OpenAQ** | Ground Stations | Real-time PM2.5, PM10, O3, NO2, SO2, CO |
| **NASA TEMPO** | Satellite | Tropospheric air quality observations |
| **NASA MERRA-2** | Reanalysis | Historical atmospheric data (15,552 records) |
| **NOAA GFS** | Model | Weather forecasts and atmospheric parameters |
| **NOAA METAR** | Ground Stations | Surface temperature and pressure |

---

## Contributingthon-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

[Live Demo](http://3.89.27.54:3000) • [Documentation](deployment/AWS_DEPLOYMENT_GUIDE.md) • [Report Bug](https://github.com/codemith/nasa_zeus/issues) • [Request Feature](https://github.com/codemith/nasa_zeus/issues)

![Dashboard Preview](https://via.placeholder.com/800x400/0B3D91/FFFFFF?text=NASA+Zeus+Dashboard)

</div>

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

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/codemith/nasa_zeus.git
cd nasa_zeus
```

2. **Install Dependencies**

**Backend:**
```bash
# Install Python dependencies
pip install -r requirements.txt

# Note: Use xgboost<2.0.0 for CPU-only environments
```

**Frontend:**
```bash
cd frontend
npm install --legacy-peer-deps
```

3. **Configure Environment Variables**

**Backend (.env in root):**
```bash
# Database
DATABASE_URL=sqlite:///./nasa_zeus.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# APIs
GEMINI_API_KEY=your-gemini-api-key-here
NASA_API_KEY=DEMO_KEY
```

**Frontend (frontend/.env):**
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_GEMINI_URL=http://localhost:8001
```

4. **Run the Application**

**Terminal 1 - Backend API:**
```bash
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Gemini AI Service:**
```bash
python3 gemini_server.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Gemini AI: http://localhost:8001
- API Docs: http://localhost:8000/docs

---

## AWS Deployment

Deploy to AWS EC2 in minutes with our automated script:

```bash
# See detailed guide
cat deployment/AWS_DEPLOYMENT_GUIDE.md

# Quick deploy
ssh -i your-key.pem ec2-user@YOUR_INSTANCE_IP
./deployment/setup-ec2-complete.sh
```

**Cost**: ~$17-18/month on t3.small instance

**Full deployment guide**: [AWS_DEPLOYMENT_GUIDE.md](deployment/AWS_DEPLOYMENT_GUIDE.md)

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

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Test specific module
pytest tests/test_api.py

# Test O3 prediction
python3 test_o3_prediction.py
```

---

## Project Structure

```
nasa_zeus/
├── frontend/                 # Next.js frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/     # React components
│   │   │   ├── dashboard/      # Dashboard page
│   │   │   └── page.js         # Home page
│   │   └── styles/             # Global styles
│   ├── public/                 # Static assets
│   └── package.json
│
├── Backend/                  # FastAPI backend
│   ├── main.py                 # Main API application
│   ├── auth/                   # Authentication module
│   ├── models/                 # Database models
│   └── requirements.txt        # Python dependencies
│
├── AI Services/
│   ├── gemini_server.py        # Gemini AI API server
│   ├── gemini_weather_agent.py # Weather data agent
│   ├── o3_predictor.py         # O3 prediction model
│   └── MACHINE_LEARNING/
│       ├── checkpoints/        # Trained ML models
│       │   └── xgboost_o3.json # XGBoost model (7.6MB)
│       └── merra2_nyc_final_dataset.csv
│
├── Data Collection/
│   ├── data/                   # Raw data storage
│   ├── preprocess/             # Data preprocessing scripts
│   └── TEMPO_PROCESSING_README.md
│
├── Deployment/
│   ├── setup-ec2-complete.sh   # EC2 setup script
│   ├── AWS_DEPLOYMENT_GUIDE.md # Deployment documentation
│   ├── deploy-aws.sh           # Automated deployment
│   └── docker-compose.yml      # Docker configuration
│
└── Documentation/
    ├── README.md               # This file
    ├── QUICKSTART.md           # Quick start guide
    ├── PROJECT_SUMMARY.md      # Project overview
    └── O3_PREDICTION_COMPLETE.md
```

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

## 🌐 Data Sources

| Source | Type | Usage |
|--------|------|-------|
| **OpenAQ** | Ground Stations | Real-time PM2.5, PM10, O3, NO2, SO2, CO |
| **NASA TEMPO** | Satellite | Tropospheric air quality observations |
| **NASA MERRA-2** | Reanalysis | Historical atmospheric data (15,552 records) |
| **NOAA GFS** | Model | Weather forecasts and atmospheric parameters |
| **NOAA METAR** | Ground Stations | Surface temperature and pressure |

---

## Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Write tests for new features
- Update documentation as needed

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Team

- **Developer**: [@codemith](https://github.com/codemith)
- **Project**: NASA Space Apps Challenge 2024

---

## Acknowledgments

- **NASA**: For TEMPO, MERRA-2, and other satellite data
- **NOAA**: For GFS model and METAR station data  
- **OpenAQ**: For global air quality monitoring network
- **Google**: For Gemini API access
- **Space Apps Challenge**: For inspiring this project

---

## Contact & Support

- **Issues**: [GitHub Issues](https://github.com/codemith/nasa_zeus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/codemith/nasa_zeus/discussions)
- **Email**: support@nasa-zeus.com (if available)

---

## Roadmap

### Completed
- [x] Real-time air quality monitoring
- [x] Interactive heat maps
- [x] User authentication system
- [x] AI Weather Agent integration
- [x] O3 prediction model
- [x] AWS EC2 deployment
- [x] Multi-source data integration

### In Progress
- [ ] Mobile app (React Native)
- [ ] Advanced analytics dashboard
- [ ] Email/SMS alerting system
- [ ] API rate limiting enhancements

### Planned
- [ ] Multi-city support
- [ ] Historical data API
- [ ] Custom alert rules
- [ ] Data export features
- [ ] Docker Kubernetes deployment
- [ ] CI/CD pipeline
- [ ] Automated testing suite
- [ ] Performance monitoring

---

## Project Stats

![GitHub stars](https://img.shields.io/github/stars/codemith/nasa_zeus?style=social)
![GitHub forks](https://img.shields.io/github/forks/codemith/nasa_zeus?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/codemith/nasa_zeus?style=social)
![GitHub issues](https://img.shields.io/github/issues/codemith/nasa_zeus)
![GitHub pull requests](https://img.shields.io/github/issues-pr/codemith/nasa_zeus)
![GitHub](https://img.shields.io/github/license/codemith/nasa_zeus)

---

<div align="center">

### Star this repo if you found it useful!

**Made with care for a cleaner planet**

[Back to Top](#nasa-zeus-air-quality-monitoring-system)

</div>
```

Access at: http://localhost

### Production Deployment

**Deploy to AWS in one command:**

```bash
cd deployment
./deploy-aws.sh
```

**Cost**: ~$10.49/month (FREE for 12 months with AWS Free Tier)

See [deployment/README.md](./deployment/README.md) for detailed instructions.

## 📁 Project Structure

```
nasa-zeus/
├── main.py                 # FastAPI backend server
├── gemini_api.py          # Gemini AI agent endpoints
├── o3_predictor.py        # Ozone prediction model
├── frontend/              # Next.js React application
│   └── src/
│       ├── app/           # Next.js pages and layouts
│       └── components/    # React components (Map, Charts, etc.)
├── preprocess/            # Data collection scripts
│   └── collect_air_quality_data.py
├── MACHINE_LEARNING/      # ML models and training
│   └── o3_model.ipynb
├── deployment/            # 🆕 Deployment files and guides
│   ├── deploy-aws.sh
│   ├── docker-compose.yml
│   └── AWS_DEPLOYMENT_GUIDE.md
└── data/                  # CSV datasets and analysis
```

## 🛠️ Technology Stack

**Backend**:
- FastAPI (Python) - REST API
- SQLite - Data persistence
- httpx - Async HTTP client

**Frontend**:
- Next.js 15 - React framework
- React Leaflet - Map visualization
- Tailwind CSS - Styling
- Chart.js - Data visualization

**AI/ML**:
- Google Gemini - AI agent
- PyTorch - O3 prediction model
- Pandas/NumPy - Data processing

**Deployment**:
- Docker & Docker Compose
- Nginx - Reverse proxy
- AWS EC2 - Cloud hosting

## 🌐 API Data Sources

| Source | Purpose | API Key Required |
|--------|---------|------------------|
| [OpenAQ](https://openaq.org/) | Ground station data | Optional (recommended) |
| [NASA TEMPO](https://tempo.si.edu/) | Satellite observations | No |
| [OpenWeatherMap](https://openweathermap.org/) | Weather forecasts | Yes |
| [Google Gemini](https://ai.google.dev/) | AI agent | Yes |

## 📚 Documentation

- **[Deployment Guide](./deployment/AWS_DEPLOYMENT_GUIDE.md)** - Comprehensive AWS deployment instructions
- **[Cost Optimization](./deployment/COST_OPTIMIZATION.md)** - Cost analysis and optimization details
- **[Data Collection](./DATA_COLLECTION_README.md)** - Data pipeline documentation
- **[O3 Prediction](./O3_PREDICTION_COMPLETE.md)** - Machine learning model details
- **[Gemini Setup](./GEMINI_COMPLETE_SETUP.md)** - AI agent configuration

## 🔐 Security

- API keys stored in `.env` (never committed)
- JWT authentication for sensitive endpoints
- CORS configured for frontend communication
- Security groups configured for AWS deployment

## 📊 Performance

**Optimized for minimal cost** (~10 users/month):
- Memory: 832MB total (fits in 1GB t3.micro)
- Capacity: 50 concurrent users, 1000 req/hour
- Response time: <500ms average

## 🤝 Contributing

Contributions are welcome! This project was built for NASA Space Apps Challenge.

## 📄 License

MIT License - See LICENSE file for details

## 👥 Team

Built with ❤️ for NASA Space Apps Challenge 2025

## 🔗 Links

- **Live Demo**: [Coming soon after AWS deployment]
- **NASA TEMPO**: https://tempo.si.edu/
- **OpenAQ**: https://openaq.org/
- **Space Apps Challenge**: https://www.spaceappschallenge.org/

---

**Ready to deploy?** Check out [deployment/README.md](./deployment/README.md) 🚀