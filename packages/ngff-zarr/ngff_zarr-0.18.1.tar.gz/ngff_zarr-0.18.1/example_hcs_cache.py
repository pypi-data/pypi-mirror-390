#!/usr/bin/env python3
"""
Example demonstrating HCS cache management.

This script shows how to configure cache sizes for memory-efficient
processing of large HCS plates.
"""

# Configure cache sizes globally
from ngff_zarr.config import config

# Set smaller cache sizes for this example
config.hcs_well_cache_size = 10   # Only cache 10 wells at a time
config.hcs_image_cache_size = 5   # Only cache 5 images per well

# Alternative: Set cache sizes per operation
from ngff_zarr.hcs import from_hcs_zarr

def demo_cache_configuration():
    """Demonstrate different ways to configure cache sizes."""
    
    print("HCS Cache Management Demo")
    print("=" * 50)
    
    # Method 1: Global configuration
    print(f"Default well cache size: {config.hcs_well_cache_size}")
    print(f"Default image cache size: {config.hcs_image_cache_size}")
    
    # Method 2: Per-operation configuration
    # (would use with actual HCS data)
    """
    # Load plate with custom cache sizes
    plate = from_hcs_zarr(
        "path/to/plate.zarr",
        well_cache_size=50,    # Cache up to 50 wells
        image_cache_size=20    # Cache up to 20 images per well
    )
    
    # Access wells and images - caching happens automatically
    well = plate.get_well("A", "01")
    image = well.get_image(0)  # First field of view
    
    # The cache will automatically evict least recently used items
    # when limits are exceeded, preventing memory bloat
    """
    
    print("\nCache Benefits:")
    print("- Prevents memory issues with large plates")
    print("- LRU eviction ensures recently accessed data stays available") 
    print("- Configurable limits for different use cases")
    print("- Automatic management - no manual cache clearing needed")

if __name__ == "__main__":
    demo_cache_configuration()
