"""
benchmark.py
============
Performance benchmark script for Knot-Theory-3D invariant engine.
Measures Alexander and Jones polynomial calculation time.
"""

import time
from topology.gauss import GaussCode

def benchmark_invariants():
    # Trefoil knot Gauss code representation
    # 1-, 2+, 3-, 1+, 2-, 3+
    trefoil_gauss = GaussCode([
        (1, -1), (2, 1), (3, -1), (1, 1), (2, -1), (3, 1)
    ])
    
    t0 = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        alexander = trefoil_gauss.alexander_polynomial()
        jones = trefoil_gauss.jones_polynomial()
    elapsed = (time.perf_counter() - t0) / iterations
    print(f"Knot Invariants Calculation Time Ms: {elapsed * 1000.0:.3f}")

if __name__ == "__main__":
    print("Running Knot-Theory-3D benchmarks...")
    benchmark_invariants()
