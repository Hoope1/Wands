"""Minimal visualisation of a solution using Pillow."""

from __future__ import annotations

from pathlib import Path
from typing import Dict

from PIL import Image, ImageDraw


SCALE = 10
GRID_W, GRID_H = 77, 50


def render(solution: Dict, out_path: str | Path) -> None:
    """Render the solution as PNG.

    Rooms are drawn in blue, the entrance block in light gray.
    """
    img = Image.new("RGB", (GRID_W * SCALE, GRID_H * SCALE), "white")
    draw = ImageDraw.Draw(img)

    # Entrance
    ent = solution["entrance"]
    draw.rectangle(
        [
            ent["x1"] * SCALE,
            (GRID_H - ent["y2"]) * SCALE,
            ent["x2"] * SCALE,
            (GRID_H - ent["y1"]) * SCALE,
        ],
        fill="lightgray",
        outline="black",
    )

    # Rooms
    for room in solution.get("rooms", []):
        draw.rectangle(
            [
                room["x"] * SCALE,
                (GRID_H - (room["y"] + room["h"])) * SCALE,
                (room["x"] + room["w"]) * SCALE,
                (GRID_H - room["y"]) * SCALE,
            ],
            fill="lightblue",
            outline="blue",
        )
        for door in room.get("doors", []):
            dx, dy = door["pos_x"] * SCALE, (GRID_H - door["pos_y"]) * SCALE
            draw.rectangle([dx - 1, dy - 1, dx + 1, dy + 1], fill="red")

    img.save(Path(out_path))
