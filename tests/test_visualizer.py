"""Tests for the visualizer module."""

from pathlib import Path
from typing import cast

from PIL import Image

from wands.visualizer import render


def test_render_creates_image(tmp_path: Path) -> None:
    """Rendering produces an image file of the expected size."""
    solution = {
        "grid_w": 5,
        "grid_h": 5,
        "entrance": {"x1": 4, "x2": 5, "y1": 4, "y2": 5},
        "rooms": [
            {
                "id": "r1",
                "type": "Dev",
                "x": 0,
                "y": 0,
                "w": 3,
                "h": 3,
                "doors": [{"side": "right", "pos_x": 3, "pos_y": 1}],
            }
        ],
    }
    out = tmp_path / "sol.png"
    render(solution, out)
    assert out.exists()
    img = Image.open(out)
    grid_w = cast(int, solution["grid_w"])
    grid_h = cast(int, solution["grid_h"])
    assert img.size == (grid_w * 10, grid_h * 10)
