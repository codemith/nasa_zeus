#!/usr/bin/env python3
"""
NOAA Surface Pressure Data Explorer
Tests availability of surface pressure data for NYC with custom time ranges
"""

import httpx
import json
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional

# NYC coordinates
NYC_LAT = 40.7128
NYC_LON = -74.0060

class NOAASurfacePressureExplorer:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=60.0)
        self.grid_info = None
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def get_grid_info(self, lat: float = NYC_LAT, lon: float = NYC_LON) -> Dict[str, Any]:
        """Get NOAA grid information for coordinates"""
        print(f"\n🌍 Getting NOAA grid info for: {lat}, {lon}")
        
        point_url = f"https://api.weather.gov/points/{lat},{lon}"
        print(f"📍 URL: {point_url}")
        
        try:
            response = await self.client.get(point_url)
            response.raise_for_status()
            
            data = response.json()
            properties = data.get("properties", {})
            
            self.grid_info = {
                "gridId": properties.get("gridId"),
                "gridX": properties.get("gridX"),
                "gridY": properties.get("gridY"),
                "forecast": properties.get("forecast"),
                "forecastHourly": properties.get("forecastHourly"),
                "forecastGridData": properties.get("forecastGridData"),
                "observationStations": properties.get("observationStations")
            }
            
            print(f"✅ Grid: {self.grid_info['gridId']} ({self.grid_info['gridX']}, {self.grid_info['gridY']})")
            print(f"🔗 Forecast Grid Data URL: {self.grid_info['forecastGridData']}")
            
            return self.grid_info
            
        except Exception as e:
            print(f"❌ Error getting grid info: {e}")
            return {}
    
    async def check_grid_data_endpoint(self) -> Dict[str, Any]:
        """Check the forecast grid data endpoint for available parameters"""
        if not self.grid_info or not self.grid_info.get("forecastGridData"):
            print("❌ No grid data URL available")
            return {}
        
        print(f"\n🔍 Checking grid data endpoint...")
        url = self.grid_info["forecastGridData"]
        print(f"📍 URL: {url}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            properties = data.get("properties", {})
            
            # Extract available parameters
            available_params = list(properties.keys())
            print(f"\n📊 Available parameters ({len(available_params)}):")
            
            pressure_related = []
            for param in sorted(available_params):
                if 'pressure' in param.lower() or 'barometric' in param.lower():
                    pressure_related.append(param)
                    print(f"  🎯 {param} (PRESSURE RELATED)")
                else:
                    print(f"  📈 {param}")
            
            # Check if surface pressure is available
            surface_pressure_data = None
            if "barometricPressure" in properties:
                surface_pressure_data = properties["barometricPressure"]
                print(f"\n🎯 Found barometricPressure data!")
            elif "pressure" in properties:
                surface_pressure_data = properties["pressure"]
                print(f"\n🎯 Found pressure data!")
            
            # Analyze surface pressure data structure
            if surface_pressure_data:
                await self.analyze_pressure_data(surface_pressure_data, "Surface Pressure")
            else:
                print(f"\n❌ No surface pressure data found in grid endpoint")
            
            return {
                "available_parameters": available_params,
                "pressure_related": pressure_related,
                "surface_pressure_data": surface_pressure_data is not None
            }
            
        except Exception as e:
            print(f"❌ Error checking grid data: {e}")
            return {}
    
    async def analyze_pressure_data(self, pressure_data: Dict[str, Any], data_type: str):
        """Analyze pressure data structure and time ranges"""
        print(f"\n🔬 Analyzing {data_type} data structure:")
        
        # Check units
        uom = pressure_data.get("uom")
        if uom:
            print(f"  📏 Units: {uom}")
        
        # Check values and time ranges
        values = pressure_data.get("values", [])
        if values:
            print(f"  📊 Number of data points: {len(values)}")
            
            # Analyze time range
            times = []
            pressures = []
            for value in values[:10]:  # Sample first 10
                valid_time = value.get("validTime")
                pressure_value = value.get("value")
                
                if valid_time and pressure_value is not None:
                    times.append(valid_time)
                    pressures.append(pressure_value)
            
            if times:
                print(f"  ⏰ Sample time range:")
                print(f"    Start: {times[0]}")
                print(f"    End: {times[-1]}")
                print(f"  📈 Sample pressure values: {pressures[:5]}")
            
            # Check for historical vs forecast data
            now = datetime.now()
            forecast_count = 0
            historical_count = 0
            
            for value in values[:20]:  # Sample first 20
                valid_time_str = value.get("validTime", "")
                if valid_time_str:
                    try:
                        # Parse ISO 8601 time
                        if "/" in valid_time_str:
                            time_part = valid_time_str.split("/")[0]
                        else:
                            time_part = valid_time_str.split("+")[0].split("-")[0]
                        
                        value_time = datetime.fromisoformat(time_part.replace("Z", "+00:00"))
                        
                        if value_time > now:
                            forecast_count += 1
                        else:
                            historical_count += 1
                    except:
                        continue
            
            print(f"  📅 Data distribution (sample of {forecast_count + historical_count}):")
            print(f"    Historical: {historical_count}")
            print(f"    Forecast: {forecast_count}")
    
    async def check_observation_stations(self) -> Dict[str, Any]:
        """Check observation stations for real-time pressure data"""
        if not self.grid_info or not self.grid_info.get("observationStations"):
            print("❌ No observation stations URL available")
            return {}
        
        print(f"\n🏪 Checking observation stations...")
        url = self.grid_info["observationStations"]
        print(f"📍 URL: {url}")
        
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            
            data = response.json()
            features = data.get("features", [])
            
            print(f"🏪 Found {len(features)} observation stations")
            
            # Test first few stations for pressure data
            pressure_stations = []
            for i, station in enumerate(features[:3]):  # Test first 3 stations
                station_id = station.get("properties", {}).get("stationIdentifier")
                if station_id:
                    print(f"\n🔍 Testing station {i+1}: {station_id}")
                    station_data = await self.test_observation_station(station_id)
                    if station_data.get("has_pressure"):
                        pressure_stations.append(station_id)
            
            return {
                "total_stations": len(features),
                "tested_stations": min(3, len(features)),
                "pressure_stations": pressure_stations
            }
            
        except Exception as e:
            print(f"❌ Error checking observation stations: {e}")
            return {}
    
    async def test_observation_station(self, station_id: str) -> Dict[str, Any]:
        """Test a specific observation station for pressure data"""
        print(f"  📡 Testing station: {station_id}")
        
        # Get latest observations
        obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
        
        try:
            response = await self.client.get(obs_url)
            response.raise_for_status()
            
            data = response.json()
            properties = data.get("properties", {})
            
            # Check for pressure measurements
            barometric_pressure = properties.get("barometricPressure")
            sea_level_pressure = properties.get("seaLevelPressure")
            
            has_pressure = barometric_pressure is not None or sea_level_pressure is not None
            
            if has_pressure:
                print(f"    ✅ Has pressure data!")
                if barometric_pressure:
                    value = barometric_pressure.get("value")
                    unit = barometric_pressure.get("unitCode")
                    print(f"      🌡️ Barometric: {value} {unit}")
                if sea_level_pressure:
                    value = sea_level_pressure.get("value")
                    unit = sea_level_pressure.get("unitCode")
                    print(f"      🌊 Sea Level: {value} {unit}")
            else:
                print(f"    ❌ No pressure data")
            
            return {
                "station_id": station_id,
                "has_pressure": has_pressure,
                "barometric_pressure": barometric_pressure,
                "sea_level_pressure": sea_level_pressure
            }
            
        except Exception as e:
            print(f"    ❌ Error testing station: {e}")
            return {"station_id": station_id, "has_pressure": False}
    
    async def test_custom_time_range(self, hours_back: int = 24, hours_forward: int = 48):
        """Test custom time range availability for surface pressure"""
        print(f"\n⏰ Testing custom time range: -{hours_back}h to +{hours_forward}h")
        
        # This would require historical data API which NOAA may not provide
        # Most NOAA APIs focus on current conditions and forecasts
        
        now = datetime.utcnow()
        start_time = now - timedelta(hours=hours_back)
        end_time = now + timedelta(hours=hours_forward)
        
        print(f"  📅 Requested range:")
        print(f"    Start: {start_time.isoformat()}Z")
        print(f"    End: {end_time.isoformat()}Z")
        
        # NOAA doesn't typically provide historical weather data through their weather API
        # Their historical data is usually accessed through different services
        print(f"  ℹ️  Note: NOAA Weather API primarily provides current and forecast data")
        print(f"  ℹ️  Historical data may require different NOAA services (NCEI, etc.)")
        
        return {
            "requested_start": start_time.isoformat(),
            "requested_end": end_time.isoformat(),
            "historical_available": False,  # Through weather API
            "forecast_available": True
        }

async def main():
    """Main test function"""
    print("🌪️ NOAA Surface Pressure Data Explorer for NYC")
    print("=" * 60)
    
    async with NOAASurfacePressureExplorer() as explorer:
        # Step 1: Get grid information
        grid_info = await explorer.get_grid_info()
        
        if not grid_info:
            print("❌ Could not get grid info. Exiting.")
            return
        
        # Step 2: Check forecast grid data endpoint
        print("\n" + "=" * 60)
        print("🔍 CHECKING FORECAST GRID DATA ENDPOINT")
        print("=" * 60)
        
        grid_results = await explorer.check_grid_data_endpoint()
        
        # Step 3: Check observation stations
        print("\n" + "=" * 60)
        print("🏪 CHECKING OBSERVATION STATIONS")
        print("=" * 60)
        
        station_results = await explorer.check_observation_stations()
        
        # Step 4: Test custom time range requirements
        print("\n" + "=" * 60)
        print("⏰ TESTING CUSTOM TIME RANGE REQUIREMENTS")
        print("=" * 60)
        
        time_range_results = await explorer.test_custom_time_range()
        
        # Summary
        print("\n" + "=" * 60)
        print("📋 SUMMARY")
        print("=" * 60)
        
        print(f"✅ Grid Info Retrieved: {bool(grid_info)}")
        print(f"📊 Grid Data Parameters: {len(grid_results.get('available_parameters', []))}")
        print(f"🎯 Pressure Parameters Found: {len(grid_results.get('pressure_related', []))}")
        print(f"🏪 Observation Stations: {station_results.get('total_stations', 0)}")
        print(f"📡 Stations with Pressure: {len(station_results.get('pressure_stations', []))}")
        
        # Recommendations
        print(f"\n🎯 RECOMMENDATIONS:")
        
        if grid_results.get('surface_pressure_data'):
            print(f"  ✅ Use forecast grid data endpoint for surface pressure forecasts")
            print(f"     URL pattern: /gridpoints/{{gridId}}/{{x}},{{y}}")
        
        if station_results.get('pressure_stations'):
            print(f"  ✅ Use observation stations for real-time surface pressure")
            print(f"     Available stations: {', '.join(station_results['pressure_stations'])}")
        
        if not grid_results.get('surface_pressure_data') and not station_results.get('pressure_stations'):
            print(f"  ❌ Limited surface pressure data available through NOAA Weather API")
            print(f"  💡 Consider alternative sources:")
            print(f"     - NOAA NCEI for historical data")
            print(f"     - OpenWeatherMap API")
            print(f"     - WeatherAPI.com")

if __name__ == "__main__":
    asyncio.run(main())