import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_frontend import compile_source, LexerError, ParserError

class FrontendTests(unittest.TestCase):
    def test_combined_frontend(self):
        result = compile_source("x = 10 + 20;")
        self.assertEqual(result["ast"].kind, "Program")
        self.assertEqual(result["tokens"][-1].kind, "EOF")

    def test_function_frontend(self):
        result = compile_source("fun greet(name) { return name; }")
        self.assertEqual(
            result["ast"].fields["body"][0].kind,
            "FunctionDeclaration"
        )

    def test_if_frontend(self):
        result = compile_source("if (x > 2) { x = 3; }")
        self.assertEqual(
            result["ast"].fields["body"][0].kind,
            "IfStatement"
        )

    def test_invalid_lexer_input(self):
        with self.assertRaises(LexerError):
            compile_source("x @ y")

    def test_invalid_parser_input(self):
        with self.assertRaises(ParserError):
            compile_source("fun {")

    def test_empty_source(self):
        result = compile_source("")
        self.assertEqual(result["ast"].kind, "Program")

if __name__ == "__main__":
    unittest.main(verbosity=2)
