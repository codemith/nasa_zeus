# NASA Zeus Air Quality System 🌍

> Real-time air quality monitoring combining ground stations, satellite data, and AI-powered predictions

[![NASA Hackathon](https://img.shields.io/badge/NASA-Hackathon-blue.svg)](https://www.spaceappschallenge.org/)
[![Python](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-15-black.svg)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green.svg)](https://fastapi.tiangolo.com/)

## 📖 Overview

NASA Zeus is a comprehensive air quality monitoring system that integrates multiple data sources into a unified dashboard with heat map visualization. Built for the NASA Space Apps Challenge, it combines:

- **Ground Stations**: Real-time data from OpenAQ API
- **Satellite Data**: NASA TEMPO satellite observations  
- **Weather Forecasts**: OpenWeatherMap integration
- **AI Agent**: Gemini-powered weather analysis and O3 predictions

## ✨ Features

- 🗺️ **Interactive Heat Map**: Real-time air quality visualization with Leaflet
- 📊 **Multi-Source Data**: Ground stations, satellite, and forecast data
- 🤖 **AI Weather Agent**: Chat interface powered by Google Gemini
- 🔮 **O3 Predictions**: Machine learning-based ozone forecasting
- 📈 **Historical Analysis**: Trend analysis and data visualization
- 🌡️ **Weather Context**: Temperature, humidity, wind, and pressure data

## 🚀 Quick Start

### Local Development

1. **Clone the repository**
```bash
git clone https://github.com/codemith/nasa-zeus.git
cd nasa-zeus
```

2. **Set up environment**
```bash
# Create .env file with your API keys
cat > .env << EOF
GEMINI_API_KEY=your_gemini_api_key
OPENWEATHER_API_KEY=your_openweather_api_key
OPENAQ_API_KEY=your_openaq_api_key
JWT_SECRET_KEY=your_secret_key
EOF
```

3. **Run with Docker** (Recommended)
```bash
cd deployment
docker-compose up --build
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