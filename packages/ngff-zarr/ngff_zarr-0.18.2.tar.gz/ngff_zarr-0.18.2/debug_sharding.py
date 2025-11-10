#!/usr/bin/env python
# SPDX-FileCopyrightText: Copyright (c) Fideus Labs LLC
# SPDX-License-Identifier: MIT

import numpy as np
from ngff_zarr import to_ngff_image, to_multiscales, to_ngff_zarr, config
from zarr.storage import MemoryStore
import dask.array as da
from dask_image import imread
import tempfile
import sys

# Get test data path from command line or use default
if len(sys.argv) > 1:
    test_data_path = sys.argv[1]
else:
    # Use a simple test case
    test_data_path = None

# Simulate the test case
default_mem_target = config.memory_target
config.memory_target = int(1e6)

print(f"Memory target set to: {config.memory_target}")

if test_data_path:
    # Use real test data
    print(f"Loading test data from: {test_data_path}")
    data = imread.imread(test_data_path)
    print(f"Loaded data shape: {data.shape}, chunks: {data.chunks}")
    image = to_ngff_image(
        data=data,
        dims=("z", "y", "x"),
        scale={"z": 2.5, "y": 1.40625, "x": 1.40625},
        translation={"z": 332.5, "y": 360.0, "x": 0.0},
        name="LIDC2",
    )
else:
    # Create a simple test array with shape similar to lung_series
    print("Creating synthetic test data")
    data = da.from_array(np.zeros((133, 256, 256), dtype=np.uint8), chunks=(128, 128, 128))
    image = to_ngff_image(
        data=data,
        dims=("z", "y", "x"),
        scale={"z": 2.5, "y": 1.40625, "x": 1.40625},
        translation={"z": 332.5, "y": 360.0, "x": 0.0},
        name="LIDC2",
    )

print(f"Original image shape: {image.data.shape}")
print(f"Original image chunks: {image.data.chunks}")

print("Creating multiscales...")
multiscales = to_multiscales(image)
print(f"Multiscales created with {len(multiscales.images)} scales")
for i, img in enumerate(multiscales.images):
    print(f"  Scale {i}: shape={img.data.shape}, chunks={img.data.chunks}")

# Try to write with sharding
test_store = MemoryStore()
chunks_per_shard = 1

print(f"\nWriting to zarr with chunks_per_shard={chunks_per_shard}...")
try:
    to_ngff_zarr(
        test_store, multiscales, version="0.5", chunks_per_shard=chunks_per_shard
    )
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

config.memory_target = default_mem_target
