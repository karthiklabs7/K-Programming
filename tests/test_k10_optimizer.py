import unittest
from interpreter.k_1_0_optimizer import optimize, optimize_program

class OptimizerTests(unittest.TestCase):
    def binary(self, op, a, b):
        return {"type": "binary", "operator": op, "left": a, "right": b}

    def number(self, value):
        return {"type": "number", "value": value}

    def test_addition(self):
        self.assertEqual(optimize(self.binary("+", self.number(2), self.number(3)))["value"], 5)

    def test_multiplication(self):
        self.assertEqual(optimize(self.binary("*", self.number(4), self.number(5)))["value"], 20)

    def test_nested_folding(self):
        node = self.binary("*", self.binary("+", self.number(2), self.number(3)), self.number(4))
        self.assertEqual(optimize(node)["value"], 20)

    def test_comparison(self):
        node = self.binary(">", self.number(8), self.number(3))
        self.assertIs(optimize(node)["value"], True)

    def test_division_by_zero_preserved(self):
        node = self.binary("/", self.number(5), self.number(0))
        self.assertEqual(optimize(node)["type"], "binary")

    def test_unknown_operator_preserved(self):
        node = self.binary("???", self.number(1), self.number(2))
        self.assertEqual(optimize(node)["type"], "binary")

    def test_identifier_not_folded(self):
        node = self.binary("+", {"type": "identifier", "name": "x"}, self.number(2))
        self.assertEqual(optimize(node)["type"], "binary")

    def test_program_tree(self):
        tree = {"type": "program", "body": [self.binary("+", self.number(6), self.number(7))]}
        result = optimize_program(tree)
        self.assertEqual(result["body"][0]["value"], 13)

if __name__ == "__main__":
    unittest.main()
