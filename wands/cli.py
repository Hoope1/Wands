"""Command line interface for the Wands solver."""

from __future__ import annotations

import argparse
import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from . import __version__
from .config import load_room_defs
from .model import SolveParams
from .progress import Progress
from .solver import SolveInterrupted, solve
from .validator import validate
from .visualizer import render


class JsonFormatter(logging.Formatter):
    """Log records im JSON-Format ausgeben."""

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - formatting
        """Formatiert einen LogRecord als JSON-String."""
        data = {
            "ts": datetime.utcnow().isoformat(),
            "level": record.levelname.lower(),
            "msg": record.getMessage(),
        }
        return json.dumps(data, ensure_ascii=False)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="wands")
    parser.add_argument("--config", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--out-png", required=True)
    parser.add_argument("--validate", required=True, dest="report")
    parser.add_argument("--threads", type=int, default=1)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--time-limit", type=float, default=1.0)
    parser.add_argument("--max-iters", type=int, default=10)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument("--log-format", choices=["text", "json"], default="text")
    parser.add_argument("--log-file")
    parser.add_argument(
        "--progress",
        choices=["auto", "json", "off"],
        default="auto",
    )
    parser.add_argument("--progress-interval", type=float, default=1.0)
    parser.add_argument("--checkpoint", type=float, default=0.0)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Beende mit Exit-Code 1 bei Validierungsfehlern.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--allow-outside-doors",
        action="store_true",
        help="Erlaubt Türen direkt am Außenrand",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Run the command-line interface."""
    parser = _build_parser()
    args = parser.parse_args(argv)
    log_stream = (
        open(args.log_file, "a", encoding="utf8") if args.log_file else sys.stdout
    )
    logger = logging.getLogger("wands")
    logger.setLevel(getattr(logging, args.log_level.upper(), logging.INFO))
    handler = logging.StreamHandler(log_stream)

    if args.log_format == "json":
        formatter: logging.Formatter = JsonFormatter()
    else:
        formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    logger.handlers = [handler]
    _ = logger.handlers

    prog: Optional[Progress] = None
    if args.progress != "off":
        fmt = "text" if args.progress == "auto" else "json"
        prog = Progress(stream=log_stream, fmt=fmt, interval=args.progress_interval)
        prog.heartbeat("start")
    logger.info("phase=start")
    interrupted = False

    if args.validate_only:
        solution = json.loads(Path(args.config).read_text(encoding="utf8"))
        report = validate(
            solution, require_no_outside_doors=not args.allow_outside_doors
        )
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
        if prog:
            prog.heartbeat("validate")
            prog.done()
        logger.info("phase=validate")
        logger.info("phase=finish")
        if args.log_file:
            log_stream.close()
        exit_code = 0
        if args.strict and not all(v["pass"] for v in report.values()):
            exit_code = 1
        return exit_code

    room_defs = load_room_defs(args.config)
    if prog:
        prog.heartbeat("parse")
    logger.info("phase=parse")

    params = SolveParams()
    params.max_iters = args.max_iters
    params.time_limit = args.time_limit
    params.seed = args.seed
    params.threads = args.threads

    last_checkpoint = 0.0

    def checkpoint_cb(sol: dict) -> None:
        nonlocal last_checkpoint
        if args.checkpoint <= 0:
            return
        now = time.time()
        if now - last_checkpoint < args.checkpoint:
            return
        Path(args.out_json).write_text(json.dumps(sol, indent=2), encoding="utf8")
        report = validate(sol, require_no_outside_doors=not args.allow_outside_doors)
        Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
        render(sol, args.out_png)
        last_checkpoint = now

    def handle_sigint(_signum, _frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handle_sigint)

    try:
        solution = solve(room_defs, params, progress=prog, checkpoint_cb=checkpoint_cb)
        logger.info("phase=solve")
    except Exception as exc:
        if isinstance(exc, SolveInterrupted):
            interrupted = True
            solution = exc.solution or {
                "grid_w": params.grid_w,
                "grid_h": params.grid_h,
                "rooms": [],
                "entrance": {
                    "x1": params.entrance.x1,
                    "x2": params.entrance.x2,
                    "y1": params.entrance.y1,
                    "y2": params.entrance.y2,
                },
                "objective": {"room_area_total": 0},
            }
            logger.info("phase=solve")
        else:
            raise

    Path(args.out_json).write_text(json.dumps(solution, indent=2), encoding="utf8")
    if prog:
        prog.heartbeat("solve")

    report = validate(solution, require_no_outside_doors=not args.allow_outside_doors)
    Path(args.report).write_text(json.dumps(report, indent=2), encoding="utf8")
    if prog:
        prog.heartbeat("validate")
    logger.info("phase=validate")

    render(solution, args.out_png)
    logger.info("phase=render")
    if prog:
        phase = "finish" if not interrupted else "finish-abort"
        prog.heartbeat("render")
        prog.done(phase)
    else:
        phase = "finish" if not interrupted else "finish-abort"
    logger.info("phase=%s", phase)
    if args.log_file:
        log_stream.close()
    exit_code = 0
    if args.strict and not all(v["pass"] for v in report.values()):
        exit_code = 1
    return exit_code


if TYPE_CHECKING:  # pragma: no cover - for vulture
    _ = JsonFormatter().format(logging.LogRecord("", 0, "", 0, "", (), None))


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
