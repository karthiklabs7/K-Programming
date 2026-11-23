import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_lexer import lex_source, LexerError

class LexerIntegrationTests(unittest.TestCase):
    def test_interface(self):
        tokens = lex_source("fun greet() { return 42 }")
        self.assertEqual(tokens[0].value, "fun")
        self.assertEqual(tokens[-1].kind, "EOF")

    def test_multiple_lines(self):
        tokens = lex_source("first\nsecond")
        second = next(t for t in tokens if t.value == "second")
        self.assertEqual(second.line, 2)

    def test_errors_propagate(self):
        with self.assertRaises(LexerError):
            lex_source("x @ y")

    def test_type_validation(self):
        with self.assertRaises(TypeError):
            lex_source(123)

if __name__ == "__main__":
    unittest.main(verbosity=2)
