"""Simplified CP-SAT based solver.

The current implementation builds a CP-SAT model that reserves the fixed
entrance block and ensures that rooms stay within the 77×50 grid. It does not
yet optimise or avoid room overlap but lays the foundation for further
development.
"""

from __future__ import annotations

from typing import List

from ortools.sat.python import cp_model

from .model import Entrance, RoomDef

GRID_W = 77
GRID_H = 50


def solve(room_defs: List[RoomDef], seed: int | None = None) -> dict:
    """Solve the room placement problem with minimal constraints.

    Parameters
    ----------
    room_defs:
        The list of room definitions to place.
    seed:
        Optional RNG seed for deterministic behaviour.
    """
    model = cp_model.CpModel()
    solver = cp_model.CpSolver()
    if seed is not None:
        solver.parameters.random_seed = seed

    entrance = Entrance()
    variables = []
    for idx, rdef in enumerate(room_defs):
        x = model.new_int_var(0, GRID_W - rdef.min_w, f"x_{idx}")
        y = model.new_int_var(0, GRID_H - rdef.min_h, f"y_{idx}")
        w = model.new_int_var(rdef.min_w, rdef.pref_w, f"w_{idx}")
        h = model.new_int_var(rdef.min_h, rdef.pref_h, f"h_{idx}")
        model.add(x + w <= GRID_W)
        model.add(y + h <= GRID_H)

        left = model.new_bool_var(f"left_{idx}")
        right = model.new_bool_var(f"right_{idx}")
        below = model.new_bool_var(f"below_{idx}")
        above = model.new_bool_var(f"above_{idx}")
        model.add(x + w <= entrance.x1).only_enforce_if(left)
        model.add(x >= entrance.x2).only_enforce_if(right)
        model.add(y + h <= entrance.y1).only_enforce_if(below)
        model.add(y >= entrance.y2).only_enforce_if(above)
        model.add_bool_or([left, right, below, above])
        variables.append((rdef, x, y, w, h))

    status = solver.solve(model)
    rooms = []
    area_total = 0
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        for rdef, x, y, w, h in variables:
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
            area_total += vw * vh

    solution = {
        "rooms": rooms,
        "entrance": {
            "x1": entrance.x1,
            "x2": entrance.x2,
            "y1": entrance.y1,
            "y2": entrance.y2,
        },
        "objective": {"room_area_total": area_total},
    }
    return solution
