#!/usr/bin/env python3
"""
Test the FastAPI surface pressure endpoint
"""

import requests
import json
from datetime import datetime

def test_surface_pressure_endpoint():
    """Test the /api/surface-pressure endpoint"""
    
    base_url = "http://localhost:8000"
    endpoint = "/api/surface-pressure"
    
    print("🧪 TESTING FASTAPI SURFACE PRESSURE ENDPOINT")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Standard NYC Request",
            "params": {
                "lat": 40.7128,
                "lon": -74.0060,
                "hours_back": 12,
                "hours_forward": 24
            }
        },
        {
            "name": "Extended Time Range", 
            "params": {
                "lat": 40.7128,
                "lon": -74.0060,
                "hours_back": 48,
                "hours_forward": 72
            }
        },
        {
            "name": "Observations Only",
            "params": {
                "lat": 40.7128,
                "lon": -74.0060,
                "hours_back": 24,
                "include_forecast": False
            }
        },
        {
            "name": "Los Angeles",
            "params": {
                "lat": 34.0522,
                "lon": -118.2437,
                "hours_back": 12,
                "hours_forward": 24
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🔬 TEST {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            # Make request
            url = f"{base_url}{endpoint}"
            response = requests.get(url, params=test_case['params'], timeout=30)
            
            print(f"📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract key information
                success = data.get('success', False)
                message = data.get('message', '')
                result_data = data.get('data', {})
                
                print(f"✅ Success: {success}")
                print(f"📝 Message: {message}")
                
                if result_data:
                    # Show data summary
                    location = result_data.get('location', {})
                    summary = result_data.get('summary', {})
                    
                    print(f"📍 Location: {location}")
                    print(f"📊 Total Points: {summary.get('total_points', 0)}")
                    print(f"🏪 Observations: {summary.get('observation_points', 0)}")
                    print(f"📈 Forecasts: {summary.get('forecast_points', 0)}")
                    
                    # Pressure statistics
                    stats = summary.get('pressure_stats', {})
                    if stats:
                        print(f"🌡️  Pressure Range: {stats.get('min_hpa', 0):.1f} - {stats.get('max_hpa', 0):.1f} hPa")
                        print(f"📊 Average: {stats.get('avg_hpa', 0):.1f} hPa")
                
            else:
                print(f"❌ Request failed")
                print(f"📝 Response: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Error - FastAPI server not running")
            print(f"💡 Start server with: python -m uvicorn main:app --reload --port 8000")
        except requests.exceptions.Timeout:
            print(f"❌ Request timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🏁 ENDPOINT TESTING COMPLETE")
    print(f"💡 Access API docs at: http://localhost:8000/docs")
    print(f"=" * 60)

if __name__ == "__main__":
    test_surface_pressure_endpoint()