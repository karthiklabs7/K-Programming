import unittest
from interpreter.k_1_0_modules import (
    KModule, KModuleError, KModuleRegistry
)


class ModuleTests(unittest.TestCase):
    def setUp(self):
        self.registry = KModuleRegistry()

    def test_create_module(self):
        module = self.registry.create("math", {"answer": 42})
        self.assertEqual(module.name, "math")

    def test_register_and_load(self):
        module = KModule("tools")
        self.registry.register(module)
        self.assertIs(self.registry.load("tools"), module)

    def test_export_and_get(self):
        module = self.registry.create("data")
        module.export("version", "1.0")
        self.assertEqual(module.get("version"), "1.0")

    def test_import_with_alias(self):
        self.registry.create("math", {"pi": 3.14})
        env = {}
        module = self.registry.import_module("math", "m", env)
        self.assertIs(env["m"], module)

    def test_import_symbol(self):
        self.registry.create("math", {"add": lambda a, b: a + b})
        env = {}
        self.registry.import_symbol("math", "add", "sum", env)
        self.assertEqual(env["sum"](2, 3), 5)

    def test_duplicate_module_rejected(self):
        self.registry.create("math")
        with self.assertRaises(KModuleError):
            self.registry.create("math")

    def test_missing_module_rejected(self):
        with self.assertRaises(KModuleError):
            self.registry.load("missing")

    def test_missing_export_rejected(self):
        module = self.registry.create("empty")
        with self.assertRaises(KModuleError):
            module.get("unknown")

    def test_module_names(self):
        self.registry.create("zeta")
        self.registry.create("alpha")
        self.assertEqual(self.registry.names(), ["alpha", "zeta"])


if __name__ == "__main__":
    unittest.main()
