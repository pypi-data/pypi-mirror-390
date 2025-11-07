#!/usr/bin/env python3
"""
Verify the HCS cache implementation is working correctly.
"""

import ngff_zarr as nz

print("✓ Successfully imported ngff_zarr")

# Check cache configuration
print(f"✓ HCS well cache size: {nz.config.hcs_well_cache_size}")
print(f"✓ HCS image cache size: {nz.config.hcs_image_cache_size}")

# Check HCS module imports
from ngff_zarr.hcs import from_hcs_zarr, LRUCache, HCSPlate, HCSWell
print("✓ Successfully imported HCS classes")

# Quick test of LRU cache
cache = LRUCache(max_size=2)
cache["a"] = 1
cache["b"] = 2
cache["c"] = 3  # Should evict "a"

assert "a" not in cache
assert "b" in cache
assert "c" in cache
print("✓ LRU cache working correctly")

print("\n🎉 All HCS cache functionality verified!")
