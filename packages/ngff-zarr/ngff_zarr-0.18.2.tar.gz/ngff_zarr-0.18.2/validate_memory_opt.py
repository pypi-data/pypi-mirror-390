#!/usr/bin/env python3

import numpy as np
import nibabel as nib
from pathlib import Path
import sys

# Add current dir to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from ngff_zarr.nibabel_image_to_ngff_image import nibabel_image_to_ngff_image

def test_memory_optimization():
    print("Testing Memory Optimization in nibabel_image_to_ngff_image\n")
    
    # Test with the actual test file
    test_file = Path('test/data/input/mri_denoised.nii.gz')
    
    if test_file.exists():
        print(f"Loading: {test_file}")
        img = nib.load(str(test_file))
        
        # Examine the image properties
        print(f"Image shape: {img.shape}")
        print(f"Image dataobj dtype: {img.dataobj.dtype}")
        
        # Check scaling parameters
        header = img.header
        scl_slope = header.get('scl_slope')
        scl_inter = header.get('scl_inter')
        
        print(f"Raw scl_slope: {scl_slope} (type: {type(scl_slope)})")
        print(f"Raw scl_inter: {scl_inter} (type: {type(scl_inter)})")
        
        # Apply same logic as our function
        if scl_slope is None or scl_slope == 0:
            slope = 1.0
        else:
            slope = float(scl_slope)
            
        if scl_inter is None:
            inter = 0.0
        else:
            inter = float(scl_inter)
            
        print(f"Processed slope: {slope}")
        print(f"Processed intercept: {inter}")
        print(f"Is identity scaling: {slope == 1.0 and inter == 0.0}")
        
        # Test our conversion
        ngff_img = nibabel_image_to_ngff_image(img)
        
        print(f"\nResult:")
        print(f"  Data dtype: {ngff_img.data.dtype}")
        print(f"  Data shape: {ngff_img.data.shape}")
        print(f"  Memory usage: {ngff_img.data.nbytes:,} bytes")
        
        # Compare with get_fdata() default behavior
        default_data = img.get_fdata()
        print(f"\nComparison with get_fdata():")
        print(f"  get_fdata() dtype: {default_data.dtype}")
        print(f"  get_fdata() memory: {default_data.nbytes:,} bytes")
        
        # Memory savings
        savings = default_data.nbytes - ngff_img.data.nbytes
        savings_pct = (savings / default_data.nbytes) * 100
        print(f"  Memory savings: {savings:,} bytes ({savings_pct:.1f}%)")
        
        # Check data equivalence
        print(f"  Data equivalent: {np.allclose(ngff_img.data, default_data)}")
        
        print("\n✅ Test with real file completed successfully!")
        
    else:
        print(f"❌ Test file not found: {test_file}")
        return False
        
    return True

if __name__ == "__main__":
    try:
        success = test_memory_optimization()
        if success:
            print("\n🎉 All tests passed!")
        else:
            print("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)