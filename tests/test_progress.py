"""Tests for the progress module."""

import io
import json

from wands.progress import Progress, ProgressEvent


def test_progress_event_creation():
    """ProgressEvent stores provided data."""
    event = ProgressEvent(ts="0", phase="solve", runtime_sec=1.0, vars=10)
    assert event.phase == "solve"
    assert event.vars == 10

def test_progress_text_and_interval():
    """Heartbeat respects interval and emits final event."""
    buf = io.StringIO()
    prog = Progress(stream=buf, fmt="text", interval=1)
    prog.heartbeat("solve", objective_best=1.0, objective_bound=2.0, gap=0.5, vars=1, constraints=2, mem_mb=3.0)
    first = buf.getvalue()
    prog.heartbeat("solve", objective_best=2.0)
    assert buf.getvalue() == first
    prog.done("finish")
    assert "finish" in buf.getvalue().splitlines()[-1]

def test_progress_json_output():
    """JSON format produces serializable output."""
    buf = io.StringIO()
    prog = Progress(stream=buf, fmt="json", interval=0)
    prog.heartbeat("start", vars=3)
    data = json.loads(buf.getvalue())
    assert data["phase"] == "start"
    assert data["vars"] == 3


def test_progress_includes_stats() -> None:
    """Progress output includes detailed statistics."""
    buf = io.StringIO()
    prog = Progress(stream=buf, fmt="text", interval=0)
    prog.heartbeat(
        "solve",
        objective_best=1.0,
        objective_bound=2.0,
        gap=0.5,
        vars=4,
        constraints=5,
        mem_mb=6.0,
    )
    out = buf.getvalue()
    assert "bound=2.0" in out
    assert "gap=0.5" in out
    assert "vars=4" in out
    assert "cons=5" in out
    assert "mem=6.0MB" in out
