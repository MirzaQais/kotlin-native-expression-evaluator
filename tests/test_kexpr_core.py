import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "poc"))

from kexpr_core import KExprError, SafeKotlinEvaluator


class SafeKotlinEvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.ev = SafeKotlinEvaluator(
            {"x": 10, "y": 7, "factor": 2, "enabled": True, "limit": 30}
        )

    def test_arithmetic(self):
        self.assertEqual(self.ev.evaluate("x + y * factor"), 24)

    def test_boolean_and_comparison(self):
        self.assertTrue(self.ev.evaluate("x > 5 && enabled"))
        self.assertTrue(self.ev.evaluate("x + y < limit"))

    def test_not(self):
        self.assertFalse(self.ev.evaluate("!enabled"))

    def test_parentheses(self):
        self.assertEqual(self.ev.evaluate("(x + y) * factor"), 34)

    def test_unknown_name(self):
        with self.assertRaises(KExprError):
            self.ev.evaluate("missing + 1")

    def test_function_call_is_blocked(self):
        with self.assertRaises(KExprError):
            self.ev.evaluate("foo()")

    def test_attribute_access_is_blocked(self):
        with self.assertRaises(KExprError):
            self.ev.evaluate("obj.field")


if __name__ == "__main__":
    unittest.main()
