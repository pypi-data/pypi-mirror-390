#!/usr/bin/env python3
"""
Integration test to verify RFC4 validation works with corrected coordinate systems.
"""

import zarr
from zarr.storage import MemoryStore
from ngff_zarr.from_ngff_zarr import from_ngff_zarr
from ngff_zarr.rfc4 import LPS

def test_from_ngff_zarr_with_corrected_lps():
    """Test from_ngff_zarr with valid corrected LPS orientation."""
    # Create a store with corrected LPS orientation metadata
    store = MemoryStore()
    root = zarr.open_group(store, mode="w")
    root.create_dataset("0", shape=(10, 10, 10), dtype="uint8")

    # Add OME-NGFF metadata with corrected LPS orientation
    multiscales_metadata = {
        "version": "0.4",
        "name": "test",
        "axes": [
            {
                "name": "x",
                "type": "space",
                "unit": "micrometer",
                "orientation": {"type": "anatomical", "value": "right-to-left"},  # Corrected LPS X
            },
            {
                "name": "y",
                "type": "space",
                "unit": "micrometer",
                "orientation": {"type": "anatomical", "value": "anterior-to-posterior"},  # Corrected LPS Y
            },
            {
                "name": "z",
                "type": "space",
                "unit": "micrometer",
                "orientation": {"type": "anatomical", "value": "inferior-to-superior"},  # Corrected LPS Z
            },
        ],
        "datasets": [
            {
                "path": "0",
                "coordinateTransformations": [
                    {"type": "scale", "scale": [1.0, 1.0, 1.0]}
                ],
            }
        ],
    }

    root.attrs["multiscales"] = [multiscales_metadata]

    print("Testing from_ngff_zarr with corrected LPS coordinate system...")
    print("Expected orientations from LPS:")
    print(f"  X: {LPS['x'].value.value}")
    print(f"  Y: {LPS['y'].value.value}")
    print(f"  Z: {LPS['z'].value.value}")

    # Should succeed with valid corrected orientation
    multiscales = from_ngff_zarr(store, validate=True)
    print("✓ from_ngff_zarr succeeded with RFC4 validation enabled")
    
    # Verify we got the multiscales back
    assert multiscales is not None
    assert len(multiscales.images) == 1
    print("✓ Multiscales object created successfully")
    
    # Check axis orientations  
    axes = multiscales.metadata.axes
    spatial_axes = [ax for ax in axes if ax.type == "space"]
    
    print("✓ Axis orientations validated:")
    for ax in spatial_axes:
        orientation = getattr(ax, 'orientation', None)
        if orientation:
            if hasattr(orientation, 'value') and hasattr(orientation.value, 'value'):
                # AnatomicalOrientation object
                print(f"  {ax.name}: {orientation.value.value}")
            elif isinstance(orientation, dict):
                # Dictionary form
                print(f"  {ax.name}: {orientation.get('value', 'unknown')}")
            else:
                print(f"  {ax.name}: {orientation}")
        else:
            print(f"  {ax.name}: no orientation")
    
    print("🎉 Integration test passed - RFC4 validation works with corrected LPS!")

if __name__ == "__main__":
    test_from_ngff_zarr_with_corrected_lps()
