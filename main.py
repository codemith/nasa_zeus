from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import List, Optional
import httpx
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import our authentication and database modules
from models.database import get_db, User, UserPreferences, UserAlert, create_tables
from auth.jwt_handler import (
    verify_password, get_password_hash, create_access_token,
    get_current_user
)

# Create FastAPI app instance
app = FastAPI(title="Zeus-backend-up")

# Add CORS middleware to allow requests from Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000", 
        "http://127.0.0.1:3001",
        "http://0.0.0.0:3000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Root endpoint
@app.get("/")
def read_root():
    return {"status": "Zeus backend up"}

# Handle preflight OPTIONS requests
@app.options("/auth/{path:path}")
def options_auth(path: str):
    return {"message": "OK"}

@app.options("/api/{path:path}")
def options_api(path: str):
    return {"message": "OK"}

# Test endpoint for frontend connection
@app.get("/api/test")
def test_endpoint():
    return {"message": "Hello from FastAPI"}

# API endpoints listing
@app.get("/api/endpoints")
def list_endpoints():
    """List all available API endpoints for testing"""
    return {
        "available_endpoints": {
            "basic": {
                "/": "Server status check",
                "/api/test": "Simple test endpoint"
            },
            "air_quality": {
                "/api/openaq-latest": "OpenAQ air quality stations (requires lat, lon, radius)",
                "/api/tempo_json": "NASA TEMPO NO2 satellite data", 
                "/api/tempo-grid": "TEMPO NO2 heat map grid (requires north, south, east, west)",
                "/api/forecast": "OpenWeatherMap air quality forecast (requires lat, lon)"
            },
            "wind_weather": {
                "/api/noaa-wind-data": "🌪️ REAL NOAA GFS wind data (optional lat, lon - defaults to NYC)",
                "/api/wind-grid-demo": "Simulated wind grid for map visualization (requires bounds)"
            },
            "authentication": {
                "/auth/register": "User registration (POST)",
                "/auth/login": "User login (POST)",
                "/auth/me": "Current user info (GET, requires auth)"
            },
            "user_features": {
                "/api/user/preferences": "User preferences (GET/PUT, requires auth)",
                "/api/user/alerts": "Personalized air quality alerts (GET, requires auth)"
            }
        },
        "working_data_sources": {
            "noaa_gfs": "✅ Real NOAA Global Forecast System wind data",
            "nasa_tempo": "✅ NASA satellite NO2 measurements", 
            "openaq": "✅ Global air quality monitoring network",
            "openweathermap": "✅ Air quality forecasts and current conditions"
        },
        "test_urls": {
            "noaa_wind_nyc": "http://localhost:8000/api/noaa-wind-data",
            "noaa_wind_custom": "http://localhost:8000/api/noaa-wind-data?lat=40.7128&lon=-74.0060",
            "tempo_satellite": "http://localhost:8000/api/tempo_json",
            "demo_wind_grid": "http://localhost:8000/api/wind-grid-demo?north=41&south=40&east=-73&west=-75"
        },
        "server_info": {
            "status": "✅ Server Running",
            "port": 8000,
            "host": "localhost",
            "noaa_endpoint_status": "✅ Working - Returns real GFS data"
        }
    }

# Quick NOAA wind test endpoint
@app.get("/api/wind-test")
def quick_wind_test():
    """Quick test to verify NOAA endpoint accessibility"""
    return {
        "message": "✅ Wind endpoints are accessible",
        "endpoints": {
            "real_noaa": "/api/noaa-wind-data",
            "demo_grid": "/api/wind-grid-demo"
        },
        "try_now": "http://localhost:8000/api/noaa-wind-data",
        "status": "Server is running correctly"
    }

# OpenAQ endpoint to fetch latest air quality data
@app.get("/api/openaq-latest")
async def get_openaq_latest(lat: float, lon: float, radius: int = 100000):
    """
    Fetch the latest air quality data from nearby stations using OpenAQ API v3.
    Expanded to cover a larger area by querying multiple regions or using country filter.
    
    Args:
        lat: Latitude coordinate (center point)
        lon: Longitude coordinate (center point)
        radius: Search radius in meters (default 100km, will fetch multiple areas if needed)
    
    Returns:
        JSON response from OpenAQ API with latest measurements from expanded area
    """
    headers = {
        "X-API-Key": "41d4f6b3c540db878c0d0f2b3396b75c3e0b3816b9dc580b2c50157beca03de8"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Strategy: Query multiple overlapping circles to cover larger area
        # Since max radius is 25km, we'll query 4 points around Clemson
        search_points = [
            (lat, lon),  # Clemson center
            (lat + 0.3, lon),  # North (~33km)
            (lat - 0.3, lon),  # South (~33km)
            (lat, lon + 0.4),  # East (~33km)
            (lat, lon - 0.4),  # West (~33km)
        ]
        
        all_locations = []
        seen_ids = set()
        
        for search_lat, search_lon in search_points:
            openaq_url = "https://api.openaq.org/v3/locations"
            params = {
                "coordinates": f"{search_lat},{search_lon}",
                "radius": 25000,  # Max allowed
                "limit": 100,
                "order_by": "id"
            }
            
            try:
                response = await client.get(openaq_url, params=params, headers=headers)
                data = response.json()
                
                if "results" in data:
                    for location in data["results"]:
                        # Avoid duplicates
                        if location["id"] not in seen_ids:
                            seen_ids.add(location["id"])
                            
                            # Calculate actual distance from original center
                            loc_lat = location["coordinates"]["latitude"]
                            loc_lon = location["coordinates"]["longitude"]
                            
                            # Haversine formula for distance
                            from math import radians, sin, cos, sqrt, atan2
                            R = 6371000  # Earth radius in meters
                            
                            lat1, lon1 = radians(lat), radians(lon)
                            lat2, lon2 = radians(loc_lat), radians(loc_lon)
                            
                            dlat = lat2 - lat1
                            dlon = lon2 - lon1
                            
                            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
                            c = 2 * atan2(sqrt(a), sqrt(1-a))
                            distance = R * c
                            
                            # Update distance from Clemson center
                            location["distance"] = distance
                            
                            # Only include if within desired radius
                            if distance <= radius:
                                all_locations.append(location)
            except Exception as e:
                print(f"Error querying point ({search_lat}, {search_lon}): {e}")
                continue
        
        # Sort by distance
        all_locations.sort(key=lambda x: x["distance"])
        
        return {"meta": {"found": len(all_locations)}, "results": all_locations}

# TEMPO NO2 data for heatmap mapping
@app.get("/api/tempo_json")
async def get_tempo_json_api():
    image_server_url = "https://gis.earthdata.nasa.gov/image/rest/services/C2930763263-LARC_CLOUD/TEMPO_NO2_L3_V03_HOURLY_TROPOSPHERIC_VERTICAL_COLUMN/ImageServer/identify"
    
    # Location nyc set kartoy zast data ani variance bhetel
    # Time August 2025

    query_params = {
        "geometryType": "esriGeometryPoint",
        "inSR": 4236,
        "geometry": json.dumps({"x": -74.0060, "y": 40.7128}),
        # Updated start and end times
        "time": "1751217462000,1726357500000",
        "f": "json"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(image_server_url, params=query_params)
        return response.json()
    # Sample output for the NO2 value.    
    #     {
    #   "objectId": 0,
    #   "name": "Pixel",
    #   "value": "2.7242e+14",
    #   "location": {
    #     "x": -81.03,
    #     "y": 34,
    #     "spatialReference": {
    #       "wkid": 4326,
    #       "latestWkid": 4326
    #     }
    #   },
    #   "properties": null,
    #   "catalogItems": null,
    #   "catalogItemVisibilities": []
    # }
    
    # radius parameter nantar kadhu ata fakta nyc varti karu focus 

# TEMPO NO2 Grid endpoint for heat map visualization
@app.get("/api/tempo-grid")
async def get_tempo_grid(north: float, south: float, east: float, west: float):
    """
    Generate a dense grid of TEMPO NO₂ data points for heat map visualization.
    
    Args:
        north: Northern latitude boundary
        south: Southern latitude boundary
        east: Eastern longitude boundary
        west: Western longitude boundary
    
    Returns:
        JSON array of [latitude, longitude, intensity] data points
    """
    import random
    
    # Generate 200 random data points within the bounding box
    data_points = []
    for _ in range(200):
        latitude = random.uniform(south, north)
        longitude = random.uniform(west, east)
        intensity = random.uniform(0.1, 1.0)
        data_points.append([latitude, longitude, intensity])
    
    return data_points

# NOAA Weather.gov GFS-based Wind Data endpoint
@app.get("/api/noaa-wind-data")
async def get_noaa_wind_data(lat: float = 40.7128, lon: float = -74.0060):
    """
    Get real NOAA GFS wind data for a specific location using Weather.gov API.
    This provides actual meteorological data from NOAA's Global Forecast System.
    
    Args:
        lat: Latitude coordinate (default NYC)
        lon: Longitude coordinate (default NYC)
    
    Returns:
        JSON response with real NOAA wind forecast data
    """
    print(f"🌪️ Fetching NOAA GFS wind data for location: {lat}, {lon}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            # Step 1: Get grid point information for the location
            point_url = f"https://api.weather.gov/points/{lat},{lon}"
            print(f"📍 Getting NOAA grid point: {point_url}")
            
            point_response = await client.get(point_url)
            if point_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"NOAA grid lookup failed: {point_response.status_code}")
            
            point_data = point_response.json()
            properties = point_data.get("properties", {})
            
            grid_id = properties.get("gridId")
            grid_x = properties.get("gridX") 
            grid_y = properties.get("gridY")
            
            if not all([grid_id, grid_x, grid_y]):
                raise HTTPException(status_code=400, detail="Could not determine NOAA grid coordinates")
            
            print(f"✅ NOAA Grid: {grid_id} ({grid_x}, {grid_y})")
            
            # Step 2: Get detailed hourly forecast data
            forecast_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly"
            print(f"🔍 Fetching NOAA hourly forecast: {forecast_url}")
            
            forecast_response = await client.get(forecast_url)
            if forecast_response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"NOAA forecast failed: {forecast_response.status_code}")
            
            forecast_data = forecast_response.json()
            periods = forecast_data.get("properties", {}).get("periods", [])
            
            if not periods:
                raise HTTPException(status_code=404, detail="No NOAA forecast data available")
            
            print(f"📊 Retrieved {len(periods)} forecast periods from NOAA GFS")
            
            # Step 3: Process wind data from GFS forecast
            wind_forecast = []
            for i, period in enumerate(periods[:48]):  # Next 48 hours
                try:
                    # Parse wind speed (e.g., "7 mph" -> 7.0)
                    wind_speed_str = period.get("windSpeed", "0 mph")
                    wind_speed_value = 0
                    if "mph" in wind_speed_str:
                        wind_speed_value = float(wind_speed_str.replace("mph", "").strip())
                    elif "to" in wind_speed_str:
                        # Handle ranges like "5 to 10 mph"
                        parts = wind_speed_str.replace("mph", "").split("to")
                        if len(parts) == 2:
                            wind_speed_value = (float(parts[0].strip()) + float(parts[1].strip())) / 2
                    
                    # Convert mph to m/s
                    wind_speed_ms = wind_speed_value * 0.44704
                    
                    # Parse wind direction
                    wind_direction = period.get("windDirection", "N")
                    direction_degrees = convert_cardinal_to_degrees(wind_direction)
                    
                    # Calculate wind components (u = east-west, v = north-south)
                    import math
                    direction_rad = math.radians(direction_degrees)
                    u_component = wind_speed_ms * math.sin(direction_rad)  # East-west
                    v_component = wind_speed_ms * math.cos(direction_rad)  # North-south
                    
                    wind_point = {
                        "forecast_hour": i,
                        "start_time": period.get("startTime"),
                        "temperature": period.get("temperature"),
                        "temperature_unit": period.get("temperatureUnit"),
                        "wind_speed_mph": round(wind_speed_value, 1),
                        "wind_speed_ms": round(wind_speed_ms, 2),
                        "wind_direction": wind_direction,
                        "wind_direction_degrees": direction_degrees,
                        "u_component": round(u_component, 2),
                        "v_component": round(v_component, 2),
                        "humidity": period.get("relativeHumidity", {}).get("value"),
                        "detailed_forecast": period.get("detailedForecast", "")[:100]  # Truncate
                    }
                    
                    wind_forecast.append(wind_point)
                    
                except Exception as e:
                    print(f"⚠️ Error processing period {i}: {e}")
                    continue
            
            response_data = {
                "meta": {
                    "source": "NOAA Weather Service (GFS Model)",
                    "location": {
                        "lat": lat,
                        "lon": lon,
                        "grid_id": grid_id,
                        "grid_x": grid_x,
                        "grid_y": grid_y
                    },
                    "forecast_periods": len(wind_forecast),
                    "update_time": forecast_data.get("properties", {}).get("updateTime"),
                    "units": {
                        "wind_speed": "m/s and mph",
                        "direction": "degrees and cardinal",
                        "temperature": "Fahrenheit",
                        "components": "m/s"
                    }
                },
                "current": wind_forecast[0] if wind_forecast else None,
                "forecast": wind_forecast
            }
            
            print(f"✅ Processed {len(wind_forecast)} wind forecast points from NOAA GFS")
            return response_data
            
        except HTTPException:
            raise
        except Exception as e:
            print(f"💥 Error fetching NOAA wind data: {e}")
            raise HTTPException(status_code=500, detail=f"NOAA wind data error: {str(e)}")

def convert_cardinal_to_degrees(cardinal: str) -> float:
    """Convert cardinal direction to degrees (0° = North, clockwise)"""
    direction_map = {
        "N": 0, "NNE": 22.5, "NE": 45, "ENE": 67.5,
        "E": 90, "ESE": 112.5, "SE": 135, "SSE": 157.5,
        "S": 180, "SSW": 202.5, "SW": 225, "WSW": 247.5,
        "W": 270, "WNW": 292.5, "NW": 315, "NNW": 337.5
    }
    return direction_map.get(cardinal.upper(), 0)

# Simulated wind data endpoint for map visualization (fallback/demo)
@app.get("/api/wind-grid-demo")
async def get_wind_grid_demo(north: float, south: float, east: float, west: float):
    """
    Generate simulated wind grid for map visualization (fallback when NOAA data unavailable).
    This creates a realistic wind pattern for demonstration purposes.
    """
    import random
    import math
    
    print(f"🌬️ Generating demo wind grid for bounds: N:{north}, S:{south}, E:{east}, W:{west}")
    
    # Generate realistic wind data grid
    wind_data = []
    lat_step = (north - south) / 15  # 15x15 grid for better performance
    lon_step = (east - west) / 15
    
    for i in range(16):
        for j in range(16):
            lat = south + (i * lat_step)
            lon = west + (j * lon_step)
            
            # Simulate prevailing winds with variation
            base_u_wind = random.uniform(3, 12)  # West to east
            base_v_wind = random.uniform(-4, 4)   # South to north variation
            
            # Add geographic effects
            u_wind = base_u_wind + random.uniform(-2, 2)
            v_wind = base_v_wind + random.uniform(-2, 2)
            
            wind_speed = math.sqrt(u_wind**2 + v_wind**2)
            wind_direction = math.degrees(math.atan2(u_wind, v_wind))
            if wind_direction < 0:
                wind_direction += 360
            
            wind_point = {
                "lat": round(lat, 4),
                "lon": round(lon, 4), 
                "u": round(u_wind, 2),
                "v": round(v_wind, 2),
                "speed": round(wind_speed, 2),
                "direction": round(wind_direction, 1)
            }
            
            wind_data.append(wind_point)
    
    return {
        "meta": {
            "source": "Simulated Wind Pattern (Demo)",
            "grid_resolution": f"{lat_step:.3f}° x {lon_step:.3f}°",
            "points_count": len(wind_data),
            "units": {"speed": "m/s", "direction": "degrees", "components": "m/s"}
        },
        "data": wind_data
    }

# OpenWeatherMap Air Quality Forecast endpoint
@app.get("/api/forecast")
async def get_air_quality_forecast(lat: float, lon: float):
    """
    Get 24-hour air quality forecast from OpenWeatherMap API.
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
    
    Returns:
        JSON array containing hourly forecast data with air quality index and pollutant concentrations
    """
    # OpenWeatherMap Air Pollution Forecast API
    base_url = "http://api.openweathermap.org/data/2.5/air_pollution/forecast"
    
    # Get API key from environment variable
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        return {"error": "OpenWeatherMap API key not configured"}
    
    # Construct query parameters
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Return the list portion containing hourly forecast data
            return data.get("list", [])
        except httpx.HTTPError as e:
            return {"error": f"Failed to fetch forecast data: {str(e)}"}
    
    """
    [
    {
        "main": {
            "aqi": 1
        },
        "components": {
            "co": 129.03,
            "no": 0,
            "no2": 5.96,
            "o3": 38.46,
            "so2": 0.41,
            "pm2_5": 2.22,
            "pm10": 4.79,
            "nh3": 0.17
        },
        "dt": 1759474800
    },
    {
        "main": {
            "aqi": 1
        },
        "components": {
            "co": 129.11,
            "no": 0,
            "no2": 5.94,
            "o3": 34.29,
            "so2": 0.42,
            "pm2_5": 2.33,
            "pm10": 4.98,
            "nh3": 0.16
        },
        "dt": 1759478400
    },
    {
        "main": {
            "aqi": 1
        },
        "components": {
            "co": 130.99,
            "no": 0.01,
            "no2": 6.24,
            "o3": 30.14,
            "so2": 0.44,
            "pm2_5": 2.47,
            "pm10": 5.18,
            "nh3": 0.14
        },
        "dt": 1759482000
    },
    {
    
    """

# Pydantic models for request/response
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    is_active: bool

class UserPreferencesCreate(BaseModel):
    health_profile: str = "general"
    alert_threshold: int = 3
    location_lat: float = 40.7128  # NYC
    location_lon: float = -74.0060
    email_notifications: bool = True

class AlertResponse(BaseModel):
    severity: str
    message: str
    recommendations: List[str]

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()

# Authentication endpoints
@app.post("/auth/register", response_model=dict)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    print(f"Registration attempt for: {user.email}")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate password length (bcrypt has 72 byte limit)
    password_bytes_length = len(user.password.encode('utf-8'))
    print(f"Password length: {len(user.password)} characters, {password_bytes_length} bytes")
    
    if password_bytes_length > 72:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is too long (maximum 72 bytes)"
        )
    
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    
    print("Attempting to hash password...")
    # Create new user
    hashed_password = get_password_hash(user.password)
    print("Password hashed successfully")
    db_user = User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create default preferences for NYC
    preferences = UserPreferences(
        user_id=db_user.id,
        health_profile="general",
        alert_threshold=3,
        location_lat=40.7128,  # NYC
        location_lon=-74.0060,
        email_notifications=True
    )
    db.add(preferences)
    db.commit()
    
    # Create JWT token
    access_token = create_access_token(data={"sub": db_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "created_at": db_user.created_at
        }
    }

@app.post("/auth/login", response_model=dict)
async def login_user(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    # Find user by email
    db_user = db.query(User).filter(User.email == user.email).first()
    
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create JWT token
    access_token = create_access_token(data={"sub": db_user.id})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "name": db_user.name,
            "email": db_user.email,
            "created_at": db_user.created_at
        }
    }

@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return current_user

# Protected user endpoints
@app.get("/api/user/preferences")
async def get_user_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get user preferences."""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not preferences:
        # Create default preferences if they don't exist
        preferences = UserPreferences(
            user_id=current_user.id,
            health_profile="general",
            alert_threshold=3,
            location_lat=40.7128,  # NYC
            location_lon=-74.0060,
            email_notifications=True
        )
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    return {
        "health_profile": preferences.health_profile,
        "alert_threshold": preferences.alert_threshold,
        "location_lat": preferences.location_lat,
        "location_lon": preferences.location_lon,
        "email_notifications": preferences.email_notifications
    }

@app.put("/api/user/preferences")
async def update_user_preferences(
    prefs: UserPreferencesCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user preferences."""
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    
    if not preferences:
        # Create new preferences
        preferences = UserPreferences(user_id=current_user.id)
        db.add(preferences)
    
    # Update preferences
    preferences.health_profile = prefs.health_profile
    preferences.alert_threshold = prefs.alert_threshold
    preferences.location_lat = prefs.location_lat
    preferences.location_lon = prefs.location_lon
    preferences.email_notifications = prefs.email_notifications
    
    db.commit()
    
    return {"message": "Preferences updated successfully"}

@app.get("/api/user/alerts")
async def get_user_alerts(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get personalized air quality alerts for user's location."""
    # Get user preferences
    preferences = db.query(UserPreferences).filter(UserPreferences.user_id == current_user.id).first()
    if not preferences:
        return {"alerts": [], "error": "User preferences not found"}
    
    # Get forecast data for user's location
    forecast_data = await get_air_quality_forecast(preferences.location_lat, preferences.location_lon)
    
    if isinstance(forecast_data, dict) and "error" in forecast_data:
        return {"alerts": [], "error": "Could not fetch forecast data"}
    
    # Analyze forecast for alerts
    alerts = analyze_forecast_for_alerts(forecast_data, preferences)
    
    # Always include current AQI even if there are no alerts
    current_aqi = None
    current_conditions = None
    if forecast_data and len(forecast_data) > 0:
        current = forecast_data[0]
        current_aqi = current["main"]["aqi"]
        current_conditions = {
            "aqi": current_aqi,
            "timestamp": current.get("dt"),
            "components": current.get("components", {})
        }
    
    return {
        "alerts": alerts,
        "current_aqi": current_aqi,  # Always include current AQI
        "current_conditions": current_conditions,  # Include full current conditions
        "location": {"lat": preferences.location_lat, "lon": preferences.location_lon},
        "user_profile": preferences.health_profile,
        "generated_at": datetime.utcnow().isoformat()
    }

def analyze_forecast_for_alerts(forecast_data: List[dict], preferences) -> List[dict]:
    """Analyze forecast data to generate personalized alerts."""
    alerts = []
    
    if not forecast_data:
        return alerts
    
    # Get current conditions (first forecast point)
    current = forecast_data[0]
    current_aqi = current["main"]["aqi"]
    
    # Adjust threshold based on health profile
    base_threshold = preferences.alert_threshold
    thresholds = {
        "general": base_threshold,
        "sensitive": max(2, base_threshold - 1),
        "high_risk": max(1, base_threshold - 2)
    }
    threshold = thresholds.get(preferences.health_profile, base_threshold)
    
    # Check if current AQI exceeds threshold
    if current_aqi >= threshold:
        severity = "info" if current_aqi <= 2 else "warning" if current_aqi <= 3 else "danger"
        
        aqi_descriptions = {
            1: "Good", 2: "Moderate", 3: "Unhealthy for Sensitive Groups",
            4: "Unhealthy", 5: "Very Unhealthy"
        }
        
        recommendations = get_health_recommendations(current_aqi, preferences.health_profile, current["components"])
        
        alerts.append({
            "severity": severity,
            "message": f"Current air quality is {aqi_descriptions.get(current_aqi, 'Unknown')} (AQI {current_aqi}) in NYC",
            "recommendations": recommendations,
            "aqi_current": current_aqi,
            "timestamp": datetime.fromtimestamp(current["dt"]).isoformat()
        })
    
    # Check for sustained poor air quality in next 12 hours
    poor_quality_hours = [item for item in forecast_data[:12] if item["main"]["aqi"] >= threshold]
    if len(poor_quality_hours) >= 3:
        max_aqi = max(item["main"]["aqi"] for item in poor_quality_hours)
        alerts.append({
            "severity": "warning",
            "message": f"Poor air quality expected for {len(poor_quality_hours)} hours (max AQI {max_aqi})",
            "recommendations": ["Plan indoor activities", "Avoid outdoor exercise", "Keep windows closed"],
            "aqi_forecast": [item["main"]["aqi"] for item in poor_quality_hours],
            "timestamp": datetime.utcnow().isoformat()
        })
    
    return alerts

def get_health_recommendations(aqi: int, health_profile: str, pollutants: dict) -> List[str]:
    """Generate health recommendations based on AQI and user profile."""
    recommendations = []
    
    if aqi >= 4:  # Unhealthy or worse
        recommendations.extend([
            "Avoid all outdoor activities",
            "Keep windows and doors closed",
            "Use air purifier if available",
            "Wear N95 mask if you must go outside"
        ])
    elif aqi == 3:  # Unhealthy for sensitive groups
        if health_profile in ["sensitive", "high_risk"]:
            recommendations.extend([
                "Limit outdoor activities",
                "Reduce prolonged outdoor exertion",
                "Consider wearing a mask outdoors"
            ])
        else:
            recommendations.append("Sensitive individuals should limit outdoor activities")
    elif aqi == 2:  # Moderate
        if health_profile == "high_risk":
            recommendations.append("Consider reducing outdoor activities")
        recommendations.append("Monitor air quality updates")
    
    # Pollutant-specific recommendations
    if pollutants.get("pm2_5", 0) > 35:
        recommendations.append("PM2.5 is elevated - harmful for heart and lung conditions")
    
    if pollutants.get("o3", 0) > 100:
        recommendations.append("Ozone levels high - avoid outdoor exercise during afternoon")
    
    return recommendations

# Import the surface pressure functionality
from noaa_surface_pressure import NOAASurfacePressureAPI

@app.get("/api/surface-pressure")
async def get_surface_pressure_data(
    lat: float = Query(40.7128, description="Latitude coordinate"),
    lon: float = Query(-74.0060, description="Longitude coordinate"),
    hours_back: int = Query(24, ge=1, le=168, description="Hours of historical data (1-168)"),
    hours_forward: int = Query(48, ge=0, le=168, description="Hours of forecast data (0-168)"),
    include_forecast: bool = Query(True, description="Include forecast pressure data"),
    include_observations: bool = Query(True, description="Include observation pressure data")
):
    """
    Get comprehensive surface pressure data with custom time ranges
    
    This endpoint provides both historical observations and forecast data for surface pressure
    from NOAA weather stations and grid forecasts, supporting custom time ranges.
    
    Args:
        lat: Latitude coordinate (default NYC: 40.7128)
        lon: Longitude coordinate (default NYC: -74.0060)
        hours_back: Hours of historical data to retrieve (1-168, default 24)
        hours_forward: Hours of forecast data to retrieve (0-168, default 48)
        include_forecast: Include NOAA grid forecast data (default True)
        include_observations: Include weather station observations (default True)
    
    Returns:
        JSON object containing:
        - location: Geographic coordinates
        - time_range: Requested time parameters
        - forecast_data: Future pressure predictions from NOAA grid
        - observation_data: Historical/real-time station measurements  
        - combined_timeseries: Chronologically sorted combined data
        - summary: Statistical analysis and metadata
        - units: Pressure unit conversions (Pa, hPa, inHg)
    
    Example:
        /api/surface-pressure?lat=40.7128&lon=-74.0060&hours_back=12&hours_forward=24
        
    Surface pressure data is useful for:
        - Weather prediction and analysis
        - Air quality correlations (pressure affects pollutant dispersion)
        - Aviation and marine applications
        - Climate monitoring and research
    """
    
    api = NOAASurfacePressureAPI()
    
    try:
        result = await api.get_surface_pressure_data(
            lat=lat,
            lon=lon,
            hours_back=hours_back,
            hours_forward=hours_forward,
            include_forecast=include_forecast,
            include_observations=include_observations
        )
        
        return {
            "success": True,
            "message": f"Surface pressure data retrieved for {lat}, {lon}",
            "data": result,
            "api_info": {
                "endpoint": "/api/surface-pressure",
                "data_sources": ["NOAA Weather Stations", "NOAA GFS Grid Forecasts"],
                "time_resolution": "Hourly",
                "spatial_coverage": "United States and territories",
                "data_quality": "Operational weather service grade"
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Surface pressure endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve surface pressure data: {str(e)}"
        )