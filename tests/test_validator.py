import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from wands.validator import validate


def test_validate_empty_solution_valid():
    solution = {"rooms": [], "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50}}
    report = validate(solution)
    assert report["valid"] is True


def test_validate_overlap_fail():
    solution = {
        "rooms": [
            {"id": "a", "type": "A", "x": 0, "y": 0, "w": 10, "h": 10, "doors": [{"side": "right", "pos_x": 10, "pos_y": 5}]},
            {"id": "b", "type": "B", "x": 5, "y": 5, "w": 10, "h": 10, "doors": [{"side": "left", "pos_x": 5, "pos_y": 10}]},
        ],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    assert report["no_overlap"] is False
    assert report["valid"] is False


def test_validate_corridor_width_fail():
    room = {"id": "r", "type": "T", "x": 3, "y": 3, "w": 71, "h": 44, "doors": [{"side": "left", "pos_x": 3, "pos_y": 20}]}
    solution = {"rooms": [room], "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50}}
    report = validate(solution)
    assert report["corridor_width"] is False
    assert report["valid"] is False
