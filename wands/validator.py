"""Validator for computed room layouts.

This module performs a number of geometric checks on the generated
solution.  It verifies that rooms do not overlap, the corridor forms one
connected component of width at least four cells and that every door
opens into the corridor.  The implementation intentionally favours a
straight‑forward brute force approach over micro‑optimisations to keep the
logic easy to reason about.
"""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Set, Tuple

GRID_W, GRID_H = 77, 50


def _check_corridor_width(grid: List[List[int]]) -> bool:
    """Return ``True`` if no corridor segment is narrower than four cells.

    The function scans each row and column of the grid and ensures that any
    sequence of corridor cells that is bounded by room cells or the plot
    boundary has length ≥4.  Although this is an \O(n²) procedure, the grid
    size is small enough that the exhaustive check is acceptable.
    """

    def _scan(lines: Iterable[Iterable[int]]) -> bool:
        for line in lines:
            run = 0
            for cell in line:
                if cell == 0:  # corridor
                    run += 1
                else:
                    if 0 < run < 4:
                        return False
                    run = 0
            if 0 < run < 4:
                return False
        return True

    if not _scan(grid):
        return False
    if not _scan(zip(*grid)):
        return False
    return True


def _flood_fill(start: Tuple[int, int], grid: List[List[int]]) -> Set[Tuple[int, int]]:
    """Return the set of corridor cells reachable from ``start``."""

    q: deque[Tuple[int, int]] = deque([start])
    seen: Set[Tuple[int, int]] = set()
    while q:
        x, y = q.popleft()
        if (x, y) in seen:
            continue
        seen.add((x, y))
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_W and 0 <= ny < GRID_H and grid[ny][nx] == 0:
                q.append((nx, ny))
    return seen


def validate(solution: Dict) -> Dict[str, bool]:
    """Validate a solution dictionary and return a report."""

    report = {
        "complement": True,
        "entrance": True,
        "no_overlap": True,
        "corridor_width": True,
        "connectivity": True,
        "doors": True,
        "reachability": True,
    }

    # build occupancy grid: 0 = corridor, 1 = room
    grid: List[List[int]] = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]

    ent = solution.get("entrance", {"x1": 56, "x2": 60, "y1": 40, "y2": 50})

    # place rooms and check overlaps
    rooms = solution.get("rooms", [])
    for room in rooms:
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        if not (0 <= x < GRID_W and 0 <= y < GRID_H and x + w <= GRID_W and y + h <= GRID_H):
            report["no_overlap"] = False
        for i in range(x, x + w):
            for j in range(y, y + h):
                if ent["x1"] <= i < ent["x2"] and ent["y1"] <= j < ent["y2"]:
                    report["entrance"] = False
                if grid[j][i] == 1:
                    report["no_overlap"] = False
                grid[j][i] = 1

    # verify entrance cells are corridor
    for i in range(ent["x1"], ent["x2"]):
        for j in range(ent["y1"], ent["y2"]):
            if grid[j][i] != 0:
                report["entrance"] = False

    # corridor width check
    if not _check_corridor_width(grid):
        report["corridor_width"] = False

    # connectivity via flood fill from first entrance cell
    start = (ent["x1"], ent["y1"])
    reachable = _flood_fill(start, grid)
    corridor_cells = {
        (i, j)
        for j in range(GRID_H)
        for i in range(GRID_W)
        if grid[j][i] == 0
    }
    if corridor_cells != reachable:
        report["connectivity"] = False

    # door checks
    for room in rooms:
        doors = room.get("doors", [])
        if not doors:
            report["doors"] = False
            continue
        for door in doors:
            side = door.get("side")
            px = door.get("pos_x")
            py = door.get("pos_y")
            if side == "left":
                if px != room["x"] or not (room["y"] < py < room["y"] + room["h"] - 1):
                    report["doors"] = False
                adj = (px - 1, py)
            elif side == "right":
                if px != room["x"] + room["w"] or not (room["y"] < py < room["y"] + room["h"] - 1):
                    report["doors"] = False
                adj = (px, py)
            elif side == "bottom":
                if py != room["y"] or not (room["x"] < px < room["x"] + room["w"] - 1):
                    report["doors"] = False
                adj = (px, py - 1)
            elif side == "top":
                if py != room["y"] + room["h"] or not (room["x"] < px < room["x"] + room["w"] - 1):
                    report["doors"] = False
                adj = (px, py)
            else:
                report["doors"] = False
                continue

            ax, ay = adj
            if not (0 <= ax < GRID_W and 0 <= ay < GRID_H) or grid[ay][ax] != 0:
                report["doors"] = False
            if (ax, ay) not in reachable:
                report["reachability"] = False

    report["valid"] = all(report.values())
    return report

