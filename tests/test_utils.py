"""Tests for grid utility functions."""

from __future__ import annotations

from wands.utils import iter_window_cells, neighbors4, windows_covering_cell


def test_windows_covering_cell() -> None:
    """Find anchors for windows covering a specific cell."""
    anchors = windows_covering_cell(1, 1, grid_w=5, grid_h=5, win=3)
    assert set(anchors) == {(0, 0), (0, 1), (1, 0), (1, 1)}


def test_iter_window_cells() -> None:
    """Iterate over every cell in a window."""
    cells = list(iter_window_cells(1, 1, 2))
    assert set(cells) == {(1, 1), (1, 2), (2, 1), (2, 2)}


def test_neighbors4() -> None:
    """Return four-neighbourhood within grid bounds."""
    assert neighbors4(0, 0, 3, 3) == [(1, 0), (0, 1)]
    assert set(neighbors4(1, 1, 3, 3)) == {(0, 1), (2, 1), (1, 0), (1, 2)}
