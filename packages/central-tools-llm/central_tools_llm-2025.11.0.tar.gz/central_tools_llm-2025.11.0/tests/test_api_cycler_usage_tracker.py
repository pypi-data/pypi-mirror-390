from __future__ import annotations

import unittest

from central_tools.cycling.api_cycler import APIKeyCycler, RateLimitRule
from central_tools.cycling.usage_tracker import UsageTracker
from central_tools.exceptions import NoAvailableAPIKey
from central_tools.models import LLMResponse


class DummyTracker(UsageTracker):
    def __init__(self, allow: bool = True) -> None:
        self.allow = allow
        self.reservations: list[dict] = []
        self.records: list[dict] = []

    def reserve(self, provider_id, model_name, key_identifier, rules, expected_tokens):
        self.reservations.append(
            {
                "provider_id": provider_id,
                "model_name": model_name,
                "key_identifier": key_identifier,
                "rules": list(rules),
                "expected_tokens": expected_tokens,
            }
        )
        return self.allow

    def record(
        self,
        provider_id,
        model_name,
        key_identifier,
        status,
        tokens_used,
        *,
        rules=None,
        reserved_tokens=None,
    ) -> None:
        self.records.append(
            {
                "provider_id": provider_id,
                "model_name": model_name,
                "key_identifier": key_identifier,
                "status": status,
                "tokens_used": tokens_used,
                "rules": list(rules or []),
                "reserved_tokens": reserved_tokens,
            }
        )


class APIKeyCyclerUsageTrackerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.rule = RateLimitRule(name="per_minute", period_seconds=60, max_calls=10, max_tokens=1000)

    def test_tracker_receives_rules_and_tokens(self) -> None:
        tracker = DummyTracker()
        cycler = APIKeyCycler(max_keys=3, usage_tracker=tracker)
        cycler.register_key(provider_id="provider", identifier="key-1", secret="s1", rules=[self.rule])

        snapshot = cycler.get_next_key_for_model(
            "provider",
            model_name="modelA",
            model_rules=[self.rule],
            expected_tokens=42,
        )
        response = LLMResponse(text="ok", raw={}, tokens_used=24)
        cycler.report_success("provider", snapshot.identifier, "modelA", response)

        self.assertEqual(len(tracker.reservations), 1)
        self.assertEqual(len(tracker.records), 1)
        record = tracker.records[0]
        self.assertEqual(record["status"], "success")
        self.assertEqual(record["reserved_tokens"], 42)
        self.assertEqual(record["tokens_used"], 24)
        self.assertEqual(record["rules"], [self.rule])

    def test_failure_flow_records_status(self) -> None:
        tracker = DummyTracker()
        cycler = APIKeyCycler(max_keys=3, usage_tracker=tracker)
        cycler.register_key(provider_id="provider", identifier="key-2", secret="s2", rules=[self.rule])

        snapshot = cycler.get_next_key_for_model(
            "provider",
            model_name="modelB",
            model_rules=[self.rule],
            expected_tokens=15,
        )
        cycler.mark_failure("provider", snapshot.identifier, "modelB")

        self.assertEqual(tracker.records[0]["status"], "failure")
        self.assertEqual(tracker.records[0]["reserved_tokens"], 15)

    def test_tracker_denial_blocks_selection(self) -> None:
        tracker = DummyTracker(allow=False)
        cycler = APIKeyCycler(max_keys=3, usage_tracker=tracker)
        cycler.register_key(provider_id="provider", identifier="key-3", secret="s3", rules=[self.rule])

        with self.assertRaises(NoAvailableAPIKey):
            cycler.get_next_key_for_model(
                "provider",
                model_name="modelC",
                model_rules=[self.rule],
                expected_tokens=10,
            )

        # Ensure no lingering reservations are recorded when reserve is denied.
        self.assertEqual(len(tracker.records), 0)


if __name__ == "__main__":
    unittest.main()
