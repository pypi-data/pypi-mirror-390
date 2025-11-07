#!/usr/bin/env python3
"""Test the zarr version checking logic"""

import sys
sys.path.insert(0, '.')

import zarr
import packaging.version

# Check version as used in the tests
zarr_version = packaging.version.parse(zarr.__version__)
zarr_version_major = zarr_version.major

print(f"Zarr version: {zarr.__version__}")
print(f"Zarr major version: {zarr_version_major}")

# Test the skip condition
skip_condition = zarr_version_major < 3
print(f"Skip condition (zarr_version_major < 3): {skip_condition}")

if skip_condition:
    print("❌ Tests would be SKIPPED (zarr-python < 3)")
else:
    print("✅ Tests would RUN (zarr-python >= 3)")

# Test the function logic
try:
    from ngff_zarr.from_ngff_zarr import from_ngff_zarr
    
    # Test with a non-URL store (should work regardless)
    test_store = {}
    print(f"Function signature includes storage_options: {'storage_options' in str(from_ngff_zarr.__code__.co_varnames)}")
    
    # Try to call with storage_options=None (should work)
    try:
        # This will fail due to missing metadata, but should accept the parameter
        from_ngff_zarr(test_store, storage_options=None)
    except Exception as e:
        if "storage_options" in str(e):
            print("❌ storage_options parameter not accepted")
        else:
            print("✅ storage_options parameter accepted (failed for other reasons)")
    
except Exception as e:
    print(f"Error importing or testing function: {e}")
