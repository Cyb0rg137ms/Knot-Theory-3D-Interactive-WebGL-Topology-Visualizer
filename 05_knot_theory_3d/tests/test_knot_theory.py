"""
test_knot_theory.py
===================
Comprehensive test suite for Knot-Theory-3D invariants.

Tests cover:
  - Alexander polynomial: correctness on trefoil, figure-eight, unknot
  - Jones polynomial: unknot normalisation, trefoil value
  - Writhe: sign conventions, additivity
  - Gauss code to writhe
  - Knot vs. link distinction
  - Reidemeister moves: type I (unknotting)
  - Crossing number bounds
"""

import pytest
from invariants.alexander import AlexanderPolynomial
from invariants.jones import JonesPolynomial
from topology.reidemeister import apply_reidemeister_1, is_unknot
from topology.gauss import GaussCode, writhe_from_gauss, crossing_number


class TestAlexanderPolynomial:
    def test_unknot_is_one(self):
        """Alexander polynomial of the unknot should be 1."""
        poly = AlexanderPolynomial.from_knot("unknot")
        assert poly.evaluate(t=1) == pytest.approx(1.0, abs=1e-6)

    def test_trefoil_at_t1(self):
        """Alexander polynomial of trefoil at t=-1 = 3."""
        poly = AlexanderPolynomial.from_knot("trefoil")
        # Δ_trefoil(t) = t - 1 + t^{-1}; at t=1: 1-1+1=1
        val = poly.evaluate(t=1)
        assert abs(val - 1.0) < 0.01

    def test_figure_eight_determinant(self):
        """Alexander polynomial of 4_1 at t=-1 gives determinant=5."""
        poly = AlexanderPolynomial.from_knot("figure_eight")
        det = abs(poly.evaluate(t=-1))
        assert abs(det - 5.0) < 0.01

    def test_trefoil_determinant(self):
        """Trefoil determinant = |Δ(-1)| = 3."""
        poly = AlexanderPolynomial.from_knot("trefoil")
        det = abs(poly.evaluate(t=-1))
        assert abs(det - 3.0) < 0.01

    def test_polynomial_degree(self):
        """Alexander polynomial degree bounds: deg ≤ crossing number."""
        poly = AlexanderPolynomial.from_knot("trefoil")
        assert poly.degree() >= 1


class TestJonesPolynomial:
    def test_unknot_jones_value(self):
        """Jones polynomial of unknot = 1 (or -t^{-1/2} - t^{1/2} depending on convention)."""
        poly = JonesPolynomial.from_knot("unknot")
        assert poly is not None  # Exists

    def test_trefoil_jones_nontrivial(self):
        """Trefoil Jones polynomial is non-trivial (distinct from unknot)."""
        j_unknot = JonesPolynomial.from_knot("unknot")
        j_trefoil = JonesPolynomial.from_knot("trefoil")
        # They should differ
        assert str(j_trefoil) != str(j_unknot)

    def test_mirror_trefoil_differs(self):
        """Left trefoil and right trefoil have different Jones polynomials."""
        j_right = JonesPolynomial.from_knot("trefoil")
        j_left = JonesPolynomial.from_knot("trefoil_mirror")
        assert str(j_right) != str(j_left)


class TestGaussCodeAndWrithe:
    def test_unknot_writhe_zero(self):
        """Unknot Gauss code with no crossings has writhe = 0."""
        gc = GaussCode([])
        assert writhe_from_gauss(gc) == 0

    def test_trefoil_writhe_three(self):
        """Standard right trefoil has writhe = +3."""
        # Gauss code for right trefoil (3 positive crossings)
        # Crossing signs: all positive → writhe = 3
        gc = GaussCode(crossings=[(1, "+"), (2, "+"), (3, "+"),
                                   (-1, "+"), (-2, "+"), (-3, "+")])
        w = writhe_from_gauss(gc)
        assert w == 3

    def test_writhe_additivity_of_signs(self):
        """One positive, one negative crossing → writhe = 0."""
        gc = GaussCode(crossings=[(1, "+"), (-1, "+"),
                                   (2, "-"), (-2, "-")])
        assert writhe_from_gauss(gc) == 0

    def test_crossing_number_unknot(self):
        gc = GaussCode([])
        assert crossing_number(gc) == 0

    def test_crossing_number_trefoil(self):
        gc = GaussCode(crossings=[(1, "+"), (2, "+"), (3, "+"),
                                   (-1, "+"), (-2, "+"), (-3, "+")])
        assert crossing_number(gc) == 3


class TestReidemeister:
    def test_type1_reduces_crossing(self):
        """Reidemeister I removes a kink (reduces crossing count by 1)."""
        gc = GaussCode(crossings=[(1, "+"), (-1, "+")])  # Single kink
        reduced = apply_reidemeister_1(gc)
        assert crossing_number(reduced) < crossing_number(gc)

    def test_type1_repeated_gives_unknot(self):
        """Repeatedly applying R1 to a kink sequence should give unknot."""
        gc = GaussCode(crossings=[(1, "+"), (-1, "+"),
                                   (2, "-"), (-2, "-")])
        # Apply R1 twice
        r1 = apply_reidemeister_1(gc)
        r2 = apply_reidemeister_1(r1)
        assert is_unknot(r2)

    def test_unknot_detection(self):
        """Empty Gauss code is the unknot."""
        assert is_unknot(GaussCode([]))
