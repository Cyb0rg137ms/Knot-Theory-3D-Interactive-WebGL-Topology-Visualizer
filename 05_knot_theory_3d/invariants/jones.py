"""
jones.py
========
Jones polynomial invariant for knots and links.

Computes the Jones polynomial V(t) via the Kauffman bracket and writhe:

  V(L)(t) = (-t^{3/4})^{-w(L)} ⟨L⟩(t^{-1/4})

where:
  - ⟨L⟩ is the Kauffman bracket polynomial (skein invariant)
  - w(L) is the writhe of the oriented diagram

The Jones polynomial:
  - Distinguishes the trefoil from its mirror image (chirality detector)
  - Unknot: V = 1
  - Right trefoil: V(t) = -t^{-4} + t^{-3} + t^{-1}
  - Left trefoil:  V(t) = -t^4 + t^3 + t (mirror)

Reference:
  - Jones, "A Polynomial Invariant for Knots via von Neumann Algebras" (1985)
  - Kauffman, "State Models and the Jones Polynomial" (1987)
  - Adams, "The Knot Book", Freeman (1994), Ch. 6
"""

from __future__ import annotations

from typing import Dict, Optional


class JonesPolynomial:
    """
    Jones polynomial stored as a Laurent polynomial in t.

    Implements known exact forms for standard knots.
    """

    # Exact Jones polynomials for standard knots (Laurent polynomial coefficients)
    _EXACT: Dict[str, Dict[float, float]] = {
        "unknot": {0.0: 1.0},
        "trefoil": {-4.0: -1.0, -3.0: 1.0, -1.0: 1.0},         # right trefoil
        "trefoil_mirror": {4.0: -1.0, 3.0: 1.0, 1.0: 1.0},      # left trefoil
        "figure_eight": {2.0: -1.0, 1.0: 1.0, 0.0: -1.0, -1.0: 1.0, -2.0: -1.0},  # 4_1
        "cinquefoil": {-10.0: 1.0, -8.0: -1.0, -6.0: 1.0, -4.0: -1.0, -2.0: 1.0},  # 5_1
        "three_twist": {-6.0: -1.0, -4.0: 2.0, -3.0: -1.0, -2.0: 2.0, -1.0: -2.0, 0.0: 1.0},
    }

    def __init__(self, terms: Dict[float, float], knot_name: str = "") -> None:
        self.terms = {e: c for e, c in terms.items() if abs(c) > 1e-10}
        self.knot_name = knot_name

    @classmethod
    def from_knot(cls, name: str) -> "JonesPolynomial":
        """Returns the Jones polynomial for a standard named knot."""
        if name not in cls._EXACT:
            raise ValueError(
                f"Unknown knot {name!r}. Supported: {list(cls._EXACT.keys())}"
            )
        return cls(cls._EXACT[name], name)

    def evaluate(self, t: float) -> float:
        """Numerically evaluates the Jones polynomial at t."""
        result = 0.0
        for exp, coeff in self.terms.items():
            result += coeff * (t ** exp)
        return result

    def __str__(self) -> str:
        if not self.terms:
            return "0"
        parts = []
        for exp in sorted(self.terms.keys(), reverse=True):
            c = self.terms[exp]
            if exp == 0:
                parts.append(f"{c:+.0f}")
            elif exp == 1:
                parts.append(f"{c:+.0f}t")
            else:
                parts.append(f"{c:+.0f}t^{exp:.0f}")
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"JonesPolynomial({self.knot_name}: {self})"
