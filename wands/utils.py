"""Utility functions for grid operations."""

from __future__ import annotations

from collections.abc import Iterator


def windows_covering_cell(
    i: int, j: int, grid_w: int, grid_h: int, win: int
) -> list[tuple[int, int]]:
    """Return all top-left anchors for ``win``×``win`` windows covering ``(i, j)``.

    Only windows fully contained in the grid are considered. Coordinates are
    zero-based with ``0 <= i < grid_w`` and ``0 <= j < grid_h``.
    """
    if not (0 <= i < grid_w and 0 <= j < grid_h):
        return []

    anchors: list[tuple[int, int]] = []
    a_min = max(0, i - win + 1)
    a_max = min(i, grid_w - win)
    b_min = max(0, j - win + 1)
    b_max = min(j, grid_h - win)
    for a in range(a_min, a_max + 1):
        for b in range(b_min, b_max + 1):
            anchors.append((a, b))
    return anchors


def iter_window_cells(a: int, b: int, win: int) -> Iterator[tuple[int, int]]:
    """Iterate over all cells within a ``win``×``win`` window starting at ``(a, b)``."""
    for x in range(a, a + win):
        for y in range(b, b + win):
            yield (x, y)


def neighbors4(i: int, j: int, grid_w: int, grid_h: int) -> list[tuple[int, int]]:
    """Return the four-neighbourhood of ``(i, j)`` within the grid bounds."""
    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    neighbours: list[tuple[int, int]] = []
    for di, dj in deltas:
        ni, nj = i + di, j + dj
        if 0 <= ni < grid_w and 0 <= nj < grid_h:
            neighbours.append((ni, nj))
    return neighbours
