from __future__ import annotations

"""Convenience script to run the full Wands process.

This wrapper supplies default paths so the solver, validator and renderer
can be executed with a single command. Additional arguments are forwarded
to the underlying :mod:`wands.cli` interface.
"""

import argparse
import sys
from typing import Sequence

from wands.cli import main as wands_main


def run(argv: Sequence[str] | None = None) -> int:
    """Parse arguments and execute the Wands pipeline.

    Parameters
    ----------
    argv:
        Optional argument list. If ``None`` the arguments from ``sys.argv``
        are used.
    """
    parser = argparse.ArgumentParser(description="Start the Wands process")
    parser.add_argument(
        "--config",
        default="rooms.yaml",
        help="Path to the rooms configuration file.",
    )
    parser.add_argument(
        "--out-json",
        default="solution.json",
        help="Output path for the solution JSON.",
    )
    parser.add_argument(
        "--out-png",
        default="solution.png",
        help="Output path for the solution visualisation PNG.",
    )
    parser.add_argument(
        "--validate",
        default="validation_report.json",
        dest="report",
        help="Output path for the validation report JSON.",
    )
    known, unknown = parser.parse_known_args(argv)
    args = [
        "--config",
        known.config,
        "--out-json",
        known.out_json,
        "--out-png",
        known.out_png,
        "--validate",
        known.report,
    ] + unknown
    return wands_main(args)


if __name__ == "__main__":
    sys.exit(run())
