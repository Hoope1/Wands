"""Kompakter Raum-Layout-Solver mit einfachem Korridor."""

from __future__ import annotations

from collections import deque
from pathlib import Path
from typing import Any, Deque, Dict, List, Tuple

import matplotlib.pyplot as plt
import yaml


def load_config(path: str | Path) -> Dict[str, Any]:
    """Lade die Raumdefinitionen aus einer YAML-Datei."""
    return yaml.safe_load(Path(path).read_text(encoding="utf8"))


def solve(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Platziere die Räume sequenziell mit 1-Zellen-Korridor."""
    width = int(cfg["grid"]["width"])
    height = int(cfg["grid"]["height"])
    entrance = cfg["entrance"]
    rooms = sorted(cfg["rooms"], key=lambda r: r["pref_w"] * r["pref_h"], reverse=True)
    grid = [[False] * width for _ in range(height)]
    placements: List[Dict[str, int]] = []

    def intersects_entrance(x: int, y: int, w: int, h: int) -> bool:
        ex, ey = entrance["x"], entrance["y"]
        ew, eh = entrance["width"], entrance["height"]
        return not (x + w <= ex or x >= ex + ew or y + h <= ey or y >= ey + eh)

    def free(x: int, y: int, w: int, h: int) -> bool:
        if x < 0 or y < 0 or x + w > width or y + h > height:
            return False
        if intersects_entrance(x, y, w, h):
            return False
        for yy in range(y - 1, y + h + 1):
            for xx in range(x - 1, x + w + 1):
                if 0 <= xx < width and 0 <= yy < height and grid[yy][xx]:
                    return False
        return True

    def place(room: Dict[str, Any]) -> Dict[str, int]:
        sizes: List[Tuple[int, int]] = []
        for w in range(room["pref_w"], room["min_w"] - 1, -room["step_w"]):
            for h in range(room["pref_h"], room["min_h"] - 1, -room["step_h"]):
                sizes.append((w, h))
        for w, h in sizes:
            for y in range(height - h + 1):
                for x in range(width - w + 1):
                    if free(x, y, w, h):
                        for yy in range(y, y + h):
                            for xx in range(x, x + w):
                                grid[yy][xx] = True
                        return {"name": room["name"], "x": x, "y": y, "w": w, "h": h}
        raise RuntimeError(f"{room['name']} passt nicht")

    for room in rooms:
        placements.append(place(room))

    return {"grid": cfg["grid"], "entrance": entrance, "rooms": placements}


def validate(sol: Dict[str, Any]) -> List[str]:
    """Prüfe Überlappung und Erreichbarkeit über freie Felder."""
    width = sol["grid"]["width"]
    height = sol["grid"]["height"]
    ex, ey = sol["entrance"]["x"], sol["entrance"]["y"]
    ew, eh = sol["entrance"]["width"], sol["entrance"]["height"]
    grid = [[0] * width for _ in range(height)]
    msgs: List[str] = []
    for room in sol["rooms"]:
        x, y, w, h = room["x"], room["y"], room["w"], room["h"]
        if x < 0 or y < 0 or x + w > width or y + h > height:
            msgs.append(f"{room['name']} liegt außerhalb des Gitters")
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                if grid[yy][xx]:
                    msgs.append(f"Überlappung bei {room['name']}")
                grid[yy][xx] = 1

    # BFS über freie Felder
    start: Deque[Tuple[int, int]] = deque()
    seen = [[False] * width for _ in range(height)]
    for yy in range(ey, ey + eh):
        for xx in range(ex, ex + ew):
            start.append((xx, yy))
            seen[yy][xx] = True
    while start:
        x, y = start.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                if not seen[ny][nx] and not grid[ny][nx]:
                    seen[ny][nx] = True
                    start.append((nx, ny))

    for room in sol["rooms"]:
        connected = False
        for yy in range(room["y"] - 1, room["y"] + room["h"] + 1):
            for xx in range(room["x"] - 1, room["x"] + room["w"] + 1):
                if 0 <= xx < width and 0 <= yy < height:
                    if not grid[yy][xx] and seen[yy][xx]:
                        connected = True
        if not connected:
            msgs.append(f"{room['name']} ist nicht erreichbar")

    if not msgs:
        msgs.append("OK")
    return msgs


def render(sol: Dict[str, Any], path: str | Path) -> None:
    """Erzeuge ein farbiges PNG der Lösung."""
    width = sol["grid"]["width"]
    height = sol["grid"]["height"]
    img = [[1.0, 1.0, 1.0] for _ in range(width * height)]
    colors = plt.cm.get_cmap("tab20", len(sol["rooms"]))
    for idx, room in enumerate(sol["rooms"]):
        color = colors(idx)[:3]
        for yy in range(room["y"], room["y"] + room["h"]):
            for xx in range(room["x"], room["x"] + room["w"]):
                img[yy * width + xx] = list(color)
    data = [img[i * width : (i + 1) * width] for i in range(height)]
    plt.imsave(path, data)
