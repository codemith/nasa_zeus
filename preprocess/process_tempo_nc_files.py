"""
TEMPO NO₂ Data Processing Script
=================================
Process downloaded TEMPO .nc files and extract NO₂ data for specific coordinates (NYC).
Creates a time-series CSV file from multiple NetCDF files.
"""

import os
import xarray as xr
import pandas as pd
from datetime import datetime
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

# Directory containing .nc files
TEMPO_DATA_DIR = 'tempo_data_nyc/'

# Target coordinates for NYC
TARGET_LAT = 40.7128
TARGET_LON = -74.0060

# Output file
OUTPUT_CSV = 'tempo_nyc_timeseries.csv'

# =============================================================================
# DATA PROCESSING FUNCTIONS
# =============================================================================

def extract_no2_from_nc(filepath: str, target_lat: float, target_lon: float) -> dict:
    """
    Extract NO₂ data from a single TEMPO NetCDF file for a specific location.
    
    Args:
        filepath: Path to the .nc file
        target_lat: Target latitude coordinate
        target_lon: Target longitude coordinate
    
    Returns:
        Dictionary containing timestamp and NO₂ value, or None if extraction fails
    """
    try:
        # TEMPO L2 files have data in groups
        # Open the product group for NO₂ data
        ds_product = xr.open_dataset(filepath, group='product')
        ds_geo = xr.open_dataset(filepath, group='geolocation')
        
        # Get the NO₂ tropospheric column data
        no2_data = ds_product['vertical_column_troposphere']
        
        # Get latitude and longitude arrays
        lat_data = ds_geo['latitude']
        lon_data = ds_geo['longitude']
        time_data = ds_geo['time']
        
        # Find the closest pixel to target coordinates
        # Calculate distance from target for each pixel
        lat_diff = lat_data - target_lat
        lon_diff = lon_data - target_lon
        distance = (lat_diff**2 + lon_diff**2)**0.5
        
        # Find the indices of the minimum distance
        min_idx = distance.argmin()
        min_idx_coords = divmod(int(min_idx), distance.shape[1])
        mirror_idx, xtrack_idx = min_idx_coords
        
        # Extract NO₂ value at that location
        no2_value = float(no2_data.isel(mirror_step=mirror_idx, xtrack=xtrack_idx).values)
        
        # Extract coordinates at that location
        actual_lat = float(lat_data.isel(mirror_step=mirror_idx, xtrack=xtrack_idx).values)
        actual_lon = float(lon_data.isel(mirror_step=mirror_idx, xtrack=xtrack_idx).values)
        
        # Extract timestamp - time is only indexed by mirror_step
        time_value = time_data.isel(mirror_step=mirror_idx).values
        timestamp = pd.to_datetime(time_value)
        
        # Close datasets
        ds_product.close()
        ds_geo.close()
        
        logger.info(f"✓ Processed {os.path.basename(filepath)}")
        logger.info(f"  NO₂: {no2_value:.2e} mol/cm², Time: {timestamp}")
        logger.info(f"  Location: ({actual_lat:.4f}, {actual_lon:.4f})")
        
        return {
            'timestamp': timestamp,
            'no2_value': no2_value,
            'latitude': actual_lat,
            'longitude': actual_lon,
            'unit': 'mol/cm²',
            'filename': os.path.basename(filepath)
        }
    
    except KeyError as e:
        logger.error(f"✗ KeyError in {os.path.basename(filepath)}: {e}")
        return None
    
    except Exception as e:
        logger.error(f"✗ Error processing {os.path.basename(filepath)}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def process_all_tempo_files(
    data_dir: str,
    target_lat: float,
    target_lon: float,
    output_csv: str
) -> pd.DataFrame:
    """
    Process all TEMPO .nc files in a directory and create a time-series CSV.
    
    Args:
        data_dir: Directory containing .nc files
        target_lat: Target latitude coordinate
        target_lon: Target longitude coordinate
        output_csv: Output CSV filename
    
    Returns:
        DataFrame with extracted NO₂ time-series data
    """
    logger.info("=" * 80)
    logger.info("TEMPO NO₂ DATA PROCESSING STARTED")
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"Target coordinates: ({target_lat}, {target_lon})")
    logger.info("=" * 80)
    
    # Create directory if it doesn't exist
    data_dir_path = Path(data_dir)
    if not data_dir_path.exists():
        logger.error(f"Directory not found: {data_dir}")
        logger.info(f"Creating directory: {data_dir}")
        data_dir_path.mkdir(parents=True, exist_ok=True)
        logger.warning("Directory was empty. Please add .nc files to process.")
        return pd.DataFrame()
    
    # Find all .nc files
    nc_files = sorted([f for f in os.listdir(data_dir) if f.endswith('.nc')])
    
    if not nc_files:
        logger.warning(f"No .nc files found in {data_dir}")
        return pd.DataFrame()
    
    logger.info(f"Found {len(nc_files)} .nc files to process")
    logger.info("-" * 80)
    
    # Store extracted data records
    records = []
    
    # Process each file
    for i, filename in enumerate(nc_files, 1):
        filepath = os.path.join(data_dir, filename)
        logger.info(f"[{i}/{len(nc_files)}] Processing: {filename}")
        
        # Extract data from file
        record = extract_no2_from_nc(filepath, target_lat, target_lon)
        
        if record is not None:
            records.append(record)
        
        logger.info("")  # Blank line for readability
    
    # Convert to DataFrame
    if not records:
        logger.warning("No data was successfully extracted from any files")
        return pd.DataFrame()
    
    df = pd.DataFrame(records)
    
    # Sort by timestamp
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Save to CSV
    df.to_csv(output_csv, index=False)
    
    logger.info("=" * 80)
    logger.info("PROCESSING COMPLETE")
    logger.info(f"Total records extracted: {len(df)}")
    logger.info(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    logger.info(f"NO₂ range: {df['no2_value'].min():.2e} to {df['no2_value'].max():.2e} molecules/cm²")
    logger.info(f"Output saved to: {output_csv}")
    logger.info("=" * 80)
    
    return df


# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Process all TEMPO files
    df = process_all_tempo_files(
        data_dir=TEMPO_DATA_DIR,
        target_lat=TARGET_LAT,
        target_lon=TARGET_LON,
        output_csv=OUTPUT_CSV
    )
    
    # Display preview of results
    if not df.empty:
        print("\n" + "=" * 80)
        print("PREVIEW OF EXTRACTED DATA")
        print("=" * 80)
        print(df.head(10))
        print("\n" + "=" * 80)
        print("DATA STATISTICS")
        print("=" * 80)
        print(df.describe())
    else:
        print("\nNo data was extracted. Please check:")
        print(f"1. The directory '{TEMPO_DATA_DIR}' contains .nc files")
        print("2. The .nc files have the correct structure")
        print("3. The coordinate bounds include the target location")
