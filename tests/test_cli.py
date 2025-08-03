"""Basic tests for the Wands CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wands import __version__


def test_cli_creates_output(tmp_path: Path) -> None:
    out_json = tmp_path / "solution.json"
    out_png = tmp_path / "solution.png"
    out_report = tmp_path / "report.json"
    cmd = [
        "python",
        "-m",
        "wands.cli",
        "--config",
        "rooms.yaml",
        "--out-json",
        str(out_json),
        "--out-png",
        str(out_png),
        "--validate",
        str(out_report),
        "--progress",
        "off",
    ]
    subprocess.run(cmd, check=True)
    assert out_json.exists(), "solution.json not created"
    assert out_png.exists(), "solution.png not created"
    assert out_report.exists(), "validation report not created"
    data = json.loads(out_json.read_text())
    assert data["entrance"]["x1"] == 56


def test_start_process_version() -> None:
    result = subprocess.run(
        [sys.executable, "start_process.py", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert __version__ in result.stdout
