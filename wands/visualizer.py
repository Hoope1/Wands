"""Render a solution grid using Pillow.

The visualizer draws a light grid, colors rooms by group and marks doors as short black
wall segments. The entrance area is filled in dark gray.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from PIL import Image, ImageDraw, ImageFont

SCALE = 10

# soft color palette by room group
GROUP_COLORS: Dict[str, tuple[int, int, int]] = {
    "Dev": (173, 216, 230),  # light blue
    "QA": (144, 238, 144),  # light green
    "Research": (224, 255, 255),  # light cyan
    "Production": (255, 200, 0),  # orange
    "Storage": (210, 180, 140),  # tan
    "Studio": (216, 191, 216),  # lavender
    "Admin": (255, 182, 193),  # light pink
    "Marketing": (255, 255, 102),  # yellow
    "Support": (221, 160, 221),  # plum
    "Console": (255, 160, 122),  # salmon
    "Server": (250, 128, 114),  # light coral
    "Training": (152, 251, 152),  # pale green
    "Facilities": (255, 228, 181),  # wheat
}
DEFAULT_ROOM_COLOR = (200, 200, 200)


def render(solution: Dict[str, Any], out_path: str | Path, scale: int = SCALE) -> None:
    """Render ``solution`` as PNG to ``out_path``."""
    grid_w = int(solution.get("grid_w", 77))
    grid_h = int(solution.get("grid_h", 50))
    img = Image.new("RGB", (grid_w * scale, grid_h * scale), "white")
    draw = ImageDraw.Draw(img)

    # rooms
    for room in solution.get("rooms", []):
        color = GROUP_COLORS.get(room.get("type"), DEFAULT_ROOM_COLOR)
        x1 = room["x"] * scale
        y1 = (grid_h - (room["y"] + room["h"])) * scale
        x2 = (room["x"] + room["w"]) * scale
        y2 = (grid_h - room["y"]) * scale
        draw.rectangle((x1, y1, x2, y2), fill=color)

    # entrance
    ent = solution.get("entrance", {})
    ex1 = ent.get("x1", 0)
    ex2 = ent.get("x2", 0)
    ey1 = ent.get("y1", 0)
    ey2 = ent.get("y2", 0)
    draw.rectangle(
        (ex1 * scale, (grid_h - ey2) * scale, ex2 * scale, (grid_h - ey1) * scale),
        fill="darkgray",
    )

    # grid lines
    for x in range(grid_w + 1):
        xp = x * scale
        draw.line([(xp, 0), (xp, grid_h * scale)], fill="lightgray", width=1)
    for y in range(grid_h + 1):
        yp = y * scale
        draw.line(
            [(0, grid_h * scale - yp), (grid_w * scale, grid_h * scale - yp)],
            fill="lightgray",
            width=1,
        )

    # doors
    for room in solution.get("rooms", []):
        for door in room.get("doors", []):
            side = door.get("side")
            px = int(door.get("pos_x"))
            py = int(door.get("pos_y"))
            if side in {"left", "right"}:
                x_pix = px * scale
                y1 = (grid_h - py) * scale
                y2 = (grid_h - (py + 1)) * scale
                draw.line([(x_pix, y1), (x_pix, y2)], fill="black", width=1)
            elif side in {"top", "bottom"}:
                y_pix = (grid_h - py) * scale
                x1 = px * scale
                x2 = (px + 1) * scale
                draw.line([(x1, y_pix), (x2, y_pix)], fill="black", width=1)

    # axis labels every 10 cells
    font = ImageFont.load_default()
    for x in range(0, grid_w + 1, 10):
        draw.text((x * scale + 1, grid_h * scale - 10), str(x), fill="black", font=font)
    for y in range(0, grid_h + 1, 10):
        draw.text((1, (grid_h - y - 1) * scale + 1), str(y), fill="black", font=font)

    img.save(Path(out_path))
