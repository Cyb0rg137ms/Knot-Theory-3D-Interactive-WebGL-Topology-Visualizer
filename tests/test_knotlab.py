"""Tests for knotlab: values cross-checked against KnotInfo and between independent algorithms."""

from __future__ import annotations

import json
import random

import numpy as np
import pytest

from knotlab import (
    BRAIDS,
    DETERMINANTS,
    PD,
    Laurent,
    PDError,
    alexander,
    bracket,
    bracket_numpy,
    bracket_reference,
    determinant,
    from_braid,
    jones,
    knot,
    torus_alexander,
    torus_braid,
    torus_curve,
)
from knotlab.alexander import det_bareiss
from knotlab.benchmarks import correctness, random_knot, run
from knotlab.cli import main
from knotlab.geometry import curve_length
from knotlab.poly import format_poly

# KnotInfo Jones polynomials (positive/standard chirality of the braid words used)
KNOWN_JONES = {
    "3_1": "-t^4 + t^3 + t",
    "4_1": "t^2 - t + 1 - t^-1 + t^-2",
    "5_1": "-t^7 + t^6 - t^5 + t^4 + t^2",
    "5_2": "-t^6 + t^5 - t^4 + 2t^3 - t^2 + t",
}
KNOWN_ALEXANDER = {
    "3_1": "t - 1 + t^-1",
    "4_1": "-t + 3 - t^-1",
    "5_1": "t^2 - t + 1 - t^-1 + t^-2",
    "5_2": "2t - 3 + 2t^-1",
    "6_1": "-2t + 5 - 2t^-1",
    "7_1": "t^3 - t^2 + t - 1 + t^-1 - t^-2 + t^-3",
}


@pytest.mark.parametrize("name", sorted(KNOWN_JONES))
def test_jones_matches_knotinfo(name: str) -> None:
    assert format_poly(jones(knot(name))) == KNOWN_JONES[name]


@pytest.mark.parametrize("name", sorted(KNOWN_ALEXANDER))
def test_alexander_matches_knotinfo(name: str) -> None:
    assert format_poly(alexander(knot(name))) == KNOWN_ALEXANDER[name]


@pytest.mark.parametrize("name", sorted(BRAIDS))
def test_determinant_two_independent_ways(name: str) -> None:
    pd = knot(name)
    assert abs(alexander(pd)(-1)) == abs(jones(pd)(-1)) == DETERMINANTS[name] == determinant(pd)
    assert jones(pd)(1) == 1 and alexander(pd)(1) == 1


@pytest.mark.parametrize("name", sorted(BRAIDS))
def test_three_bracket_engines_agree(name: str) -> None:
    pd = knot(name)
    assert bracket(pd) == bracket_reference(pd) == bracket_numpy(pd)


def test_engines_agree_on_random_braids() -> None:
    rng = random.Random(7)
    for _ in range(40):
        n = rng.choice([4, 6, 8, 10])
        pd = random_knot(n, 3, rng)
        assert bracket(pd) == bracket_reference(pd)


def test_jones_methods_and_bad_method() -> None:
    pd = knot("5_2")
    assert jones(pd, "contract") == jones(pd, "reference") == jones(pd, "numpy")
    with pytest.raises(ValueError):
        jones(pd, "magic")


def test_mirror_inverts_jones_and_keeps_alexander() -> None:
    pd = knot("3_1")
    v, vm = jones(pd), jones(pd.mirror())
    assert vm == Laurent({-e: c for e, c in v.terms.items()})
    assert alexander(pd.mirror()) == alexander(pd)
    a = jones(knot("4_1"))  # amphichiral
    assert a == Laurent({-e: c for e, c in a.terms.items()})


def test_kink_and_reidemeister_invariance() -> None:
    assert jones(PD(((1, 1, 2, 2),))) == Laurent({0: 1})
    assert jones(from_braid([1, 1, 1, 2], strands=3)) == jones(knot("3_1"))  # Markov stabilisation
    assert jones(from_braid([1, -1, 1, 1, 1])) == jones(knot("3_1"))  # R2


def test_large_braid_contraction_fast_path() -> None:
    pd = from_braid(torus_braid(2, 41))  # 41 crossings: 2^41 states would be infeasible
    assert alexander(pd) == torus_alexander(2, 41)
    assert abs(jones(pd)(-1)) == 41


def test_torus_closed_form_matches_fox_calculus() -> None:
    for p, q in [(2, 3), (2, 5), (3, 4), (3, 5), (2, 9)]:
        assert torus_alexander(p, q) == alexander(knot(f"T({p},{q})"))
    with pytest.raises(ValueError):
        torus_alexander(2, 4)
    assert torus_alexander(1, 5) == Laurent({0: 1})


def test_links_rejected() -> None:
    with pytest.raises(PDError):
        from_braid([1, 1])
    with pytest.raises(PDError):
        from_braid([])
    with pytest.raises(ValueError):
        random_knot(5, 3, random.Random(0))  # parity makes this impossible
    with pytest.raises(KeyError):
        knot("9_99")


def test_det_bareiss_matches_numpy_on_integers() -> None:
    rng = np.random.default_rng(0)
    for _ in range(10):
        m = rng.integers(-4, 5, size=(4, 4))
        lm = [[Laurent({0: int(x)}) for x in row] for row in m]
        assert det_bareiss(lm)(1) == round(np.linalg.det(m))


def test_torus_curve_geometry() -> None:
    pts = torus_curve(2, 3, samples=400)
    assert pts.shape == (400, 3)
    assert np.allclose(np.hypot(np.hypot(pts[:, 0], pts[:, 1]) - 2.0, pts[:, 2]), 0.8)
    assert curve_length(pts) > 2 * np.pi * 1.2 * 2


def test_correctness_report() -> None:
    c = correctness()
    assert c["passed"] == c["total"] == len(BRAIDS)


def test_quick_bench_writes_artifacts(tmp_path) -> None:  # type: ignore[no-untyped-def]
    res = run(tmp_path, quick=True)
    assert (tmp_path / "bench.json").exists()
    assert res["scaling"][0]["reference_ms"] is not None


def test_cli(capsys) -> None:  # type: ignore[no-untyped-def]
    assert main(["invariants", "figure_eight"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["determinant"] == 5 and out["jones"] == KNOWN_JONES["4_1"]
    assert main(["braid", "1", "1", "1"]) == 0
    assert json.loads(capsys.readouterr().out)["alexander"] == "t - 1 + t^-1"
    assert main(["curve", "2", "3", "--samples", "8"]) == 0
    assert len(json.loads(capsys.readouterr().out)) == 8


def test_seifert_matrix_path_is_computed() -> None:
    from invariants.alexander import AlexanderPolynomial

    tre = AlexanderPolynomial.from_seifert_matrix([[-1, 1], [0, -1]])
    fig8 = AlexanderPolynomial.from_seifert_matrix([[1, 1], [0, -1]])
    assert tre.laurent() == alexander(knot("3_1"))
    assert fig8.laurent() == alexander(knot("4_1"))
    assert AlexanderPolynomial.from_seifert_matrix([[0]]).laurent() == Laurent({0: 1})
    with pytest.raises(ValueError):
        AlexanderPolynomial.from_seifert_matrix([[0, 0], [0, 0]])


def test_gauss_from_pd_and_cyclic_r1() -> None:
    from topology.gauss import GaussCode, crossing_number, writhe_from_gauss
    from topology.reidemeister import apply_reidemeister_1

    g = GaussCode.from_pd(knot("3_1"))
    assert crossing_number(g) == 3 and writhe_from_gauss(g) == 3
    kink_across_seam = GaussCode([(-1, "+"), (2, "-"), (3, "+"), (-2, "-"), (-3, "+"), (1, "+")])
    assert crossing_number(apply_reidemeister_1(kink_across_seam)) == 2
