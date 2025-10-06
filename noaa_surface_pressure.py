"""
NOAA Surface Pressure API Integration
Adds surface pressure data retrieval with custom time ranges to the Zeus Air Quality system
"""

from fastapi import HTTPException
import httpx
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import logging

logger = logging.getLogger(__name__)

class NOAASurfacePressureAPI:
    """Handler for NOAA surface pressure data with custom time ranges"""
    
    def __init__(self):
        self.base_url = "https://api.weather.gov"
        self.timeout = 60.0
    
    async def get_surface_pressure_data(
        self,
        lat: float = 40.7128,
        lon: float = -74.0060,
        hours_back: int = 24,
        hours_forward: int = 48,
        include_forecast: bool = True,
        include_observations: bool = True
    ) -> Dict:
        """
        Get comprehensive surface pressure data for a location with custom time range
        
        Args:
            lat: Latitude coordinate (default NYC)
            lon: Longitude coordinate (default NYC)  
            hours_back: Hours of historical data to retrieve
            hours_forward: Hours of forecast data to retrieve
            include_forecast: Include forecast pressure data
            include_observations: Include observation pressure data
            
        Returns:
            Combined surface pressure data with metadata
        """
        
        logger.info(f"🌡️ Fetching surface pressure data for {lat}, {lon}")
        logger.info(f"   Time range: -{hours_back}h to +{hours_forward}h")
        
        result = {
            "location": {"lat": lat, "lon": lon},
            "time_range": {
                "hours_back": hours_back,
                "hours_forward": hours_forward,
                "requested_at": datetime.utcnow().isoformat() + "Z"
            },
            "forecast_data": [],
            "observation_data": [],
            "metadata": {},
            "units": {
                "pressure": "Pa",
                "pressure_hpa": "hPa",  
                "pressure_inhg": "inHg"
            }
        }
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Step 1: Get NOAA grid information
                grid_info = await self._get_grid_info(client, lat, lon)
                result["metadata"]["grid"] = grid_info
                
                # Step 2: Get forecast pressure data if requested
                if include_forecast and grid_info:
                    forecast_data = await self._get_forecast_pressure(
                        client, grid_info, hours_forward
                    )
                    result["forecast_data"] = forecast_data
                
                # Step 3: Get observation pressure data if requested  
                if include_observations and grid_info:
                    observation_data = await self._get_observation_pressure(
                        client, grid_info, hours_back, hours_forward
                    )
                    result["observation_data"] = observation_data
                
                # Step 4: Combine and sort all data chronologically
                combined_data = self._combine_pressure_data(
                    result["forecast_data"],
                    result["observation_data"]
                )
                result["combined_timeseries"] = combined_data
                
                # Step 5: Add summary statistics
                result["summary"] = self._calculate_pressure_summary(combined_data)
                
                logger.info(f"✅ Retrieved pressure data: {len(result['forecast_data'])} forecast + {len(result['observation_data'])} observations")
                
                return result
                
            except Exception as e:
                logger.error(f"❌ Error fetching surface pressure data: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to fetch surface pressure data: {str(e)}"
                )
    
    async def _get_grid_info(self, client: httpx.AsyncClient, lat: float, lon: float) -> Dict:
        """Get NOAA grid information and station list"""
        
        point_url = f"{self.base_url}/points/{lat},{lon}"
        logger.debug(f"📍 Getting grid info: {point_url}")
        
        try:
            response = await client.get(point_url)
            response.raise_for_status()
            
            data = response.json()
            properties = data.get("properties", {})
            
            grid_info = {
                "gridId": properties.get("gridId"),
                "gridX": properties.get("gridX"),
                "gridY": properties.get("gridY"),
                "forecast_grid_url": properties.get("forecastGridData"),
                "stations_url": properties.get("observationStations")
            }
            
            # Get nearby stations for observations
            if grid_info["stations_url"]:
                stations = await self._get_nearby_stations(client, grid_info["stations_url"])
                grid_info["stations"] = stations
            
            return grid_info
            
        except Exception as e:
            logger.error(f"❌ Grid info error: {e}")
            raise
    
    async def _get_nearby_stations(self, client: httpx.AsyncClient, stations_url: str) -> List[str]:
        """Get list of nearby observation stations"""
        
        try:
            response = await client.get(stations_url)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            # Extract station IDs, prioritize major NYC airports and weather stations
            stations = []
            priority_stations = ["KNYC", "KLGA", "KEWR", "KJFK", "KTEB"]  # NYC area
            
            for feature in features:
                station_id = feature.get("properties", {}).get("stationIdentifier")
                if station_id:
                    if station_id in priority_stations:
                        stations.insert(0, station_id)  # Add to front
                    else:
                        stations.append(station_id)
            
            # Limit to top 10 stations to avoid excessive API calls
            return stations[:10]
            
        except Exception as e:
            logger.warning(f"⚠️ Could not get stations: {e}")
            return ["KNYC", "KLGA", "KEWR"]  # Fallback to major NYC stations
    
    async def _get_forecast_pressure(
        self,
        client: httpx.AsyncClient,
        grid_info: Dict,
        hours_forward: int
    ) -> List[Dict]:
        """Get forecast pressure data from NOAA grid"""
        
        if not grid_info.get("forecast_grid_url"):
            logger.warning("⚠️ No forecast grid URL available")
            return []
        
        try:
            response = await client.get(grid_info["forecast_grid_url"])
            response.raise_for_status()
            
            data = response.json()
            pressure_data = data.get("properties", {}).get("pressure")
            
            if not pressure_data:
                logger.warning("⚠️ No pressure data in forecast grid")
                return []
            
            values = pressure_data.get("values", [])
            uom = pressure_data.get("uom", "Pa")
            
            # Filter forecast data within time range
            now = datetime.utcnow()
            end_time = now + timedelta(hours=hours_forward)
            
            forecast_points = []
            for value in values:
                valid_time_str = value.get("validTime", "")
                pressure_val = value.get("value")
                
                if valid_time_str and pressure_val is not None:
                    try:
                        # Parse NOAA time format
                        time_part = valid_time_str.split("/")[0] if "/" in valid_time_str else valid_time_str
                        dt = datetime.fromisoformat(time_part.replace("Z", "+00:00"))
                        
                        # Only include future data within range
                        if now <= dt <= end_time:
                            forecast_points.append({
                                "timestamp": dt.isoformat() + "Z",
                                "pressure_pa": pressure_val,
                                "pressure_hpa": round(pressure_val / 100, 2),
                                "pressure_inhg": round(pressure_val * 0.0002953, 3),
                                "source": "forecast",
                                "grid_point": f"{grid_info.get('gridId')} ({grid_info.get('gridX')}, {grid_info.get('gridY')})"
                            })
                    
                    except Exception as e:
                        logger.debug(f"⚠️ Time parsing error: {e}")
                        continue
            
            logger.info(f"📈 Forecast points: {len(forecast_points)}")
            return sorted(forecast_points, key=lambda x: x["timestamp"])
            
        except Exception as e:
            logger.error(f"❌ Forecast pressure error: {e}")
            return []
    
    async def _get_observation_pressure(
        self,
        client: httpx.AsyncClient,
        grid_info: Dict,
        hours_back: int,
        hours_forward: int = 1  # Include recent observations
    ) -> List[Dict]:
        """Get observation pressure data from NOAA stations"""
        
        stations = grid_info.get("stations", ["KNYC"])
        if not stations:
            logger.warning("⚠️ No observation stations available")
            return []
        
        # Define time range
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours_back)
        end_time = now + timedelta(hours=hours_forward)
        
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        all_observations = []
        
        for station_id in stations[:3]:  # Limit to top 3 stations to avoid rate limits
            try:
                # Get observations for time range
                obs_url = f"{self.base_url}/stations/{station_id}/observations"
                params = {"start": start_iso, "end": end_iso}
                
                logger.debug(f"📡 Getting observations from {station_id}")
                
                response = await client.get(obs_url, params=params)
                if response.status_code != 200:
                    logger.warning(f"⚠️ Station {station_id} returned {response.status_code}")
                    continue
                
                data = response.json()
                features = data.get("features", [])
                
                for feature in features:
                    props = feature.get("properties", {})
                    timestamp = props.get("timestamp")
                    barometric = props.get("barometricPressure")
                    sea_level = props.get("seaLevelPressure")
                    
                    if timestamp and (barometric or sea_level):
                        # Use barometric pressure if available, otherwise sea level
                        pressure_data = barometric if barometric and barometric.get("value") else sea_level
                        
                        if pressure_data and pressure_data.get("value") is not None:
                            pressure_pa = pressure_data.get("value")
                            quality = pressure_data.get("qualityControl", "Unknown")
                            
                            # Only include high-quality data
                            if quality in ["V", "C", "S"]:  # Valid, Corrected, Suspect but usable
                                all_observations.append({
                                    "timestamp": timestamp,
                                    "pressure_pa": pressure_pa,
                                    "pressure_hpa": round(pressure_pa / 100, 2),
                                    "pressure_inhg": round(pressure_pa * 0.0002953, 3),
                                    "source": "observation",
                                    "station": station_id,
                                    "quality": quality,
                                    "pressure_type": "barometric" if barometric else "sea_level"
                                })
                
                logger.debug(f"📊 {station_id}: {len([f for f in features if f.get('properties', {}).get('barometricPressure')])}")
                
            except Exception as e:
                logger.warning(f"⚠️ Station {station_id} error: {e}")
                continue
        
        logger.info(f"🏪 Observation points: {len(all_observations)}")
        return sorted(all_observations, key=lambda x: x["timestamp"])
    
    def _combine_pressure_data(self, forecast_data: List[Dict], observation_data: List[Dict]) -> List[Dict]:
        """Combine and deduplicate forecast and observation data"""
        
        combined = []
        
        # Add all observations
        combined.extend(observation_data)
        
        # Add forecast data, avoiding overlap with observations
        obs_times = {obs["timestamp"] for obs in observation_data}
        
        for forecast in forecast_data:
            # Only add forecast if no observation exists for that time
            if forecast["timestamp"] not in obs_times:
                combined.append(forecast)
        
        # Sort chronologically
        return sorted(combined, key=lambda x: x["timestamp"])
    
    def _calculate_pressure_summary(self, combined_data: List[Dict]) -> Dict:
        """Calculate summary statistics for pressure data"""
        
        if not combined_data:
            return {}
        
        pressures = [point["pressure_hpa"] for point in combined_data]
        
        return {
            "total_points": len(combined_data),
            "observation_points": len([p for p in combined_data if p["source"] == "observation"]),
            "forecast_points": len([p for p in combined_data if p["source"] == "forecast"]),
            "pressure_stats": {
                "min_hpa": min(pressures),
                "max_hpa": max(pressures),
                "avg_hpa": round(sum(pressures) / len(pressures), 2),
                "range_hpa": round(max(pressures) - min(pressures), 2)
            },
            "time_range": {
                "start": combined_data[0]["timestamp"],
                "end": combined_data[-1]["timestamp"]
            }
        }

# FastAPI endpoint implementation
async def get_noaa_surface_pressure(
    lat: float = 40.7128,
    lon: float = -74.0060,
    hours_back: int = 24,
    hours_forward: int = 48
) -> Dict:
    """
    FastAPI endpoint for NOAA surface pressure data
    
    Args:
        lat: Latitude coordinate (default NYC)
        lon: Longitude coordinate (default NYC)
        hours_back: Hours of historical data (default 24)
        hours_forward: Hours of forecast data (default 48)
    
    Returns:
        Comprehensive surface pressure data with custom time range
    """
    
    api = NOAASurfacePressureAPI()
    return await api.get_surface_pressure_data(
        lat=lat,
        lon=lon, 
        hours_back=hours_back,
        hours_forward=hours_forward
    )