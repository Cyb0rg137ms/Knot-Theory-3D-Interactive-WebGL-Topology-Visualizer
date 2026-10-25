# Architecture (v2)

```mermaid
flowchart LR
    subgraph Inputs
        N[named knot<br/>3_1 … 7_7, T(p,q)] --> T[knotlab.table]
        B[braid word] --> FB[pd.from_braid]
        P[PD code] --> PD
    end
    T --> FB --> PD[knotlab.pd.PD<br/>validate · writhe · mirror]
    PD --> J[knotlab.jones<br/>bracket: tangle contraction]
    PD --> JR[bracket_reference<br/>2^n union-find]
    PD --> JN[bracket_numpy<br/>2^n vectorised]
    PD --> A[knotlab.alexander<br/>Fox matrix + Bareiss over Z t]
    J & JR & JN --> V["V(t) = (−A³)^−w ⟨K⟩"]
    A --> D["Δ(t), det = |Δ(−1)|"]
    V --> X{"|V(−1)| == |Δ(−1)|"}
    D --> X
    G[knotlab.geometry<br/>torus curve, closed-form Δ] --> W[web/ React + three.js viewer<br/>src/lib/torus.ts]
    PD --> GC[topology.gauss / reidemeister<br/>v1 API]
    J --> INV[invariants.jones / alexander<br/>v1 API, now computed]
    A --> INV
```

## Modules

| module | role |
|---|---|
| `knotlab/poly.py` | exact Laurent polynomials over Z (add, mul, pow, exact division, normalisation) |
| `knotlab/pd.py` | PD codes (KnotTheory convention, positive iff `j == l+1 mod 2n`), braid closure → PD, mirror, writhe, components |
| `knotlab/jones.py` | Kauffman bracket three ways and the Jones polynomial |
| `knotlab/alexander.py` | Wirtinger/Fox Alexander matrix, fraction-free Bareiss determinant in Z[t, t⁻¹] |
| `knotlab/table.py` | KnotInfo braid words for all 14 prime knots ≤ 7 crossings + reference determinants, torus braids |
| `knotlab/geometry.py` | vectorised torus-knot curve, closed-form torus Alexander |
| `knotlab/benchmarks.py`, `cli.py` | reproducible benchmark (JSON + PNG) and `knotlab` command |
| `invariants/`, `topology/` | v1 public API kept; values are now computed rather than looked up |
| `web/` | Vite + React Three Fiber viewer; `src/lib/torus.ts` computes Δ for T(p,q) exactly |

## Tangle contraction (default bracket)

Crossings are added one at a time in a greedy order that keeps the open
frontier small. The state is a map *pairing of open edge-ends → polynomial in A*.
Adding a crossing splits each entry into its A- and B-smoothing, merges the two
new arcs into the pairing, and multiplies by `d = −A² − A⁻²` whenever an arc
closes a loop. The number of pairings is bounded by a Catalan number of the
frontier width, so the cost depends on diagram *width*, not 2^n. Narrow
diagrams (3-strand braids) are near-linear in practice; wide diagrams are still
exponential.

## Correctness strategy

No invariant value is hard-coded in the algorithms. Tests check that:
1. Jones/Alexander for 3_1, 4_1, 5_1, 5_2, 6_1, 7_1 equal KnotInfo;
2. for all 14 table knots, |Δ(−1)| (Fox calculus) = |V(−1)| (state sum) = KnotInfo determinant;
3. the three bracket engines agree exactly on the table and on random braids;
4. mirror inverts V, keeps Δ; 4_1 is amphichiral; R1/R2/Markov moves leave V unchanged;
5. torus closed form = Fox calculus; Seifert-matrix path = Fox calculus;
6. the TypeScript closed form matches the Python values (vitest).
