"""
Example: Scheduled Air Quality Data Collection
==============================================
This script demonstrates how to set up automated data collection
for multiple cities using the air quality data collection module.
"""

import asyncio
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

from preprocess.collect_air_quality_data import collect_all_data, save_to_csv, Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define cities to monitor
CITIES = [
    {"name": "New York City", "lat": 40.7128, "lon": -74.0060, "radius": 25000},
    {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437, "radius": 25000},
    {"name": "Chicago", "lat": 41.8781, "lon": -87.6298, "radius": 25000},
    {"name": "Houston", "lat": 29.7604, "lon": -95.3698, "radius": 25000},
    {"name": "Phoenix", "lat": 33.4484, "lon": -112.0740, "radius": 25000},
]


async def collect_for_city(city: Dict) -> None:
    """
    Collect air quality data for a single city.
    
    Args:
        city: Dictionary with city name, lat, lon, and radius
    """
    logger.info(f"Starting collection for {city['name']}")
    
    try:
        # Collect data
        df = await collect_all_data(
            lat=city["lat"],
            lon=city["lon"],
            radius=city["radius"]
        )
        
        if not df.empty:
            # Save to city-specific CSV file
            filename = f"air_quality_{city['name'].lower().replace(' ', '_')}.csv"
            save_to_csv(df, filename=filename, append=True)
            
            logger.info(f"✓ {city['name']}: Collected {len(df)} records")
        else:
            logger.warning(f"⚠ {city['name']}: No data collected")
    
    except Exception as e:
        logger.error(f"✗ {city['name']}: Collection failed - {str(e)}")


async def collect_all_cities() -> None:
    """
    Collect air quality data for all configured cities concurrently.
    """
    logger.info("=" * 80)
    logger.info(f"MULTI-CITY DATA COLLECTION STARTED - {datetime.now()}")
    logger.info(f"Cities: {len(CITIES)}")
    logger.info("=" * 80)
    
    # Run collections concurrently
    tasks = [collect_for_city(city) for city in CITIES]
    await asyncio.gather(*tasks)
    
    logger.info("=" * 80)
    logger.info("MULTI-CITY DATA COLLECTION COMPLETED")
    logger.info("=" * 80)


def main():
    """Main entry point for scheduled execution."""
    asyncio.run(collect_all_cities())


if __name__ == "__main__":
    # This can be scheduled with cron, systemd timer, or task scheduler
    # Example cron entry (runs every hour):
    # 0 * * * * cd /path/to/project && python3 example_scheduled_collection.py >> logs/scheduled.log 2>&1
    
    main()
