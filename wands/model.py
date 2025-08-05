"""Domain models for the Wands solver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional

__all__ = [
    "Door",
    "RoomPlacement",
    "Entrance",
    "RoomDef",
    "SolveParams",
]


@dataclass
class Door:
    """Door on a room wall leading into the corridor."""

    side: str
    pos_x: int
    pos_y: int


@dataclass
class RoomPlacement:
    """A concrete placement of a room in the grid."""

    id: str
    type: str
    x: int
    y: int
    w: int
    h: int
    doors: List[Door] = field(default_factory=list)


@dataclass
class Entrance:
    """Fixed entrance block."""

    x1: int = 56
    x2: int = 60
    y1: int = 40
    y2: int = 50


@dataclass
class RoomDef:
    """Definition of a room type to be placed."""

    name: str
    group: str
    pref_w: int
    pref_h: int
    min_w: int
    min_h: int
    step_w: int
    step_h: int
    priority: int
    efficiency_factor: float
    duplicate_id: Optional[str] = None


@dataclass
class SolveParams:
    """Solver parameters and fixed problem constants."""

    grid_w: int = 77
    grid_h: int = 50
    entrance_x: int = 56
    entrance_w: int = 4
    entrance_y: int = 40
    entrance_h: int = 10
    corridor_win: int = 4
    max_iters: int = 1000
    max_cut_rounds: int = 10
    time_limit: int | None = None
    seed: int | None = None
    threads: int | None = None

    def entrance_bounds(self) -> tuple[int, int, int, int]:
        """Return entrance bounds as ``(x1, x2, y1, y2)``."""
        x1 = self.entrance_x
        x2 = self.entrance_x + self.entrance_w
        y1 = self.entrance_y
        y2 = self.entrance_y + self.entrance_h
        return x1, x2, y1, y2


if TYPE_CHECKING:  # pragma: no cover - for vulture
    _door_dummy = Door("left", 0, 0)
    _door_dummy.pos_x
    _door_dummy.pos_y
    _room_dummy = RoomPlacement("", "", 0, 0, 0, 0, [])
    _room_dummy.id
    _room_dummy.type
    _entrance_dummy = Entrance()
    _def_dummy = RoomDef("", "", 0, 0, 0, 0, 0, 0, 0, 0.0)
    _def_dummy.priority
    _def_dummy.efficiency_factor
    _def_dummy.duplicate_id
