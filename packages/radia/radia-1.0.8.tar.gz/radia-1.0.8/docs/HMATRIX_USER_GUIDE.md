# H-Matrix Field Acceleration - User Guide

**For Radia Users**
**Version:** 1.1.0
**Date:** 2025-11-09

---

## Overview

H-matrix acceleration can speed up field evaluation by **2-50×** for large problems (N > 100 elements, M > 100 observation points). This guide shows how to use it correctly for both **speed AND accuracy**.

---

## Quick Start

### Basic Usage (with Accuracy)

```python
import radia as rad
import numpy as np

# 1. Create magnetic elements
magnet1 = rad.ObjRecMag([0, 0, 0], [20, 20, 30], [0, 0, 1.0])
magnet2 = rad.ObjRecMag([50, 0, 0], [20, 20, 30], [0, 0, 1.0])

# 2. ✅ IMPORTANT: Subdivide for accuracy
magnet1_div = rad.ObjDivMag(magnet1, [3, 3, 3])  # 27 sub-elements
magnet2_div = rad.ObjDivMag(magnet2, [3, 3, 3])

# 3. Build geometry
geometry = rad.ObjCnt([magnet1_div, magnet2_div])

# 4. Enable H-matrix acceleration
rad.SetHMatrixFieldEval(1, 1e-6)  # enable=1, tolerance=1e-6

# 5. Evaluate field at multiple points (batch mode)
obs_points = [[x, y, 50] for x in np.linspace(0, 100, 200)
                          for y in np.linspace(0, 100, 200)]

# Use H-matrix (fast and accurate)
H_field = rad.FldBatch(geometry, 'h', obs_points, use_hmatrix=1)
B_field = rad.FldBatch(geometry, 'b', obs_points, use_hmatrix=1)
```

**Result:**
- ✅ Speedup: 5-20× faster than direct calculation
- ✅ Accuracy: < 1% error with proper subdivision

---

## Why Subdivision is Important

### The Problem: Point Dipole Approximation

H-matrix uses magnetic dipole formula:

```
H(r) = (1/4π) * [3(m·r̂)r̂ - m] / |r|³
```

This is **exact** for point sources but **approximate** for finite-sized elements.

### Without Subdivision ❌

```python
# DON'T DO THIS for accurate results
magnet = rad.ObjRecMag([0,0,0], [20,20,30], [0,0,1.0])  # Single large element
geometry = rad.ObjCnt([magnet])
rad.SetHMatrixFieldEval(1, 1e-6)
H = rad.FldBatch(geometry, 'h', [[30,0,0]], 1)  # ❌ 20-30% error!
```

**Problem:** Large element treated as single point dipole → large approximation error

### With Subdivision ✅

```python
# DO THIS for accurate results
magnet = rad.ObjRecMag([0,0,0], [20,20,30], [0,0,1.0])
magnet_div = rad.ObjDivMag(magnet, [3,3,3])  # ✅ 27 smaller elements
geometry = rad.ObjCnt([magnet_div])
rad.SetHMatrixFieldEval(1, 1e-6)
H = rad.FldBatch(geometry, 'h', [[30,0,0]], 1)  # ✅ < 1% error!
```

**Solution:** Sub-elements are smaller → better point approximation → accurate results

---

## Subdivision Guidelines

### Rule of Thumb

```
sub_element_size ≈ min_distance_to_obs / 5
```

Where:
- `sub_element_size` = element_size / k (for k×k×k subdivision)
- `min_distance_to_obs` = closest distance from element to observation points

### Practical Guidelines

| Scenario | Subdivision | Example |
|----------|-------------|---------|
| **Close-range** (dist < 3× size) | `[5,5,5]` or finer | Field inside a gap between magnets |
| **Medium-range** (dist ≈ 5-10× size) | `[3,3,3]` | Field in working area of a device |
| **Far-field** (dist > 20× size) | `[2,2,2]` or none | Field mapping at large distance |

### Example: Quadrupole Magnet

```python
# Quadrupole with 4 poles, each 40mm × 40mm × 100mm
# Observation points in center region (20mm from poles)

pole_size = [40, 40, 100]
min_distance = 20  # mm from pole center to obs. points

# Calculate subdivision
# Want sub_element_size ≈ 20/5 = 4mm
# pole_size / k = 4mm → k = 40/4 = 10

k = 5  # Use 5 for efficiency (creates 5³=125 sub-elements per pole)

pole1 = rad.ObjRecMag([30, 0, 0], pole_size, [1, 0, 0])
pole1_div = rad.ObjDivMag(pole1, [k, k, k])

# ... repeat for other poles ...

geometry = rad.ObjCnt([pole1_div, pole2_div, pole3_div, pole4_div])
rad.SetHMatrixFieldEval(1, 1e-6)

# Accurate field evaluation
obs_points = [[x, y, 0] for x in np.linspace(-10, 10, 100)
                         for y in np.linspace(-10, 10, 100)]
H = rad.FldBatch(geometry, 'h', obs_points, 1)
```

---

## Performance Considerations

### Memory Usage

| Configuration | Elements | Source Points | Memory (approx) |
|---------------|----------|---------------|-----------------|
| No subdivision | 100 | 100 | ~1 MB |
| `[2,2,2]` subdivision | 100 | 800 | ~5 MB |
| `[3,3,3]` subdivision | 100 | 2,700 | ~15 MB |
| `[5,5,5]` subdivision | 100 | 12,500 | ~60 MB |

### Speedup vs Subdivision Trade-off

Finer subdivision → More source points → Lower speedup

```python
# Example: N=100 elements, M=1000 observation points

# No subdivision:
#   N=100 sources → Speedup ≈ 15×, Accuracy ≈ 70% (bad)

# [3,3,3] subdivision:
#   N=2700 sources → Speedup ≈ 5×, Accuracy ≈ 99% (good)

# [5,5,5] subdivision:
#   N=12500 sources → Speedup ≈ 2×, Accuracy ≈ 99.9% (excellent)
```

**Recommendation:** Use `[3,3,3]` subdivision as default - good balance of speed and accuracy.

---

## When to Use H-Matrix

### ✅ Good Use Cases

1. **Field mapping** with many observation points (M > 100)
   ```python
   # 100×100 grid = 10,000 points
   obs_grid = [[x, y, z0] for x in linspace() for y in linspace()]
   # H-matrix: 10-50× faster
   ```

2. **Iterative optimization** where geometry is fixed
   ```python
   # Build H-matrix once
   rad.SetHMatrixFieldEval(1, 1e-6)

   # Evaluate many times with different observation points
   for scan_position in scan_positions:
       H = rad.FldBatch(geometry, 'h', [scan_position], 1)  # Fast!
   ```

3. **Large assemblies** (N > 100 elements)
   ```python
   # 200 magnets, each subdivided 3×3×3
   # N = 200 × 27 = 5,400 sources
   # M = 1,000 observation points
   # Speedup: 10-20×
   ```

### ❌ Poor Use Cases

1. **Small problems** (N < 50, M < 50)
   - Direct calculation is already fast
   - H-matrix overhead not worth it

2. **Single-point evaluation**
   - Use `rad.Fld(obj, 'h', [x,y,z])` instead
   - H-matrix is for batch evaluation only

3. **Very fine subdivision required** (> `[7,7,7]`)
   - Too many source points → no speedup
   - Consider direct calculation or coarser subdivision

---

## Advanced Configuration

### H-Matrix Parameters

```python
rad.SetHMatrixFieldEval(
    enable,        # 1=enable, 0=disable
    tolerance,     # ACA tolerance (default: 1e-6)
    min_cluster_size=10,   # Optional: minimum cluster size
    use_openmp=1           # Optional: enable parallelization
)
```

**Tolerance:** Controls accuracy vs memory trade-off
- `1e-4`: Faster build, less memory, slightly lower accuracy
- `1e-6`: **Recommended default**
- `1e-8`: Slower build, more memory, highest accuracy

### Adaptive Subdivision Example

```python
def subdivide_smart(element, obs_points):
    """Automatically determine subdivision level."""
    element_size = np.max(element.size)

    # Find closest observation point
    min_dist = min(np.linalg.norm(np.array(pt) - np.array(element.center))
                   for pt in obs_points)

    # Calculate subdivision
    ratio = min_dist / element_size

    if ratio < 3:
        k = 5  # Close range - fine subdivision
    elif ratio < 10:
        k = 3  # Medium range - default subdivision
    elif ratio < 20:
        k = 2  # Far range - coarse subdivision
    else:
        k = 1  # Very far - no subdivision

    return rad.ObjDivMag(element, [k, k, k]) if k > 1 else element
```

---

## Troubleshooting

### Issue 1: Large Errors (> 10%)

**Cause:** Elements not subdivided or insufficient subdivision

**Solution:**
```python
# Check log output
# Should see: "Extracted N source points (including sub-elements)"
# If N ≈ number of elements → no subdivision!

# Fix: Add subdivision
magnet_div = rad.ObjDivMag(magnet, [3,3,3])
```

### Issue 2: Slow Performance (No Speedup)

**Cause:** Too many source points from excessive subdivision

**Solution:**
```python
# Reduce subdivision level
# Change [5,5,5] → [3,3,3]
# Or use H-matrix only for large M (> 1000 obs. points)
```

### Issue 3: High Memory Usage

**Cause:** Large N × M matrix

**Solution:**
```python
# Option 1: Reduce subdivision
magnet_div = rad.ObjDivMag(magnet, [2,2,2])  # Instead of [5,5,5]

# Option 2: Increase tolerance
rad.SetHMatrixFieldEval(1, 1e-4)  # Instead of 1e-6

# Option 3: Process observation points in batches
for batch in split_into_batches(obs_points, batch_size=1000):
    H_batch = rad.FldBatch(geometry, 'h', batch, 1)
```

---

## Complete Example

```python
#!/usr/bin/env python
"""
H-Matrix Field Evaluation - Complete Example

Demonstrates proper usage for accurate and fast field computation.
"""

import radia as rad
import numpy as np
import matplotlib.pyplot as plt

# 1. Create geometry
print("[1] Creating geometry...")

# Permanent magnet array (5×5 grid)
magnets = []
L = 10  # mm
gap = 5  # mm
M = 1.2  # T

for i in range(5):
    for j in range(5):
        x = i * (L + gap)
        y = j * (L + gap)

        # Alternating magnetization pattern
        Mz = M if (i + j) % 2 == 0 else -M

        magnet = rad.ObjRecMag([x, y, 0], [L, L, L], [0, 0, Mz])

        # ✅ SUBDIVIDE for accuracy
        magnet_div = rad.ObjDivMag(magnet, [3, 3, 3])
        magnets.append(magnet_div)

geometry = rad.ObjCnt(magnets)
print(f"  Created {len(magnets)} magnets, each subdivided 3×3×3")
print(f"  Total source points: {len(magnets) * 27}")

# 2. Enable H-matrix
print("[2] Enabling H-matrix acceleration...")
rad.SetHMatrixFieldEval(1, 1e-6)

# 3. Define observation points (field mapping above array)
print("[3] Creating observation grid...")
z0 = 20  # mm above array
x_range = np.linspace(-5, 60, 100)
y_range = np.linspace(-5, 60, 100)

obs_points = [[x, y, z0] for x in x_range for y in y_range]
print(f"  {len(obs_points)} observation points")

# 4. Compute field
print("[4] Computing field...")
import time

# H-matrix evaluation
t0 = time.time()
B_hmatrix = rad.FldBatch(geometry, 'b', obs_points, use_hmatrix=1)
t_hmatrix = time.time() - t0
print(f"  H-matrix time: {t_hmatrix*1000:.2f} ms")

# Direct evaluation (for comparison)
t0 = time.time()
B_direct = rad.FldBatch(geometry, 'b', obs_points, use_hmatrix=0)
t_direct = time.time() - t0
print(f"  Direct time: {t_direct*1000:.2f} ms")
print(f"  Speedup: {t_direct/t_hmatrix:.2f}×")

# 5. Check accuracy
B_hmatrix = np.array(B_hmatrix)
B_direct = np.array(B_direct)
error = np.linalg.norm(B_hmatrix - B_direct, axis=1) / np.linalg.norm(B_direct, axis=1)
rms_error = np.sqrt(np.mean(error**2))
print(f"  RMS error: {rms_error*100:.2f}%")

# 6. Visualize
print("[5] Plotting results...")
Bz_hmat = B_hmatrix[:, 2].reshape(len(x_range), len(y_range))

plt.figure(figsize=(10, 8))
plt.contourf(x_range, y_range, Bz_hmat.T, levels=50, cmap='RdBu_r')
plt.colorbar(label='Bz (T)')
plt.title(f'Magnetic Field Map (H-matrix, {rms_error*100:.2f}% error, {t_direct/t_hmatrix:.1f}× speedup)')
plt.xlabel('x (mm)')
plt.ylabel('y (mm)')
plt.axis('equal')
plt.grid(True, alpha=0.3)
plt.savefig('hmatrix_field_map.png', dpi=150)
print("  Saved: hmatrix_field_map.png")

print("\n✅ Complete!")
print(f"   Speedup: {t_direct/t_hmatrix:.2f}×")
print(f"   Accuracy: {(1-rms_error)*100:.1f}%")
```

---

## Summary

### Key Points

1. ✅ **Always subdivide** elements using `rad.ObjDivMag()` before H-matrix
2. ✅ Use `[3,3,3]` subdivision as default (good balance)
3. ✅ H-matrix is for **batch evaluation** (many observation points)
4. ✅ Expected speedup: 2-50× depending on problem size
5. ✅ Expected accuracy: < 1% error with proper subdivision

### Recommended Workflow

```
Create elements → Subdivide [3,3,3] → Build geometry →
Enable H-matrix → Batch field evaluation → Profit!
```

---

**Questions?** See `docs/hmatrix_field_accuracy_solution.md` for technical details.

**Author:** Radia Development Team
**Last Updated:** 2025-11-09
