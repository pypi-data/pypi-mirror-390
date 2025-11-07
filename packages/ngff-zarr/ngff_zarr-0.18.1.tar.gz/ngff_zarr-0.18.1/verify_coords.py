#!/usr/bin/env python3
from ngff_zarr.rfc4 import LPS, RAS

print('LPS coordinate system:')
for axis, orientation in LPS.items():
    print(f'  {axis}: {orientation.value.value}')

print()
print('RAS coordinate system:')  
for axis, orientation in RAS.items():
    print(f'  {axis}: {orientation.value.value}')
