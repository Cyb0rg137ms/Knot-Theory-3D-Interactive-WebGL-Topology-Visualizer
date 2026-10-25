"""
alexander.py
============
Back-compatible Alexander-polynomial API, now *computed* (v1 used a lookup table
with wrong entries for 5_1 and 5_2, and ``from_seifert_matrix`` returned a
constant).

``Δ(t)`` is computed from a PD code (Fox calculus, :mod:`knotlab.alexander`) or
from a Seifert matrix as ``det(M − t·Mᵀ)``, both exact over Z[t].
"""

from __future__ import annotations

from typing import Dict, List, Optional

from knotlab.alexander import alexander, det_bareiss
from knotlab.pd import PD
from knotlab.poly import Laurent, format_poly
from knotlab.table import knot


class Polynomial:
    """Laurent polynomial ``{exponent: coefficient}`` (kept for v1 compatibility)."""

    def __init__(self, terms: Optional[Dict[int, float]] = None) -> None:
        self.terms: Dict[int, float] = {}
        if terms:
            for exp, coeff in terms.items():
                if abs(coeff) > 1e-10:
                    self.terms[exp] = coeff

    def evaluate(self, t: float) -> float:
        result = 0.0
        for exp, coeff in self.terms.items():
            if t == 0 and exp < 0:
                return float("inf")
            result += coeff * (t**exp)
        return result

    def degree(self) -> int:
        return max((abs(e) for e in self.terms), default=0)

    def __repr__(self) -> str:
        return format_poly(Laurent({e: round(c) for e, c in self.terms.items()}), "t")


_MIRRORS = {"trefoil_left": "3_1", "trefoil_mirror": "3_1"}


class AlexanderPolynomial:
    """Alexander polynomial of a knot (symmetrised, Δ(1) = 1)."""

    def __init__(self, polynomial: Polynomial, knot_name: str = "") -> None:
        self._poly = polynomial
        self.knot_name = knot_name

    @classmethod
    def from_laurent(cls, p: Laurent, name: str = "") -> AlexanderPolynomial:
        return cls(Polynomial({e: float(c) for e, c in p.terms.items()}), name)

    @classmethod
    def from_pd(cls, pd: PD, name: str = "") -> AlexanderPolynomial:
        return cls.from_laurent(alexander(pd), name)

    @classmethod
    def from_seifert_matrix(cls, M: List[List[int]], name: str = "") -> AlexanderPolynomial:
        """Δ(t) = det(M − t·Mᵀ), normalised. A 1×1 zero matrix is treated as the unknot."""
        n = len(M)
        if n == 0 or (n == 1 and M[0][0] == 0):
            return cls(Polynomial({0: 1.0}), name or "unknot")
        mat = [[Laurent({0: M[i][j], 1: -M[j][i]}) for j in range(n)] for i in range(n)]
        d = det_bareiss(mat)
        if d.is_zero():
            raise ValueError("det(M - t M^T) is identically zero; not a Seifert matrix of a knot")
        d = d.normalize(symmetric=n % 2 == 0)
        if d.evaluate(1) < 0:
            d = -d
        return cls.from_laurent(d, name)

    @classmethod
    def from_knot(cls, name: str) -> AlexanderPolynomial:
        """Named knot: ``unknot``, ``trefoil``, ``trefoil_left``, ``figure_eight``,
        ``cinquefoil``, ``three_twist``, any ``n_k`` up to 7 crossings, or ``T(p,q)``."""
        if name == "unknot":
            return cls(Polynomial({0: 1.0}), name)
        try:
            pd = knot(_MIRRORS.get(name, name))
        except KeyError as exc:
            raise ValueError(str(exc)) from exc
        return cls.from_pd(pd, name)

    def laurent(self) -> Laurent:
        return Laurent({e: round(c) for e, c in self._poly.terms.items()})

    @property
    def terms(self) -> Dict[int, float]:
        return dict(self._poly.terms)

    def evaluate(self, t: float) -> float:
        return self._poly.evaluate(t)

    def degree(self) -> int:
        return self._poly.degree()

    def __repr__(self) -> str:
        return f"AlexanderPolynomial({self.knot_name}: {self._poly})"
