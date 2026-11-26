#!/usr/bin/env python3
"""Tests for address validation and address watching helpers."""

import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


VALIDATE = load("validate_ergo_address", ROOT / "scripts" / "validate_ergo_address.py")
WATCH = load("watch_address", ROOT / "scripts" / "watch_address.py")

ADDR = "9hTcHpkQYmq8AETagsQ6RypRoGrXifC4g4dYECqfePLKFcGTLYc"


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class ValidationTests(unittest.TestCase):
    def test_valid_address(self):
        result = VALIDATE.validate(ADDR, fetcher=lambda a: {"summary": {"id": a}})
        self.assertTrue(result["valid"])
        self.assertTrue(result["checked_with_api"])

    def test_rejects_non_base58(self):
        result = VALIDATE.validate("not an address", fetcher=lambda a: self.fail("API must not be called"))
        self.assertFalse(result["valid"])
        self.assertFalse(result["checked_with_api"])

    def test_rejects_api_mismatch(self):
        result = VALIDATE.validate(ADDR, fetcher=lambda a: {"summary": {"id": "other"}})
        self.assertFalse(result["valid"])
        self.assertIn("different", result["reason"])


class WatchTests(unittest.TestCase):
    def opener(self, balance):
        payload = {"transactions": {"totalBalance": balance}}
        data = json.dumps(payload).encode("utf-8")
        return lambda request, timeout: FakeResponse(data)

    def test_first_run_is_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            event = WATCH.observe(ADDR, str(state), opener=self.opener(500), now=lambda: 1000)
            self.assertEqual(event["status"], "unchanged")
            self.assertIsNone(event["increase_nanoerg"])
            self.assertEqual(json.loads(state.read_text())["balance_nanoerg"], 500)

    def test_increase_is_observed(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            WATCH.observe(ADDR, str(state), opener=self.opener(500), now=lambda: 1000)
            event = WATCH.observe(ADDR, str(state), opener=self.opener(502), now=lambda: 1001)
            self.assertEqual(event["status"], "observed")
            self.assertEqual(event["increase_nanoerg"], 2)
            self.assertEqual(event["balance_nanoerg"], 502)

    def test_decrease_is_not_reported_as_payment(self):
        with tempfile.TemporaryDirectory() as tmp:
            state = Path(tmp) / "state.json"
            WATCH.observe(ADDR, str(state), opener=self.opener(500), now=lambda: 1000)
            event = WATCH.observe(ADDR, str(state), opener=self.opener(400), now=lambda: 1001)
            self.assertNotEqual(event["status"], "observed")
            self.assertEqual(event["increase_nanoerg"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
