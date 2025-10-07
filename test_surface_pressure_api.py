#!/usr/bin/env python3
"""
Test the NOAA Surface Pressure API implementation
"""

import asyncio
import json
from noaa_surface_pressure import NOAASurfacePressureAPI

async def test_surface_pressure_api():
    """Test the surface pressure API implementation"""
    
    print("🧪 TESTING NOAA SURFACE PRESSURE API")
    print("=" * 60)
    
    api = NOAASurfacePressureAPI()
    
    # Test 1: Standard NYC request
    print("\n🔬 TEST 1: Standard NYC Request")
    print("-" * 40)
    
    try:
        result = await api.get_surface_pressure_data(
            lat=40.7128,
            lon=-74.0060,
            hours_back=12,
            hours_forward=24
        )
        
        print(f"✅ API Call Successful")
        print(f"📍 Location: {result['location']}")
        print(f"📊 Forecast Points: {len(result['forecast_data'])}")
        print(f"🏪 Observation Points: {len(result['observation_data'])}")
        print(f"📈 Combined Points: {len(result['combined_timeseries'])}")
        
        # Show summary
        summary = result.get('summary', {})
        if summary:
            stats = summary.get('pressure_stats', {})
            print(f"\n📊 Pressure Statistics:")
            print(f"  Min: {stats.get('min_hpa', 0):.1f} hPa")
            print(f"  Max: {stats.get('max_hpa', 0):.1f} hPa") 
            print(f"  Avg: {stats.get('avg_hpa', 0):.1f} hPa")
            print(f"  Range: {stats.get('range_hpa', 0):.1f} hPa")
        
        # Show sample data points
        if result['combined_timeseries']:
            print(f"\n📈 Sample Data Points (First 5):")
            for i, point in enumerate(result['combined_timeseries'][:5]):
                timestamp = point['timestamp']
                pressure = point['pressure_hpa']
                source = point['source']
                station = point.get('station', point.get('grid_point', 'N/A'))
                print(f"  {i+1}. {timestamp} -> {pressure:7.1f} hPa ({source}) [{station}]")
        
    except Exception as e:
        print(f"❌ TEST 1 FAILED: {e}")
    
    # Test 2: Custom time range
    print(f"\n🔬 TEST 2: Custom Time Range (48h back, 12h forward)")
    print("-" * 40)
    
    try:
        result = await api.get_surface_pressure_data(
            lat=40.7128,
            lon=-74.0060,
            hours_back=48,
            hours_forward=12
        )
        
        print(f"✅ Custom Range Successful")
        print(f"📊 Total Points: {len(result['combined_timeseries'])}")
        
        summary = result.get('summary', {})
        if summary:
            time_range = summary.get('time_range', {})
            print(f"⏰ Time Coverage:")
            print(f"  Start: {time_range.get('start', 'N/A')}")
            print(f"  End: {time_range.get('end', 'N/A')}")
        
    except Exception as e:
        print(f"❌ TEST 2 FAILED: {e}")
    
    # Test 3: Different location (Los Angeles)
    print(f"\n🔬 TEST 3: Different Location (Los Angeles)")
    print("-" * 40)
    
    try:
        result = await api.get_surface_pressure_data(
            lat=34.0522,
            lon=-118.2437,
            hours_back=6,
            hours_forward=18
        )
        
        print(f"✅ LA Request Successful")
        print(f"📍 Location: {result['location']}")
        grid_info = result.get('metadata', {}).get('grid', {})
        print(f"🗺️ Grid: {grid_info.get('gridId')} ({grid_info.get('gridX')}, {grid_info.get('gridY')})")
        print(f"📊 Total Points: {len(result['combined_timeseries'])}")
        
    except Exception as e:
        print(f"❌ TEST 3 FAILED: {e}")
    
    # Test 4: Only observations
    print(f"\n🔬 TEST 4: Observations Only")
    print("-" * 40)
    
    try:
        result = await api.get_surface_pressure_data(
            lat=40.7128,
            lon=-74.0060,
            hours_back=24,
            hours_forward=0,
            include_forecast=False,
            include_observations=True
        )
        
        print(f"✅ Observations Only Successful")
        print(f"📊 Observation Points: {len(result['observation_data'])}")
        print(f"📈 Forecast Points: {len(result['forecast_data'])}")
        print(f"📈 Combined Points: {len(result['combined_timeseries'])}")
        
    except Exception as e:
        print(f"❌ TEST 4 FAILED: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"✅ TESTING COMPLETE")
    print(f"=" * 60)

if __name__ == "__main__":
    asyncio.run(test_surface_pressure_api())