import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as N

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_ast_runtime import Environment, evaluate, KRuntimeError


def number(value):
    return N(kind="Number", value=value)


def identifier(name):
    return N(kind="Identifier", name=name)


def binary(left, op, right):
    return N(kind="Binary", left=left, operator=op, right=right)


class ASTRuntimeTests(unittest.TestCase):
    def test_arithmetic_precedence_tree(self):
        self.assertEqual(evaluate(binary(
            number(2), "+", binary(number(3), "*", number(4)))), 14)

    def test_variables(self):
        env = Environment()
        env.set("score", 25)
        self.assertEqual(evaluate(identifier("score"), env), 25)

    def test_assignment(self):
        env = Environment()
        node = N(kind="Assignment", left=identifier("x"), right=number(9))
        self.assertEqual(evaluate(node, env), 9)
        self.assertEqual(env.get("x"), 9)

    def test_comparison(self):
        self.assertTrue(evaluate(binary(number(8), ">", number(3))))

    def test_arrays_and_index(self):
        env = Environment()
        env.set("items", [10, 20, 30])
        node = N(kind="Index", object=identifier("items"), index=number(1))
        self.assertEqual(evaluate(node, env), 20)

    def test_builtin_call(self):
        node = N(kind="Call", callee=identifier("double"),
                 arguments=[number(6)])
        self.assertEqual(evaluate(node, builtins={"double": lambda x: x * 2}), 12)

    def test_undefined_variable_error(self):
        with self.assertRaises(KRuntimeError):
            evaluate(identifier("missing"), Environment())

    def test_unsupported_node_error(self):
        with self.assertRaises(KRuntimeError):
            evaluate(N(kind="UnknownNode"))

    def test_boolean_logic(self):
        node = binary(number(1), "and", number(2))
        self.assertTrue(evaluate(node))


if __name__ == "__main__":
    unittest.main(verbosity=2)
