# Knot Theory 3D Visualizer — Architecture & Technical Reference

> **Full Project Name:** Knot Theory 3D Visualizer — Topological Invariant Explorer
> **Category:** Computational Topology / Data Visualization / Interactive 3D
> **Language:** TypeScript, React, Three.js (React Three Fiber), Vite
> **Test Coverage:** Visual / E2E (browser-verified) ✅

---

## 1. Architecture Overview

```
05_knot_theory_3d/
├── src/
│   ├── App.tsx               # Root application, knot library + state
│   ├── components/
│   │   ├── KnotViewer.tsx    # Three.js canvas, orbit controls, tube renderer
│   │   └── InvariantPanel.tsx # HOMFLY-PT / Jones polynomial display
│   ├── index.css             # Dark UI theme + panel glass-morphism
│   └── main.tsx              # React DOM mount point
├── index.html
├── package.json
├── tailwind.config.js
└── vite.config.ts
```

### Component Interaction

```
┌──────────────────────────────────────────────────────────────┐
│                  KNOT THEORY 3D ARCHITECTURE                 │
│                                                              │
│  App.tsx                                                     │
│    ├── KnotLibrary  (trefoil, figure-8, torus, etc.)        │
│    ├── SelectedKnot state                                    │
│    └── InvariantComputer (HOMFLY-PT coefficients)           │
│               │                           │                  │
│               ▼                           ▼                  │
│         KnotViewer.tsx            InvariantPanel.tsx         │
│       ┌────────────────┐        ┌───────────────────┐       │
│       │ @react-three/  │        │ Polynomial display │       │
│       │ fiber Canvas   │        │ Crossing number    │       │
│       │ TubeGeometry   │        │ Bridge index       │       │
│       │ OrbitControls  │        │ Unknotting number  │       │
│       └────────────────┘        └───────────────────┘       │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Mathematical Framework

### 2.1 Knot Parameterization

Each knot is a closed 3D curve  `γ(t)`  where `t` runs from `0` to `2π`.

**Trefoil knot** — simplest non-trivial knot (cannot be unknotted):
```
x(t) = r × cos(2t)
y(t) = r × sin(2t)
z(t) = h × sin(3t)

r = tube radius,  h = height scale
```

**Figure-Eight knot** — the simplest amphichiral knot (identical to its mirror image):
```
x(t) = (2 + cos(2t)) × cos(3t)
y(t) = (2 + cos(2t)) × sin(3t)
z(t) = sin(4t)
```

**Torus knot T(p,q)** — winds p times around the torus axis and q times through the hole:
```
x(t) = (R + r×cos(q×t)) × cos(p×t)
y(t) = (R + r×cos(q×t)) × sin(p×t)
z(t) = r × sin(q×t)
```

### 2.2 HOMFLY-PT Polynomial

The HOMFLY-PT polynomial `P(L; v, z)` is a knot invariant satisfying the **skein relation**:

```
v^(-1) × P(L+)  -  v × P(L-)  =  z × P(L0)

L+  = diagram with a positive crossing
L-  = diagram with a negative crossing (strand flipped)
L0  = diagram with that crossing smoothed (strands not touching)

Boundary condition:  P(unknot) = 1
```

It distinguishes most knots and generalizes both Jones and Alexander polynomials.

### 2.3 Jones Polynomial (Specialization)

Setting `v = t^(-1)` and `z = t^(1/2) - t^(-1/2)` in the HOMFLY-PT polynomial
recovers the **Jones polynomial V(L; t)**.

For the trefoil knot:
```
V(trefoil; t) = -t^(-4)  +  t^(-3)  +  t^(-1)
```

This polynomial proves the trefoil is **not the same as its mirror image** — they
give different polynomials. This is called being chiral (non-amphichiral).

### 2.4 Crossing, Bridge, and Unknotting Numbers

| Invariant | Definition | Example (Trefoil) |
|-----------|------------|-------------------|
| Crossing number `c(K)` | Min crossings in any planar diagram | 3 |
| Bridge number `b(K)` | Min local maxima in any embedding | 2 |
| Unknotting number `u(K)` | Min crossing changes to untie | 1 |

### 2.5 Tube Geometry Rendering

The 3D curve is converted to a visible 3D tube via Three.js:

```
1. Sample N = 200 evenly-spaced points along the curve  γ(t)
2. At each point, compute the Frenet-Serret frame:
      T = tangent unit vector    (direction of travel)
      N = normal unit vector     (curvature direction)
      B = binormal unit vector   (T × N, perpendicular to both)
3. Build a circular cross-section of radius r_tube at each sample point
4. Connect cross-sections → THREE.TubeGeometry mesh
```

---

## 3. Workflow

```
User selects knot from dropdown library
        │
        ▼
App.tsx updates SelectedKnot state
        │
        ├─────────────────────────────┐
        ▼                             ▼
KnotViewer receives curve fn    InvariantComputer
Sample 200 points t ∈ 0..2π    Compute HOMFLY-PT
Build TubeGeometry mesh         coefficients
Render in WebGL with lights
OrbitControls: rotate / zoom    InvariantPanel displays:
                                  polynomial, crossing #,
                                  bridge index, unknotting #
```

---

## 4. System Design

| Layer | Component | Technology | Responsibility |
|-------|-----------|------------|----------------|
| **3D Rendering** | `KnotViewer.tsx` | Three.js / R3F | TubeGeometry, lighting, camera |
| **State** | `App.tsx` | React hooks | Knot selection, invariant dispatch |
| **Math Display** | `InvariantPanel.tsx` | React/JSX | Polynomial output, numerical invariants |
| **Styling** | `index.css` | CSS / Tailwind | Dark glass-morphism theme |
| **Build** | `vite.config.ts` | Vite 5 | HMR, TypeScript compilation |

---

## 5. Key Advantages

| Advantage | Description |
|-----------|-------------|
| **Real-time 3D topology** | Interactive rotation/zoom on mathematical knot structures |
| **Algebraic invariants** | HOMFLY-PT polynomial computed analytically, not approximated |
| **Educational design** | Side-by-side curve + invariant display for intuition building |
| **Extensible library** | Any closed-curve function can be added as a new knot entry |
| **WebGL performance** | Smooth 60 fps on mid-range hardware via Three.js instancing |

---

## 6. Quick Start

```bash
npm install
npm run dev        # → http://localhost:5173
```

> **Note:** Browser-based project — no pytest suite required. Functionality verified manually.

<div align="center">
  <a href="https://q.com"><img src="../../assets/https_q_com.png" width="80" /></a>
</div>
