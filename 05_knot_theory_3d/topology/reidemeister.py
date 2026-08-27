"""
reidemeister.py
===============
Reidemeister move implementations for Gauss codes.

Reidemeister moves are the three local diagram moves that preserve knot type:
  - Type I:   Adds/removes a kink (crossing with both strands adjacent)
  - Type II:  Slides one arc over another (adds/removes 2 crossings)
  - Type III: Triangle slide (preserves crossing count, changes connectivity)
"""
from __future__ import annotations
from topology.gauss import GaussCode, crossing_number


def apply_reidemeister_1(gc: GaussCode) -> GaussCode:
    """
    Applies Reidemeister move I (kink removal) if a kink is detected.

    A kink occurs when the same crossing label appears consecutively in the
    Gauss code (e.g. [1, -1, ...] → strand passes through itself).
    """
    crossings = list(gc.crossings)
    i = 0
    while i < len(crossings) - 1:
        label_a, sign_a = crossings[i]
        label_b, sign_b = crossings[i + 1]
        # Same crossing label, opposite occurrence → kink
        if abs(label_a) == abs(label_b):
            # Remove both crossings
            crossings.pop(i)
            crossings.pop(i)
            # Re-label remaining crossings to remove gaps
            crossings = _relabel(crossings)
            i = 0  # Restart
        else:
            i += 1
    return GaussCode(crossings)


def _relabel(crossings):
    """Re-labels crossing indices to be consecutive after removal."""
    label_map = {}
    new_crossings = []
    counter = 1
    for label, sign in crossings:
        abs_label = abs(label)
        if abs_label not in label_map:
            label_map[abs_label] = counter
            counter += 1
        new_label = label_map[abs_label] * (1 if label > 0 else -1)
        new_crossings.append((new_label, sign))
    return new_crossings


def is_unknot(gc: GaussCode) -> bool:
    """Returns True if the Gauss code represents the unknot (no crossings)."""
    return crossing_number(gc) == 0
