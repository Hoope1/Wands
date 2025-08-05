"""Validator for computed room layouts."""

from __future__ import annotations

from collections import deque
from typing import Dict, Iterable, List, Set, Tuple

from .utils import iter_window_cells, neighbors4, windows_covering_cell

GRID_W, GRID_H = 77, 50
WIN = 4


def build_grid(solution: Dict) -> Tuple[List[List[int]], Dict[str, bool]]:
    """Build an occupancy grid from ``solution``."""
    grid: List[List[int]] = [[0 for _ in range(GRID_W)] for _ in range(GRID_H)]
    ent = solution.get("entrance", {"x1": 56, "x2": 60, "y1": 40, "y2": 50})

    flags = {"entrance_area": True, "no_overlap": True, "bounds": True}
    rooms = solution.get("rooms", [])

    for rid, room in enumerate(rooms, start=1):
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        if not (0 <= x and 0 <= y and x + w <= GRID_W and y + h <= GRID_H):
            flags["no_overlap"] = False
            flags["bounds"] = False
        for i in range(x, x + w):
            for j in range(y, y + h):
                if not (0 <= i < GRID_W and 0 <= j < GRID_H):
                    flags["no_overlap"] = False
                    flags["bounds"] = False
                    continue
                if ent["x1"] <= i < ent["x2"] and ent["y1"] <= j < ent["y2"]:
                    flags["entrance_area"] = False
                if grid[j][i] == 0:
                    grid[j][i] = rid
                else:
                    flags["no_overlap"] = False
                    grid[j][i] = -1
    return grid, flags


def _corridor_line_width(grid: List[List[int]], i: int, j: int) -> int:
    """Return the maximum straight corridor width through ``(i,j)``."""
    left = right = up = down = 0
    for x in range(i - 1, -1, -1):
        if grid[j][x] != 0:
            break
        left += 1
    for x in range(i + 1, GRID_W):
        if grid[j][x] != 0:
            break
        right += 1
    for y in range(j - 1, -1, -1):
        if grid[y][i] != 0:
            break
        down += 1
    for y in range(j + 1, GRID_H):
        if grid[y][i] != 0:
            break
        up += 1
    return max(left + right + 1, up + down + 1)


def _has_diagonal_pinch(grid: List[List[int]]) -> Tuple[bool, Tuple[int, int] | None]:
    """Detect 2×2 diagonal narrowings in the corridor."""
    for i in range(GRID_W - 1):
        for j in range(GRID_H - 1):
            a = grid[j][i]
            b = grid[j][i + 1]
            c = grid[j + 1][i]
            d = grid[j + 1][i + 1]
            if a > 0 and d > 0 and b == 0 and c == 0:
                return True, (i, j)
            if b > 0 and c > 0 and a == 0 and d == 0:
                return True, (i, j)
    return False, None


def _check_corridor_width(grid: List[List[int]]) -> Tuple[bool, str]:
    """Verify minimal corridor width including diagonal narrowings."""
    for j in range(GRID_H):
        for i in range(GRID_W):
            if grid[j][i] != 0:
                continue
            anchors = windows_covering_cell(i, j, GRID_W, GRID_H, WIN)
            for a, b in anchors:
                if all(grid[yy][xx] == 0 for xx, yy in iter_window_cells(a, b, WIN)):
                    break
            else:
                return False, f"Engstelle bei ({i},{j})"
            if _corridor_line_width(grid, i, j) < WIN:
                return False, f"Engstelle bei ({i},{j})"
    pinch, pos = _has_diagonal_pinch(grid)
    if pinch and pos is not None:
        return False, f"Diagonale Engstelle bei {pos}"
    return True, "Breite ≥4 überall"


def _bfs(
    starts: Iterable[Tuple[int, int]], grid: List[List[int]]
) -> Set[Tuple[int, int]]:
    """Breadth first search over corridor cells from multiple starts."""
    q: deque[Tuple[int, int]] = deque()
    seen: Set[Tuple[int, int]] = set()
    for s in starts:
        x, y = s
        if 0 <= x < GRID_W and 0 <= y < GRID_H and grid[y][x] == 0:
            q.append((x, y))
    while q:
        i, j = q.popleft()
        if (i, j) in seen:
            continue
        seen.add((i, j))
        for ni, nj in neighbors4(i, j, GRID_W, GRID_H):
            if grid[nj][ni] == 0 and (ni, nj) not in seen:
                q.append((ni, nj))
    return seen


def _door_adjacent(room: Dict, door: Dict) -> Tuple[bool, Tuple[int, int] | None]:
    x, y, w, h = room["x"], room["y"], room["w"], room["h"]
    side = door.get("side")
    px_any = door.get("pos_x")
    py_any = door.get("pos_y")
    if not isinstance(px_any, int) or not isinstance(py_any, int):
        return False, None
    px, py = px_any, py_any
    if side == "left":
        if px != x or not (y < py < y + h - 1):
            return False, None
        return True, (px - 1, py)
    if side == "right":
        if px != x + w or not (y < py < y + h - 1):
            return False, None
        return True, (px, py)
    if side == "bottom":
        if py != y or not (x < px < x + w - 1):
            return False, None
        return True, (px, py - 1)
    if side == "top":
        if py != y + h or not (x < px < x + w - 1):
            return False, None
        return True, (px, py)
    return False, None


def _check_doors(
    rooms: List[Dict],
    grid: List[List[int]],
    reachable: Set[Tuple[int, int]],
    require_no_outside_doors: bool,
) -> Tuple[bool, str]:
    errors: List[str] = []
    for room in rooms:
        doors = room.get("doors", [])
        if not doors:
            errors.append(f"Raum {room.get('id')} ohne Tür")
            continue
        valid = False
        for door in doors:
            ok, adj = _door_adjacent(room, door)
            if not ok or adj is None:
                errors.append(f"Ungültige Tür in Raum {room.get('id')}")
                continue
            ax, ay = adj
            if not (0 <= ax < GRID_W and 0 <= ay < GRID_H):
                errors.append(f"Tür von Raum {room.get('id')} außerhalb")
                continue
            if grid[ay][ax] != 0:
                errors.append(f"Tür von Raum {room.get('id')} führt nicht in Gang")
                continue
            if _corridor_line_width(grid, ax, ay) < WIN:
                errors.append(f"Tür von Raum {room.get('id')} führt in Engstelle")
                continue
            if require_no_outside_doors and (
                ax in {0, GRID_W - 1} or ay in {0, GRID_H - 1}
            ):
                errors.append(f"Tür von Raum {room.get('id')} am Außenrand")
                continue
            if (ax, ay) not in reachable:
                errors.append(f"Tür von Raum {room.get('id')} nicht erreichbar")
                continue
            valid = True
        if not valid:
            errors.append(f"Raum {room.get('id')} ohne gültige Tür")
    if errors:
        return False, "; ".join(errors)
    return True, "Alle Türen gültig"


def validate(
    solution: Dict, require_no_outside_doors: bool = True
) -> Dict[str, Dict[str, object]]:
    """Validate ``solution`` and return a structured report.

    Parameters
    ----------
    solution:
        Lösung, die geprüft werden soll.
    require_no_outside_doors:
        Wenn ``True`` (Standard), dürfen Türen nicht direkt ins Freie führen.
    """
    grid, flags = build_grid(solution)

    corridor_cells = [
        (i, j) for j in range(GRID_H) for i in range(GRID_W) if grid[j][i] == 0
    ]
    room_cells = [
        (i, j) for j in range(GRID_H) for i in range(GRID_W) if grid[j][i] > 0
    ]
    unknown_cells = [
        (i, j) for j in range(GRID_H) for i in range(GRID_W) if grid[j][i] < 0
    ]

    complement_pass = not unknown_cells and flags["bounds"]
    report: Dict[str, Dict[str, object]] = {
        "complement": {
            "pass": complement_pass,
            "info": f"corridor={len(corridor_cells)} rooms={len(room_cells)}",
        },
        "entrance_area": {
            "pass": flags["entrance_area"],
            "info": ("Eingang frei" if flags["entrance_area"] else "Eingang blockiert"),
        },
        "no_overlap": {
            "pass": flags["no_overlap"] and flags["bounds"],
            "info": (
                "keine Überlappung"
                if flags["no_overlap"]
                else "Überlappung/Bereichsfehler"
            ),
        },
    }

    width_ok, width_info = _check_corridor_width(grid)
    report["corridor_width"] = {"pass": width_ok, "info": width_info}

    ent = solution.get("entrance", {"x1": 56, "x2": 60, "y1": 40, "y2": 50})
    starts = [
        (i, j) for i in range(ent["x1"], ent["x2"]) for j in range(ent["y1"], ent["y2"])
    ]
    reachable = _bfs(starts, grid)
    corr_set = set(corridor_cells)
    conn_pass = corr_set == reachable
    report["corridor_connectivity"] = {
        "pass": conn_pass,
        "info": f"erreichbar={len(reachable)} corridor={len(corr_set)}",
    }

    doors_pass, doors_info = _check_doors(
        solution.get("rooms", []), grid, reachable, require_no_outside_doors
    )
    report["doors"] = {"pass": doors_pass, "info": doors_info}
    return report
