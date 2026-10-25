"""Compute Jones/Alexander for the table, a braid, and a 41-crossing torus knot."""

from knotlab import BRAIDS, alexander, determinant, from_braid, jones, knot, torus_braid
from knotlab.poly import format_poly

for name in BRAIDS:
    pd = knot(name)
    print(f"{name:>4}  det={determinant(pd):>3}  V(t) = {format_poly(jones(pd))}")

pd = from_braid([1, -2, 1, -2])  # figure-eight as a braid closure
print("braid 1 -2 1 -2 ->", format_poly(alexander(pd)))

big = from_braid(torus_braid(2, 41))  # 2^41 states: infeasible by state sum, fast by contraction
print("T(2,41): |V(-1)| =", round(abs(jones(big)(-1))))
