#!/usr/bin/env python3
"""
Quick test to verify that LPS/RAS coordinate systems are corrected.
"""

from ngff_zarr.rfc4 import LPS, RAS, itk_lps_to_anatomical_orientation

def test_lps_directions():
    """Test that LPS directions are correct."""
    print("Testing LPS coordinate system:")
    print(f"LPS X (L): {LPS['x']} (should be 'right-to-left')")
    print(f"LPS Y (P): {LPS['y']} (should be 'anterior-to-posterior')")
    print(f"LPS Z (S): {LPS['z']} (should be 'inferior-to-superior')")
    
    assert LPS['x'].value.value == 'right-to-left', f"Expected 'right-to-left', got {LPS['x'].value.value}"
    assert LPS['y'].value.value == 'anterior-to-posterior', f"Expected 'anterior-to-posterior', got {LPS['y'].value.value}"
    assert LPS['z'].value.value == 'inferior-to-superior', f"Expected 'inferior-to-superior', got {LPS['z'].value.value}"
    print("✓ LPS directions are correct\n")

def test_ras_directions():
    """Test that RAS directions are correct."""
    print("Testing RAS coordinate system:")
    print(f"RAS X (R): {RAS['x']} (should be 'left-to-right')")
    print(f"RAS Y (A): {RAS['y']} (should be 'posterior-to-anterior')")
    print(f"RAS Z (S): {RAS['z']} (should be 'inferior-to-superior')")
    
    assert RAS['x'].value.value == 'left-to-right', f"Expected 'left-to-right', got {RAS['x'].value.value}"
    assert RAS['y'].value.value == 'posterior-to-anterior', f"Expected 'posterior-to-anterior', got {RAS['y'].value.value}"
    assert RAS['z'].value.value == 'inferior-to-superior', f"Expected 'inferior-to-superior', got {RAS['z'].value.value}"
    print("✓ RAS directions are correct\n")

def test_itk_lps_mapping():
    """Test that ITK LPS mapping works correctly."""
    print("Testing ITK LPS to anatomical orientation mapping:")
    
    # Test each axis mapping
    x_result = itk_lps_to_anatomical_orientation('x')
    y_result = itk_lps_to_anatomical_orientation('y')
    z_result = itk_lps_to_anatomical_orientation('z')
    
    print(f"ITK LPS X axis: {x_result}")
    print(f"ITK LPS Y axis: {y_result}")
    print(f"ITK LPS Z axis: {z_result}")
    
    assert x_result is not None and x_result.value.value == 'right-to-left', f"Expected 'right-to-left', got {x_result}"
    assert y_result is not None and y_result.value.value == 'anterior-to-posterior', f"Expected 'anterior-to-posterior', got {y_result}"
    assert z_result is not None and z_result.value.value == 'inferior-to-superior', f"Expected 'inferior-to-superior', got {z_result}"
    print("✓ ITK LPS mapping is correct\n")

if __name__ == "__main__":
    test_lps_directions()
    test_ras_directions()
    test_itk_lps_mapping()
    print("🎉 All coordinate system corrections verified!")
