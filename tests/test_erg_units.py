#!/usr/bin/env python3
"""Tests for the ERG/nanoERG helper."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "erg_units.py"
SPEC = importlib.util.spec_from_file_location("erg_units", str(MODULE_PATH))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class UnitTests(unittest.TestCase):
    def test_exact_conversions(self):
        self.assertEqual(MODULE.parse_amount("1"), 1_000_000_000)
        self.assertEqual(MODULE.parse_amount("0.001"), 1_000_000)
        self.assertEqual(MODULE.parse_amount("12.000000001"), 12_000_000_001)
        self.assertEqual(MODULE.parse_amount("0.000000001"), 1)

    def test_format_roundtrip(self):
        for text in ("0", "0.001", "1", "12.000000001", "3.5"):
            with self.subTest(text=text):
                self.assertEqual(MODULE.format_amount(MODULE.parse_amount(text)), text if text != "0" else "0")

    def test_invalid_amounts(self):
        for bad in ("-1", "1.1234567890", "abc", "1e3", ""):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    MODULE.parse_amount(bad)

    def test_fee_floor(self):
        self.assertFalse(MODULE.fee_is_sane(0))
        self.assertFalse(MODULE.fee_is_sane(999_999))
        self.assertTrue(MODULE.fee_is_sane(1_000_000))
        self.assertTrue(MODULE.fee_is_sane(2_000_000))
        self.assertFalse(MODULE.fee_is_sane(2_000_000, exactly_minimum=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
