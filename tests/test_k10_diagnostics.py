import unittest
from interpreter.k_1_0_diagnostics import (
    KDiagnostic, KDiagnostics, KDebugLogger,
    k_stack_trace, k_assert, DIAGNOSTIC_BUILTINS
)


class DiagnosticsTests(unittest.TestCase):
    def test_diagnostic_format(self):
        item = KDiagnostic(
            "Unexpected token", "SyntaxError", "main.k", 4, 8
        )
        self.assertEqual(
            item.format(),
            "main.k:4:8: error [SyntaxError]: Unexpected token"
        )

    def test_syntax_error(self):
        diagnostics = KDiagnostics("test.k")
        item = diagnostics.syntax_error("Invalid syntax", 3, 5)
        self.assertEqual(item.category, "SyntaxError")
        self.assertEqual(item.filename, "test.k")
        self.assertTrue(diagnostics.has_errors())

    def test_type_error(self):
        diagnostics = KDiagnostics()
        item = diagnostics.type_error("Wrong type", 2, 4)
        self.assertEqual(item.category, "TypeError")

    def test_runtime_error(self):
        diagnostics = KDiagnostics()
        item = diagnostics.runtime_error("Failed", 7, 1)
        self.assertEqual(item.line, 7)

    def test_multiple_errors(self):
        diagnostics = KDiagnostics()
        diagnostics.syntax_error("One")
        diagnostics.runtime_error("Two")
        self.assertEqual(len(diagnostics.format_all()), 2)

    def test_clear_errors(self):
        diagnostics = KDiagnostics()
        diagnostics.syntax_error("Problem")
        diagnostics.clear()
        self.assertFalse(diagnostics.has_errors())

    def test_debug_logger(self):
        logger = KDebugLogger(enabled=True)
        logger.log("Started")
        self.assertEqual(logger.entries, ["[DEBUG] Started"])
        logger.clear()
        self.assertEqual(logger.entries, [])

    def test_disabled_logger(self):
        logger = KDebugLogger()
        self.assertIsNone(logger.log("Hidden"))
        self.assertEqual(logger.entries, [])

    def test_stack_trace(self):
        try:
            raise ValueError("sample")
        except ValueError as error:
            trace = k_stack_trace(error)
        self.assertIn("ValueError: sample", trace)

    def test_assert_builtin(self):
        self.assertTrue(k_assert(True))
        with self.assertRaises(AssertionError):
            k_assert(False, "failed")

    def test_builtin_registry(self):
        self.assertIn("assert", DIAGNOSTIC_BUILTINS)
        self.assertIn("stack_trace", DIAGNOSTIC_BUILTINS)


if __name__ == "__main__":
    unittest.main()
