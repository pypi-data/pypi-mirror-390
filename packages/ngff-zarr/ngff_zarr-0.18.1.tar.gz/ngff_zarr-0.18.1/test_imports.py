#!/usr/bin/env python3

import sys
print('Python:', sys.executable)

try:
    import zarr
    print('zarr version:', zarr.__version__)
except Exception as e:
    print('zarr failed:', e)

try:
    from ngff_zarr.hcs import HCSPlate
    print('HCSPlate import works')
except Exception as e:
    print('HCSPlate import failed:', e)

try:
    from ngff_zarr.v04.zarr_metadata import Plate
    print('Plate import works')
except Exception as e:
    print('Plate import failed:', e)
