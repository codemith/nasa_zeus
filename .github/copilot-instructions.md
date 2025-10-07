# NASA Zeus Air Quality System - AI Agent Instructions

## Project Overview

This is a full-stack air quality monitoring system built for NASA hackathon, combining multiple data sources (OpenAQ ground stations, NASA TEMPO satellite, OpenWeatherMap forecasts) into a unified dashboard with heat map visualization.

## Architecture

-   **Backend**: FastAPI (`main.py`) - single file with CORS for frontend communication
-   **Frontend**: Next.js 15 with React Leaflet (`frontend/`) - map-centered visualization
-   **Data Collection**: Async Python scripts (`preprocess/`) - modular collection from 3 APIs
-   **Data Storage**: CSV files in `data/` directory - simple append-based persistence

## Key Development Patterns

### API Integration Strategy

All external API calls use `httpx` async client with comprehensive error handling. Example pattern:

```python
async with httpx.AsyncClient(timeout=30.0) as client:
    try:
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as e:
        # Log and return empty list, never crash
        return []
```

### Data Normalization Convention

All data sources are normalized to consistent schema in `normalize_data()`:

-   Timestamp (UTC), source, location_name, lat/lon, parameter, value, unit
-   Weather context fields: temperature, humidity, wind_speed, wind_deg, pressure
-   AQI mapping: 1=Good, 2=Fair, 3=Moderate, 4=Poor, 5=Very Poor

### Environment Configuration

-   Two separate requirements files: `requirements.txt` (FastAPI) and `requirements_data_collection.txt` (data scripts)
-   API keys in `.env` file - OpenWeatherMap required, OpenAQ optional but recommended
-   Use `python-dotenv` for environment variable loading

### Frontend Architecture

-   Dynamic imports for map components to prevent SSR issues: `dynamic(() => import('./components/Map'), { ssr: false })`
-   React Leaflet with heatmap layer for visualization
-   Direct API calls to FastAPI backend running on different port

## Critical Workflows

### Development Setup

```bash
# Backend
pip install -r requirements.txt
uvicorn main:app --reload

# Frontend (separate terminal)
cd frontend
npm install
npm run dev

# Data collection setup verification
python test_setup.py
```

### Data Collection Pipeline

1. Run `collect_air_quality_data.py` for one-time collection
2. Use `example_scheduled_collection.py` for multiple cities
3. Data appends to existing CSV with deduplication
4. Scheduling via cron: `0 * * * * cd /path && python3 collect_air_quality_data.py`

### API Endpoint Patterns

FastAPI endpoints follow specific patterns:

-   `/api/openaq-latest`: Queries multiple overlapping circles (25km radius limit workaround)
-   `/api/tempo-grid`: Generates mock grid data for heatmap (replace with real TEMPO data)
-   `/api/forecast`: Returns OpenWeatherMap 24-hour forecast array

## Project-Specific Conventions

### Error Handling Philosophy

Never crash on API failures - always return empty arrays/lists and log errors. Frontend should gracefully handle missing data.

### Coordinate System

All coordinates use WGS84 (lat/lon decimal degrees). Distance calculations use Haversine formula for accuracy.

### File Organization

-   `preprocess/` contains standalone data collection scripts that can be imported or run directly
-   `frontend/src/app/components/` for React components (Map.tsx, ForecastChart.tsx, InfoPanel.tsx)
-   `data/` directory auto-created, contains CSV files and analysis outputs

### Testing Strategy

Use `test_setup.py` to verify environment before development. No formal test suite - relies on API connectivity tests and manual validation.

## Integration Points

### Backend ↔ Data Collection

FastAPI endpoints replicate data collection logic from `preprocess/collect_air_quality_data.py`. Keep both in sync when adding new data sources.

### Frontend ↔ Backend Communication

-   Frontend expects specific JSON structures from backend APIs
-   CORS configured for wildcard origins in development
-   Error states handled with fallback mock data

### External Dependencies

-   OpenAQ API v3 requires API key for production use
-   NASA TEMPO has no official rate limits but be conservative
-   OpenWeatherMap free tier: 60 calls/minute, cache forecast data

## Development Tips

-   Use `--no-save` flag when testing data collection to avoid CSV pollution
-   Frontend development: restart Next.js dev server when map components change
-   API debugging: Check `data_collection.log` for detailed error messages
-   For new pollutant parameters, update both normalization schema and frontend visualization
