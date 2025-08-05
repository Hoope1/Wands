"""Tests for data model classes."""

from wands.model import Door, Entrance, RoomDef, RoomPlacement, SolveParams


def test_dataclass_instantiation() -> None:
    """Basic instantiation and attribute access should work."""
    door = Door("left", 1, 2)
    placement = RoomPlacement("r1", "office", 0, 0, 3, 3, [door])
    entrance = Entrance()
    rdef = RoomDef("office", "g1", 3, 3, 2, 2, 1, 1, 1, 1.0)
    params = SolveParams()

    assert placement.doors == [door]
    assert entrance.x2 - entrance.x1 == 4
    assert rdef.name == "office"
    assert params.grid_w == 77
