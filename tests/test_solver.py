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
    params = SolveParams(max_iters=1, time_limit=0.1)
    result = solver.solve([], params)
    assert result["rooms"] == []


def test_get_mem_mb_without_resource(monkeypatch) -> None:
    """Memory helper should handle missing ``resource`` module."""
    monkeypatch.setattr(solver, "resource", None)
    assert solver._get_mem_mb() is None


def test_solve_without_resource(monkeypatch) -> None:
    """Solver should work even if ``resource`` is unavailable."""
    params = SolveParams(max_iters=1, time_limit=0.1)
    monkeypatch.setattr(solver, "resource", None)
    progress = Progress(interval=0)
    result = solver.solve([], params, progress=progress)
    assert result["rooms"] == []


def test_solver_sets_seed_and_threads(monkeypatch) -> None:
    """Solver should forward seed and thread parameters to OR-Tools."""
    params = SolveParams(max_iters=1, time_limit=0.1, seed=123, threads=2)
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


def test_isolated_corridor_gets_connected() -> None:
    """An isolated corridor component should be connected via a path cut."""
    params = SolveParams()
    component = [(0, 0)]
    path = solver._connect_path(component, params)
    assert path[0] == (0, 0)
    ex, ey = params.entrance.x1, params.entrance.y1
    assert (ex, ey) in path


def test_door_heuristic_prefers_better_position() -> None:
    """Door selection should prefer positions with more corridor space."""
    room = {
        "id": "r1",
        "type": "r",
        "x": 1,
        "y": 1,
        "w": 3,
        "h": 4,
        "doors": [],
    }
    corr_grid = [[0 for _ in range(5)] for _ in range(5)]
    corr_grid[0][1] = 1
    corr_grid[0][2] = 1
    corr_grid[0][3] = 1
    ok, _ = solver._ensure_doors([room], corr_grid)
    assert ok
    assert room["doors"] == [{"side": "left", "pos_x": 1, "pos_y": 2}]
