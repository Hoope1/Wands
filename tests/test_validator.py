"""Tests for the validator module."""

from wands.validator import validate


def test_validate_empty_solution_valid() -> None:
    """Empty solution should pass all checks."""
    solution = {
        "rooms": [],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    for key in (
        "complement",
        "entrance_area",
        "no_overlap",
        "corridor_width",
        "corridor_connectivity",
        "doors",
    ):
        assert report[key]["pass"] is True


def test_validate_overlap_fail() -> None:
    """Overlapping rooms must fail the overlap check."""
    room_a = {
        "id": "a",
        "type": "A",
        "x": 0,
        "y": 0,
        "w": 10,
        "h": 10,
        "doors": [{"side": "right", "pos_x": 10, "pos_y": 5}],
    }
    room_b = {
        "id": "b",
        "type": "B",
        "x": 5,
        "y": 5,
        "w": 10,
        "h": 10,
        "doors": [{"side": "left", "pos_x": 5, "pos_y": 10}],
    }
    solution = {
        "rooms": [room_a, room_b],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    assert report["no_overlap"]["pass"] is False


def test_validate_corridor_width_fail() -> None:
    """Corridor width below threshold should fail validation."""
    room = {
        "id": "r",
        "type": "T",
        "x": 3,
        "y": 3,
        "w": 71,
        "h": 44,
        "doors": [{"side": "left", "pos_x": 3, "pos_y": 20}],
    }
    solution = {
        "rooms": [room],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    assert report["corridor_width"]["pass"] is False


def test_validate_corridor_connectivity_fail() -> None:
    """Disconnected corridor components should fail validation."""
    room_a = {
        "id": "a",
        "type": "A",
        "x": 1,
        "y": 0,
        "w": 10,
        "h": 2,
        "doors": [{"side": "right", "pos_x": 11, "pos_y": 1}],
    }
    room_b = {
        "id": "b",
        "type": "B",
        "x": 0,
        "y": 1,
        "w": 11,
        "h": 49,
        "doors": [{"side": "right", "pos_x": 11, "pos_y": 25}],
    }
    solution = {
        "rooms": [room_a, room_b],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    assert report["corridor_connectivity"]["pass"] is False


def test_validate_missing_door_fail() -> None:
    """Rooms without doors should fail door validation."""
    room = {
        "id": "r",
        "type": "T",
        "x": 10,
        "y": 10,
        "w": 6,
        "h": 6,
        "doors": [],
    }
    solution = {
        "rooms": [room],
        "entrance": {"x1": 56, "x2": 60, "y1": 40, "y2": 50},
    }
    report = validate(solution)
    assert report["doors"]["pass"] is False
