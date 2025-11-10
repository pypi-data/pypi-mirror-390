import sys
sys.path.insert(0, '.')

import nibabel as nib
from ngff_zarr import nibabel_image_to_ngff_image
from test._data import test_data_dir

print('=== AIL.nii.gz ===')
ail_path = test_data_dir / "input" / "AIL.nii.gz"
ail_img = nib.load(str(ail_path))
ail_ngff = nibabel_image_to_ngff_image(ail_img, add_anatomical_orientation=True)
print(f'AIL axes_orientations: {ail_ngff.axes_orientations}')
if ail_ngff.axes_orientations:
    for dim, orientation in ail_ngff.axes_orientations.items():
        print(f'  {dim}: {orientation.value}')

print()
print('=== RIP.nii.gz ===')
rip_path = test_data_dir / "input" / "RIP.nii.gz"
rip_img = nib.load(str(rip_path))
rip_ngff = nibabel_image_to_ngff_image(rip_img, add_anatomical_orientation=True)
print(f'RIP axes_orientations: {rip_ngff.axes_orientations}')
if rip_ngff.axes_orientations:
    for dim, orientation in rip_ngff.axes_orientations.items():
        print(f'  {dim}: {orientation.value}')
