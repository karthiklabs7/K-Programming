import unittest
from interpreter.k_1_0_safety import KRuntimeSafety, KSafetyError

class SafetyTests(unittest.TestCase):
    def setUp(self):
        self.safe = KRuntimeSafety(max_depth=3, max_items=4)

    def test_primitives(self):
        for value in (None, True, 12, 2.5, "K"):
            self.assertTrue(self.safe.validate_value(value))

    def test_nested_list(self):
        self.assertTrue(self.safe.validate_value([1, [2, 3]]))

    def test_nested_depth_limit(self):
        with self.assertRaises(KSafetyError):
            self.safe.validate_value([[[[[1]]]]])

    def test_collection_limit(self):
        with self.assertRaises(KSafetyError):
            self.safe.validate_value([1, 2, 3, 4, 5])

    def test_dictionary(self):
        self.assertTrue(self.safe.validate_value({"K": 1}))

    def test_unsupported_object(self):
        with self.assertRaises(KSafetyError):
            self.safe.validate_value(object())

    def test_number_type(self):
        self.assertTrue(self.safe.check_type(12, "number"))

    def test_bool_not_number(self):
        with self.assertRaises(KSafetyError):
            self.safe.check_type(True, "number")

    def test_wrong_type(self):
        with self.assertRaises(KSafetyError):
            self.safe.check_type(12, "string")

    def test_unknown_type(self):
        with self.assertRaises(KSafetyError):
            self.safe.check_type(12, "unknown")

if __name__ == "__main__":
    unittest.main()
