"""CP-SAT based solver with corridor and door constraints.

This module implements a CP-SAT model that places axis-aligned rectangular
rooms on a discrete grid. The corridor is modelled as the complement of all
rooms. Corridor width is enforced via ``win``×``win`` windows. After each solve
the solution is checked for doors and corridor connectivity. Missing doors and
isolated corridor components trigger additional cutting planes and the model is
resolved. The process repeats until all mandatory criteria are met or the
maximum number of cut rounds is reached.
"""

from __future__ import annotations

try:
    import resource  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - windows fallback
    resource = None  # type: ignore[assignment]
from collections import deque
from typing import Callable, Sequence, cast

from ortools.sat.python import cp_model

from .model import RoomDef, SolveParams
from .progress import Progress
from .utils import iter_window_cells, neighbors4, windows_covering_cell


class SolveInterrupted(RuntimeError):
    """Raised when the solving process is interrupted.

    Contains the best solution found so far in ``solution``.
    """

    def __init__(self, solution: dict | None):
        """Store the best solution available when interruption occurred."""
        super().__init__("solving interrupted")
        self.solution = solution


def allowed_values(min_v: int, step: int, max_v: int) -> cp_model.Domain:
    """Return a CP-SAT domain with values from ``min_v`` to ``max_v``."""
    if step <= 0:
        raise ValueError("step must be positive")
    if max_v < min_v:
        raise ValueError("max_v must be >= min_v")
    values = list(range(min_v, max_v + 1, step))
    return cp_model.Domain.from_values(values)


def _get_mem_mb() -> float | None:
    """Return current RSS memory in MB or ``None`` if unavailable."""
    if resource is None:
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024


def _build_model(
    room_defs: Sequence[RoomDef],
    params: SolveParams,
    door_cuts: Sequence[Sequence[tuple[int, int]]],
    island_cuts: Sequence[Sequence[tuple[int, int]]],
) -> tuple[
    cp_model.CpModel,
    list[
        tuple[
            RoomDef,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
        ]
    ],
    list[list[cp_model.IntVar]],
    list[list[cp_model.IntVar]],
]:
    """Create the CP-SAT model and return variables used later."""
    gw, gh = params.grid_w, params.grid_h
    x1, x2, y1, y2 = params.entrance_bounds()

    model = cp_model.CpModel()

    # Room placement variables
    room_vars: list[
        tuple[
            RoomDef,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
        ]
    ] = []
    for idx, rdef in enumerate(room_defs):
        w_dom = allowed_values(rdef.min_w, rdef.step_w, rdef.pref_w)
        h_dom = allowed_values(rdef.min_h, rdef.step_h, rdef.pref_h)
        w = model.new_int_var_from_domain(w_dom, f"w_{idx}")
        h = model.new_int_var_from_domain(h_dom, f"h_{idx}")
        x = model.new_int_var(0, gw - rdef.min_w, f"x_{idx}")
        y = model.new_int_var(0, gh - rdef.min_h, f"y_{idx}")
        model.add(x + w <= gw)
        model.add(y + h <= gh)
        room_vars.append((rdef, x, y, w, h))

    # Cell variables
    in_r: list[list[list[cp_model.IntVar]]] = []
    for r_idx, _ in enumerate(room_defs):
        r_cells: list[list[cp_model.IntVar]] = []
        for i in range(gw):
            row: list[cp_model.IntVar] = []
            for j in range(gh):
                b = model.new_bool_var(f"in_{r_idx}_{i}_{j}")
                row.append(b)
            r_cells.append(row)
        in_r.append(r_cells)

    room_cell: list[list[cp_model.IntVar]] = [
        [model.new_bool_var(f"room_{i}_{j}") for j in range(gh)] for i in range(gw)
    ]
    corr_cell: list[list[cp_model.IntVar]] = [
        [model.new_bool_var(f"corr_{i}_{j}") for j in range(gh)] for i in range(gw)
    ]

    # Link cell variables with room rectangles
    for r_idx, (_, x, y, w, h) in enumerate(room_vars):
        for i in range(gw):
            for j in range(gh):
                b = in_r[r_idx][i][j]
                model.add(x <= i).only_enforce_if(b)
                model.add(i + 1 <= x + w).only_enforce_if(b)
                model.add(y <= j).only_enforce_if(b)
                model.add(j + 1 <= y + h).only_enforce_if(b)

    for i in range(gw):
        for j in range(gh):
            cell_rooms = [in_r[r_idx][i][j] for r_idx in range(len(room_defs))]
            model.add(sum(cell_rooms) == room_cell[i][j])
            model.add(room_cell[i][j] + corr_cell[i][j] == 1)
            model.add(sum(cell_rooms) <= 1)

    # Entrance fixed as corridor
    for i in range(x1, x2):
        for j in range(y1, y2):
            model.add(corr_cell[i][j] == 1)
            model.add(room_cell[i][j] == 0)
            for r_idx in range(len(room_defs)):
                model.add(in_r[r_idx][i][j] == 0)

    # Corridor width via sliding windows
    win = params.corridor_win
    win_full: dict[tuple[int, int], cp_model.IntVar] = {}
    for a in range(0, gw - win + 1):
        for b_idx in range(0, gh - win + 1):
            wv = model.new_bool_var(f"win_{a}_{b_idx}")
            win_full[(a, b_idx)] = cast(cp_model.IntVar, wv)
            for i, j in iter_window_cells(a, b_idx, win):
                model.add(corr_cell[i][j] >= wv)

    for i in range(gw):
        for j in range(gh):
            covers = [win_full[p] for p in windows_covering_cell(i, j, gw, gh, win)]
            if covers:
                model.add(corr_cell[i][j] <= sum(covers))

    # Apply accumulated cuts
    for cut in door_cuts:
        model.add(sum(corr_cell[i][j] for (i, j) in cut) >= 1)
    for comp in island_cuts:
        model.add(sum(corr_cell[i][j] for (i, j) in comp) <= len(comp) - 1)

    # Objective: maximise number of room cells
    model.maximize(sum(room_cell[i][j] for i in range(gw) for j in range(gh)))

    return model, room_vars, room_cell, corr_cell


def _extract_solution(
    solver: cp_model.CpSolver,
    room_vars: Sequence[
        tuple[
            RoomDef,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
            cp_model.IntVar,
        ]
    ],
    room_cell: Sequence[Sequence[cp_model.IntVar]],
    corr_cell: Sequence[Sequence[cp_model.IntVar]],
) -> tuple[list[dict], list[list[int]], list[list[int]], int]:
    """Extract placements, room and corridor grids and total area."""
    gw = len(room_cell)
    gh = len(room_cell[0]) if gw else 0

    rooms: list[dict] = []
    for rdef, x, y, w, h in room_vars:
        vx = solver.value(x)
        vy = solver.value(y)
        vw = solver.value(w)
        vh = solver.value(h)
        rooms.append(
            {
                "id": rdef.name,
                "type": rdef.group,
                "x": vx,
                "y": vy,
                "w": vw,
                "h": vh,
                "doors": [],
            }
        )

    room_grid = [
        [int(solver.value(room_cell[i][j])) for j in range(gh)] for i in range(gw)
    ]
    corr_grid = [
        [int(solver.value(corr_cell[i][j])) for j in range(gh)] for i in range(gw)
    ]
    area_total = sum(room_grid[i][j] for i in range(gw) for j in range(gh))
    return rooms, room_grid, corr_grid, area_total


def _door_candidates(
    room: dict,
    corr_grid: Sequence[Sequence[int]],
) -> tuple[list[tuple[str, int, int]], list[tuple[int, int]]]:
    """Return (doors, cut_positions) for ``room`` based on ``corr_grid``."""
    gw = len(corr_grid)
    gh = len(corr_grid[0]) if gw else 0
    x, y, w, h = room["x"], room["y"], room["w"], room["h"]

    door_list: list[tuple[str, int, int]] = []
    cut_positions: list[tuple[int, int]] = []

    # Helper to register candidate
    def check(side: str, cx: int, cy: int, px: int, py: int) -> None:
        if 0 <= px < gw and 0 <= py < gh:
            cut_positions.append((px, py))
            if corr_grid[px][py] == 1:
                door_list.append((side, cx, cy))

    for yy in range(y + 1, y + h - 1):
        check("left", x, yy, x - 1, yy)
        check("right", x + w - 1, yy, x + w, yy)
    for xx in range(x + 1, x + w - 1):
        check("bottom", xx, y, xx, y - 1)
        check("top", xx, y + h - 1, xx, y + h)

    return door_list, cut_positions


def _ensure_doors(
    rooms: list[dict],
    corr_grid: Sequence[Sequence[int]],
) -> tuple[bool, list[list[tuple[int, int]]]]:
    """Assign doors to rooms if possible and return (ok, cuts)."""
    cuts: list[list[tuple[int, int]]] = []
    all_ok = True
    for room in rooms:
        doors, cut_pos = _door_candidates(room, corr_grid)
        if doors:
            side, dx, dy = doors[0]
            room["doors"].append({"side": side, "pos_x": dx, "pos_y": dy})
        else:
            all_ok = False
            if cut_pos:
                cuts.append(cut_pos)
    return all_ok, cuts


def _corridor_components(
    corr_grid: Sequence[Sequence[int]],
    params: SolveParams,
) -> list[list[tuple[int, int]]]:
    """Return corridor components not connected to the entrance."""
    gw, gh = params.grid_w, params.grid_h
    x1, x2, y1, y2 = params.entrance_bounds()

    start = [(i, j) for i in range(x1, x2) for j in range(y1, y2)]
    visited = set(start)
    q = deque(start)
    while q:
        i, j = q.popleft()
        for ni, nj in neighbors4(i, j, gw, gh):
            if corr_grid[ni][nj] and (ni, nj) not in visited:
                visited.add((ni, nj))
                q.append((ni, nj))

    components: list[list[tuple[int, int]]] = []
    for i in range(gw):
        for j in range(gh):
            if corr_grid[i][j] and (i, j) not in visited:
                comp: list[tuple[int, int]] = []
                q.append((i, j))
                visited.add((i, j))
                while q:
                    ci, cj = q.popleft()
                    comp.append((ci, cj))
                    for ni, nj in neighbors4(ci, cj, gw, gh):
                        if corr_grid[ni][nj] and (ni, nj) not in visited:
                            visited.add((ni, nj))
                            q.append((ni, nj))
                components.append(comp)
    return components


def solve(
    room_defs: list[RoomDef],
    params: SolveParams,
    progress: Progress | None = None,
    checkpoint_cb: Callable[[dict], None] | None = None,
) -> dict:
    """Solve the room placement problem under the given ``params``.

    ``progress`` is used to emit heartbeat events after each iteration.
    ``checkpoint_cb`` is invoked with the latest solution to allow
    periodic persistence.
    """
    door_cuts: list[list[tuple[int, int]]] = []
    island_cuts: list[list[tuple[int, int]]] = []

    max_rounds = getattr(params, "max_cut_rounds", getattr(params, "max_iters", 10))

    last_solution = None
    try:
        for _ in range(max_rounds):
            model, room_vars, room_cell, corr_cell = _build_model(
                room_defs, params, door_cuts, island_cuts
            )
            solver = cp_model.CpSolver()
            time_limit = getattr(params, "time_limit", 1.0)
            solver.parameters.max_time_in_seconds = float(time_limit or 1.0)
            _ = solver.parameters.max_time_in_seconds
            status = solver.solve(model)
            if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                return {
                    "rooms": [],
                    "entrance": {
                        "x1": params.entrance_x,
                        "x2": params.entrance_x + params.entrance_w,
                        "y1": params.entrance_y,
                        "y2": params.entrance_y + params.entrance_h,
                    },
                    "objective": {"room_area_total": 0},
                }

            rooms, room_grid, corr_grid, area_total = _extract_solution(
                solver, room_vars, room_cell, corr_cell
            )

            last_solution = {
                "rooms": rooms,
                "entrance": {
                    "x1": params.entrance_x,
                    "x2": params.entrance_x + params.entrance_w,
                    "y1": params.entrance_y,
                    "y2": params.entrance_y + params.entrance_h,
                },
                "objective": {"room_area_total": area_total},
            }
            if progress:
                bound = solver.best_objective_bound
                gap = None
                if bound:
                    gap = (bound - area_total) / bound
                progress.heartbeat(
                    "solve",
                    objective_best=area_total,
                    objective_bound=bound,
                    gap=gap,
                    vars=len(model.Proto().variables),
                    constraints=len(model.Proto().constraints),
                    mem_mb=_get_mem_mb(),
                )
            if checkpoint_cb:
                checkpoint_cb(last_solution)

            doors_ok, new_door_cuts = _ensure_doors(rooms, corr_grid)
            components = _corridor_components(corr_grid, params)
            if doors_ok and not components:
                return last_solution
            door_cuts.extend(new_door_cuts)
            if components:
                island_cuts.append(components[0])
    except KeyboardInterrupt:
        raise SolveInterrupted(last_solution)

    if last_solution is None:
        raise RuntimeError("CP-SAT solver failed to find a solution")
    return last_solution
