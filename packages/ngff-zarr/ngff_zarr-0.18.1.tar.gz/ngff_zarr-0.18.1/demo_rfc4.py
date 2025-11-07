#!/usr/bin/env python3
"""Demo script for RFC 4 anatomical orientation support in ngff-zarr."""

import numpy as np
import tempfile
from pathlib import Path

from ngff_zarr import NgffImage, to_multiscales, to_ngff_zarr
from ngff_zarr.rfc4 import AnatomicalOrientation, AnatomicalOrientationValues


def demo_rfc4_anatomical_orientation():
    """Demonstrate RFC 4 anatomical orientation functionality."""
    print("🧠 RFC 4 Anatomical Orientation Demo")
    print("=" * 40)
    
    # Create a simple 3D medical image volume (50x60x70 voxels)
    print("1. Creating 3D medical image volume...")
    data = np.random.rand(50, 60, 70).astype(np.float32)
    print(f"   Volume shape: {data.shape} (z, y, x)")
    
    # Define anatomical orientations for medical imaging (LPS coordinate system)
    print("\n2. Defining anatomical orientations (LPS coordinate system)...")
    orientations = {
        'x': AnatomicalOrientation(value=AnatomicalOrientationValues.left_to_right),
        'y': AnatomicalOrientation(value=AnatomicalOrientationValues.posterior_to_anterior),
        'z': AnatomicalOrientation(value=AnatomicalOrientationValues.inferior_to_superior),
    }
    
    for axis, orientation in orientations.items():
        print(f"   {axis}-axis: {orientation.value.value}")
    
    # Create NgffImage with spatial metadata and anatomical orientations
    print("\n3. Creating NgffImage with anatomical orientation metadata...")
    ngff_image = NgffImage(
        data=data,
        dims=('z', 'y', 'x'),
        scale={'x': 0.5, 'y': 0.5, 'z': 1.0},  # 0.5mm x 0.5mm x 1.0mm voxels
        translation={'x': 0.0, 'y': 0.0, 'z': 0.0},
        axes_units={'x': 'millimeter', 'y': 'millimeter', 'z': 'millimeter'},
        axes_orientations=orientations
    )
    print(f"   Created NgffImage with {len(orientations)} spatial axes with orientation")
    
    # Convert to multiscales for multi-resolution pyramid
    print("\n4. Converting to multiscales pyramid...")
    multiscales = to_multiscales(ngff_image, scale_factors=[1, 2, 4])
    print(f"   Created pyramid with {len(multiscales.images)} resolution levels")
    
    # Demonstrate with RFC 4 enabled
    print("\n5. Writing to OME-Zarr with RFC 4 ENABLED...")
    with tempfile.TemporaryDirectory() as temp_dir:
        store_path_rfc4 = Path(temp_dir) / "medical_image_rfc4.ome.zarr"
        
        to_ngff_zarr(
            store=str(store_path_rfc4),
            multiscales=multiscales,
            enabled_rfcs=[4],  # Enable RFC 4
            version="0.4"
        )
        
        # Read back and inspect metadata
        import zarr
        zarr_group = zarr.open(str(store_path_rfc4), mode='r')
        multiscales_metadata = zarr_group.attrs['multiscales'][0]
        
        print("   ✅ RFC 4 enabled - orientation metadata preserved:")
        for axis in multiscales_metadata['axes']:
            if 'orientation' in axis:
                print(f"     {axis['name']}-axis: {axis['orientation']['value']}")
        
        # Demonstrate with RFC 4 disabled (default)
        print("\n6. Writing to OME-Zarr with RFC 4 DISABLED (default)...")
        store_path_standard = Path(temp_dir) / "medical_image_standard.ome.zarr"
        
        to_ngff_zarr(
            store=str(store_path_standard),
            multiscales=multiscales,
            # enabled_rfcs not specified, so RFC 4 is disabled
            version="0.4"
        )
        
        # Read back and inspect metadata
        zarr_group_standard = zarr.open(str(store_path_standard), mode='r')
        multiscales_metadata_standard = zarr_group_standard.attrs['multiscales'][0]
        
        print("   ✅ RFC 4 disabled - orientation metadata filtered out:")
        axes_with_orientation = [ax for ax in multiscales_metadata_standard['axes'] if 'orientation' in ax]
        if axes_with_orientation:
            print(f"     Found {len(axes_with_orientation)} axes with orientation (unexpected!)")
        else:
            print("     No axes have orientation metadata (as expected)")
    
    print("\n7. Summary:")
    print("   • RFC 4 adds anatomical orientation to spatial axes")
    print("   • When enabled, orientation metadata is preserved in OME-Zarr")
    print("   • When disabled, orientation metadata is filtered out for compatibility")
    print("   • Perfect for medical imaging workflows with ITK/SimpleITK!")
    
    print("\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    demo_rfc4_anatomical_orientation()
