import tempfile
import unittest
from pathlib import Path
from interpreter.k_1_0_files import (
    KFileSystem, KFileError, FILE_BUILTINS
)


class FileHandlingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.fs = KFileSystem(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_write_and_read(self):
        self.assertTrue(self.fs.write("hello.txt", "Hello K"))
        self.assertEqual(self.fs.read("hello.txt"), "Hello K")

    def test_append(self):
        self.fs.write("data.txt", "K")
        self.fs.append("data.txt", " Programming")
        self.assertEqual(self.fs.read("data.txt"), "K Programming")

    def test_exists(self):
        self.assertFalse(self.fs.exists("missing.txt"))
        self.fs.write("present.txt", "yes")
        self.assertTrue(self.fs.exists("present.txt"))

    def test_create_nested_directory(self):
        self.assertTrue(self.fs.mkdir("one/two"))
        self.assertTrue((Path(self.temp.name) / "one/two").is_dir())

    def test_list_directory(self):
        self.fs.write("b.txt", "B")
        self.fs.write("a.txt", "A")
        self.assertEqual(self.fs.list_dir("."), ["a.txt", "b.txt"])

    def test_nested_file(self):
        self.fs.write("folder/file.txt", "nested")
        self.assertEqual(self.fs.read("folder/file.txt"), "nested")

    def test_missing_file_error(self):
        with self.assertRaises(KFileError):
            self.fs.read("missing.txt")

    def test_path_traversal_rejected(self):
        with self.assertRaises(KFileError):
            self.fs.write("../outside.txt", "blocked")

    def test_builtin_registry(self):
        self.assertIn("read_file", FILE_BUILTINS)
        self.assertIn("write_file", FILE_BUILTINS)
        self.assertIn("list_dir", FILE_BUILTINS)


if __name__ == "__main__":
    unittest.main()
