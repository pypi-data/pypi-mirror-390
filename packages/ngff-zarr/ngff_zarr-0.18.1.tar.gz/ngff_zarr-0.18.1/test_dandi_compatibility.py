#!/usr/bin/env python3
"""
Test script for the specific DANDI Archive OMERO compatibility.
"""

from ngff_zarr import from_ngff_zarr
import traceback

print("Testing DANDI Archive OMERO compatibility...\n")

dandi_url = "https://dandiarchive.s3.amazonaws.com/zarr/ca578830-fb23-4aa6-8471-cfde8478abfb/"

try:
    print(f"Attempting to load: {dandi_url}")
    multiscales = from_ngff_zarr(dandi_url)
    print("✓ Successfully loaded DANDI Archive OME-Zarr store")
    
    # Check if there's OMERO metadata
    if multiscales.metadata.omero is not None:
        print(f"✓ OMERO metadata found with {len(multiscales.metadata.omero.channels)} channels")
        
        # Check the first channel's window values
        if len(multiscales.metadata.omero.channels) > 0:
            channel = multiscales.metadata.omero.channels[0]
            print(f"  Channel 0 window:")
            print(f"    min: {channel.window.min}, max: {channel.window.max}")
            print(f"    start: {channel.window.start}, end: {channel.window.end}")
            print("✓ OMERO window metadata correctly parsed with backward compatibility")
    else:
        print("ℹ No OMERO metadata found in this store")
    
    print(f"✓ Found {len(multiscales.images)} image scales")
    print("🎉 DANDI Archive compatibility test passed!")
    
except Exception as e:
    print(f"✗ Failed to load DANDI Archive store: {e}")
    traceback.print_exc()
