"""
Quick Test Script - Verify Data Collection Setup
================================================
Run this to quickly verify your environment is set up correctly.
"""

import asyncio
import sys

def check_dependencies():
    """Check if all required packages are installed."""
    print("Checking dependencies...")
    
    required = ["httpx", "pandas", "numpy"]
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    print("✓ All dependencies installed\n")
    return True


def check_env_vars():
    """Check if environment variables are set."""
    import os
    
    print("Checking environment variables...")
    
    openweather_key = os.getenv("OPENWEATHER_API_KEY")
    openaq_key = os.getenv("OPENAQ_API_KEY")
    
    if openweather_key:
        print(f"  ✓ OPENWEATHER_API_KEY set")
    else:
        print(f"  ⚠ OPENWEATHER_API_KEY not set (using default)")
    
    if openaq_key:
        print(f"  ✓ OPENAQ_API_KEY set")
    else:
        print(f"  ⚠ OPENAQ_API_KEY not set (OpenAQ v3 requires API key)")
        print(f"    Get one at: https://openaq.org/")
    
    print()


async def test_apis():
    """Test connectivity to each API."""
    print("Testing API connectivity...")
    
    from collect_air_quality_data import (
        fetch_openaq_data,
        fetch_tempo_data,
        fetch_openweather_forecast
    )
    
    lat, lon = 40.7128, -74.0060
    
    # Test OpenWeatherMap
    print("  Testing OpenWeatherMap API...")
    ow_data = await fetch_openweather_forecast(lat, lon)
    if ow_data:
        print(f"    ✓ OpenWeatherMap: {len(ow_data)} records")
    else:
        print(f"    ✗ OpenWeatherMap: No data")
    
    # Test OpenAQ
    print("  Testing OpenAQ API...")
    oaq_data = await fetch_openaq_data(lat, lon, 25000)
    if oaq_data:
        print(f"    ✓ OpenAQ: {len(oaq_data)} records")
    else:
        print(f"    ⚠ OpenAQ: No data (API key may be required)")
    
    # Test TEMPO
    print("  Testing NASA TEMPO API...")
    tempo_data = await fetch_tempo_data(lat, lon)
    if tempo_data:
        print(f"    ✓ TEMPO: {len(tempo_data)} records")
    else:
        print(f"    ⚠ TEMPO: No data (may be temporary network issue)")
    
    print()
    
    total = len(ow_data) + len(oaq_data) + len(tempo_data)
    return total > 0


async def main():
    """Run all checks."""
    print("\n" + "=" * 60)
    print("AIR QUALITY DATA COLLECTION - SETUP CHECK")
    print("=" * 60 + "\n")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check environment
    check_env_vars()
    
    # Test APIs
    success = await test_apis()
    
    # Summary
    print("=" * 60)
    if success:
        print("✓ Setup complete! At least one API is working.")
        print("\nRun the full script with:")
        print("  python collect_air_quality_data.py")
    else:
        print("✗ Setup incomplete. Please check API keys and network.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
