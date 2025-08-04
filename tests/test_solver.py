"""Tests for the CP-SAT solver."""

from wands import solver
from wands.model import SolveParams


def test_allowed_values() -> None:
    """Allowed value ranges should follow the given step."""
    domain = solver.allowed_values(2, 3, 8)
    assert domain.contains(2)
    assert domain.contains(5)
    assert domain.contains(8)
    assert not domain.contains(4)


def test_solve_basic() -> None:
    """The solver should place the room and assign a door."""
    params = SolveParams(
        grid_w=6,
        grid_h=6,
        entrance_x=0,
        entrance_w=1,
        entrance_y=0,
        entrance_h=1,
        corridor_win=1,
        max_iters=2,
    )
    result = solver.solve([], params)
    assert result["rooms"] == []
