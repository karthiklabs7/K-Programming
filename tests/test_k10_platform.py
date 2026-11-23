import unittest
from interpreter.k_1_0_platform import (
    platform_name, platform_info, normalize_path, is_absolute_path
)

class PlatformTests(unittest.TestCase):
    def test_platform_name(self):
        self.assertIn(platform_name(), ("Windows", "Linux", "Android", "macOS", "Unknown"))

    def test_platform_info(self):
        info = platform_info()
        self.assertTrue(info["name"])
        self.assertTrue(info["python"])

    def test_normalize_path(self):
        self.assertTrue(normalize_path("sample.txt"))

    def test_absolute_path(self):
        self.assertTrue(is_absolute_path("/tmp/sample.txt"))

if __name__ == "__main__":
    unittest.main()
