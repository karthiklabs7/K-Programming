import unittest
from interpreter.k_1_0_stdlib import (
    KStdLibError, K_STDLIB, k_type, k_number, k_string,
    k_boolean, k_range, k_min, k_max, k_sum, k_sorted,
    k_abs, k_round, k_sqrt, k_power, k_floor, k_ceil
)


class StandardLibraryTests(unittest.TestCase):
    def test_type_detection(self):
        self.assertEqual(k_type(None), "null")
        self.assertEqual(k_type(True), "boolean")
        self.assertEqual(k_type(10), "number")
        self.assertEqual(k_type("K"), "string")
        self.assertEqual(k_type([1]), "list")
        self.assertEqual(k_type({"a": 1}), "map")

    def test_conversions(self):
        self.assertEqual(k_number("25"), 25)
        self.assertEqual(k_number("2.5"), 2.5)
        self.assertEqual(k_string(10), "10")
        self.assertTrue(k_boolean(1))

    def test_range(self):
        self.assertEqual(k_range(1, 5), [1, 2, 3, 4])
        self.assertEqual(k_range(2, 8, 2), [2, 4, 6])

    def test_min_max_sum(self):
        values = [4, 1, 8]
        self.assertEqual(k_min(values), 1)
        self.assertEqual(k_max(values), 8)
        self.assertEqual(k_sum(values), 13)

    def test_sorted(self):
        self.assertEqual(k_sorted([3, 1, 2]), [1, 2, 3])

    def test_numeric_utilities(self):
        self.assertEqual(k_abs(-5), 5)
        self.assertEqual(k_round(3.14159, 2), 3.14)
        self.assertEqual(k_sqrt(81), 9)
        self.assertEqual(k_power(2, 3), 8)
        self.assertEqual(k_floor(3.8), 3)
        self.assertEqual(k_ceil(3.2), 4)

    def test_invalid_conversion(self):
        with self.assertRaises(KStdLibError):
            k_number("not-a-number")

    def test_invalid_sqrt(self):
        with self.assertRaises(KStdLibError):
            k_sqrt(-1)

    def test_registry(self):
        self.assertIn("type", K_STDLIB)
        self.assertIn("sqrt", K_STDLIB)
        self.assertEqual(K_STDLIB["sum"]([1, 2, 3]), 6)


if __name__ == "__main__":
    unittest.main()
