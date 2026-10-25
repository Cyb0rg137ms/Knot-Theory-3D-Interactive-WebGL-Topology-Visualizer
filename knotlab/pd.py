"""Planar-diagram (PD) codes, braid closures, writhe and arcs.

Convention (KnotTheory`/KnotInfo): ``X[i, j, k, l]`` lists the four edge labels
counter-clockwise starting from the *incoming under-strand*; the under-strand
runs i -> k. Edges are labelled 1..2n consecutively along the orientation, so the
over-strand runs l -> j when ``j - l == 1`` (or wraps around), and such a
crossing is positive.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

Crossing = tuple[int, int, int, int]


class PDError(ValueError):
    """Malformed PD code or braid word."""


@dataclass(frozen=True)
class PD:
    crossings: tuple[Crossing, ...]

    @classmethod
    def from_list(cls, xs: Sequence[Sequence[int]]) -> PD:
        pd = cls(tuple(tuple(int(v) for v in x) for x in xs))  # type: ignore[misc]
        pd.validate()
        return pd

    @property
    def n(self) -> int:
        return len(self.crossings)

    def validate(self) -> None:
        if any(len(x) != 4 for x in self.crossings):
            raise PDError("every crossing needs exactly 4 edge labels")
        if not self.crossings:
            return
        labels = [v for x in self.crossings for v in x]
        m = 2 * self.n
        if sorted(set(labels)) != list(range(1, m + 1)):
            raise PDError(f"edge labels must be exactly 1..{m}")
        for v in set(labels):
            if labels.count(v) != 2:
                raise PDError(f"edge {v} must appear exactly twice")
        # single component: consecutive labels must follow the under/over strands
        if len(components(self)) != 1:
            raise PDError("PD code describes a link (more than one component); only knots are supported")

    def signs(self) -> list[int]:
        return [crossing_sign(x, 2 * self.n) for x in self.crossings]

    def writhe(self) -> int:
        return sum(self.signs())

    def mirror(self) -> PD:
        """Mirror image: swap over/under at every crossing."""
        out = []
        m = 2 * self.n
        for i, j, k, l in self.crossings:
            if _next(l, m) == j:  # over l->j becomes the under strand
                out.append((l, i, j, k))
            else:  # over j->l
                out.append((j, k, l, i))
        return PD(tuple(out))

    def to_list(self) -> list[list[int]]:
        return [list(x) for x in self.crossings]


def _next(e: int, m: int) -> int:
    return e % m + 1


def crossing_sign(x: Crossing, m: int) -> int:
    _i, j, _k, l = x
    if _next(l, m) == j:
        return 1
    if _next(j, m) == l:
        return -1
    raise PDError(f"crossing {x}: over-strand labels {j},{l} are not consecutive")


def components(pd: PD) -> list[list[int]]:
    """Edge cycles obtained by following successor edges through crossings."""
    succ: dict[int, int] = {}
    m = 2 * pd.n
    for i, j, k, l in pd.crossings:
        succ[i] = k
        if _next(l, m) == j:
            succ[l] = j
        else:
            succ[j] = l
    seen: set[int] = set()
    comps = []
    for start in sorted(succ):
        if start in seen:
            continue
        cyc = []
        e = start
        while e not in seen:
            seen.add(e)
            cyc.append(e)
            e = succ.get(e, e)
        comps.append(cyc)
    return comps


def arcs(pd: PD) -> tuple[list[int], int]:
    """Map each edge to its arc index (arcs break only at under-crossings)."""
    m = 2 * pd.n
    parent = list(range(m + 1))

    def find(a: int) -> int:
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for _, j, _, l in pd.crossings:
        parent[find(j)] = find(l)
    roots: dict[int, int] = {}
    arc_of = [0] * (m + 1)
    for e in range(1, m + 1):
        arc_of[e] = roots.setdefault(find(e), len(roots))
    return arc_of, len(roots)


def from_braid(word: Sequence[int], strands: int | None = None) -> PD:
    """PD code of the closure of a braid word (``k`` = σ_k, ``-k`` = σ_k^{-1}).

    σ_k^{+1} is a positive crossing. Raises :class:`PDError` if the closure is a link.
    """
    if not word:
        raise PDError("empty braid word (closure is an unlink)")
    s = strands or (max(abs(g) for g in word) + 1)
    if any(g == 0 or abs(g) >= s for g in word):
        raise PDError(f"generators must be in ±1..{s - 1}")
    nxt = s
    cur = list(range(s))  # temporary edge id at each position
    raw: list[tuple[Crossing, int, int, int, int]] = []  # (X, under_in, under_out, over_in, over_out)
    for g in word:
        p = abs(g) - 1
        a, b = cur[p], cur[p + 1]  # bottom-left, bottom-right
        tr, tl = nxt, nxt + 1  # new top-right (continues a), top-left (continues b)
        nxt += 2
        if g < 0:  # under BL->TR, over BR->TL  (negative)
            raw.append(((a, b, tr, tl), a, tr, b, tl))
        else:  # under BR->TL, over BL->TR  (positive)
            raw.append(((b, tr, tl, a), b, tl, a, tr))
        cur[p], cur[p + 1] = tl, tr
    alias = {cur[pos]: pos for pos in range(s)}  # closure: top edge == bottom edge

    def canon(e: int) -> int:
        return alias.get(e, e)

    succ = {}
    for _, ui, uo, oi, oo in raw:
        succ[canon(ui)] = canon(uo)
        succ[canon(oi)] = canon(oo)
    if len(succ) != 2 * len(word):
        raise PDError("a strand has no crossings; closure has an unknotted extra component")
    order, e = [], canon(raw[0][1])
    while e not in order:
        order.append(e)
        e = succ[e]
    if len(order) != 2 * len(word):
        raise PDError("braid closure is a link, not a knot (permutation is not a single cycle)")
    label = {e: i + 1 for i, e in enumerate(order)}
    pd = PD(tuple(tuple(label[canon(v)] for v in x) for x, *_ in raw))  # type: ignore[misc]
    pd.validate()
    return pd
