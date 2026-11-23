import unittest
from unittest.mock import patch
from interpreter import k_1_0_ast_runner as runner


class ASTRunnerTests(unittest.TestCase):
    def test_frontend_ast_is_sent_to_runtime(self):
        fake_ast = object()
        with patch.object(
            runner, "compile_source",
            return_value={"tokens": [], "ast": fake_ast}
        ) as frontend, patch.object(
            runner, "execute", return_value=42
        ) as runtime:
            result = runner.run_ast("sample K source")
            self.assertEqual(result, 42)
            frontend.assert_called_once_with("sample K source")
            runtime.assert_called_once_with(
                fake_ast, environment=None, builtins=None
            )

    def test_invalid_frontend_result_is_rejected(self):
        with patch.object(runner, "compile_source", return_value={}):
            with self.assertRaises(RuntimeError):
                runner.run_ast("sample")


if __name__ == "__main__":
    unittest.main()
