#!/usr/bin/env python3
"""Quick test of the FastAPI server and surface pressure endpoint"""

import requests
import json

def test_server():
    try:
        # Test basic health
        print("🧪 Testing FastAPI server...")
        
        # Test the surface pressure endpoint
        url = "http://localhost:8001/api/surface-pressure"
        params = {
            "lat": 40.7128,
            "lon": -74.0060,
            "hours_back": 1,
            "hours_forward": 0
        }
        
        print(f"📡 Testing: {url}")
        print(f"📊 Params: {params}")
        
        response = requests.get(url, params=params, timeout=30)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success: {data.get('success', False)}")
            print(f"📝 Message: {data.get('message', 'No message')}")
            
            result_data = data.get('data', {})
            if result_data:
                obs_count = len(result_data.get('observation_data', []))
                print(f"🏪 Observations: {obs_count}")
                
                if obs_count > 0:
                    latest = result_data['observation_data'][-1]
                    print(f"🌡️ Latest Pressure: {latest.get('pressure_hpa', 'N/A')} hPa")
                    print(f"📡 Station: {latest.get('station', 'N/A')}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"📝 Response: {response.text[:200]}...")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server not running or wrong port")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_server()