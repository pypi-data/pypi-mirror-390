from __future__ import annotations

import unittest

from central_tools.cycling.api_cycler import RateLimitRule
from central_tools.cycling.redis_tracker import RedisUsageTracker


class FakeClock:
    def __init__(self) -> None:
        self.value = 0.0

    def now(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        self.value += seconds


class FakeRedis:
    def __init__(self, now_func) -> None:
        self._store: dict[str, int] = {}
        self._expiry: dict[str, float] = {}
        self._now = now_func

    def mget(self, keys):
        self._prune()
        return [self._store.get(key) for key in keys]

    def incrby(self, key, amount):
        self._prune()
        current = int(self._store.get(key, 0))
        current += amount
        self._store[key] = current
        return current

    def expire(self, key, ttl):
        self._prune()
        self._expiry[key] = self._now() + ttl
        return True

    def get(self, key):
        self._prune()
        return self._store.get(key)

    def ttl(self, key):
        self._prune()
        if key not in self._store:
            return -2
        expires_at = self._expiry.get(key)
        if expires_at is None:
            return -1
        remaining = int(expires_at - self._now())
        return remaining if remaining >= 0 else -2

    def _prune(self) -> None:
        now = self._now()
        expired = [key for key, ts in self._expiry.items() if ts <= now]
        for key in expired:
            self._store.pop(key, None)
            self._expiry.pop(key, None)


class RedisUsageTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.clock = FakeClock()
        self.client = FakeRedis(self.clock.now)
        self.tracker = RedisUsageTracker(self.client, time_func=self.clock.now, use_pipeline=False)
        self.rule = RateLimitRule(name="per_minute", period_seconds=60, max_calls=2, max_tokens=100)

    def test_reserve_and_record_enforce_limits(self) -> None:
        self.assertTrue(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=40))
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "success",
            tokens_used=30,
            rules=[self.rule],
            reserved_tokens=40,
        )

        self.assertTrue(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=50))
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "success",
            tokens_used=70,
            rules=[self.rule],
            reserved_tokens=50,
        )

        self.assertFalse(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=10))

    def test_limits_reset_after_window(self) -> None:
        self.assertTrue(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=30))
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "success",
            tokens_used=30,
            rules=[self.rule],
            reserved_tokens=30,
        )

        self.assertTrue(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=60))
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "success",
            tokens_used=60,
            rules=[self.rule],
            reserved_tokens=60,
        )

        self.assertFalse(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=1))

        # Advance beyond the TTL (period + padding) so the counters expire.
        self.clock.advance(70)
        self.assertTrue(self.tracker.reserve("google", "gemini", "k1", [self.rule], expected_tokens=50))

    def test_snapshot_reports_usage(self) -> None:
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "success",
            tokens_used=25,
            rules=[self.rule],
            reserved_tokens=25,
        )
        snapshot = self.tracker.get_usage_snapshot("google", "gemini", [self.rule])
        self.assertIn("per_minute", snapshot)
        self.assertEqual(snapshot["per_minute"]["calls"], 1)
        self.assertEqual(snapshot["per_minute"].get("tokens"), 25)
        self.assertIn("calls_ttl", snapshot["per_minute"])
        self.assertGreater(snapshot["per_minute"]["calls_ttl"], 0)
        self.assertGreater(snapshot["statuses"].get("success", 0), 0)
        self.assertIn("statuses_ttl", snapshot)
        self.assertIn("success", snapshot["statuses_ttl"])

    def test_reserved_tokens_used_when_actual_zero(self) -> None:
        self.tracker.record(
            "google",
            "gemini",
            "k1",
            "failure",
            tokens_used=0,
            rules=[self.rule],
            reserved_tokens=40,
        )
        snapshot = self.tracker.get_usage_snapshot("google", "gemini", [self.rule])
        self.assertEqual(snapshot["per_minute"].get("tokens"), 40)


if __name__ == "__main__":
    unittest.main()
