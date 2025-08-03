"""Command line interface for the Wands solver."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

from . import __version__
from .config import load_room_defs
from .solver import solve
from .validator import validate
from .visualizer import render


def configure_logging(level: str, fmt: str, log_file: str | None) -> None:
    """Configure application logging."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    else:
        handlers.append(logging.StreamHandler(sys.stdout))
    if fmt == "json":
        formatter = logging.Formatter("%(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    for h in handlers:
        h.setFormatter(formatter)
    logging.basicConfig(level=log_level, handlers=handlers, force=True)


PHASES = ["parse", "build", "solve", "validate", "render", "finish"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="wands")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-png", required=True)
    parser.add_argument("--validate", required=True, dest="report")
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--log-format", choices=["text", "json"], default="text")
    parser.add_argument("--log-file")
    parser.add_argument("--progress", choices=["auto", "off"], default="auto")
    parser.add_argument("--progress-interval", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--time-limit", type=float, default=0.0)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--version", action="version", version=__version__)
    args = parser.parse_args(argv)

    configure_logging(args.log_level, args.log_format, args.log_file)
    logger = logging.getLogger(__name__)
    start_time = time.time()

    logger.info("phase=%s", "start")

    if args.validate_only:
        solution = json.loads(Path(args.config).read_text(encoding="utf8"))
        report = validate(solution)
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
        return 0

    room_defs = load_room_defs(args.config)
    if args.progress != "off":
        logger.info("phase=%s", "parse")
        time.sleep(args.progress_interval)
    solution = solve(room_defs, seed=args.seed)
    Path(args.out_json).write_text(json.dumps(solution, indent=2), encoding="utf8")
    if args.progress != "off":
        logger.info("phase=%s", "solve")
        time.sleep(args.progress_interval)
    report = validate(solution)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
    if args.progress != "off":
        logger.info("phase=%s", "validate")
        time.sleep(args.progress_interval)
    render(solution, args.out_png)
    if args.progress != "off":
        logger.info("phase=%s", "render")
        time.sleep(args.progress_interval)

    duration = time.time() - start_time
    logger.info("phase=%s runtime_sec=%.3f", "finish", duration)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
