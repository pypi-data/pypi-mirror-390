#!/usr/bin/env python
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'build', 'Release'))

import radia as rad

print("Step 1: Creating geometry")
b = rad.ObjRecMag([0,0,0], [10,10,10])
g = rad.ObjCnt([b])
rad.ObjDivMag(b, [2,2,2])
rad.MatApl(g, rad.MatStd('NdFeB', 1000))
print(f"  Created: block={b}, group={g}")

print("\nStep 2: Creating 100 observation points")
pts = [[20+i*0.1, 0, 0] for i in range(100)]
print(f"  Created {len(pts)} points")

print("\nStep 3: Enabling H-matrix")
rad.SetHMatrixFieldEval(1, 1e-6)
print("  Enabled")

print("\nStep 4: Computing field (builds H-matrix)")
print("  Calling FldBatch...")
sys.stdout.flush()
try:
	B1 = rad.FldBatch(g, 'bz', pts, use_hmatrix=1)
	print(f"  Success: got {len(B1) if isinstance(B1, list) else 1} values")
except Exception as e:
	print(f"  ERROR: {e}")
	import traceback
	traceback.print_exc()
	sys.exit(1)

print("\nStep 5: Changing magnetization")
rad.MatApl(g, rad.MatLin([1,1,1], [500,0,866]))
print("  Changed")

print("\nStep 6: Calling UpdateHMatrixMagnetization")
sys.stdout.flush()
try:
	rad.UpdateHMatrixMagnetization(g)
	print("  SUCCESS!")
except Exception as e:
	print(f"  ERROR: {e}")
	import traceback
	traceback.print_exc()
	sys.exit(1)

print("\nAll steps completed!")
