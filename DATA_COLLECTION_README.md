# Air Quality Data Collection Script

## Overview
This script collects historical and forecast air quality data from multiple sources:
- **OpenAQ**: Ground station measurements (NO2, O3, SO2, CO, PM2.5, PM10)
- **NASA TEMPO**: Satellite NO₂ measurements
- **OpenWeatherMap**: Air quality forecasts + weather context (temperature, humidity, wind)

The data is normalized into a unified Pandas DataFrame and stored in CSV format for ML model training or analysis.

## Features
✅ Async API calls using `httpx` for fast concurrent data collection  
✅ Comprehensive error handling and logging  
✅ Modular design for scheduling with cron/Prefect/Airflow  
✅ Automatic deduplication when appending to existing datasets  
✅ Weather context integration (temperature, humidity, wind, pressure)  
✅ Command-line interface for flexible execution  

## Installation

### 1. Install Dependencies
```bash
pip install -r requirements_data_collection.txt
```

Or install individually:
```bash
pip install httpx pandas numpy python-dotenv
```

### 2. Set Environment Variables (Optional)
Create a `.env` file in the project root:
```bash
# Optional: OpenAQ API key (v3 API works without it for basic usage)
OPENAQ_API_KEY=your_key_here

# Required: OpenWeatherMap API key
OPENWEATHER_API_KEY=your_key_here
```

## Usage

### Basic Usage (Default NYC location)
```bash
python collect_air_quality_data.py
```

### Custom Location
```bash
# Collect data for Los Angeles with 50km radius
python collect_air_quality_data.py --lat 34.0522 --lon -118.2437 --radius 50000
```

### Command-Line Options
```bash
python collect_air_quality_data.py --help
```

**Available Arguments:**
- `--lat`: Latitude coordinate (default: 40.7128 - NYC)
- `--lon`: Longitude coordinate (default: -74.0060 - NYC)
- `--radius`: Search radius in meters for OpenAQ (default: 25000 = 25km)
- `--no-save`: Don't save to CSV, just print to console
- `--overwrite`: Overwrite existing CSV instead of appending
- `--output`: Custom output filename (default: air_quality_dataset.csv)

### Examples

**Collect and append to existing dataset:**
```bash
python collect_air_quality_data.py --lat 40.7128 --lon -74.0060
```

**Collect and overwrite existing dataset:**
```bash
python collect_air_quality_data.py --lat 40.7128 --lon -74.0060 --overwrite
```

**Collect data for San Francisco, save to custom file:**
```bash
python collect_air_quality_data.py --lat 37.7749 --lon -122.4194 --output sf_air_quality.csv
```

**Test API connections without saving:**
```bash
python collect_air_quality_data.py --no-save
```

## Output Data Schema

The script generates a CSV file with the following columns:

| Column         | Type     | Description                                      |
|----------------|----------|--------------------------------------------------|
| timestamp      | datetime | UTC timestamp of measurement/forecast            |
| source         | string   | Data source (openaq, tempo, openweather_forecast)|
| location_name  | string   | Station/sensor name                              |
| latitude       | float    | Latitude coordinate                              |
| longitude      | float    | Longitude coordinate                             |
| parameter      | string   | Pollutant type (NO2, O3, SO2, CO, PM2.5, PM10, NH3)|
| value          | float    | Measured/forecasted value                        |
| unit           | string   | Measurement unit (μg/m³, molecules/cm²)          |
| aqi            | int      | Air Quality Index (1-5, OpenWeatherMap only)     |
| temperature    | float    | Temperature in Celsius (forecast only)           |
| humidity       | int      | Relative humidity % (forecast only)              |
| wind_speed     | float    | Wind speed in m/s (forecast only)                |
| wind_deg       | int      | Wind direction in degrees (forecast only)        |
| pressure       | int      | Atmospheric pressure in hPa (forecast only)      |

### Sample Output
```csv
timestamp,source,location_name,latitude,longitude,parameter,value,unit,aqi,temperature,humidity,wind_speed,wind_deg,pressure
2025-10-03T12:00:00+00:00,openaq,Manhattan,40.7580,-73.9855,PM2.5,12.5,μg/m³,,,,,,
2025-10-03T12:00:00+00:00,tempo,TEMPO Satellite,40.7128,-74.0060,NO2,2.72e+14,molecules/cm²,,,,,,
2025-10-03T15:00:00+00:00,openweather_forecast,OpenWeatherMap Forecast,40.7128,-74.0060,O3,45.2,μg/m³,2,18.5,65,3.2,180,1013
```

## Scheduling for Automated Collection

### Option 1: Cron (Linux/macOS)
Edit crontab:
```bash
crontab -e
```

Add entry to run every hour:
```bash
0 * * * * cd /path/to/nasa-zeus && /usr/bin/python3 collect_air_quality_data.py >> data/cron.log 2>&1
```

### Option 2: Prefect Flow
```python
from prefect import flow, task
from collect_air_quality_data import main

@task
async def collect_air_quality():
    df = await main(lat=40.7128, lon=-74.0060)
    return df

@flow
def air_quality_pipeline():
    data = collect_air_quality()
    # Add more tasks (preprocessing, model training, etc.)
    return data

if __name__ == "__main__":
    air_quality_pipeline()
```

### Option 3: Airflow DAG
```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import asyncio
from collect_air_quality_data import main

def run_collection():
    asyncio.run(main(lat=40.7128, lon=-74.0060))

default_args = {
    'owner': 'airflow',
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'air_quality_collection',
    default_args=default_args,
    schedule_interval='0 * * * *',  # Hourly
    start_date=datetime(2025, 10, 1),
    catchup=False,
) as dag:
    
    collect_task = PythonOperator(
        task_id='collect_air_quality_data',
        python_callable=run_collection,
    )
```

## Logging

Logs are written to both console and `data_collection.log` file:
- INFO: Successful API calls, data statistics
- WARNING: Empty responses, missing data
- ERROR: API failures, HTTP errors, network issues

**View logs:**
```bash
tail -f data_collection.log
```

## API Rate Limits & Best Practices

### OpenAQ API
- **Rate Limit**: ~100 requests/hour (without API key)
- **With API Key**: Higher limits available
- **Best Practice**: Cache results for 15-30 minutes

### NASA TEMPO API
- **Rate Limit**: No official limit documented
- **Best Practice**: Avoid excessive requests (>1 per minute)

### OpenWeatherMap API
- **Free Tier**: 60 calls/minute, 1,000,000 calls/month
- **Best Practice**: Cache forecast data for 1 hour

## Troubleshooting

### Issue: "No data collected from any source"
**Solution**: Check your internet connection and API keys

### Issue: "HTTP 429 Too Many Requests"
**Solution**: You've hit the rate limit. Wait before retrying or upgrade API plan

### Issue: "pandas module not found"
**Solution**: Install dependencies:
```bash
pip install -r requirements_data_collection.txt
```

### Issue: "Permission denied" when saving CSV
**Solution**: Ensure `data/` directory has write permissions:
```bash
chmod -R 755 data/
```

## Module Functions

The script can also be imported and used programmatically:

```python
import asyncio
from collect_air_quality_data import (
    fetch_openaq_data,
    fetch_tempo_data,
    fetch_openweather_forecast,
    normalize_data,
    save_to_csv,
    collect_all_data
)

# Collect data for specific location
df = asyncio.run(collect_all_data(lat=34.0522, lon=-118.2437, radius=50000))

# Or fetch from individual sources
openaq_data = asyncio.run(fetch_openaq_data(34.0522, -118.2437, 25000))
tempo_data = asyncio.run(fetch_tempo_data(34.0522, -118.2437))
forecast_data = asyncio.run(fetch_openweather_forecast(34.0522, -118.2437))

# Normalize and save
all_data = openaq_data + tempo_data + forecast_data
df = normalize_data(all_data)
save_to_csv(df, filename="custom_dataset.csv")
```

## Next Steps

1. **Build ML Model**: Use collected data to train air quality prediction models
2. **Add More Sources**: Integrate additional APIs (PurpleAir, EPA AirNow)
3. **Historical Data**: Modify TEMPO fetcher to collect historical satellite data
4. **Data Validation**: Add quality checks for outliers and missing values
5. **Database Storage**: Replace CSV with PostgreSQL/TimescaleDB for production

## License
MIT License - Feel free to modify and use for your projects!
