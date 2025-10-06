#!/usr/bin/env python3
"""
Quick test script for O3 prediction endpoint
"""

import requests
import json
from datetime import datetime

print("🧪 Testing O3 Prediction System")
print("=" * 60)

# Test endpoint
url = "http://localhost:8001/predict-o3"
params = {"location": "New York City"}

print(f"\n📍 Making request to: {url}")
print(f"📍 Location: {params['location']}")
print("\n⏳ Fetching atmospheric data and predicting O3...")
print("   (This may take 10-15 seconds for Gemini to search...)\n")

try:
    response = requests.get(url, params=params, timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        
        if data.get('success'):
            # Display prediction
            print(f"\n🎯 O3 PREDICTION: {data.get('o3_prediction', 'N/A')} {data.get('unit', 'ppb')}")
            print(f"📊 Confidence: {data.get('confidence', 'unknown').upper()}")
            print(f"🤖 Model: {data.get('model_type', 'unknown')}")
            print(f"📍 Location: {data.get('location', 'unknown')}")
            
            # Display atmospheric data
            if 'atmospheric_data' in data:
                atm = data['atmospheric_data']
                print(f"\n🌍 ATMOSPHERIC DATA:")
                print(f"   Timestamp: {atm.get('query_timestamp', 'unknown')}")
                
                if 'parameters' in atm:
                    print(f"\n   Parameters Used:")
                    for param, details in atm['parameters'].items():
                        if isinstance(details, dict):
                            value = details.get('value', 'N/A')
                            unit = details.get('unit', '')
                            source = details.get('source', 'N/A')
                            confidence = details.get('confidence', 'unknown')
                            
                            # Emoji for confidence
                            conf_emoji = '✅' if confidence == 'high' else '⚠️' if confidence == 'medium' else '❓'
                            
                            print(f"   {conf_emoji} {param}: {value} {unit}")
                            print(f"      Source: {source}")
                
                if 'sources' in atm:
                    print(f"\n   📚 Data Sources:")
                    for source in atm['sources']:
                        print(f"      • {source}")
        else:
            print(f"\n❌ Prediction failed:")
            print(f"   Error: {data.get('error', 'Unknown error')}")
            print(f"   Message: {data.get('message', 'No message')}")
        
        # Save full response
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"o3_prediction_test_{timestamp}.json"
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Full response saved to: {filename}")
        
    else:
        print(f"❌ HTTP Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    print("❌ Request timed out (> 30 seconds)")
    print("   Gemini search may be taking longer than expected")
    
except requests.exceptions.ConnectionError:
    print("❌ Could not connect to server")
    print("   Make sure the server is running on http://localhost:8001")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)
