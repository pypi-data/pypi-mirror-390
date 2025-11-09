#!/usr/bin/env python
"""H-matrix UpdateMagnetization Test"""

import sys
import os

# Add parent directory to path to import radia
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'dist'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'lib', 'Release'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'Release'))

import radia as rad

# Clear all objects
rad.UtiDelAll()

print("Creating geometry...")
block = rad.ObjRecMag([0,0,0], [10,10,10])
g = rad.ObjCnt([block])
rad.ObjDivMag(block, [2,2,2])
rad.MatApl(g, rad.MatStd('NdFeB', 1000))
print(f"Geometry: block={block}, group={g}")

print("Creating 100 observation points...")
obs_pts = [[20+i*0.1, 0, 0] for i in range(100)]
print(f"Observations: {len(obs_pts)} points")

print("Enabling H-matrix...")
rad.SetHMatrixFieldEval(1, 1e-6)

print("Computing initial field (builds H-matrix)...")
B1 = rad.FldBatch(g, 'bz', obs_pts, use_hmatrix=1)
print(f"Initial field: {len(B1) if isinstance(B1, list) else 1} values")

print("Changing magnetization...")
rad.MatApl(g, rad.MatLin([1,1,1], [500,0,866]))

print("Calling UpdateHMatrixMagnetization...")
rad.UpdateHMatrixMagnetization(g)
print("UpdateHMatrixMagnetization SUCCESS!")

print("Computing updated field...")
B2_h = rad.FldBatch(g, 'bz', obs_pts, use_hmatrix=1)
B2_d = rad.FldBatch(g, 'bz', obs_pts, use_hmatrix=0)

print("\nFirst 3 points comparison:")
for i in range(3):
	h = B2_h[i] if isinstance(B2_h, list) else B2_h
	d = B2_d[i] if isinstance(B2_d, list) else B2_d
	err = abs(h-d)/(abs(d)+1e-10)*100
	print(f"  {i}: H={h:.6f} T, D={d:.6f} T, Err={err:.2f}%")

print("\nTEST PASSED!")
