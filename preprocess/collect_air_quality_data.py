"""
Air Quality Data Collection Script
===================================
Collects historical and forecast air quality data from multiple sources:
- OpenAQ: Ground station measurements
- NASA TEMPO: Satellite NO₂ measurements
- OpenWeatherMap: Air quality forecast and weather context

Designed to be modular for scheduling with cron/Prefect/Airflow.
"""

import asyncio
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
import json

import httpx
import pandas as pd
from httpx import AsyncClient, HTTPStatusError, RequestError

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """Configuration settings for data collection"""
    
    # API Keys
    OPENAQ_API_KEY = os.getenv("OPENAQ_API_KEY", "")  # Optional for v3
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "06c71052de74828712e5a6a7712ee8fa")
    
    # API Endpoints
    OPENAQ_BASE_URL = "https://api.openaq.org/v3"
    TEMPO_BASE_URL = "https://openapidata.larc.nasa.gov/arcgis/rest/services/TEMPO/TEMPO_NO2_L3/ImageServer"
    OPENWEATHER_BASE_URL = "http://api.openweathermap.org/data/2.5"
    
    # Data Storage
    DATA_DIR = Path("data")
    OUTPUT_FILE = "air_quality_dataset.csv"
    
    # API Request Settings
    TIMEOUT = 30.0
    MAX_RETRIES = 3
    
    # Default collection parameters
    DEFAULT_RADIUS = 25000  # 25km for OpenAQ
    DEFAULT_LOCATION = {"lat": 40.7128, "lon": -74.0060}  # NYC

# =============================================================================
# DATA FETCHING FUNCTIONS
# =============================================================================

async def fetch_openaq_data(
    lat: float,
    lon: float,
    radius: int = Config.DEFAULT_RADIUS,
    client: Optional[AsyncClient] = None
) -> List[Dict[str, Any]]:
    """
    Fetch ground station air quality measurements from OpenAQ API.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        radius: Search radius in meters (max 25000 for single query)
        client: Optional httpx AsyncClient (will create if not provided)
    
    Returns:
        List of normalized measurement dictionaries
    """
    logger.info(f"Fetching OpenAQ data for location ({lat}, {lon}) with radius {radius}m")
    
    should_close = False
    if client is None:
        client = AsyncClient(timeout=Config.TIMEOUT)
        should_close = True
    
    measurements = []
    
    try:
        # OpenAQ v3 locations endpoint
        url = f"{Config.OPENAQ_BASE_URL}/locations/latest"
        
        headers = {}
        if Config.OPENAQ_API_KEY:
            headers["X-API-Key"] = Config.OPENAQ_API_KEY
        
        params = {
            "coordinates": f"{lat},{lon}",
            "radius": radius,
            "limit": 100
        }
        
        response = await client.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if "results" in data and data["results"]:
            timestamp = datetime.now(timezone.utc).isoformat()
            
            for location in data["results"]:
                location_lat = location.get("coordinates", {}).get("latitude")
                location_lon = location.get("coordinates", {}).get("longitude")
                location_name = location.get("name", "Unknown")
                
                # Extract sensor measurements
                for sensor in location.get("sensors", []):
                    parameter = sensor.get("parameter", {})
                    param_name = parameter.get("name", "").upper()
                    
                    measurement = {
                        "timestamp": timestamp,
                        "source": "openaq",
                        "location_name": location_name,
                        "latitude": location_lat,
                        "longitude": location_lon,
                        "parameter": param_name,
                        "value": sensor.get("latest", {}).get("value"),
                        "unit": parameter.get("units", ""),
                        "aqi": None,  # OpenAQ doesn't provide AQI directly
                    }
                    measurements.append(measurement)
            
            logger.info(f"Successfully fetched {len(measurements)} measurements from OpenAQ")
        else:
            logger.warning("No OpenAQ data found for specified location")
    
    except HTTPStatusError as e:
        logger.error(f"HTTP error fetching OpenAQ data: {e.response.status_code} - {e.response.text}")
    except RequestError as e:
        logger.error(f"Request error fetching OpenAQ data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching OpenAQ data: {str(e)}")
    finally:
        if should_close:
            await client.aclose()
    
    return measurements


async def fetch_tempo_data(
    lat: float,
    lon: float,
    time_range: Optional[str] = None,
    client: Optional[AsyncClient] = None
) -> List[Dict[str, Any]]:
    """
    Fetch NASA TEMPO NO₂ satellite measurements.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        time_range: Optional time range for historical data (format: "YYYY-MM-DD,YYYY-MM-DD")
        client: Optional httpx AsyncClient
    
    Returns:
        List of normalized measurement dictionaries
    """
    logger.info(f"Fetching TEMPO NO₂ data for location ({lat}, {lon})")
    
    should_close = False
    if client is None:
        client = AsyncClient(timeout=Config.TIMEOUT)
        should_close = True
    
    measurements = []
    
    try:
        url = f"{Config.TEMPO_BASE_URL}/identify"
        
        params = {
            "f": "json",
            "geometryType": "esriGeometryPoint",
            "geometry": json.dumps({"x": lon, "y": lat, "spatialReference": {"wkid": 4326}}),
            "returnGeometry": "false",
            "returnCatalogItems": "false",
        }
        
        if time_range:
            params["time"] = time_range
        
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if "value" in data:
            timestamp = datetime.now(timezone.utc).isoformat()
            
            # Extract location from response
            location = data.get("location", {})
            actual_lon = location.get("x", lon)
            actual_lat = location.get("y", lat)
            
            measurement = {
                "timestamp": timestamp,
                "source": "tempo",
                "location_name": "TEMPO Satellite",
                "latitude": actual_lat,
                "longitude": actual_lon,
                "parameter": "NO2",
                "value": float(data["value"]) if data["value"] else None,
                "unit": "molecules/cm²",
                "aqi": None,  # TEMPO doesn't provide AQI
            }
            measurements.append(measurement)
            
            logger.info(f"Successfully fetched TEMPO NO₂ measurement: {data['value']}")
        else:
            logger.warning("No TEMPO data available for specified location")
    
    except HTTPStatusError as e:
        logger.error(f"HTTP error fetching TEMPO data: {e.response.status_code}")
    except RequestError as e:
        logger.error(f"Request error fetching TEMPO data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching TEMPO data: {str(e)}")
    finally:
        if should_close:
            await client.aclose()
    
    return measurements


async def fetch_openweather_forecast(
    lat: float,
    lon: float,
    client: Optional[AsyncClient] = None
) -> List[Dict[str, Any]]:
    """
    Fetch air quality forecast and weather context from OpenWeatherMap.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        client: Optional httpx AsyncClient
    
    Returns:
        List of normalized forecast dictionaries with weather context
    """
    logger.info(f"Fetching OpenWeatherMap forecast for location ({lat}, {lon})")
    
    should_close = False
    if client is None:
        client = AsyncClient(timeout=Config.TIMEOUT)
        should_close = True
    
    measurements = []
    
    try:
        # Fetch air quality forecast
        aq_url = f"{Config.OPENWEATHER_BASE_URL}/air_pollution/forecast"
        aq_params = {
            "lat": lat,
            "lon": lon,
            "appid": Config.OPENWEATHER_API_KEY
        }
        
        aq_response = await client.get(aq_url, params=aq_params)
        aq_response.raise_for_status()
        aq_data = aq_response.json()
        
        # Fetch weather forecast for context
        weather_url = f"{Config.OPENWEATHER_BASE_URL}/forecast"
        weather_params = {
            "lat": lat,
            "lon": lon,
            "appid": Config.OPENWEATHER_API_KEY,
            "units": "metric"
        }
        
        weather_response = await client.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        # Create weather lookup by timestamp
        weather_lookup = {}
        if "list" in weather_data:
            for item in weather_data["list"]:
                timestamp = item.get("dt")
                weather_lookup[timestamp] = {
                    "temperature": item.get("main", {}).get("temp"),
                    "humidity": item.get("main", {}).get("humidity"),
                    "wind_speed": item.get("wind", {}).get("speed"),
                    "wind_deg": item.get("wind", {}).get("deg"),
                    "pressure": item.get("main", {}).get("pressure"),
                }
        
        # Process air quality forecast
        if "list" in aq_data:
            for forecast_item in aq_data["list"]:
                forecast_time = forecast_item.get("dt")
                timestamp = datetime.fromtimestamp(forecast_time, tz=timezone.utc).isoformat()
                
                # Get corresponding weather data
                weather_context = weather_lookup.get(forecast_time, {})
                
                # Extract AQI
                aqi = forecast_item.get("main", {}).get("aqi")
                
                # Extract pollutant components
                components = forecast_item.get("components", {})
                
                # Create separate measurements for each pollutant
                pollutants = {
                    "CO": components.get("co"),
                    "NO2": components.get("no2"),
                    "O3": components.get("o3"),
                    "SO2": components.get("so2"),
                    "PM2.5": components.get("pm2_5"),
                    "PM10": components.get("pm10"),
                    "NH3": components.get("nh3")
                }
                
                for pollutant, value in pollutants.items():
                    if value is not None:
                        measurement = {
                            "timestamp": timestamp,
                            "source": "openweather_forecast",
                            "location_name": "OpenWeatherMap Forecast",
                            "latitude": lat,
                            "longitude": lon,
                            "parameter": pollutant,
                            "value": value,
                            "unit": "μg/m³",
                            "aqi": aqi,
                            "temperature": weather_context.get("temperature"),
                            "humidity": weather_context.get("humidity"),
                            "wind_speed": weather_context.get("wind_speed"),
                            "wind_deg": weather_context.get("wind_deg"),
                            "pressure": weather_context.get("pressure"),
                        }
                        measurements.append(measurement)
            
            logger.info(f"Successfully fetched {len(measurements)} forecast measurements from OpenWeatherMap")
        else:
            logger.warning("No forecast data available from OpenWeatherMap")
    
    except HTTPStatusError as e:
        logger.error(f"HTTP error fetching OpenWeatherMap data: {e.response.status_code}")
    except RequestError as e:
        logger.error(f"Request error fetching OpenWeatherMap data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error fetching OpenWeatherMap data: {str(e)}")
    finally:
        if should_close:
            await client.aclose()
    
    return measurements

# =============================================================================
# DATA NORMALIZATION
# =============================================================================

def normalize_data(measurements: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Normalize all API responses into a unified Pandas DataFrame.
    
    Args:
        measurements: List of measurement dictionaries from various sources
    
    Returns:
        Normalized Pandas DataFrame with consistent schema
    """
    logger.info(f"Normalizing {len(measurements)} measurements into DataFrame")
    
    if not measurements:
        logger.warning("No measurements to normalize")
        return pd.DataFrame()
    
    # Create DataFrame
    df = pd.DataFrame(measurements)
    
    # Ensure consistent column order and types
    column_order = [
        "timestamp",
        "source",
        "location_name",
        "latitude",
        "longitude",
        "parameter",
        "value",
        "unit",
        "aqi",
        "temperature",
        "humidity",
        "wind_speed",
        "wind_deg",
        "pressure"
    ]
    
    # Add missing columns with None values
    for col in column_order:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns
    df = df[column_order]
    
    # Convert timestamp to datetime
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    
    # Convert numeric columns
    numeric_cols = ["latitude", "longitude", "value", "aqi", "temperature", 
                    "humidity", "wind_speed", "wind_deg", "pressure"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    
    # Sort by timestamp
    df = df.sort_values("timestamp").reset_index(drop=True)
    
    logger.info(f"Normalized DataFrame shape: {df.shape}")
    logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    logger.info(f"Sources: {df['source'].unique().tolist()}")
    logger.info(f"Parameters: {df['parameter'].unique().tolist()}")
    
    return df

# =============================================================================
# DATA STORAGE
# =============================================================================

def save_to_csv(df: pd.DataFrame, filename: str = Config.OUTPUT_FILE, append: bool = True) -> None:
    """
    Save DataFrame to CSV file.
    
    Args:
        df: DataFrame to save
        filename: Output filename (relative to DATA_DIR)
        append: If True, append to existing file; if False, overwrite
    """
    if df.empty:
        logger.warning("DataFrame is empty, nothing to save")
        return
    
    # Create data directory if it doesn't exist
    Config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    filepath = Config.DATA_DIR / filename
    
    try:
        if append and filepath.exists():
            # Load existing data
            existing_df = pd.read_csv(filepath, parse_dates=["timestamp"])
            
            # Combine and remove duplicates
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df = combined_df.drop_duplicates(
                subset=["timestamp", "source", "latitude", "longitude", "parameter"],
                keep="last"
            )
            combined_df = combined_df.sort_values("timestamp").reset_index(drop=True)
            
            combined_df.to_csv(filepath, index=False)
            logger.info(f"Appended data to {filepath} (total rows: {len(combined_df)})")
        else:
            df.to_csv(filepath, index=False)
            logger.info(f"Saved data to {filepath} ({len(df)} rows)")
    
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        raise

# =============================================================================
# MAIN ORCHESTRATION
# =============================================================================

async def collect_all_data(lat: float, lon: float, radius: int = Config.DEFAULT_RADIUS) -> pd.DataFrame:
    """
    Collect data from all sources concurrently.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        radius: Search radius for OpenAQ (meters)
    
    Returns:
        Normalized DataFrame with all collected data
    """
    logger.info(f"Starting data collection for location ({lat}, {lon})")
    
    async with AsyncClient(timeout=Config.TIMEOUT) as client:
        # Fetch data from all sources concurrently
        tasks = [
            fetch_openaq_data(lat, lon, radius, client),
            fetch_tempo_data(lat, lon, client=client),
            fetch_openweather_forecast(lat, lon, client)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Combine all measurements
        all_measurements = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Task {i} failed with exception: {result}")
            else:
                all_measurements.extend(result)
    
    # Normalize to DataFrame
    df = normalize_data(all_measurements)
    
    return df


async def main(
    lat: float = Config.DEFAULT_LOCATION["lat"],
    lon: float = Config.DEFAULT_LOCATION["lon"],
    radius: int = Config.DEFAULT_RADIUS,
    save: bool = True,
    append: bool = True
) -> pd.DataFrame:
    """
    Main function to orchestrate data collection and storage.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        radius: Search radius for OpenAQ (meters)
        save: Whether to save to CSV
        append: Whether to append to existing CSV or overwrite
    
    Returns:
        DataFrame with collected and normalized data
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info("AIR QUALITY DATA COLLECTION STARTED")
    logger.info(f"Location: ({lat}, {lon})")
    logger.info(f"Radius: {radius}m")
    logger.info("=" * 80)
    
    try:
        # Collect data
        df = await collect_all_data(lat, lon, radius)
        
        # Save to CSV
        if save and not df.empty:
            save_to_csv(df, append=append)
        
        # Summary statistics
        logger.info("=" * 80)
        logger.info("COLLECTION SUMMARY")
        logger.info(f"Total records: {len(df)}")
        logger.info(f"Sources: {df['source'].nunique() if not df.empty else 0}")
        logger.info(f"Parameters: {df['parameter'].nunique() if not df.empty else 0}")
        logger.info(f"Duration: {(datetime.now() - start_time).total_seconds():.2f} seconds")
        logger.info("=" * 80)
        
        return df
    
    except Exception as e:
        logger.error(f"Data collection failed: {str(e)}", exc_info=True)
        raise


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Collect air quality data from multiple sources")
    parser.add_argument("--lat", type=float, default=Config.DEFAULT_LOCATION["lat"],
                        help=f"Latitude (default: {Config.DEFAULT_LOCATION['lat']})")
    parser.add_argument("--lon", type=float, default=Config.DEFAULT_LOCATION["lon"],
                        help=f"Longitude (default: {Config.DEFAULT_LOCATION['lon']})")
    parser.add_argument("--radius", type=int, default=Config.DEFAULT_RADIUS,
                        help=f"Search radius in meters (default: {Config.DEFAULT_RADIUS})")
    parser.add_argument("--no-save", action="store_true",
                        help="Don't save to CSV (just print to console)")
    parser.add_argument("--overwrite", action="store_true",
                        help="Overwrite existing CSV instead of appending")
    parser.add_argument("--output", type=str, default=Config.OUTPUT_FILE,
                        help=f"Output filename (default: {Config.OUTPUT_FILE})")
    
    args = parser.parse_args()
    
    # Update config with command-line arguments
    if args.output != Config.OUTPUT_FILE:
        Config.OUTPUT_FILE = args.output
    
    # Run data collection
    df = asyncio.run(main(
        lat=args.lat,
        lon=args.lon,
        radius=args.radius,
        save=not args.no_save,
        append=not args.overwrite
    ))
    
    # Print preview
    if not df.empty:
        print("\n" + "=" * 80)
        print("DATA PREVIEW")
        print("=" * 80)
        print(df.head(10).to_string())
        print("\n" + "=" * 80)
        print("DATA SUMMARY")
        print("=" * 80)
        print(df.describe())
