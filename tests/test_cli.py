"""Basic tests for the Wands CLI."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wands import __version__


def test_cli_e2e(tmp_path: Path) -> None:
    """Run the CLI end-to-end and validate entrance area."""
    root = Path(__file__).resolve().parents[1]
    out_json = tmp_path / "solution.json"
    out_png = tmp_path / "solution.png"
    out_report = tmp_path / "validation_report.json"
    cmd = [
        sys.executable,
        "-m",
        "wands",
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
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert out_json.exists(), "solution.json not created"
    assert out_png.exists(), "solution.png not created"
    assert out_report.exists(), "validation report not created"
    report = json.loads(out_report.read_text())
    assert report["entrance_area"]["pass"] is True


def test_cli_validate_only(tmp_path: Path) -> None:
    """CLI validates an existing solution without solving."""
    solution = tmp_path / "solution.json"
    png = tmp_path / "solution.png"
    report = tmp_path / "report.json"
    cmd = [
        "python",
        "-m",
        "wands.cli",
        "--config",
        "rooms.yaml",
        "--out-json",
        str(solution),
        "--out-png",
        str(png),
        "--validate",
        str(report),
        "--progress",
        "off",
    ]
    subprocess.run(cmd, check=True)

    report2 = tmp_path / "report2.json"
    cmd2 = [
        "python",
        "-m",
        "wands.cli",
        "--config",
        str(solution),
        "--out-json",
        str(tmp_path / "unused.json"),
        "--out-png",
        str(tmp_path / "unused.png"),
        "--validate",
        str(report2),
        "--progress",
        "off",
        "--validate-only",
    ]
    subprocess.run(cmd2, check=True)
    assert report2.exists(), "validation report not created"


def test_cli_strict_exit_code(tmp_path: Path) -> None:
    """--strict returns exit code 1 bei Validierungsfehlern."""
    bad_solution = {
        "rooms": [
            {
                "id": "r",
                "type": "R",
                "x": 0,
                "y": 0,
                "w": 1,
                "h": 1,
                "doors": [],
            }
        ],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    sol = tmp_path / "bad.json"
    sol.write_text(json.dumps(bad_solution), encoding="utf8")
    report = tmp_path / "report.json"
    cmd = [
        sys.executable,
        "-m",
        "wands",
        "--config",
        str(sol),
        "--out-json",
        str(tmp_path / "out.json"),
        "--out-png",
        str(tmp_path / "out.png"),
        "--validate",
        str(report),
        "--progress",
        "off",
        "--validate-only",
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0
    result2 = subprocess.run(cmd + ["--strict"], capture_output=True, text=True)
    assert result2.returncode == 1


def test_cli_version() -> None:
    """The module reports its version string."""
    result = subprocess.run(
        [sys.executable, "-m", "wands", "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert __version__ in result.stdout


def test_start_process_version() -> None:
    """start_process.py should expose the package version."""
    result = subprocess.run(
        [sys.executable, "start_process.py", "--version"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert __version__ in result.stdout
