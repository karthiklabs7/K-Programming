import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_lexer_engine import tokenize, LexerError


class LexerTests(unittest.TestCase):
    def values(self, source):
        return [(t.kind, t.value) for t in tokenize(source)]

    def test_identifiers_and_keywords(self):
        result = self.values("fun greet name")
        self.assertEqual(result[0], ("KEYWORD", "fun"))
        self.assertEqual(result[1], ("IDENTIFIER", "greet"))
        self.assertEqual(result[2], ("IDENTIFIER", "name"))

    def test_numbers(self):
        result = self.values("123 4.5")
        self.assertEqual(result[0][1], 123)
        self.assertEqual(result[1][1], 4.5)

    def test_strings_and_escapes(self):
        result = self.values(r'"hello" "a\nb"')
        self.assertEqual(result[0][1], "hello")
        self.assertEqual(result[1][1], "a\nb")

    def test_operators(self):
        result = self.values("x == 10 && y >= 2")
        self.assertIn(("OPERATOR", "=="), result)
        self.assertIn(("OPERATOR", "&&"), result)
        self.assertIn(("OPERATOR", ">="), result)

    def test_comments(self):
        result = self.values("x = 1 # comment\n y = 2 // other")
        vals = [v for k, v in result]
        self.assertIn("x", vals)
        self.assertIn("y", vals)
        self.assertNotIn("comment", vals)

    def test_line_tracking(self):
        result = tokenize("x\n  y")
        y = next(t for t in result if t.value == "y")
        self.assertEqual((y.line, y.column), (2, 3))

    def test_invalid_character(self):
        with self.assertRaises(LexerError):
            tokenize("x @ y")

    def test_unterminated_string(self):
        with self.assertRaises(LexerError):
            tokenize('"unfinished')

    def test_eof(self):
        self.assertEqual(self.values("")[0], ("EOF", None))


if __name__ == "__main__":
    unittest.main(verbosity=2)
