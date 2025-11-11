from __future__ import annotations

import unittest

from central_tools.cycling.api_cycler import APIKeyCycler
from central_tools.integrations.redis_tracker import RedisConfig, attach_usage_tracker, build_usage_tracker
from central_tools.cycling.usage_tracker import UsageTracker


class DummyRedisClient:
    def mget(self, keys):
        return [0 for _ in keys]

    def incrby(self, key, amount):  # pragma: no cover - unused in this test
        return 0

    def expire(self, key, ttl):  # pragma: no cover - unused in this test
        return True


class DummyTracker(UsageTracker):
    def reserve(self, provider_id, model_name, key_identifier, rules, expected_tokens):
        return True

    def record(self, provider_id, model_name, key_identifier, status, tokens_used, *, rules=None, reserved_tokens=None):
        return None


class RedisSettingsTests(unittest.TestCase):
    def test_config_from_env(self) -> None:
        env = {
            "REDIS_HOST": "cache",
            "REDIS_PORT": "6380",
            "REDIS_DB": "2",
            "REDIS_USER": "user",
            "REDIS_PASSWORD": "pass",
            "REDIS_SSL": "true",
            "REDIS_NAMESPACE": "ns",
            "REDIS_TTL_PADDING": "7",
            "REDIS_STATUS_TTL": "120",
        }
        config = RedisConfig.from_env(env)
        self.assertEqual(config.host, "cache")
        self.assertEqual(config.port, 6380)
        self.assertEqual(config.db, 2)
        self.assertTrue(config.ssl)
        self.assertEqual(config.namespace, "ns")
        self.assertEqual(config.ttl_padding, 7)
        self.assertEqual(config.status_ttl, 120)

    def test_build_usage_tracker_with_custom_client(self) -> None:
        config = RedisConfig()
        client = DummyRedisClient()
        tracker = build_usage_tracker(config, client=client)
        self.assertIsNotNone(tracker)

    def test_attach_usage_tracker_sets_on_cycler(self) -> None:
        cycler = APIKeyCycler()
        tracker = DummyTracker()
        attach_usage_tracker(cycler, tracker)
        self.assertIs(cycler._tracker, tracker)  # type: ignore[attr-defined]


if __name__ == "__main__":
    unittest.main()
