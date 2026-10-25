"""
jones.py
========
Back-compatible Jones-polynomial API, now computed from a PD code with the
Kauffman bracket (:mod:`knotlab.jones`). v1 used a lookup table whose entries
for 4_1, 5_1 and 5_2 were wrong (e.g. its 4_1 had V(1) = −1; every knot has V(1) = 1).

Convention: KnotInfo / KnotTheory. ``trefoil`` is the positive trefoil
(V = t + t³ − t⁴); ``trefoil_mirror`` / ``trefoil_left`` is its mirror.
"""

from __future__ import annotations

from typing import Dict

from knotlab.jones import jones
from knotlab.pd import PD
from knotlab.poly import Laurent, format_poly
from knotlab.table import knot


class JonesPolynomial:
    """Jones polynomial stored as ``{exponent: coefficient}``."""

    def __init__(self, terms: Dict[float, float], knot_name: str = "") -> None:
        self.terms = {e: c for e, c in terms.items() if abs(c) > 1e-10}
        self.knot_name = knot_name

    @classmethod
    def from_pd(cls, pd: PD, name: str = "") -> JonesPolynomial:
        p = jones(pd)
        return cls({float(e): float(c) for e, c in p.terms.items()}, name)

    @classmethod
    def from_knot(cls, name: str) -> JonesPolynomial:
        if name == "unknot":
            return cls({0.0: 1.0}, name)
        mirror = name in ("trefoil_mirror", "trefoil_left")
        try:
            pd = knot("3_1" if mirror else name)
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        return cls.from_pd(pd.mirror() if mirror else pd, name)

    def laurent(self) -> Laurent:
        return Laurent({round(e): round(c) for e, c in self.terms.items()})

    def evaluate(self, t: float) -> float:
        return sum(c * (t**e) for e, c in self.terms.items())

    def __str__(self) -> str:
        return format_poly(self.laurent(), "t")

    def __repr__(self) -> str:
        return f"JonesPolynomial({self.knot_name}: {self})"
