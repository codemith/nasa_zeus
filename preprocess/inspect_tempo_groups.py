"""
Deeper inspection of TEMPO NetCDF file - check for groups
"""
import xarray as xr
import netCDF4 as nc4

filepath = 'tempo_data_nyc/TEMPO_NO2_L2_NRT_V02_20251003T234442Z_S014G06.nc'

print(f"\nInspecting with netCDF4: {filepath}\n")
print("=" * 80)

# Use netCDF4 to see groups
with nc4.Dataset(filepath, 'r') as ds:
    print("\nROOT LEVEL:")
    print(f"Dimensions: {list(ds.dimensions.keys())}")
    print(f"Variables: {list(ds.variables.keys())}")
    print(f"Groups: {list(ds.groups.keys())}")
    
    print("\n" + "=" * 80)
    print("\nEXPLORING GROUPS:")
    
    for group_name in ds.groups.keys():
        print(f"\n📁 GROUP: {group_name}")
        group = ds.groups[group_name]
        print(f"   Variables: {list(group.variables.keys())[:10]}")
        
        # Check for subgroups
        if group.groups:
            print(f"   Subgroups: {list(group.groups.keys())}")
            for subgroup_name in group.groups.keys():
                subgroup = group.groups[subgroup_name]
                print(f"\n   📁 SUBGROUP: {group_name}/{subgroup_name}")
                print(f"      Variables: {list(subgroup.variables.keys())[:10]}")

print("\n" + "=" * 80)
print("\nTrying to open specific groups with xarray:")

# Try opening the geolocation group
try:
    ds_geo = xr.open_dataset(filepath, group='geolocation')
    print("\n✓ geolocation group variables:")
    for var in ds_geo.data_vars:
        print(f"  - {var}")
    ds_geo.close()
except Exception as e:
    print(f"\n✗ Error opening geolocation: {e}")

# Try opening product group
try:
    ds_product = xr.open_dataset(filepath, group='product')
    print("\n✓ product group variables:")
    for var in ds_product.data_vars:
        print(f"  - {var}: {ds_product[var].shape}")
    ds_product.close()
except Exception as e:
    print(f"\n✗ Error opening product: {e}")
