import unittest
from interpreter.k_1_0_ast_oop import (
    KClass, KInstance, KBoundMethod, KOOPError,
    get_member, set_member, instantiate
)


class OOPRuntimeTests(unittest.TestCase):
    def test_class_creation(self):
        c = KClass("Person")
        self.assertEqual(c.name, "Person")

    def test_instance_creation(self):
        obj = instantiate(KClass("Person"))
        self.assertIsInstance(obj, KInstance)

    def test_attribute_set_and_get(self):
        obj = instantiate(KClass("Person"))
        set_member(obj, "name", "K")
        self.assertEqual(get_member(obj, "name"), "K")

    def test_method_binding(self):
        c = KClass("Person", {
            "greet": lambda self: "Hello " + self.get("name")
        })
        obj = instantiate(c)
        set_member(obj, "name", "K")
        self.assertEqual(get_member(obj, "greet")(), "Hello K")

    def test_method_receives_arguments(self):
        c = KClass("Calc", {
            "add": lambda self, a, b: a + b
        })
        obj = instantiate(c)
        self.assertEqual(get_member(obj, "add")(4, 5), 9)

    def test_initializer(self):
        c = KClass("Person", {
            "init": lambda self, name: self.set("name", name)
        })
        obj = instantiate(c, "K")
        self.assertEqual(get_member(obj, "name"), "K")

    def test_missing_member_error(self):
        obj = instantiate(KClass("Person"))
        with self.assertRaises(KOOPError):
            get_member(obj, "missing")

    def test_invalid_instantiation(self):
        with self.assertRaises(KOOPError):
            instantiate("not a class")


if __name__ == "__main__":
    unittest.main()
