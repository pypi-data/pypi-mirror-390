#!/usr/bin/env python3

import numpy as np
import nibabel as nib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from ngff_zarr.nibabel_image_to_ngff_image import nibabel_image_to_ngff_image

def test_scaling_fix():
    print("Testing scaling fix...")

    # Test slope-only scaling
    print("\n1. Testing slope-only scaling:")
    data = np.random.randint(0, 100, size=(10, 10, 10), dtype=np.uint8)
    affine = np.eye(4)
    img = nib.Nifti1Image(data, affine)

    # Set slope only
    img.header['scl_slope'] = 0.5
    img.header['scl_inter'] = 0.0

    # Our conversion
    ngff_image = nibabel_image_to_ngff_image(img)

    # Reference (what nibabel produces)
    reference = img.get_fdata(dtype=np.float32)

    print(f"  Data dtype: {ngff_image.data.dtype}")
    print(f"  Reference dtype: {reference.dtype}")
    print(f"  Arrays equal: {np.array_equal(ngff_image.data, reference)}")
    print(f"  Max diff: {np.max(np.abs(ngff_image.data - reference))}")

    # Test intercept-only scaling
    print("\n2. Testing intercept-only scaling:")
    data2 = np.random.randint(0, 100, size=(10, 10, 10), dtype=np.uint8)
    img2 = nib.Nifti1Image(data2, affine)

    # Set intercept only
    img2.header['scl_slope'] = 1.0
    img2.header['scl_inter'] = 5.0

    # Our conversion
    ngff_image2 = nibabel_image_to_ngff_image(img2)

    # Reference (what nibabel produces)
    reference2 = img2.get_fdata(dtype=np.float32)

    print(f"  Data dtype: {ngff_image2.data.dtype}")
    print(f"  Reference dtype: {reference2.dtype}")
    print(f"  Arrays equal: {np.array_equal(ngff_image2.data, reference2)}")
    print(f"  Max diff: {np.max(np.abs(ngff_image2.data - reference2))}")

    # Verify the fix worked
    success = (np.array_equal(ngff_image.data, reference) and
               np.array_equal(ngff_image2.data, reference2))

    if success:
        print("\n✅ All scaling tests passed! The fix works correctly.")
    else:
        print("\n❌ Scaling tests failed.")

    return success

if __name__ == "__main__":
    try:
        success = test_scaling_fix()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)