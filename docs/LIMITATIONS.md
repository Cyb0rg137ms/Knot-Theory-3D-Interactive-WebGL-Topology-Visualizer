# Limitations (v2)

* **Knots only.** Links (multi-component) are rejected with `PDError`; the multivariable Alexander polynomial and link Jones are not implemented.
* **Worst case is still exponential.** Tangle contraction is fast for narrow diagrams (benchmarks use 3-strand braids). For wide diagrams the number of boundary pairings grows like a Catalan number; the two 2^n state-sum engines are capped at 22 crossings.
* **Alexander cost** is polynomial but uses exact Laurent arithmetic in pure Python: ~2.3 s at 128 crossings on our 8-vCPU box (see `docs/assets/bench.json`).
* **The NumPy state sum is slower than the plain union-find** (≈1.5–2.5× on our machine). It is kept only as an independent cross-check, not as an optimisation.
* **Knot table** covers the 14 prime knots up to 7 crossings plus torus knots; arbitrary knots must be supplied as PD codes or braid words. Chirality follows the braid words in `knotlab/table.py` (KnotInfo's braid notation).
* **Gauss-code utilities** (`topology/`) are the v1 heuristics: R1 removal now handles the cyclic seam, but there is no R2/R3 simplification and `is_unknot` is only a sufficient test.
* **Web viewer** renders torus knots only (drei `TorusKnot`) and computes their Alexander polynomial in the browser; it does not call the Python engine. The production bundle is ~1.1 MB (no code-splitting yet).
* **No GPU**: everything is CPU; the "GPU-accelerated" wording of v1 referred only to WebGL rendering.
