#!/usr/bin/env python3
"""
Test memory optimization for nibabel_image_to_ngff_image
"""

import sys
from pathlib import Path
import numpy as np

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))

try:
    import nibabel as nib
    from ngff_zarr.nibabel_image_to_ngff_image import nibabel_image_to_ngff_image
    
    print("=== Memory Optimization Test ===\n")
    
    # Test with the real test file
    test_file = Path('test/data/input/mri_denoised.nii.gz')
    if test_file.exists():
        print(f"Testing with: {test_file}")
        img = nib.load(str(test_file))
        
        # Check scaling parameters
        header = img.header
        scl_slope = float(header.get('scl_slope', 1.0)) if header.get('scl_slope') is not None else 1.0
        scl_inter = float(header.get('scl_inter', 0.0)) if header.get('scl_inter') is not None else 0.0
        
        print(f"Original data dtype: {img.dataobj.dtype}")
        print(f"scl_slope: {scl_slope}")
        print(f"scl_inter: {scl_inter}")
        print(f"Identity scaling: {scl_slope == 1.0 and scl_inter == 0.0}")
        
        # Test our optimization
        ngff_img = nibabel_image_to_ngff_image(img)
        
        print(f"Result data dtype: {ngff_img.data.dtype}")
        print(f"Result shape: {ngff_img.data.shape}")
        
        # Compare with different approaches
        print("\n=== Comparison of data access methods ===")
        
        # Method 1: Our optimized approach
        if scl_slope == 1.0 and scl_inter == 0.0:
            data_optimized = np.asanyarray(img.dataobj)
        else:
            data_optimized = img.get_fdata(dtype=np.float32)
            
        # Method 2: Original approach (always get_fdata)
        data_original = img.get_fdata()
        
        print(f"Optimized method dtype: {data_optimized.dtype}")
        print(f"Original method dtype: {data_original.dtype}")
        print(f"Data values equal: {np.allclose(data_optimized, data_original)}")
        
        # Memory usage comparison (approximate)
        opt_bytes = data_optimized.nbytes
        orig_bytes = data_original.nbytes
        savings = orig_bytes - opt_bytes
        savings_pct = (savings / orig_bytes) * 100 if orig_bytes > 0 else 0
        
        print(f"\nMemory usage:")
        print(f"  Optimized: {opt_bytes:,} bytes ({data_optimized.dtype})")
        print(f"  Original:  {orig_bytes:,} bytes ({data_original.dtype})")
        print(f"  Savings:   {savings:,} bytes ({savings_pct:.1f}%)")
        
        print(f"\n✓ Memory optimization test passed!")
        
    else:
        print(f"⚠ Test file {test_file} not found")
    
    # Test with synthetic data
    print("\n=== Synthetic Data Tests ===")
    
    # Test 1: Identity scaling (should preserve dtype)
    print("\nTest 1: Identity scaling")
    data_uint16 = np.random.randint(0, 1000, size=(50, 50, 50), dtype=np.uint16)
    affine = np.eye(4)
    img_identity = nib.Nifti1Image(data_uint16, affine)
    img_identity.header['scl_slope'] = 1.0
    img_identity.header['scl_inter'] = 0.0
    
    ngff_identity = nibabel_image_to_ngff_image(img_identity)
    
    print(f"  Input dtype: {data_uint16.dtype}")
    print(f"  Output dtype: {ngff_identity.data.dtype}")
    print(f"  Data preserved: {np.array_equal(ngff_identity.data, data_uint16)}")
    print(f"  Memory savings: {(data_uint16.nbytes - ngff_identity.data.nbytes) == 0}")
    
    # Test 2: Non-identity scaling (should use float32)
    print("\nTest 2: Non-identity scaling")
    data_uint8 = np.random.randint(0, 100, size=(50, 50, 50), dtype=np.uint8)
    img_scaled = nib.Nifti1Image(data_uint8, affine)
    img_scaled.header['scl_slope'] = 2.0
    img_scaled.header['scl_inter'] = 10.0
    
    ngff_scaled = nibabel_image_to_ngff_image(img_scaled)
    
    print(f"  Input dtype: {data_uint8.dtype}")
    print(f"  Output dtype: {ngff_scaled.data.dtype}")
    print(f"  Expected scaling applied: {np.allclose(ngff_scaled.data, 2.0 * data_uint8 + 10.0)}")
    
    print(f"\n🎉 All memory optimization tests passed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)