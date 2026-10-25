"""Reproducible benchmarks: correctness on the knot table + scaling of the two bracket engines."""

from __future__ import annotations

import json
import logging
import platform
import random
import statistics
import time
from collections.abc import Callable
from functools import partial
from pathlib import Path
from typing import Any

from knotlab.alexander import alexander
from knotlab.jones import bracket, bracket_numpy, bracket_reference, jones
from knotlab.pd import PD, PDError, from_braid
from knotlab.table import BRAIDS, DETERMINANTS, knot

log = logging.getLogger(__name__)


def _time(fn: Callable[[], object], repeats: int) -> float:
    ts = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        fn()
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts) * 1e3


def random_knot(n: int, strands: int, rng: random.Random) -> PD:
    """Random braid word of length n whose closure is a knot (single component).

    Each generator is a transposition, so an s-cycle (a knot) needs n ≡ s − 1 (mod 2).
    """
    if (n - (strands - 1)) % 2:
        raise ValueError(f"no {strands}-strand braid of length {n} closes to a knot (parity)")
    while True:
        word = [rng.choice([1, -1]) * rng.randint(1, strands - 1) for _ in range(n)]
        if {abs(w) for w in word} != set(range(1, strands)):
            continue
        try:
            return from_braid(word, strands=strands)
        except PDError:  # closure is a link; draw again
            continue


def correctness() -> dict[str, Any]:
    rows = []
    for name in BRAIDS:
        pd = knot(name)
        da = abs(alexander(pd)(-1))
        dj = abs(jones(pd)(-1))
        rows.append({"knot": name, "expected": DETERMINANTS[name], "alexander": da, "jones": dj,
                     "ok": da == dj == DETERMINANTS[name]})  # fmt: skip
    return {"rows": rows, "passed": sum(r["ok"] for r in rows), "total": len(rows)}


def scaling(sizes: list[int], seed: int, repeats: int, ref_max: int) -> list[dict[str, Any]]:
    """Random 3-strand braid closures (even n). The state-sum engines stop at ``ref_max``."""
    rng = random.Random(seed)
    out = []
    for n in sizes:
        pd = random_knot(n, 3, rng)
        row: dict[str, Any] = {"crossings": n}
        row["contract_ms"] = _time(partial(bracket, pd), repeats)
        small = n <= ref_max
        row["reference_ms"] = _time(partial(bracket_reference, pd), repeats) if small else None
        row["numpy_ms"] = _time(partial(bracket_numpy, pd), repeats) if small else None
        if small:
            assert bracket(pd) == bracket_reference(pd) == bracket_numpy(pd)
        row["alexander_ms"] = _time(partial(alexander, pd), repeats)
        log.info("n=%d %s", n, row)
        out.append(row)
    return out


def run(out_dir: Path | None = None, quick: bool = False, seed: int = 0) -> dict[str, Any]:
    sizes = [4, 6, 8, 10, 12, 14, 20, 40] if quick else [4, 6, 8, 10, 12, 14, 16, 18, 24, 32, 48, 64, 96, 128]
    res = {
        "machine": {"python": platform.python_version(), "platform": platform.platform()},
        "seed": seed,
        "correctness": correctness(),
        "scaling": scaling(sizes, seed, 1 if quick else 3, 14 if quick else 16),
    }
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "bench.json").write_text(json.dumps(res, indent=2))
        _plot(res, out_dir / "bracket_scaling.png")
    return res


def _plot(res: dict[str, Any], path: Path) -> None:
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:  # pragma: no cover
        log.warning("matplotlib missing; skipping plot")
        return
    rows = res["scaling"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.semilogy(
        [r["crossings"] for r in rows],
        [r["contract_ms"] for r in rows],
        "o-",
        label="bracket, tangle contraction (default)",
    )
    ref = [r for r in rows if r["reference_ms"] is not None]
    ax.semilogy(
        [r["crossings"] for r in ref],
        [r["reference_ms"] for r in ref],
        "s-",
        label="bracket, 2^n states, union-find",
    )
    ax.semilogy(
        [r["crossings"] for r in ref], [r["numpy_ms"] for r in ref], "x--", label="bracket, 2^n states, numpy"
    )
    ax.semilogy(
        [r["crossings"] for r in rows],
        [r["alexander_ms"] for r in rows],
        "^-",
        label="Alexander (Fox + Bareiss)",
    )
    ax.set_xlabel("crossings (random 3-strand braid closures)")
    ax.set_ylabel("median time [ms]")
    ax.set_title("Jones via 2^n state sum vs tangle contraction; Alexander via Fox calculus")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    plt.close(fig)
