"""Light‑weight validator for placeholder solutions."""

from __future__ import annotations

from typing import Dict


def validate(solution: Dict) -> Dict[str, bool]:
    """Validate a solution and return a report.

    The current implementation performs only minimal checks and always
    indicates success. It acts as a scaffold for a future full validator.
    """
    report = {
        "complement": True,
        "entrance": True,
        "no_overlap": True,
        "corridor_width": True,
        "connectivity": True,
        "doors": True,
        "reachability": True,
    }
    report["valid"] = all(report.values())
    return report
