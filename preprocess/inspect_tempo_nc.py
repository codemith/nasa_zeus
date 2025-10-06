"""
Quick script to inspect TEMPO NetCDF file structure
"""
import xarray as xr
import sys

if len(sys.argv) > 1:
    filepath = sys.argv[1]
else:
    filepath = 'tempo_data_nyc/TEMPO_NO2_L2_NRT_V02_20251003T234442Z_S014G06.nc'

print(f"\nInspecting: {filepath}\n")
print("=" * 80)

ds = xr.open_dataset(filepath)

print("\nDATASET OVERVIEW:")
print(ds)

print("\n" + "=" * 80)
print("\nDATA VARIABLES:")
for var in ds.data_vars:
    print(f"  - {var}")
    print(f"    Shape: {ds[var].shape}")
    print(f"    Dims: {ds[var].dims}")
    if ds[var].attrs:
        print(f"    Attrs: {list(ds[var].attrs.keys())[:5]}")
    print()

print("=" * 80)
print("\nCOORDINATES:")
for coord in ds.coords:
    print(f"  - {coord}: {ds[coord].shape}")

print("\n" + "=" * 80)
print("\nGLOBAL ATTRIBUTES:")
for attr in list(ds.attrs.keys())[:10]:
    print(f"  - {attr}: {ds.attrs[attr]}")

ds.close()
