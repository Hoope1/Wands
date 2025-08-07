"""Kommandozeilen-Einstieg."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from solver import load_config, render, solve, validate


def main(argv: list[str] | None = None) -> int:
    """Einfacher CLI-Wrapper."""
    args = argv or sys.argv[1:]
    if len(args) != 4:
        print("usage: python main.py rooms.yaml solution.json solution.png report.txt")
        return 1
    cfg_path, out_json, out_png, out_report = args
    cfg = load_config(cfg_path)
    solution = solve(cfg)
    Path(out_json).write_text(json.dumps(solution, indent=2), encoding="utf8")
    render(solution, out_png)
    report = "\n".join(validate(solution))
    Path(out_report).write_text(report, encoding="utf8")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
