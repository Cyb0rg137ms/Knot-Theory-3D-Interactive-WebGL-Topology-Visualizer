"""Command line: ``knotlab invariants 5_2``, ``knotlab braid 1 1 1``, ``knotlab bench``."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from knotlab.alexander import alexander, determinant
from knotlab.geometry import torus_curve
from knotlab.jones import jones
from knotlab.pd import PD, from_braid
from knotlab.poly import format_poly
from knotlab.table import knot


def _report(pd: PD, name: str) -> dict[str, object]:
    a, v = alexander(pd), jones(pd)
    return {"knot": name, "crossings": pd.n, "pd": [list(x) for x in pd.crossings],
            "alexander": format_poly(a), "jones": format_poly(v), "determinant": determinant(pd)}  # fmt: skip


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="knotlab", description=__doc__)
    ap.add_argument("-v", "--verbose", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("invariants", help="invariants of a named knot (3_1, figure_eight, T(3,4), ...)")
    s.add_argument("name")
    s = sub.add_parser("braid", help="invariants of a braid closure, e.g. 1 -2 1 -2")
    s.add_argument("word", nargs="+", type=int)
    s = sub.add_parser("curve", help="write T(p,q) space curve as JSON")
    s.add_argument("p", type=int)
    s.add_argument("q", type=int)
    s.add_argument("--samples", type=int, default=512)
    s = sub.add_parser("bench", help="run benchmarks")
    s.add_argument("--out", type=Path, default=Path("docs/assets"))
    s.add_argument("--quick", action="store_true")
    s.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING, format="%(levelname)s %(message)s"
    )

    if args.cmd == "invariants":
        print(json.dumps(_report(knot(args.name), args.name), indent=2))
    elif args.cmd == "braid":
        print(json.dumps(_report(from_braid(args.word), "braid " + " ".join(map(str, args.word))), indent=2))
    elif args.cmd == "curve":
        print(json.dumps(torus_curve(args.p, args.q, args.samples).round(5).tolist()))
    else:
        from knotlab.benchmarks import run

        res = run(args.out, quick=args.quick, seed=args.seed)
        c = res["correctness"]
        print(f"correctness: {c['passed']}/{c['total']} knots, |Δ(-1)| = |V(-1)| = KnotInfo determinant")
        for r in res["scaling"]:
            ref = "-" if r["reference_ms"] is None else f"{r['reference_ms']:.2f}"
            npy = "-" if r["numpy_ms"] is None else f"{r['numpy_ms']:.2f}"
            print(
                f"n={r['crossings']:>3}  contract {r['contract_ms']:9.2f} ms  union-find {ref:>9} ms  "
                f"numpy {npy:>9} ms  alexander {r['alexander_ms']:8.2f} ms"
            )
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
