#!/usr/bin/env python
"""End-to-end test of RFC4 validation functionality."""

import numpy as np
import dask.array as da
from zarr.storage import MemoryStore
from ngff_zarr import from_ngff_zarr, to_ngff_zarr, to_multiscales
from ngff_zarr.ngff_image import NgffImage
from ngff_zarr.rfc4 import LPS

print('Creating test data with LPS orientation...')
data = np.random.randint(0, 255, size=(10, 20, 30), dtype=np.uint8)
dask_data = da.from_array(data)

ngff_image = NgffImage(
    data=dask_data,
    dims=('z', 'y', 'x'),
    scale={'z': 2.5, 'y': 1.0, 'x': 1.0},
    translation={'z': 0.0, 'y': 0.0, 'x': 0.0},
    name='test_image',
    axes_orientations=LPS
)

print('Converting to multiscales and storing...')
multiscales = to_multiscales(ngff_image)
store = MemoryStore()
to_ngff_zarr(store, multiscales, version='0.4', enabled_rfcs=[4])

print('Reading back with validation enabled...')
multiscales_back = from_ngff_zarr(store, validate=True)

print('✓ RFC4 validation passed successfully!')
print(f'✓ Read back {len(multiscales_back.images)} image(s)')
print('✓ Complete workflow with RFC4 orientation validation works!')
