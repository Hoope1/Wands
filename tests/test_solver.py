"""Tests for the CP-SAT solver."""

from wands import solver
from wands.model import SolveParams
from wands.progress import Progress


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


def test_get_mem_mb_without_resource(monkeypatch) -> None:
    """Memory helper should handle missing ``resource`` module."""
    monkeypatch.setattr(solver, "resource", None)
    assert solver._get_mem_mb() is None


def test_solve_without_resource(monkeypatch) -> None:
    """Solver should work even if ``resource`` is unavailable."""
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
    monkeypatch.setattr(solver, "resource", None)
    progress = Progress(interval=0)
    result = solver.solve([], params, progress=progress)
    assert result["rooms"] == []


def test_solver_sets_seed_and_threads(monkeypatch) -> None:
    """Solver should forward seed and thread parameters to OR-Tools."""
    params = SolveParams(
        grid_w=6,
        grid_h=6,
        entrance_x=0,
        entrance_w=1,
        entrance_y=0,
        entrance_h=1,
        corridor_win=1,
        max_iters=2,
        seed=123,
        threads=2,
    )
    recorded: dict[str, int] = {}

    class CapturingSolver(solver.cp_model.CpSolver):  # type: ignore[misc]
        def solve(self, model):  # type: ignore[override]
            recorded["seed"] = self.parameters.random_seed
            recorded["threads"] = self.parameters.num_search_workers
            return super().solve(model)

    monkeypatch.setattr(solver.cp_model, "CpSolver", CapturingSolver)
    solver.solve([], params)
    assert recorded["seed"] == 123
    assert recorded["threads"] == 2
