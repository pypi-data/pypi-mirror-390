"""Lightweight HTTP endpoint to expose tracker snapshots."""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable, Iterable, Sequence

from ..cycling import RateLimitRule
from ..cycling.usage_tracker import UsageTracker


@dataclass(slots=True)
class SnapshotTarget:
    provider_id: str
    model_name: str | None
    rules: Sequence[RateLimitRule]
    label: str | None = None


class _SnapshotAggregator:
    def __init__(self, tracker: UsageTracker, targets: Sequence[SnapshotTarget]) -> None:
        self._tracker = tracker
        self._targets = list(targets)

    def snapshot(self) -> dict[str, object]:
        data: dict[str, object] = {}
        for target in self._targets:
            label = target.label or self._default_label(target)
            data[label] = self._tracker.get_usage_snapshot(
                target.provider_id,
                target.model_name,
                list(target.rules),
            )
        return data

    @staticmethod
    def _default_label(target: SnapshotTarget) -> str:
        model_part = target.model_name or "global"
        return f"{target.provider_id}:{model_part}"


def start_usage_snapshot_server(
    tracker: UsageTracker,
    targets: Sequence[SnapshotTarget],
    *,
    host: str = "0.0.0.0",
    port: int = 8000,
    path: str = "/usage",
    ready_callback: Callable[[str], None] | None = None,
) -> ThreadingHTTPServer:
    aggregator = _SnapshotAggregator(tracker, targets)
    if not path.startswith("/"):
        raise ValueError("path must start with '/' for HTTP handler")
    expected_paths = {"/", path}

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 - required name
            if self.path not in expected_paths:
                self.send_response(404)
                self.end_headers()
                return
            payload = aggregator.snapshot()
            body = json.dumps(payload).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:  # noqa: A003 - inherit signature
            return

    server = ThreadingHTTPServer((host, port), Handler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    if ready_callback:
        ready_callback(f"http://{host}:{server.server_port}{path}")

    return server


__all__ = ["SnapshotTarget", "start_usage_snapshot_server"]
