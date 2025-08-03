"""Dummy solver producing an empty solution.

This module provides a placeholder implementation that merely returns the
fixed entrance block without placing any rooms. It exists to demonstrate the
expected I/O flow of the application.
"""

from __future__ import annotations

import random
from typing import List

from .model import Entrance, RoomDef


def solve(room_defs: List[RoomDef], seed: int | None = None) -> dict:
    """Return a trivial solution without rooms.

    Parameters
    ----------
    room_defs:
        The list of room definitions (currently unused).
    seed:
        Optional RNG seed for deterministic behaviour.
    """
    if seed is not None:
        random.seed(seed)
    entrance = Entrance()
    solution = {
        "rooms": [],
        "entrance": {
            "x1": entrance.x1,
            "x2": entrance.x2,
            "y1": entrance.y1,
            "y2": entrance.y2,
        },
        "objective": {"room_area_total": 0},
    }
    return solution
