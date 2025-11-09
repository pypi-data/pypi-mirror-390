# H-Matrix Field Evaluation - Accuracy Issue Analysis

**Date**: 2025-11-08
**Status**: Issue Identified, Fix Required

---

## 問題の概要

H-matrix field evaluation の精度が低い（20-30% 相対誤差）。

---

## 根本原因

### 現在の実装

**ExtractSourceGeometry() (radhmat_field.cpp:149-213)**

```cpp
// 各要素を単一の点双極子として扱っている
TVector3d center = g3d->CentrPoint;     // 要素の中心点
double volume = relaxable->Volume();     // 要素全体の体積
TVector3d moment = M * vol_m3;          // 総磁気モーメント

// 結果: 各要素 → 1個のソースポイント
```

### 問題点

Radia の実際の要素構造：
- 各要素（radTg3dRelax）は **subdivision（小要素）** に分割されている
- 例：3×3×3 = 27個の小要素
- 各小要素が独立した磁気モーメントを持つ
- 緩和法では、**各要素内で先に3×3行列を解いている**

現在の H-matrix 実装：
- ❌ 各要素を **単一の点双極子** として扱う
- ❌ Subdivision を完全に無視
- ❌ 要素内部の磁場分布が考慮されない

結果：
- 単一双極子テスト: ✅ 完璧（誤差ゼロ）
- 複数双極子テスト: ❌ 20-30% 誤差

---

## 検証結果

### 単一双極子テスト (test_kernel_accuracy.py)

```
Point                Hx (A/m)        Hy (A/m)        Hz (A/m)        Error
[20, 0, 0]          1.571e-02      -4.910e-03      -9.819e-03       0.00e+00
[0, 20, 0]         -7.855e-03       9.819e-03      -9.819e-03       0.00e+00
[0, 0, 20]         -7.855e-03      -4.910e-03       1.964e-02       0.00e+00

✓ FieldKernel 実装は正しい
```

### 複数双極子ベンチマーク (benchmark_hmatrix.py)

```
N=100, M=100:  相対RMS誤差 = 21.9%
N=200, M=200:  相対RMS誤差 = 24.1%
N=500, M=500:  相対RMS誤差 = 29.8%

✗ Subdivision を考慮していないため誤差が大きい
```

---

## 正しい実装方針

### Option 1: Sub-element レベルでの H-matrix 構築（推奨）

各要素の subdivision を取得し、すべての sub-element を individual source points として扱う。

**擬似コード**:
```cpp
int ExtractSourceGeometry(radTGroup* source_group) {
    for(auto& elem_pair : source_group->GroupMapOfHandlers) {
        radTg3d* g3d = elem_pair.second.rep;

        // Try to get sub-elements
        radTGroup* group = dynamic_cast<radTGroup*>(g3d);
        if(group && group->GroupMapOfHandlers.size() > 0) {
            // Recursively extract sub-elements
            ExtractSourceGeometry(group);
        }
        else {
            // Leaf element - extract as single source
            ExtractSingleElement(g3d);
        }
    }
}
```

**利点**:
- 正確な磁場計算（緩和法と同等）
- 各 sub-element の磁気モーメントを正確に反映

**欠点**:
- ソースポイント数が増加（N × subdivision factor）
- H-matrix サイズ増加
- 構築時間増加

### Option 2: 要素レベルでの積分カーネル

点双極子カーネルの代わりに、有限サイズ要素の積分カーネルを使用。

**積分カーネル**:
```
H(r_obs) = ∫∫∫_V [3(M·r̂)r̂ - M] / (4π|r|³) dV
```

**利点**:
- ソースポイント数は変わらない
- より正確な近距離場

**欠点**:
- カーネル評価が複雑
- 計算コストが高い
- ACA 近似の効率が低下する可能性

---

## 実装の優先順位

### Phase 1: Sub-element 抽出（最優先）

1. **radTGroup の再帰的処理**
   - GroupMapOfHandlers を再帰的に走査
   - すべての leaf elements を抽出

2. **Sub-element 情報の取得**
   - 各 sub-element の中心座標
   - 各 sub-element の磁気モーメント
   - Subdivision 構造の保持

3. **H-matrix 構築**
   - Sub-element 数を N_sub として H-matrix 構築
   - FieldKernel は変更不要（すでに正しい）

### Phase 2: 性能最適化

1. **階層的クラスタリング**
   - 同一要素内の sub-elements を1つのクラスターに
   - 遠方では要素単位で近似
   - 近距離では sub-element 単位で計算

2. **Adaptive subdivision**
   - 観測点が遠い要素は粗い subdivision
   - 観測点が近い要素は細かい subdivision

---

## 推定工数

| タスク | 工数 | 優先度 |
|--------|------|--------|
| Sub-element 抽出実装 | 4-6時間 | 最高 |
| テスト・検証 | 2-3時間 | 高 |
| 性能最適化 | 8-12時間 | 中 |
| ドキュメント作成 | 2時間 | 高 |

**Total**: 16-23時間

---

## 暫定的な対策

精度が重要でない場合の回避策：

1. **要素を細かく subdivision してから H-matrix 構築**
   ```python
   # Python side で事前に subdivision
   magnet = rad.ObjRecMag([0,0,0], [10,10,10], [0,0,1])
   subdivided = rad.ObjDivMag(magnet, [5,5,5])  # 5x5x5 = 125 sub-elements
   group = rad.ObjCnt([subdivided])

   # H-matrix 構築（より正確）
   H = rad.FldBatch(group, 'h', obs_points, use_hmatrix=1)
   ```

2. **大規模問題のみ H-matrix 使用**
   - N < 500: 直接計算（正確）
   - N ≥ 500: H-matrix（高速だが近似）

---

## 関連ファイル

- **実装**: `src/core/radhmat_field.cpp::ExtractSourceGeometry()` (line 149-213)
- **テスト**: `test_kernel_accuracy.py`, `benchmark_hmatrix.py`
- **Issue**: このドキュメント

---

## References

1. **Radia Relaxation Method**
   - 各要素内で 3×3 interaction matrix を先に解く
   - Sub-element レベルでの磁場計算

2. **HACApK Documentation**
   - Adaptive Cross Approximation
   - Point source kernel

3. **Magnetic Dipole Field**
   - H(r) = (1/4π) [3(m·r̂)r̂ - m] / r³
   - Valid for point dipoles

---

**Author**: Radia Development Team
**Last Updated**: 2025-11-08
