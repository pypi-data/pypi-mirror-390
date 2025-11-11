from __future__ import annotations

import json
import unittest
import urllib.error
import urllib.request

from central_tools.cycling.api_cycler import RateLimitRule
from central_tools.monitoring import SnapshotTarget, start_usage_snapshot_server


class DummyTracker:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str | None]] = []

    def get_usage_snapshot(self, provider_id: str, model_name: str | None, rules):
        self.calls.append((provider_id, model_name))
        return {
            "per_minute": {
                "calls": 3,
                "tokens": 120,
                "calls_ttl": 50,
            }
        }


class UsageSnapshotServerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = RateLimitRule(name="per_minute", period_seconds=60, max_calls=100)
        self.tracker = DummyTracker()

    def test_http_endpoint_returns_snapshot(self) -> None:
        server = start_usage_snapshot_server(
            tracker=self.tracker,
            targets=[SnapshotTarget(provider_id="google", model_name="gemini", rules=[self.rule])],
            host="127.0.0.1",
            port=0,
            path="/usage",
        )
        try:
            url = f"http://127.0.0.1:{server.server_port}/usage"
            with urllib.request.urlopen(url, timeout=2) as response:
                self.assertEqual(response.status, 200)
                payload = json.loads(response.read())
            self.assertIn("google:gemini", payload)
            self.assertEqual(payload["google:gemini"]["per_minute"]["calls"], 3)
            self.assertEqual(self.tracker.calls, [("google", "gemini")])
        finally:
            server.shutdown()
            server.server_close()

    def test_unknown_path_returns_404(self) -> None:
        server = start_usage_snapshot_server(
            tracker=self.tracker,
            targets=[SnapshotTarget(provider_id="google", model_name=None, rules=[self.rule])],
            host="127.0.0.1",
            port=0,
        )
        try:
            url = f"http://127.0.0.1:{server.server_port}/other"
            with self.assertRaises(urllib.error.HTTPError) as ctx:
                urllib.request.urlopen(url, timeout=2)
            self.assertEqual(ctx.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    unittest.main()
