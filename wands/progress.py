"""Progress reporting utilities."""

import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Optional, TextIO


@dataclass
class ProgressEvent:
    """Represents a progress update for the solving process."""

    ts: str
    phase: str
    runtime_sec: float
    eta_sec: Optional[float] = None
    objective_best: Optional[float] = None
    objective_bound: Optional[float] = None
    gap: Optional[float] = None
    vars: Optional[int] = None
    constraints: Optional[int] = None
    mem_mb: Optional[float] = None
    note: Optional[str] = None


class Progress:
    """Emit progress updates in text or JSON lines format."""

    def __init__(
        self,
        stream: Optional[TextIO] = None,
        fmt: str = "text",
        interval: float = 1.0,
    ) -> None:
        """Initialize the progress reporter."""
        self.stream = stream if stream is not None else sys.stdout
        self.fmt = fmt
        self.interval = interval
        self._start = time.time()
        self._last = 0.0

    def _write(self, event: ProgressEvent) -> None:
        if self.fmt == "json":
            self.stream.write(json.dumps(asdict(event), ensure_ascii=False) + "\n")
        else:
            parts = [
                event.ts,
                event.phase,
                f"t={event.runtime_sec:.3f}s",
            ]
            if event.eta_sec is not None:
                parts.append(f"eta={event.eta_sec:.3f}s")
            if event.objective_best is not None:
                parts.append(f"best={event.objective_best}")
            if event.objective_bound is not None:
                parts.append(f"bound={event.objective_bound}")
            if event.gap is not None:
                parts.append(f"gap={event.gap}")
            if event.vars is not None:
                parts.append(f"vars={event.vars}")
            if event.constraints is not None:
                parts.append(f"cons={event.constraints}")
            if event.mem_mb is not None:
                parts.append(f"mem={event.mem_mb:.1f}MB")
            if event.note:
                parts.append(event.note)
            self.stream.write(" ".join(parts) + "\n")
        self.stream.flush()

    def heartbeat(self, phase: str, **data: Any) -> None:
        """Emit a progress event if the interval has elapsed."""
        now = time.time()
        if now - self._last < self.interval:
            return
        self._last = now
        event = ProgressEvent(
            ts=datetime.utcnow().isoformat(),
            phase=phase,
            runtime_sec=now - self._start,
            **data,
        )
        self._write(event)

    def done(self, phase: str = "finish", **data: Any) -> None:
        """Emit a final progress event without interval restriction."""
        now = time.time()
        self._last = now
        event = ProgressEvent(
            ts=datetime.utcnow().isoformat(),
            phase=phase,
            runtime_sec=now - self._start,
            **data,
        )
        self._write(event)
