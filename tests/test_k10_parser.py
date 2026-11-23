import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_parser_engine import parse, ParserError

class ParserTests(unittest.TestCase):
    def test_number_expression(self):
        tree = parse("1 + 2 * 3")
        expr = tree.fields["body"][0].fields["expression"]
        self.assertEqual(expr.kind, "Binary")
        self.assertEqual(expr.fields["right"].kind, "Binary")

    def test_grouping(self):
        tree = parse("(1 + 2) * 3")
        self.assertEqual(tree.fields["body"][0].fields["expression"].kind, "Binary")

    def test_assignment(self):
        tree = parse("x = 42;")
        self.assertEqual(tree.fields["body"][0].fields["expression"].kind, "Assignment")

    def test_function_call(self):
        tree = parse("greet('K');")
        self.assertEqual(tree.fields["body"][0].fields["expression"].kind, "Call")

    def test_member_access(self):
        tree = parse("person.name")
        self.assertEqual(tree.fields["body"][0].fields["expression"].kind, "Member")

    def test_array(self):
        tree = parse("[1, 2, 3]")
        self.assertEqual(tree.fields["body"][0].fields["expression"].kind, "Array")

    def test_function_declaration(self):
        tree = parse("fun greet(name) { return name; }")
        self.assertEqual(tree.fields["body"][0].kind, "FunctionDeclaration")

    def test_if_else(self):
        tree = parse("if (x > 1) { x = 2; } else { x = 3; }")
        self.assertEqual(tree.fields["body"][0].kind, "IfStatement")

    def test_while(self):
        tree = parse("while (x < 5) { x = x + 1; }")
        self.assertEqual(tree.fields["body"][0].kind, "WhileStatement")

    def test_class_methods(self):
        tree = parse("class Person { fun greet(self) { return 1; } }")
        self.assertEqual(tree.fields["body"][0].kind, "ClassDeclaration")

    def test_invalid_syntax(self):
        with self.assertRaises(ParserError):
            parse("fun {")

    def test_empty_program(self):
        self.assertEqual(parse("").kind, "Program")

if __name__ == "__main__":
    unittest.main(verbosity=2)
