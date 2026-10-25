"""Benchmark shim (v1 entry point). Equivalent to ``python -m knotlab bench``."""

from knotlab.cli import main

if __name__ == "__main__":
    raise SystemExit(main(["bench", *__import__("sys").argv[1:]]))
