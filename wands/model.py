"""Domain models for the Wands solver."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Door:
    """Door on a room wall leading into the corridor."""

    side: str
    pos_x: int
    pos_y: int


@dataclass
class Room:
    """Placed room with doors."""

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
