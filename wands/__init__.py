"""Wands package providing room planning utilities."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version
from pathlib import Path

try:
    __version__ = version("wands")
except PackageNotFoundError:  # pragma: no cover - fallback for local runs
    try:
        try:
            import tomllib  # type: ignore[import-not-found]
        except ModuleNotFoundError:  # pragma: no cover - python<3.11
            import tomli as tomllib  # type: ignore
        project = Path(__file__).resolve().parent.parent / "pyproject.toml"
        with project.open("rb") as f:
            __version__ = tomllib.load(f)["project"]["version"]
    except Exception:  # pragma: no cover - ultimate fallback
        __version__ = "0.0.0"

__all__ = ["__version__"]
