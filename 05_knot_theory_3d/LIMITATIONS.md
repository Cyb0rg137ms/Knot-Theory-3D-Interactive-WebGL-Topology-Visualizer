"""
LIMITATIONS.md — Knot Theory 3D
==============================

# Known Limitations and Future Work

## Invariant Computations

### 1. Incomplete Invariants (Alexander Polynomial)
The Alexander polynomial is an incomplete invariant:
- It cannot distinguish certain distinct knots. For example, it returns $1$ for the Kinoshita-Terasaka knot and the Conway knot, which are both non-trivial knots.
- It is symmetric under mirroring ($\Delta(t) = \Delta(t^{-1})$), meaning it cannot detect **chirality** (it cannot distinguish a left-handed trefoil from a right-handed trefoil).

The **Jones polynomial** solves the chirality detection issue (as shown in our benchmarks and tests) but is still incomplete.

### 2. Gaussian Elimination Matrix Determinant
Our Alexander matrix determinant calculation uses a standard numerical Gaussian elimination.
- For very large matrices (complex knots with crossing number $C > 100$), floating-point errors accumulate.
- Production knot tools compute the determinant symbolically over Laurent polynomial rings using fraction-free elimination (e.g. Bareiss algorithm) or modular arithmetic.

---

## Topology (Gauss Code & Reidemeister)

### 1. Simple Reidemeister I Move
Our `apply_reidemeister_1` only detects type I moves where the same crossing occurs consecutively on the strand.
- It does not support type II (sliding two strands apart) or type III (triangle slides).
- Determining if two Gauss codes represent the same knot is an NP-hard problem. Without full Reidemeister move matching (which requires backtracking search), we cannot prove knot equivalence in general.

### 2. Manual Crossing Signs
In our `GaussCode` model, signs of crossing nodes are declared manually. Real knot diagram editors compute these signs automatically from the strand direction cross-products (right-hand rule).
"""
