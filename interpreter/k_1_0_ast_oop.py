"""K 1.0 object-oriented runtime foundation."""


class KOOPError(Exception):
    pass


class KInstance:
    def __init__(self, klass):
        self.klass = klass
        self.attributes = {}

    def get(self, name):
        if name in self.attributes:
            return self.attributes[name]
        if name in self.klass.methods:
            return KBoundMethod(self, self.klass.methods[name])
        raise KOOPError(
            f"Undefined member '{name}' in class '{self.klass.name}'"
        )

    def set(self, name, value):
        if not isinstance(name, str) or not name:
            raise KOOPError("Invalid attribute name")
        self.attributes[name] = value
        return value


class KBoundMethod:
    def __init__(self, instance, function):
        self.instance = instance
        self.function = function

    def __call__(self, *args):
        return self.function(self.instance, *args)


class KClass:
    def __init__(self, name, methods=None):
        if not isinstance(name, str) or not name:
            raise KOOPError("Class needs a valid name")
        self.name = name
        self.methods = dict(methods or {})

    def instantiate(self, *args):
        instance = KInstance(self)
        initializer = self.methods.get("init")
        if initializer is not None:
            initializer(instance, *args)
        elif args:
            raise KOOPError(
                f"Class '{self.name}' has no init method"
            )
        return instance


def get_member(obj, name):
    if isinstance(obj, KInstance):
        return obj.get(name)
    if isinstance(obj, KClass):
        if name in obj.methods:
            return obj.methods[name]
    raise KOOPError(f"Cannot read member '{name}'")


def set_member(obj, name, value):
    if not isinstance(obj, KInstance):
        raise KOOPError("Only objects support attribute assignment")
    return obj.set(name, value)


def instantiate(klass, *args):
    if not isinstance(klass, KClass):
        raise KOOPError("Value is not a K class")
    return klass.instantiate(*args)
