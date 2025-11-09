#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'dist'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'lib', 'Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'Release'))

import radia as rad

rad.UtiDelAll()

# Step 1
block = rad.ObjRecMag([0,0,0], [10,10,10])
g = rad.ObjCnt([block])
rad.ObjDivMag(block, [2,2,2])
rad.MatApl(g, rad.MatStd('NdFeB', 1000))

# Step 2 - only 2 points (H-matrix won't activate, should use direct)
pts = [[20,0,0], [30,0,0]]
B1 = rad.FldBatch(g, 'bz', pts, use_hmatrix=1)
print(f"Field (2 points): {B1}")

# Step 3 - change magnetization
rad.MatApl(g, rad.MatLin([1,1,1], [500,0,866]))

# Step 4 - compute again
B2 = rad.FldBatch(g, 'bz', pts, use_hmatrix=1)
print(f"Updated field (2 points): {B2}")

print("Test completed successfully!")
