"""Exact integer Laurent polynomials ``{exponent: coefficient}`` (no floats)."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


class Laurent:
    """Immutable Laurent polynomial with integer coefficients."""

    __slots__ = ("_t",)

    def __init__(self, terms: Mapping[int, int] | None = None) -> None:
        self._t: dict[int, int] = {int(e): int(c) for e, c in (terms or {}).items() if c != 0}

    # construction -----------------------------------------------------------
    @classmethod
    def mono(cls, exp: int, coeff: int = 1) -> Laurent:
        return cls({exp: coeff})

    @classmethod
    def from_coeffs(cls, coeffs: Iterable[int], low: int = 0) -> Laurent:
        return cls({low + i: c for i, c in enumerate(coeffs)})

    # access -------------------------------------------------------------------
    @property
    def terms(self) -> dict[int, int]:
        return dict(self._t)

    def is_zero(self) -> bool:
        return not self._t

    @property
    def min_exp(self) -> int:
        return min(self._t) if self._t else 0

    @property
    def max_exp(self) -> int:
        return max(self._t) if self._t else 0

    def span(self) -> int:
        return self.max_exp - self.min_exp if self._t else 0

    def lead(self) -> int:
        return self._t[self.max_exp] if self._t else 0

    # arithmetic -----------------------------------------------------------------
    def __add__(self, other: Laurent) -> Laurent:
        out = dict(self._t)
        for e, c in other._t.items():
            out[e] = out.get(e, 0) + c
        return Laurent(out)

    def __neg__(self) -> Laurent:
        return Laurent({e: -c for e, c in self._t.items()})

    def __sub__(self, other: Laurent) -> Laurent:
        return self + (-other)

    def __mul__(self, other: Laurent | int) -> Laurent:
        if isinstance(other, int):
            return Laurent({e: c * other for e, c in self._t.items()})
        out: dict[int, int] = {}
        for e1, c1 in self._t.items():
            for e2, c2 in other._t.items():
                out[e1 + e2] = out.get(e1 + e2, 0) + c1 * c2
        return Laurent(out)

    __rmul__ = __mul__

    def __pow__(self, n: int) -> Laurent:
        if n < 0:
            if len(self._t) != 1:
                raise ValueError("only monomials have Laurent inverses")
            ((e, c),) = self._t.items()
            if abs(c) != 1:
                raise ValueError("monomial coefficient must be +-1 to invert")
            return Laurent({-e * -n: c ** (-n)})
        out = Laurent({0: 1})
        base = self
        while n:
            if n & 1:
                out = out * base
            base = base * base
            n >>= 1
        return out

    def shift(self, k: int) -> Laurent:
        return Laurent({e + k: c for e, c in self._t.items()})

    def subs_power(self, k: int) -> Laurent:
        """Substitute x -> x^k (k may be negative)."""
        return Laurent({e * k: c for e, c in self._t.items()})

    def divexact(self, other: Laurent) -> Laurent:
        """Exact division; raises ValueError if ``other`` does not divide ``self``."""
        if other.is_zero():
            raise ZeroDivisionError("division by zero polynomial")
        rem = dict(self._t)
        q: dict[int, int] = {}
        dmax, dlead = other.max_exp, other.lead()
        dmin = other.min_exp
        while rem:
            rmax = max(rem)
            if rmax - dmax < min(rem) - dmin:
                raise ValueError("not an exact division")
            c, r = divmod(rem[rmax], dlead)
            if r:
                raise ValueError("not an exact division (non-integer quotient)")
            e = rmax - dmax
            q[e] = c
            for de, dc in other._t.items():
                rem[e + de] = rem.get(e + de, 0) - c * dc
                if rem[e + de] == 0:
                    del rem[e + de]
        return Laurent(q)

    def __call__(self, x: float | complex) -> float | complex:
        return sum(c * x**e for e, c in self._t.items())

    def evaluate(self, x: float) -> float:
        return float(self(x))  # type: ignore[arg-type]

    # comparison / display -------------------------------------------------------
    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            other = Laurent({0: other})
        return isinstance(other, Laurent) and self._t == other._t

    def __hash__(self) -> int:
        return hash(frozenset(self._t.items()))

    def normalize(self, symmetric: bool = True) -> Laurent:
        """Divide out ±x^k: positive constant/lead and (optionally) symmetric exponents."""
        if not self._t:
            return self
        p = self.shift(-self.min_exp)
        if symmetric:
            if p.span() % 2:
                raise ValueError("odd span cannot be centred")
            p = p.shift(-p.span() // 2)
        if p.lead() < 0:
            p = -p
        return p

    def __repr__(self) -> str:
        return f"Laurent({self})"

    def __str__(self) -> str:
        return format_poly(self, "t")


def format_poly(p: Laurent, var: str = "t", denom: int = 1) -> str:
    """Human readable, highest power first; exponents divided by ``denom``."""
    if p.is_zero():
        return "0"
    parts = []
    for i, e in enumerate(sorted(p.terms, reverse=True)):
        c = p.terms[e]
        sign = "-" if c < 0 else ("+" if i else "")
        a = abs(c)
        if e % denom:
            ex = f"{e}/{denom}"
        else:
            ex = str(e // denom)
        if e == 0:
            body = str(a)
        else:
            mon = var if ex == "1" else f"{var}^{ex}"
            body = mon if a == 1 else f"{a}{mon}"
        parts.append(f"{' ' if i else ''}{sign}{' ' if i else ''}{body}".replace("  ", " "))
    return "".join(parts).strip()
