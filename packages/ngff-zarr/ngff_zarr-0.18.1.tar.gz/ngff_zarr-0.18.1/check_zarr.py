#!/usr/bin/env python3
"""Check zarr version and FsspecStore availability"""

import zarr
import packaging.version

zarr_version = packaging.version.parse(zarr.__version__)
zarr_version_major = zarr_version.major

print(f'Zarr version: {zarr.__version__}')
print(f'Zarr major version: {zarr_version_major}')
print(f'Has FsspecStore: {hasattr(zarr.storage, "FsspecStore") if hasattr(zarr, "storage") else False}')

# Test the version check logic
if zarr_version_major >= 3 and hasattr(zarr.storage, 'FsspecStore'):
    print('✓ FsspecStore available')
else:
    print('✗ FsspecStore not available')
