import unittest
from interpreter.k_1_0_collections import (
    KList, KMap, KCollectionError, k_list, k_map,
    k_len, k_push, k_pop, k_keys, k_values,
    k_contains, k_get, k_set, COLLECTION_BUILTINS
)


class CollectionTests(unittest.TestCase):
    def test_list_creation_and_add(self):
        items = k_list(1, 2)
        self.assertIsInstance(items, KList)
        self.assertEqual(items.add(3), 3)
        self.assertEqual(items, [1, 2, 3])

    def test_list_remove_and_first_last(self):
        items = k_list(10, 20, 30)
        self.assertEqual(items.first(), 10)
        self.assertEqual(items.last(), 30)
        self.assertEqual(items.remove_at(1), 20)

    def test_map_creation_and_put(self):
        data = k_map(name="K")
        self.assertIsInstance(data, KMap)
        data.put("version", 1)
        self.assertEqual(data["version"], 1)

    def test_map_keys_values(self):
        data = k_map(a=1, b=2)
        self.assertEqual(k_keys(data), ["a", "b"])
        self.assertEqual(k_values(data), [1, 2])

    def test_length_and_push_pop(self):
        items = k_list(4)
        k_push(items, 5)
        self.assertEqual(k_len(items), 2)
        self.assertEqual(k_pop(items), 5)

    def test_get_set_contains(self):
        data = k_map(score=90)
        self.assertTrue(k_contains(data, "score"))
        self.assertEqual(k_get(data, "score"), 90)
        self.assertEqual(k_get(data, "missing", 0), 0)
        self.assertEqual(k_set(data, "score", 100), 100)
        self.assertEqual(data["score"], 100)

    def test_map_remove(self):
        data = k_map(a=1)
        self.assertEqual(data.remove_key("a"), 1)
        self.assertFalse(data.has("a"))

    def test_invalid_operations(self):
        with self.assertRaises(KCollectionError):
            k_push("text", 1)
        with self.assertRaises(KCollectionError):
            k_keys([1, 2])
        with self.assertRaises(KCollectionError):
            k_list().first()

    def test_builtin_registry(self):
        self.assertIn("list", COLLECTION_BUILTINS)
        self.assertIn("map", COLLECTION_BUILTINS)
        self.assertEqual(COLLECTION_BUILTINS["len"]([1, 2]), 2)


if __name__ == "__main__":
    unittest.main()
