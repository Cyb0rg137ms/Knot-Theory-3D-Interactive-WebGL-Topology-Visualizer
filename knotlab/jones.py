"""Kauffman bracket and Jones polynomial from a PD code.

``<K> = Σ_states A^(#A − #B) · d^(loops − 1)``, ``d = −A² − A⁻²``, and
``V(t) = (−A³)^(−w) <K>`` at ``A = t^(−1/4)``.

Three implementations, all tested to agree exactly:

* :func:`bracket` (default) – crossing-by-crossing *tangle contraction*: keeps a map
  from "how the open strand ends are paired" to a polynomial, closing loops as
  they form. Cost grows with the number of boundary pairings (Catalan in the
  frontier width), not with 2^n, so narrow diagrams (e.g. 3-strand braids) scale
  to hundreds of crossings. Worst case is still exponential.
* :func:`bracket_reference` – all 2^n states one at a time with a union-find.
* :func:`bracket_numpy` – all 2^n states at once with NumPy label propagation.
  Measured *slower* than the reference on our machine (see README); kept as a
  documented negative result and an independent cross-check.
"""

from __future__ import annotations

from collections import Counter

import numpy as np

from knotlab.pd import PD
from knotlab.poly import Laurent

MAX_CROSSINGS = 22  # 2^22 states × 44 edges of int8/int16 labels is the memory ceiling we allow

_D = Laurent({2: -1, -2: -1})  # loop value d = -A^2 - A^-2


def _assemble(counter: Counter[tuple[int, int]]) -> Laurent:
    out = Laurent()
    dpow: dict[int, Laurent] = {0: Laurent({0: 1})}
    for (ab, loops), cnt in counter.items():
        k = loops - 1
        if k not in dpow:
            dpow[k] = _D**k
        out = out + dpow[k].shift(ab) * cnt
    return out


def bracket_reference(pd: PD) -> Laurent:
    """Kauffman bracket by explicit enumeration with a union-find per state."""
    n = pd.n
    if n == 0:
        return Laurent({0: 1})
    counter: Counter[tuple[int, int]] = Counter()
    m = 2 * n
    for state in range(1 << n):
        parent = list(range(m + 1))

        def find(a: int, parent: list[int] = parent) -> int:
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a

        na = 0
        for c, (i, j, k, l) in enumerate(pd.crossings):
            if (state >> c) & 1:  # B-smoothing: (i,l)(j,k)
                pairs = ((i, l), (j, k))
            else:  # A-smoothing: (i,j)(k,l)
                pairs = ((i, j), (k, l))
                na += 1
            for a, b in pairs:
                parent[find(a)] = find(b)
        loops = len({find(e) for e in range(1, m + 1)})
        counter[(na - (n - na), loops)] += 1
    return _assemble(counter)


def bracket_numpy(pd: PD, chunk: int = 1 << 16) -> Laurent:
    """Vectorised state sum: loops counted by min-label propagation over all states."""
    n = pd.n
    if n == 0:
        return Laurent({0: 1})
    if n > MAX_CROSSINGS:
        raise ValueError(f"{n} crossings exceeds the state-sum limit of {MAX_CROSSINGS}")
    m = 2 * n
    X = np.asarray(pd.crossings, dtype=np.int32) - 1  # 0-based edges, shape (n, 4)
    counter: Counter[tuple[int, int]] = Counter()
    total = 1 << n
    for start in range(0, total, chunk):
        states = np.arange(start, min(total, start + chunk), dtype=np.int64)
        bits = ((states[:, None] >> np.arange(n)) & 1).astype(bool)  # (S, n) True = B-smoothing
        # partner edges: A joins (i,j),(k,l); B joins (i,l),(j,k)
        i, j, k, l = X[:, 0], X[:, 1], X[:, 2], X[:, 3]
        u1 = i[None, :].repeat(len(states), 0)
        v1 = np.where(bits, l, j)
        u2 = np.where(bits, j, k)
        v2 = np.where(bits, k, l)
        us = np.concatenate([u1, u2], axis=1)  # (S, 2n) endpoints of the 2n smoothing arcs
        vs = np.concatenate([v1, v2], axis=1)
        rows = np.arange(len(states))[:, None]
        lab = np.tile(np.arange(m, dtype=np.int32), (len(states), 1))
        while True:  # propagate min label across arcs until stable (pointer jumping)
            lu, lv = lab[rows, us], lab[rows, vs]
            mn = np.minimum(lu, lv)
            new = lab.copy()
            np.minimum.at(new, (np.broadcast_to(rows, us.shape), us), mn)
            np.minimum.at(new, (np.broadcast_to(rows, vs.shape), vs), mn)
            new = new[rows, new]  # jump: label := label of label
            if np.array_equal(new, lab):
                break
            lab = new
        loops = (lab == np.arange(m)[None, :]).sum(axis=1)
        nb = bits.sum(axis=1)
        ab = (n - nb) - nb
        keys, cnts = np.unique(np.stack([ab, loops], axis=1), axis=0, return_counts=True)
        for (a, lp), c in zip(keys.tolist(), cnts.tolist(), strict=True):
            counter[(a, lp)] += c
    return _assemble(counter)


def _frontier_order(crossings: list[tuple[int, ...]]) -> list[int]:
    """Greedy order: next crossing shares the most edges with the open frontier."""
    left = set(range(len(crossings)))
    order: list[int] = []
    open_edges: set[int] = set()
    while left:
        best = max(left, key=lambda c: (len(open_edges.intersection(crossings[c])), -c))
        left.remove(best)
        order.append(best)
        for e in crossings[best]:
            open_edges ^= {e}
    return order


def bracket(pd: PD) -> Laurent:
    """Kauffman bracket by tangle contraction (exact; see module docstring)."""
    if pd.n == 0:
        return Laurent({0: 1})
    xs = [tuple(x) for x in pd.crossings]
    # state: frozenset of (a, b) pairs of open edge-ends -> Laurent polynomial in A
    states: dict[frozenset[tuple[int, int]], Laurent] = {frozenset(): Laurent({0: 1})}
    for c in _frontier_order(xs):
        i, j, k, l = xs[c]
        new: dict[frozenset[tuple[int, int]], Laurent] = {}
        for match, poly in states.items():
            partner: dict[int, int] = {}
            for a, b in match:
                partner[a], partner[b] = b, a
            for shift, arcs in ((1, ((i, j), (k, l))), (-1, ((i, l), (j, k)))):
                p = dict(partner)
                loops = 0
                for x, y in arcs:
                    if x == y:  # an edge with both ends at this crossing, joined to itself
                        loops += 1
                        continue
                    if x in p and y in p:
                        if p[x] == y:
                            loops += 1
                            del p[x], p[y]
                            continue
                        px, py = p.pop(x), p.pop(y)
                        del p[px], p[py]
                        p[px], p[py] = py, px
                    elif x in p:
                        px = p.pop(x)
                        p[px], p[y] = y, px
                    elif y in p:
                        py = p.pop(y)
                        p[py], p[x] = x, py
                    else:
                        p[x], p[y] = y, x
                key = frozenset((a, b) for a, b in p.items() if a < b)
                term = poly.shift(shift) * (_D**loops) if loops else poly.shift(shift)
                new[key] = new[key] + term if key in new else term
        states = new
    total = states[frozenset()]
    return total.divexact(_D)  # <unknot> = 1: the last closed loop is not weighted


def jones(pd: PD, method: str = "contract") -> Laurent:
    """Jones polynomial in ``t``. ``method``: ``contract`` (default), ``reference`` or ``numpy``."""
    engines = {"contract": bracket, "reference": bracket_reference, "numpy": bracket_numpy}
    if method not in engines:
        raise ValueError(f"method must be one of {sorted(engines)}")
    br = engines[method](pd)
    w = pd.writhe()
    f = Laurent({3 * -w: (-1) ** w})  # (-A^3)^(-w) = (-1)^w A^(-3w)
    in_a = f * br  # polynomial in A; exponents divisible by 4 for knots
    if any(e % 4 for e in in_a.terms):
        raise ValueError("bracket exponents not divisible by 4: input is not a knot diagram")
    return Laurent({-e // 4: c for e, c in in_a.terms.items()})  # A = t^(-1/4)
