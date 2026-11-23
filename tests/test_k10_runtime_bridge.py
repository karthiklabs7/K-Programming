import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "interpreter"))
from k_1_0_runtime_bridge import run_with_frontend, RuntimeBridgeError

class RuntimeBridgeTests(unittest.TestCase):
    def test_frontend_and_execution(self):
        received = []
        result = run_with_frontend(
            "x = 10 + 20;",
            lambda source: received.append(source) or "executed"
        )
        self.assertEqual(received, ["x = 10 + 20;"])
        self.assertEqual(result["execution"], "executed")
        self.assertEqual(result["execution_engine"], "legacy")
        self.assertEqual(result["frontend"]["ast"].kind, "Program")

    def test_function_source(self):
        result = run_with_frontend(
            "fun greet(name) { return name; }",
            lambda source: "ok"
        )
        self.assertEqual(result["execution"], "ok")

    def test_invalid_syntax_not_executed(self):
        called = []
        with self.assertRaises(RuntimeBridgeError):
            run_with_frontend("fun {", lambda s: called.append(s))
        self.assertEqual(called, [])

    def test_invalid_input(self):
        with self.assertRaises(TypeError):
            run_with_frontend(123, lambda s: None)

if __name__ == "__main__":
    unittest.main(verbosity=2)
