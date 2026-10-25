"""Torus-knot space curves (vectorised) and the closed-form torus-knot Alexander polynomial."""

from __future__ import annotations

from math import gcd

import numpy as np

from knotlab.poly import Laurent


def torus_curve(p: int, q: int, samples: int = 1024, R: float = 2.0, r: float = 0.8) -> np.ndarray:
    """(samples, 3) points on T(p, q): wraps p times around the axis, q times through the hole."""
    th = np.linspace(0.0, 2.0 * np.pi, samples, endpoint=False)
    rad = R + r * np.cos(q * th)
    return np.stack([rad * np.cos(p * th), rad * np.sin(p * th), r * np.sin(q * th)], axis=1)


def curve_length(points: np.ndarray) -> float:
    d = np.diff(np.vstack([points, points[:1]]), axis=0)
    return float(np.linalg.norm(d, axis=1).sum())


def torus_alexander(p: int, q: int) -> Laurent:
    """Δ_{T(p,q)}(t) = (t^{pq} − 1)(t − 1) / ((t^p − 1)(t^q − 1)), symmetrised.

    Valid for coprime p, q >= 1; gcd > 1 gives a link, |p| or |q| == 1 the unknot.
    """
    p, q = abs(p), abs(q)
    if p == 0 or q == 0 or gcd(p, q) != 1:
        raise ValueError("T(p,q) is a knot only for coprime non-zero p, q")
    if p == 1 or q == 1:
        return Laurent({0: 1})
    num = Laurent({p * q: 1, 0: -1}) * Laurent({1: 1, 0: -1})
    den = Laurent({p: 1, 0: -1}) * Laurent({q: 1, 0: -1})
    return num.divexact(den).normalize(symmetric=True)
