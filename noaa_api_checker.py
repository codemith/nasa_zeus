#!/usr/bin/env python3

"""
NOAA NOMADS GFS Data API Checker for NYC Location
This script tests various NOAA NOMADS endpoints to find working GFS data sources.
"""

import asyncio
import httpx
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# NYC coordinates
NYC_LAT = 40.7128
NYC_LON = -74.0060

class NOAAChecker:
    def __init__(self):
        self.base_urls = {
            "nomads_opendap": "https://nomads.ncep.noaa.gov/dods/gfs_0p25",
            "nomads_direct": "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25.pl",
            "weather_gov_api": "https://api.weather.gov/gridpoints",
            "nomads_grib_filter": "https://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p25_1hr.pl"
        }
    
    async def test_weather_gov_api(self):
        """Test the weather.gov API which provides GFS-based data in JSON format"""
        print("🌤️ Testing WEATHER.GOV API (GFS-based JSON)")
        print("=" * 60)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                # First, get the grid point for NYC
                point_url = f"https://api.weather.gov/points/{NYC_LAT},{NYC_LON}"
                print(f"📍 Getting grid point for NYC: {point_url}")
                
                response = await client.get(point_url)
                if response.status_code == 200:
                    point_data = response.json()
                    print("✅ Grid point lookup successful!")
                    
                    properties = point_data.get("properties", {})
                    grid_id = properties.get("gridId")
                    grid_x = properties.get("gridX")
                    grid_y = properties.get("gridY")
                    
                    print(f"   Grid ID: {grid_id}")
                    print(f"   Grid X: {grid_x}, Grid Y: {grid_y}")
                    
                    if grid_id and grid_x and grid_y:
                        # Get forecast data
                        forecast_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast/hourly"
                        print(f"🔍 Fetching hourly forecast: {forecast_url}")
                        
                        forecast_response = await client.get(forecast_url)
                        if forecast_response.status_code == 200:
                            forecast_data = forecast_response.json()
                            periods = forecast_data.get("properties", {}).get("periods", [])
                            
                            if periods:
                                print(f"✅ Forecast data available! ({len(periods)} periods)")
                                
                                # Show sample data
                                sample = periods[0]
                                print("\n📊 Sample forecast data:")
                                print(f"   Time: {sample.get('startTime')}")
                                print(f"   Temperature: {sample.get('temperature')}°{sample.get('temperatureUnit')}")
                                print(f"   Wind Speed: {sample.get('windSpeed')}")
                                print(f"   Wind Direction: {sample.get('windDirection')}")
                                print(f"   Humidity: {sample.get('relativeHumidity', {}).get('value')}%")
                                
                                return True, forecast_data
                            else:
                                print("❌ No forecast periods found")
                        else:
                            print(f"❌ Forecast request failed: {forecast_response.status_code}")
                    else:
                        print("❌ Grid information incomplete")
                else:
                    print(f"❌ Grid point lookup failed: {response.status_code}")
                    print(f"Response: {response.text[:200]}")
                    
            except Exception as e:
                print(f"💥 Error testing weather.gov API: {e}")
                
        return False, None
    
    async def test_nomads_opendap(self):
        """Test NOMADS OpenDAP access for GFS data"""
        print("\n🌐 Testing NOMADS OpenDAP (Direct GFS Access)")
        print("=" * 60)
        
        # Get current date for GFS run
        now = datetime.utcnow()
        # GFS runs are at 00, 06, 12, 18 UTC
        gfs_hours = [0, 6, 12, 18]
        latest_run = max([h for h in gfs_hours if h <= now.hour])
        gfs_date = now.strftime("%Y%m%d")
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                # Test if we can access GFS data catalog
                catalog_url = f"{self.base_urls['nomads_opendap']}/{gfs_date}/gfs_0p25_{latest_run:02d}z.info"
                print(f"📋 Checking GFS catalog: {catalog_url}")
                
                response = await client.get(catalog_url)
                if response.status_code == 200:
                    print("✅ GFS catalog accessible!")
                    print("📊 Available variables in GFS model:")
                    
                    # Look for wind and pressure variables
                    content = response.text
                    wind_vars = []
                    if "ugrd10m" in content.lower():
                        wind_vars.append("UGRD (U-wind component)")
                    if "vgrd10m" in content.lower():
                        wind_vars.append("VGRD (V-wind component)")
                    if "prmsl" in content.lower():
                        wind_vars.append("PRMSL (Sea level pressure)")
                    if "tmp2m" in content.lower():
                        wind_vars.append("TMP (Temperature)")
                    
                    for var in wind_vars:
                        print(f"   ✓ {var}")
                    
                    return True, {"catalog_url": catalog_url, "variables": wind_vars}
                else:
                    print(f"❌ GFS catalog not accessible: {response.status_code}")
                    
            except Exception as e:
                print(f"💥 Error testing NOMADS OpenDAP: {e}")
        
        return False, None
    
    async def test_nomads_grib_filter(self):
        """Test NOMADS GRIB filter for wind data"""
        print("\n📦 Testing NOMADS GRIB Filter (Wind Data)")
        print("=" * 60)
        
        # Calculate date/time for latest GFS run
        now = datetime.utcnow()
        gfs_hours = [0, 6, 12, 18]
        latest_run = max([h for h in gfs_hours if h <= now.hour])
        gfs_date = now.strftime("%Y%m%d")
        
        # NYC bounding box (expanded slightly for testing)
        north = NYC_LAT + 1.0  # ~41.7
        south = NYC_LAT - 1.0  # ~39.7  
        east = NYC_LON + 1.0   # ~-73.0
        west = NYC_LON - 1.0   # ~-75.0
        
        params = {
            "file": f"gfs.t{latest_run:02d}z.pgrb2.0p25.f000",  # Current analysis
            "var_UGRD": "on",  # U-wind component
            "var_VGRD": "on",  # V-wind component
            "lev_10_m_above_ground": "on",  # 10m above ground
            "subregion": "",
            "leftlon": west,
            "rightlon": east,
            "toplat": north,
            "bottomlat": south,
            "dir": f"/gfs.{gfs_date}/{latest_run:02d}/atmos"
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                url = self.base_urls["nomads_grib_filter"]
                print(f"🔍 Testing GRIB filter: {url}")
                print(f"📍 Region: {south:.1f}°N to {north:.1f}°N, {west:.1f}°E to {east:.1f}°E")
                print(f"⏰ GFS Run: {gfs_date}_{latest_run:02d}Z")
                
                response = await client.get(url, params=params)
                print(f"📊 Response Status: {response.status_code}")
                print(f"📏 Content Length: {len(response.content)} bytes")
                
                if response.status_code == 200 and len(response.content) > 1000:
                    print("✅ GRIB data successfully retrieved!")
                    
                    # Check if this is actual GRIB data
                    content_type = response.headers.get("content-type", "")
                    print(f"📋 Content-Type: {content_type}")
                    
                    # GRIB files start with "GRIB" magic bytes
                    if response.content[:4] == b"GRIB":
                        print("✅ Valid GRIB file format detected!")
                        return True, {
                            "grib_size": len(response.content),
                            "content_type": content_type,
                            "params_used": params
                        }
                    else:
                        print("⚠️ Response received but not GRIB format")
                        print(f"First 50 bytes: {response.content[:50]}")
                else:
                    print(f"❌ GRIB request failed or empty response")
                    if response.status_code != 200:
                        print(f"Error content: {response.text[:200]}")
                        
            except Exception as e:
                print(f"💥 Error testing NOMADS GRIB filter: {e}")
        
        return False, None
    
    async def find_alternative_wind_apis(self):
        """Look for alternative wind data APIs"""
        print("\n🔍 Testing Alternative Wind Data APIs")
        print("=" * 60)
        
        alternative_apis = [
            {
                "name": "OpenWeatherMap Current Weather",
                "url": f"https://api.openweathermap.org/data/2.5/weather?lat={NYC_LAT}&lon={NYC_LON}&appid=06c71052de74828712e5a6a7712ee8fa"
            },
            {
                "name": "Windy API (Visual Crossing Weather)",
                "url": f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{NYC_LAT},{NYC_LON}?key=YOUR_KEY"
            }
        ]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for api in alternative_apis:
                try:
                    print(f"🧪 Testing: {api['name']}")
                    
                    if "YOUR_KEY" in api["url"]:
                        print("   ⚠️ Requires API key - skipping")
                        continue
                    
                    response = await client.get(api["url"])
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Look for wind data
                        wind_data = {}
                        if "wind" in data:
                            wind_data = data["wind"]
                        elif "current" in data and "wind" in data["current"]:
                            wind_data = data["current"]["wind"]
                        
                        if wind_data:
                            print(f"   ✅ Wind data available!")
                            print(f"      Speed: {wind_data.get('speed', 'N/A')}")
                            print(f"      Direction: {wind_data.get('deg', 'N/A')}°")
                        else:
                            print(f"   📊 Response received but checking structure...")
                            # Show some keys to understand the structure
                            if isinstance(data, dict):
                                print(f"      Top-level keys: {list(data.keys())[:5]}")
                    else:
                        print(f"   ❌ Failed: {response.status_code}")
                        
                except Exception as e:
                    print(f"   💥 Error: {e}")

async def main():
    """Main function to test all NOAA APIs"""
    print("🚀 NOAA NOMADS GFS Data API Checker for NYC")
    print("=" * 80)
    print(f"📍 Testing location: NYC ({NYC_LAT}, {NYC_LON})")
    print(f"⏰ Current UTC time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    checker = NOAAChecker()
    
    # Test different APIs in order of preference
    results = {}
    
    # 1. Test Weather.gov API (most accessible)
    weather_gov_success, weather_data = await checker.test_weather_gov_api()
    results["weather_gov"] = {"success": weather_gov_success, "data": weather_data}
    
    # 2. Test NOMADS OpenDAP access
    opendap_success, opendap_data = await checker.test_nomads_opendap()
    results["nomads_opendap"] = {"success": opendap_success, "data": opendap_data}
    
    # 3. Test NOMADS GRIB filter
    grib_success, grib_data = await checker.test_nomads_grib_filter()
    results["nomads_grib"] = {"success": grib_success, "data": grib_data}
    
    # 4. Test alternative APIs
    await checker.find_alternative_wind_apis()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY OF RESULTS")
    print("=" * 80)
    
    working_apis = []
    for api_name, result in results.items():
        status = "✅ WORKING" if result["success"] else "❌ FAILED"
        print(f"{api_name.upper()}: {status}")
        if result["success"]:
            working_apis.append(api_name)
    
    if working_apis:
        print(f"\n🎉 Success! {len(working_apis)} API(s) working:")
        for api in working_apis:
            print(f"   ✓ {api}")
        
        print("\n💡 Recommended implementation approach:")
        if "weather_gov" in working_apis:
            print("   1. Use Weather.gov API for easy JSON-based wind data")
            print("   2. Data is GFS-based and updates every hour")
            print("   3. No API key required")
        elif "nomads_grib" in working_apis:
            print("   1. Use NOMADS GRIB filter for direct GFS access")
            print("   2. Requires GRIB file processing")
            print("   3. More complex but most accurate")
    else:
        print("\n⚠️ No direct NOAA APIs working. Consider:")
        print("   1. Using OpenWeatherMap for basic wind data")
        print("   2. Implementing GRIB processing libraries")
        print("   3. Using third-party weather APIs")

if __name__ == "__main__":
    asyncio.run(main())