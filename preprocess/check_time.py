"""
Check time variable structure
"""
import xarray as xr

filepath = 'tempo_data_nyc/TEMPO_NO2_L2_NRT_V02_20251003T234442Z_S014G06.nc'

ds_geo = xr.open_dataset(filepath, group='geolocation')

print("Time variable info:")
print(ds_geo['time'])
print(f"\nShape: {ds_geo['time'].shape}")
print(f"Dims: {ds_geo['time'].dims}")
print(f"Type: {ds_geo['time'].dtype}")

print("\n\nLatitude variable info:")
print(ds_geo['latitude'])

ds_geo.close()
