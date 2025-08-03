"""Configuration loading utilities."""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

import yaml

from .model import RoomDef


def load_room_defs(path: str | Path) -> List[RoomDef]:
    """Load room definitions from a YAML or JSON file.

    The file must contain a list of room definition objects as described in
    :class:`RoomDef`.
    """
    file_path = Path(path)
    text = file_path.read_text(encoding="utf8")
    data = (
        yaml.safe_load(text)
        if file_path.suffix in {".yml", ".yaml"}
        else json.loads(text)
    )
    room_defs: List[RoomDef] = []
    for item in data:
        room_defs.append(RoomDef(**item))
    return room_defs
