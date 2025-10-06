# TEMPO NetCDF Processing Guide

## Overview
The `process_tempo_nc_files.py` script extracts NO₂ data from TEMPO satellite NetCDF files for a specific location (NYC by default).

## What the Script Does
1. **Loops through all `.nc` files** in the `tempo_data_nyc/` directory
2. **Extracts NO₂ data** from the `product/vertical_column_troposphere` variable
3. **Finds the closest pixel** to the target coordinates (40.7128°N, -74.0060°W for NYC)
4. **Extracts the timestamp** from the `geolocation/time` variable
5. **Saves results to CSV** (`tempo_nyc_timeseries.csv`) with columns:
   - `timestamp`: Date/time of measurement
   - `no2_value`: NO₂ tropospheric column (mol/cm²)
   - `latitude`: Actual pixel latitude
   - `longitude`: Actual pixel longitude
   - `unit`: Measurement unit
   - `filename`: Source .nc file

## Requirements
```bash
pip install xarray netcdf4 pandas
```

## Usage
```bash
python3 process_tempo_nc_files.py
```

## Downloading TEMPO Data for NYC

### Important Note
TEMPO satellite data is organized into **granules** that cover different geographic regions. Each granule covers a specific scan area, and not all granules include NYC coordinates.

### How to Download NYC-Specific TEMPO Data

1. **Visit NASA Earthdata Search**
   - Go to: https://search.earthdata.nasa.gov/
   - Log in with your Earthdata account (free registration)

2. **Search for TEMPO Data**
   - Search for: `TEMPO_NO2_L2_NRT` or `TEMPO_NO2_L3`
   - Select the dataset from the results

3. **Filter by Location**
   - Click "Spatial" in the left sidebar
   - Draw a bounding box around NYC:
     - North: 41.0°N
     - South: 40.5°N
     - East: -73.7°W
     - West: -74.3°W
   
4. **Filter by Time**
   - Select your desired date range
   - TEMPO provides hourly daytime coverage

5. **Download Files**
   - Click on individual granules to preview coverage
   - Verify the granule includes NYC in its bounds
   - Download the `.nc` files
   - Place them in the `tempo_data_nyc/` directory

### Alternative: Direct Data Access
You can also use the NASA LAADS DAAC:
- URL: https://ladsweb.modaps.eosdis.nasa.gov/
- Product: TEMPO_NO2_L2_NRT_V02
- Filter by date and geographic bounds

### Verifying Coverage
Before processing, you can check if a TEMPO file covers NYC:

```python
import xarray as xr

ds = xr.open_dataset('your_file.nc', group='geolocation')
lats = ds['latitude'].values
lons = ds['longitude'].values

print(f"Lat range: {lats.min():.2f} to {lats.max():.2f}")
print(f"Lon range: {lons.min():.2f} to {lons.max():.2f}")

# NYC is at (40.7128, -74.0060)
if 40.5 <= lats.max() and lats.min() <= 41.0:
    if -74.3 <= lons.max() and lons.min() <= -73.7:
        print("✓ This granule covers NYC!")
    else:
        print("✗ Longitude range doesn't include NYC")
else:
    print("✗ Latitude range doesn't include NYC")

ds.close()
```

## Output Format
The resulting `tempo_nyc_timeseries.csv` contains time-series data:

```csv
timestamp,no2_value,latitude,longitude,unit,filename
2025-10-03 15:23:45,2.45e+15,40.7234,-74.0123,mol/cm²,TEMPO_NO2_L2_NRT_V02_20251003T152345Z_S008G03.nc
2025-10-03 16:23:45,2.38e+15,40.7234,-74.0123,mol/cm²,TEMPO_NO2_L2_NRT_V02_20251003T162345Z_S009G03.nc
...
```

## Understanding TEMPO Data Structure

TEMPO Level 2 (L2) NetCDF files have a hierarchical group structure:

```
root/
├── product/
│   ├── vertical_column_troposphere  ← NO₂ data (131 x 2048)
│   ├── vertical_column_stratosphere
│   └── vertical_column_troposphere_uncertainty
├── geolocation/
│   ├── latitude  (131 x 2048)
│   ├── longitude (131 x 2048)
│   └── time (131)  ← timestamps
├── support_data/
└── qa_statistics/
```

- **Dimensions**: `mirror_step` (131) × `xtrack` (2048)
- **NO₂ Units**: mol/cm² (moles per square centimeter)
- **Time**: One timestamp per mirror step (scan line)

## Troubleshooting

### "No .nc files found"
- Ensure files are in `tempo_data_nyc/` directory
- Check files end with `.nc` extension

### "No data was successfully extracted"
- Verify the TEMPO granule covers your target coordinates
- Check file is not corrupted: `ncdump -h your_file.nc`

### "KeyError: 'vertical_column_troposphere'"
- Make sure you're using Level 2 (L2) product files
- Level 3 (L3) files have different structure

## Advanced Usage

### Change Target Location
Edit the script constants:
```python
TARGET_LAT = 34.0522  # Los Angeles
TARGET_LON = -118.2437
```

### Change Output File
```python
OUTPUT_CSV = 'tempo_la_timeseries.csv'
```

### Process Multiple Locations
Modify the script to loop over multiple target coordinates.

## Related Scripts
- `inspect_tempo_nc.py`: Examine file structure
- `inspect_tempo_groups.py`: View available groups and variables
- `collect_air_quality_data.py`: Collect data from multiple APIs
