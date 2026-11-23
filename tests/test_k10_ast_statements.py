import sys
import unittest
from pathlib import Path
from types import SimpleNamespace as N

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))

from k_1_0_ast_runtime import Environment
from k_1_0_ast_statements import execute, KRuntimeError


def node(kind, **kwargs):
    return N(kind=kind, **kwargs)


def num(value):
    return node("Number", value=value)


def var(name):
    return node("Identifier", name=name)


def binary(left, op, right):
    return node("Binary", left=left, operator=op, right=right)


def assign(name, value):
    return node("ExpressionStatement",
                expression=node("Assignment", left=var(name), right=value))


class ASTStatementTests(unittest.TestCase):
    def test_variable_declaration(self):
        env = Environment()
        execute(node("VariableDeclaration", name="x", initializer=num(7)), env)
        self.assertEqual(env.get("x"), 7)

    def test_expression_statement(self):
        env = Environment()
        execute(assign("x", num(12)), env)
        self.assertEqual(env.get("x"), 12)

    def test_if_true(self):
        env = Environment()
        statement = node("IfStatement", condition=num(1),
                         then_branch=assign("x", num(5)),
                         else_branch=assign("x", num(9)))
        execute(statement, env)
        self.assertEqual(env.get("x"), 5)

    def test_if_else(self):
        env = Environment()
        statement = node("IfStatement", condition=num(0),
                         then_branch=assign("x", num(5)),
                         else_branch=assign("x", num(9)))
        execute(statement, env)
        self.assertEqual(env.get("x"), 9)

    def test_while_loop(self):
        env = Environment()
        env.set("i", 0)
        body = node("Block", body=[
            assign("i", binary(var("i"), "+", num(1)))
        ])
        loop = node("WhileStatement",
                    condition=binary(var("i"), "<", num(4)),
                    body=body)
        execute(loop, env)
        self.assertEqual(env.get("i"), 4)

    def test_break(self):
        env = Environment()
        env.set("i", 0)
        body = node("Block", body=[
            assign("i", binary(var("i"), "+", num(1))),
            node("IfStatement", condition=binary(var("i"), "==", num(2)),
                 then_branch=node("BreakStatement"), else_branch=None)
        ])
        execute(node("WhileStatement", condition=num(1), body=body), env)
        self.assertEqual(env.get("i"), 2)

    def test_continue(self):
        env = Environment()
        env.set("i", 0)
        env.set("total", 0)
        body = node("Block", body=[
            assign("i", binary(var("i"), "+", num(1))),
            node("IfStatement", condition=binary(var("i"), "==", num(2)),
                 then_branch=node("ContinueStatement"), else_branch=None),
            assign("total", binary(var("total"), "+", var("i")))
        ])
        execute(node("WhileStatement",
                     condition=binary(var("i"), "<", num(3)),
                     body=body), env)
        self.assertEqual(env.get("total"), 4)

    def test_function_and_return(self):
        env = Environment()
        function = node("FunctionDeclaration", name="double",
                        params=["n"],
                        body=node("Block", body=[
                            node("ReturnStatement",
                                 value=binary(var("n"), "*", num(2)))
                        ]))
        execute(function, env)
        result = env.get("double")(6)
        self.assertEqual(result, 12)

    def test_function_argument_validation(self):
        env = Environment()
        execute(node("FunctionDeclaration", name="one",
                     params=["x"], body=node("Block", body=[])), env)
        with self.assertRaises(KRuntimeError):
            env.get("one")()

    def test_unsupported_statement(self):
        with self.assertRaises(KRuntimeError):
            execute(node("UnknownStatement"))

if __name__ == "__main__":
    unittest.main(verbosity=2)
