import unittest
from interpreter.k_1_0_ast_statements import execute, KThrown


class ASTExceptionTests(unittest.TestCase):
    def test_throw_value(self):
        node = {
            "type": "throw_statement",
            "value": {"type": "literal", "value": "problem"}
        }
        with self.assertRaises(KThrown) as caught:
            execute(node)
        self.assertEqual(caught.exception.value, "problem")

    def test_try_catch_handles_thrown_value(self):
        node = {
            "type": "try_catch_statement",
            "try_body": {
                "type": "block",
                "body": [{
                    "type": "throw_statement",
                    "value": {"type": "literal", "value": "handled"}
                }]
            },
            "catch_name": "error",
            "catch_body": {
                "type": "block",
                "body": [{
                    "type": "expression_statement",
                    "expression": {
                        "type": "identifier", "name": "error"
                    }
                }]
            }
        }
        self.assertEqual(execute(node), "handled")

    def test_try_without_error(self):
        node = {
            "type": "try_catch_statement",
            "try_body": {
                "type": "block",
                "body": [{
                    "type": "expression_statement",
                    "expression": {"type": "literal", "value": 25}
                }]
            },
            "catch_body": {"type": "block", "body": []}
        }
        self.assertEqual(execute(node), 25)

    def test_uncaught_throw_propagates(self):
        node = {
            "type": "try_catch_statement",
            "try_body": {
                "type": "block",
                "body": [{
                    "type": "throw_statement",
                    "value": {"type": "literal", "value": 99}
                }]
            }
        }
        with self.assertRaises(KThrown):
            execute(node)


if __name__ == "__main__":
    unittest.main()
