"""
gauss.py
========
Gauss code representation and invariants for knot diagrams.
"""
from __future__ import annotations
from typing import TYPE_CHECKING, List, Tuple

if TYPE_CHECKING:
    from knotlab.pd import PD


class GaussCode:
    """
    Represents a knot as a Gauss code.

    A Gauss code is an ordered sequence of crossing visits (label, sign)
    where sign ∈ {"+", "-"} and the code lists alternating over/under crossings.
    """
    def __init__(self, crossings: List[Tuple]) -> None:
        self.crossings = list(crossings)

    def __repr__(self) -> str:
        return f"GaussCode({self.crossings})"

    @classmethod
    def from_pd(cls, pd: "PD") -> "GaussCode":
        """Signed Gauss code from a PD code.

        Each crossing (numbered 1..n in PD order) appears twice: ``+c`` when the
        strand passes over, ``-c`` when under; the second tuple entry is the
        crossing sign (``"+"``/``"-"``).
        """
        from knotlab.pd import crossing_sign

        m = 2 * pd.n
        visits = {}
        for c, x in enumerate(pd.crossings, start=1):
            i, j, k, l = x
            sign = "+" if crossing_sign(x, m) > 0 else "-"
            visits[i] = (-c, sign)
            over_in = l if l % m + 1 == j else j
            visits[over_in] = (c, sign)
        return cls([visits[e] for e in range(1, m + 1)])


def writhe_from_gauss(gc: GaussCode) -> int:
    """
    Computes the writhe of a knot from its Gauss code.

    Writhe = (number of positive crossings) - (number of negative crossings).
    In the Gauss code convention, each crossing appears twice;
    we count each crossing once at its first occurrence.
    """
    seen = set()
    w = 0
    for label, sign in gc.crossings:
        abs_label = abs(label)
        if abs_label not in seen:
            seen.add(abs_label)
            w += 1 if sign == "+" else -1
    return w


def crossing_number(gc: GaussCode) -> int:
    """Returns the number of distinct crossings in the Gauss code."""
    return len(set(abs(label) for label, _ in gc.crossings))
