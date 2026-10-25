"""Prime knots up to 7 crossings as braid words, with reference determinants.

Braid words follow KnotInfo's ``braid_notation`` column; determinants are
KnotInfo's values. The determinants are *not* used to compute anything - tests
check that both independently computed invariants (|Δ(−1)| and |V(−1)|)
reproduce them.
"""

from __future__ import annotations

from knotlab.pd import PD, from_braid

BRAIDS: dict[str, list[int]] = {
    "3_1": [1, 1, 1],
    "4_1": [1, -2, 1, -2],
    "5_1": [1, 1, 1, 1, 1],
    "5_2": [1, 1, 1, 2, -1, 2],
    "6_1": [1, 1, 2, -1, -3, 2, -3],
    "6_2": [1, 1, 1, -2, 1, -2],
    "6_3": [1, 1, -2, 1, -2, -2],
    "7_1": [1, 1, 1, 1, 1, 1, 1],
    "7_2": [1, 1, 1, 2, -1, 2, 3, -2, 3],
    "7_3": [1, 1, 1, 1, 1, 2, -1, 2],
    "7_4": [1, 1, 2, -1, 2, 2, 3, -2, 3],
    "7_5": [1, 1, 1, 1, 2, -1, 2, 2],
    "7_6": [1, 1, -2, 1, 3, -2, 3],
    "7_7": [1, -2, 1, -2, 3, -2, 3],
}

DETERMINANTS: dict[str, int] = {
    "3_1": 3, "4_1": 5, "5_1": 5, "5_2": 7, "6_1": 9, "6_2": 11, "6_3": 13,
    "7_1": 7, "7_2": 11, "7_3": 13, "7_4": 15, "7_5": 17, "7_6": 19, "7_7": 21,
}  # fmt: skip

ALIASES = {
    "trefoil": "3_1",
    "figure_eight": "4_1",
    "cinquefoil": "5_1",
    "three_twist": "5_2",
}


def torus_braid(p: int, q: int) -> list[int]:
    """Braid word of the torus knot T(p, q) on p strands: (σ1 … σ_{p-1})^q."""
    if p < 2 or q == 0:
        raise ValueError("need p >= 2 and q != 0")
    gen = list(range(1, p))
    word = gen * abs(q)
    return word if q > 0 else [-g for g in word]


def knot(name: str) -> PD:
    """PD code for a table name (``3_1``), alias (``figure_eight``) or ``T(p,q)``.

    ``trefoil`` / ``3_1`` are the *positive* (right-handed in KnotInfo's
    convention) trefoil, whose Jones polynomial is t + t^3 - t^4.
    """
    key = ALIASES.get(name, name)
    if key in BRAIDS:
        return from_braid(BRAIDS[key])
    if key.startswith("T(") and key.endswith(")"):
        p, q = (int(v) for v in key[2:-1].split(","))
        return from_braid(torus_braid(p, q), strands=p)
    raise KeyError(f"unknown knot {name!r}; known: {sorted(BRAIDS)} + aliases {sorted(ALIASES)} + 'T(p,q)'")
