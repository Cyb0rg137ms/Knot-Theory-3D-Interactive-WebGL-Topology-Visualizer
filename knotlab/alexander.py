"""Alexander polynomial from a PD code via Fox calculus on the Wirtinger presentation.

At a crossing with over-arc k, incoming under-arc i and outgoing under-arc j the
Wirtinger relation abelianises to the Alexander-matrix row

* positive crossing: ``(1 − t)`` at k, ``t`` at i, ``−1`` at j
* negative crossing: ``(1 − t)`` at k, ``−1`` at i, ``t`` at j   (row × −t, a unit)

Deleting one row and one column and taking the determinant gives Δ(t) up to
±t^k; we normalise to the symmetric form with Δ(1) = 1. The determinant is
computed exactly with fraction-free (Bareiss) elimination over Z[t].
"""

from __future__ import annotations

from knotlab.pd import PD, arcs, crossing_sign
from knotlab.poly import Laurent

_ONE = Laurent({0: 1})
_ZERO = Laurent()


def alexander_matrix(pd: PD) -> list[list[Laurent]]:
    arc_of, n_arcs = arcs(pd)
    m = 2 * pd.n
    rows = []
    for x in pd.crossings:
        i, j, k, _l = x
        row = [_ZERO] * n_arcs
        s = crossing_sign(x, m)
        over, a_in, a_out = arc_of[j], arc_of[i], arc_of[k]
        row[over] = row[over] + Laurent({0: 1, 1: -1})
        if s > 0:
            row[a_in] = row[a_in] + Laurent({1: 1})
            row[a_out] = row[a_out] + Laurent({0: -1})
        else:
            row[a_in] = row[a_in] + Laurent({0: -1})
            row[a_out] = row[a_out] + Laurent({1: 1})
        rows.append(row)
    return rows


def det_bareiss(mat: list[list[Laurent]]) -> Laurent:
    """Exact determinant over Z[t, t^-1] by Bareiss fraction-free elimination."""
    a = [row[:] for row in mat]
    n = len(a)
    if n == 0:
        return _ONE
    sign = 1
    prev = _ONE
    for k in range(n - 1):
        if a[k][k].is_zero():
            swap = next((r for r in range(k + 1, n) if not a[r][k].is_zero()), None)
            if swap is None:
                return _ZERO
            a[k], a[swap] = a[swap], a[k]
            sign = -sign
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * a[k][k] - a[i][k] * a[k][j]).divexact(prev)
        prev = a[k][k]
    return a[n - 1][n - 1] * sign


def alexander(pd: PD) -> Laurent:
    """Symmetrised Alexander polynomial with Δ(1) = 1 (Conway normalisation up to sign of t)."""
    if pd.n == 0:
        return _ONE
    mat = alexander_matrix(pd)
    minor = [row[:-1] for row in mat[:-1]]
    d = det_bareiss(minor)
    if d.is_zero():
        raise ValueError("Alexander minor vanished; diagram is not a knot")
    d = d.normalize(symmetric=True)
    if d.evaluate(1) < 0:
        d = -d
    return d


def determinant(pd: PD) -> int:
    """Knot determinant |Δ(−1)|."""
    return abs(round(alexander(pd)(-1).real))  # type: ignore[union-attr]
