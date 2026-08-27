"""
gauss.py
========
Gauss code representation and invariants for knot diagrams.
"""
from __future__ import annotations
from typing import List, Optional, Tuple


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
