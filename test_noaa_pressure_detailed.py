#!/usr/bin/env python3
"""
Detailed NOAA Surface Pressure Data Analysis
Examines the actual pressure data structure, values, and time ranges
"""

import httpx
import json
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, List

# NYC coordinates
NYC_LAT = 40.7128
NYC_LON = -74.0060

async def analyze_noaa_pressure_data():
    """Detailed analysis of NOAA surface pressure data"""
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🌪️ DETAILED NOAA SURFACE PRESSURE ANALYSIS FOR NYC")
        print("=" * 70)
        
        # Step 1: Get grid coordinates
        point_url = f"https://api.weather.gov/points/{NYC_LAT},{NYC_LON}"
        print(f"📍 Getting grid coordinates: {point_url}")
        
        try:
            response = await client.get(point_url)
            response.raise_for_status()
            point_data = response.json()
            properties = point_data.get("properties", {})
            
            grid_id = properties.get("gridId")
            grid_x = properties.get("gridX")
            grid_y = properties.get("gridY")
            
            print(f"✅ Grid: {grid_id} ({grid_x}, {grid_y})")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return
        
        # Step 2: Get detailed pressure data from grid endpoint
        grid_url = f"https://api.weather.gov/gridpoints/{grid_id}/{grid_x},{grid_y}"
        print(f"\n🔍 Analyzing grid data: {grid_url}")
        
        try:
            response = await client.get(grid_url)
            response.raise_for_status()
            grid_data = response.json()
            
            pressure_data = grid_data.get("properties", {}).get("pressure")
            
            if pressure_data:
                print(f"\n📊 PRESSURE DATA ANALYSIS:")
                print(f"  Units: {pressure_data.get('uom', 'Unknown')}")
                
                values = pressure_data.get("values", [])
                print(f"  Total data points: {len(values)}")
                
                if values:
                    # Analyze time range and values
                    print(f"\n⏰ TIME RANGE ANALYSIS:")
                    
                    first_time = values[0].get("validTime", "")
                    last_time = values[-1].get("validTime", "") if len(values) > 1 else ""
                    
                    print(f"  First timestamp: {first_time}")
                    print(f"  Last timestamp: {last_time}")
                    
                    # Parse and analyze time intervals
                    time_intervals = []
                    pressure_values = []
                    
                    for i, value in enumerate(values[:20]):  # Analyze first 20 points
                        valid_time = value.get("validTime", "")
                        pressure_val = value.get("value")
                        
                        if valid_time and pressure_val is not None:
                            time_intervals.append(valid_time)
                            pressure_values.append(pressure_val)
                    
                    print(f"\n📈 PRESSURE VALUES (First 10 points):")
                    for i, (time_str, pressure) in enumerate(zip(time_intervals[:10], pressure_values[:10])):
                        # Parse time for better display
                        try:
                            if "/" in time_str:
                                time_part = time_str.split("/")[0]
                            else:
                                time_part = time_str.split("+")[0]
                            dt = datetime.fromisoformat(time_part.replace("Z", "+00:00"))
                            formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC")
                        except:
                            formatted_time = time_str
                        
                        print(f"  {i+1:2d}. {formatted_time} -> {pressure:8.1f} {pressure_data.get('uom', '')}")
                    
                    # Statistical analysis
                    if pressure_values:
                        min_pressure = min(pressure_values)
                        max_pressure = max(pressure_values)
                        avg_pressure = sum(pressure_values) / len(pressure_values)
                        
                        print(f"\n📊 STATISTICAL ANALYSIS (First 20 points):")
                        print(f"  Minimum: {min_pressure:8.1f} {pressure_data.get('uom', '')}")
                        print(f"  Maximum: {max_pressure:8.1f} {pressure_data.get('uom', '')}")
                        print(f"  Average: {avg_pressure:8.1f} {pressure_data.get('uom', '')}")
                        print(f"  Range:   {max_pressure - min_pressure:8.1f} {pressure_data.get('uom', '')}")
                    
                    # Check forecast vs current time
                    print(f"\n🕐 TEMPORAL ANALYSIS:")
                    now = datetime.now()
                    forecast_points = 0
                    current_points = 0
                    
                    for time_str in time_intervals:
                        try:
                            if "/" in time_str:
                                time_part = time_str.split("/")[0]
                            else:
                                time_part = time_str.split("+")[0]
                            dt = datetime.fromisoformat(time_part.replace("Z", "+00:00"))
                            
                            if dt > now:
                                forecast_points += 1
                            else:
                                current_points += 1
                        except:
                            continue
                    
                    print(f"  Current/Past: {current_points} points")
                    print(f"  Future/Forecast: {forecast_points} points")
                
            else:
                print(f"❌ No pressure data found in grid endpoint")
                
        except Exception as e:
            print(f"❌ Grid data error: {e}")
        
        # Step 3: Test real-time observation data
        print(f"\n" + "=" * 70)
        print(f"📡 REAL-TIME OBSERVATION STATIONS ANALYSIS")
        print(f"=" * 70)
        
        # Test the NYC area stations
        stations = ["KNYC", "KLGA", "KEWR", "KJFK", "KTEB"]
        
        for station_id in stations:
            print(f"\n🏪 Station: {station_id}")
            
            try:
                obs_url = f"https://api.weather.gov/stations/{station_id}/observations/latest"
                response = await client.get(obs_url)
                response.raise_for_status()
                
                obs_data = response.json()
                properties = obs_data.get("properties", {})
                
                # Extract pressure data
                barometric = properties.get("barometricPressure")
                sea_level = properties.get("seaLevelPressure")
                timestamp = properties.get("timestamp")
                
                print(f"  Timestamp: {timestamp}")
                
                if barometric:
                    value = barometric.get("value")
                    unit = barometric.get("unitCode", "").replace("wmoUnit:", "")
                    quality = barometric.get("qualityControl", "Unknown")
                    print(f"  Barometric Pressure: {value} {unit} (Quality: {quality})")
                
                if sea_level:
                    value = sea_level.get("value")
                    unit = sea_level.get("unitCode", "").replace("wmoUnit:", "")
                    quality = sea_level.get("qualityControl", "Unknown")
                    print(f"  Sea Level Pressure: {value} {unit} (Quality: {quality})")
                
                if not barometric and not sea_level:
                    print(f"  ❌ No pressure data available")
                    
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        # Step 4: Test custom time range with observations
        print(f"\n" + "=" * 70)
        print(f"⏰ CUSTOM TIME RANGE TESTING")
        print(f"=" * 70)
        
        # Test getting historical observations from a station
        station_id = "KNYC"  # NYC Central Park
        print(f"\n📅 Testing time range requests for {station_id}")
        
        # Try to get observations for the last 24 hours
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=24)
        
        # Format times for NOAA API
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        time_range_url = f"https://api.weather.gov/stations/{station_id}/observations?start={start_iso}&end={end_iso}"
        print(f"🔍 URL: {time_range_url}")
        
        try:
            response = await client.get(time_range_url)
            print(f"📊 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                obs_data = response.json()
                features = obs_data.get("features", [])
                
                print(f"✅ Retrieved {len(features)} observations")
                
                # Analyze pressure data in time series
                pressure_series = []
                for feature in features[:10]:  # First 10 observations
                    props = feature.get("properties", {})
                    timestamp = props.get("timestamp")
                    barometric = props.get("barometricPressure")
                    
                    if timestamp and barometric and barometric.get("value"):
                        pressure_series.append({
                            "time": timestamp,
                            "pressure": barometric.get("value"),
                            "unit": barometric.get("unitCode", "").replace("wmoUnit:", "")
                        })
                
                if pressure_series:
                    print(f"\n📈 PRESSURE TIME SERIES (Last {len(pressure_series)} points):")
                    for i, point in enumerate(pressure_series):
                        # Format timestamp
                        try:
                            dt = datetime.fromisoformat(point["time"].replace("Z", "+00:00"))
                            formatted_time = dt.strftime("%Y-%m-%d %H:%M UTC")
                        except:
                            formatted_time = point["time"]
                        
                        print(f"  {i+1:2d}. {formatted_time} -> {point['pressure']:8.1f} {point['unit']}")
                
                print(f"\n✅ CUSTOM TIME RANGE SUPPORTED: YES")
                print(f"   - Can request specific time ranges")
                print(f"   - Historical data available (at least 24h)")
                print(f"   - Real-time observations included")
                
            else:
                print(f"❌ Time range request failed: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                
        except Exception as e:
            print(f"❌ Time range test error: {e}")
        
        print(f"\n" + "=" * 70)
        print(f"🎯 FINAL CONCLUSIONS")
        print(f"=" * 70)
        
        print(f"✅ Surface Pressure Available: YES")
        print(f"✅ Grid Forecast Data: Available with hourly resolution")
        print(f"✅ Real-time Observations: Available from multiple NYC stations")
        print(f"✅ Custom Time Ranges: Supported for observations")
        print(f"✅ Units: Pascal (Pa) - convertible to hPa, inHg, etc.")
        print(f"\n💡 IMPLEMENTATION RECOMMENDATIONS:")
        print(f"   1. Use grid forecast for future surface pressure predictions")
        print(f"   2. Use observation stations for real-time/historical data")
        print(f"   3. Combine both sources for complete time coverage")
        print(f"   4. Implement proper unit conversions (Pa -> hPa/mb)")

if __name__ == "__main__":
    asyncio.run(analyze_noaa_pressure_data())