# NGSolve Integration API Reference

**rad_ngsolve.RadiaField() - Coordinate Transformation Support**

---

## rad_ngsolve.RadiaField ⭐ NGSolve Integration

```python
field_cf = rad_ngsolve.RadiaField(
	radia_obj,
	field_type,
	origin=None,
	u_axis=None,
	v_axis=None,
	w_axis=None
)
```

Creates an NGSolve CoefficientFunction for Radia magnetic field evaluation with optional coordinate transformation.

---

## Parameters

- **`radia_obj`**: Radia object key (from `rad.Obj...()` functions)
- **`field_type`**: Field type selector
  - `'b'`: Magnetic flux density (T)
  - `'h'`: Magnetic field (A/m)
  - `'a'`: Vector potential (T·m)
  - `'m'`: Magnetization (A/m)
- **`origin`**: `[x, y, z]` - Translation of local coordinate system (meters, default: `[0, 0, 0]`)
- **`u_axis`**: `[ux, uy, uz]` - Local x-axis direction in global coordinates (default: `[1, 0, 0]`)
- **`v_axis`**: `[vx, vy, vz]` - Local y-axis direction in global coordinates (default: `[0, 1, 0]`)
- **`w_axis`**: `[wx, wy, wz]` - Local z-axis direction in global coordinates (default: `[0, 0, 1]`)

---

## Returns

NGSolve `CoefficientFunction` for 3D vector field

---

## Coordinate Transformation

The transformation maps between global NGSolve mesh coordinates and local Radia object coordinates:

```
r_local = R^T * (r_global - origin)
F_global = R * F_local(r_local)
```

Where `R = [u_axis | v_axis | w_axis]` is the rotation matrix.

---

## Use Cases

1. **Rotated Magnets**: Define magnets in natural local coordinates, place them at arbitrary orientations
2. **Translated Magnets**: Position magnets offset from global origin
3. **Complex Assemblies**: Combine multiple magnets with different orientations
4. **Rotating Machinery**: Simulate rotors, motors with time-dependent transformations

---

## Examples

### Example 1: Identity Transformation (No rotation)

```python
import radia as rad
from ngsolve import *
import rad_ngsolve

# Create magnet
dipole = rad.ObjRecMag([0, 0, 0], [20, 10, 10], [1.0, 0, 0])

# No transformation - magnet aligned with global axes
A_cf = rad_ngsolve.RadiaField(dipole, 'a')
B_cf = rad_ngsolve.RadiaField(dipole, 'b')

# Use in NGSolve
mesh = Mesh(...)
gf = GridFunction(HCurl(mesh))
gf.Set(A_cf)
```

### Example 2: 45° Rotation Around Z-Axis

```python
import math

# Rotation matrix for 45° around z
cos45 = math.cos(math.radians(45))
sin45 = math.sin(math.radians(45))

u_axis = [cos45, sin45, 0]   # Rotated x-axis
v_axis = [-sin45, cos45, 0]  # Rotated y-axis
w_axis = [0, 0, 1]            # z-axis unchanged

# Create CoefficientFunction with rotation
A_cf_rotated = rad_ngsolve.RadiaField(
	dipole, 'a',
	u_axis=u_axis,
	v_axis=v_axis,
	w_axis=w_axis
)
```

### Example 3: Combined Translation and Rotation

```python
# Translate 10mm, 5mm, 0mm and rotate 30°
origin = [0.010, 0.005, 0.0]  # meters

cos30 = math.cos(math.radians(30))
sin30 = math.sin(math.radians(30))

u_axis = [cos30, sin30, 0]
v_axis = [-sin30, cos30, 0]
w_axis = [0, 0, 1]

A_cf = rad_ngsolve.RadiaField(
	dipole, 'a',
	origin=origin,
	u_axis=u_axis,
	v_axis=v_axis,
	w_axis=w_axis
)
```

### Example 4: Verify curl(A) = B

```python
# With coordinate transformation, curl(A) = B relationship is preserved
curl_A = curl(A_cf_rotated)
B_cf = rad_ngsolve.RadiaField(
	dipole, 'b',
	u_axis=u_axis,
	v_axis=v_axis,
	w_axis=w_axis
)

# At any point in global coordinates:
test_point = mesh(x, y, z)
curl_A_val = curl_A(test_point)
B_val = B_cf(test_point)

# Verify curl(A) = B
import numpy as np
assert np.allclose(curl_A_val, B_val, atol=1e-4)
```

---

## Mathematical Background

### Vector Potential Transformation

For vector potential **A**:
- **A** transforms as a vector: **A**_global = **R** · **A**_local
- Curl operator is invariant under orthogonal transformations
- Therefore: ∇ × **A**_global = **R** · (∇ × **A**_local) = **B**_global

This ensures:
- ∇ × **A** = **B** holds in both coordinate systems
- Field strength and direction are preserved
- Gauge invariance is maintained

### Transformation Matrix

```
R = [u_axis | v_axis | w_axis]

    [ux  vx  wx]
  = [uy  vy  wy]
    [uz  vz  wz]
```

Requirements:
- Orthonormal: `u · v = 0`, `u · w = 0`, `v · w = 0`
- Unit vectors: `|u| = |v| = |w| = 1`
- Right-handed: `w = u × v`

---

## Units

- **Radia** uses millimeters (mm)
- **NGSolve** uses meters (m)
- **Automatic conversion**: Origin and field evaluation points are converted between mm ↔ m
- **Field values** remain in SI units (T, A/m, T·m)

---

## Implementation Notes

- Axes must form orthonormal set: `u · v = 0`, `|u| = |v| = |w| = 1`
- Right-handed coordinate system: `w = u × v`
- Transformation is applied in C++ for performance
- Compatible with all field types ('b', 'h', 'a', 'm')

---

## See Also

- [NGSOLVE_USAGE_GUIDE.md](NGSOLVE_USAGE_GUIDE.md) - Complete NGSolve integration guide
- [`examples/NGSolve_Integration/test_coordinate_transform.py`](../examples/NGSolve_Integration/test_coordinate_transform.py) - Full test examples
- [`examples/NGSolve_Integration/demo_field_types.py`](../examples/NGSolve_Integration/demo_field_types.py) - Field types demonstration

---

**Date**: 2025-11-08
**Maintained By**: Radia Development Team
**License**: LGPL-2.1 (modifications), BSD-style (original RADIA from ESRF)
