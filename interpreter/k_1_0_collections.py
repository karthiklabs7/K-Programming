"""K 1.0 advanced collection runtime."""


class KCollectionError(Exception):
    pass


class KList(list):
    def add(self, value):
        self.append(value)
        return value

    def remove_at(self, index):
        try:
            return self.pop(index)
        except (IndexError, TypeError) as error:
            raise KCollectionError(str(error)) from error

    def first(self):
        if not self:
            raise KCollectionError("List is empty")
        return self[0]

    def last(self):
        if not self:
            raise KCollectionError("List is empty")
        return self[-1]


class KMap(dict):
    def put(self, key, value):
        self[key] = value
        return value

    def has(self, key):
        return key in self

    def remove_key(self, key):
        if key not in self:
            raise KCollectionError(f"Missing map key: {key}")
        return self.pop(key)

    def get_value(self, key, default=None):
        return self.get(key, default)


def k_list(*values):
    return KList(values)


def k_map(**values):
    return KMap(values)


def k_len(collection):
    try:
        return len(collection)
    except TypeError as error:
        raise KCollectionError(str(error)) from error


def k_push(collection, value):
    if isinstance(collection, KList):
        return collection.add(value)
    if isinstance(collection, list):
        collection.append(value)
        return value
    raise KCollectionError("push requires a list")


def k_pop(collection, index=-1):
    if isinstance(collection, list):
        try:
            return collection.pop(index)
        except (IndexError, TypeError) as error:
            raise KCollectionError(str(error)) from error
    raise KCollectionError("pop requires a list")


def k_keys(collection):
    if isinstance(collection, dict):
        return list(collection.keys())
    raise KCollectionError("keys requires a map")


def k_values(collection):
    if isinstance(collection, dict):
        return list(collection.values())
    raise KCollectionError("values requires a map")


def k_contains(collection, value):
    try:
        return value in collection
    except TypeError as error:
        raise KCollectionError(str(error)) from error


def k_get(collection, key, default=None):
    try:
        return collection[key] if key in collection else default
    except (TypeError, KeyError) as error:
        raise KCollectionError(str(error)) from error


def k_set(collection, key, value):
    if not isinstance(collection, (list, dict)):
        raise KCollectionError("set requires a list or map")
    try:
        collection[key] = value
        return value
    except (IndexError, TypeError, KeyError) as error:
        raise KCollectionError(str(error)) from error


COLLECTION_BUILTINS = {
    "list": k_list,
    "map": k_map,
    "len": k_len,
    "push": k_push,
    "pop": k_pop,
    "keys": k_keys,
    "values": k_values,
    "contains": k_contains,
    "get": k_get,
    "set": k_set,
}
