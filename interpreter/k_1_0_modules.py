"""K 1.0 module and package registry."""


class KModuleError(Exception):
    pass


class KModule:
    def __init__(self, name, exports=None):
        if not isinstance(name, str) or not name.strip():
            raise KModuleError("Invalid module name")
        self.name = name
        self.exports = dict(exports or {})

    def export(self, name, value):
        if not isinstance(name, str) or not name:
            raise KModuleError("Invalid export name")
        self.exports[name] = value
        return value

    def get(self, name):
        if name not in self.exports:
            raise KModuleError(
                f"Module '{self.name}' has no export '{name}'"
            )
        return self.exports[name]


class KModuleRegistry:
    def __init__(self):
        self.modules = {}

    def register(self, module):
        if not isinstance(module, KModule):
            raise KModuleError("Expected a KModule")
        if module.name in self.modules:
            raise KModuleError(
                f"Module already registered: {module.name}"
            )
        self.modules[module.name] = module
        return module

    def create(self, name, exports=None):
        return self.register(KModule(name, exports))

    def load(self, name):
        if name not in self.modules:
            raise KModuleError(f"Module not found: {name}")
        return self.modules[name]

    def import_module(self, name, alias=None, environment=None):
        module = self.load(name)
        target = environment if environment is not None else {}
        key = alias or name
        target[key] = module
        return module

    def import_symbol(self, module_name, symbol, alias=None,
                      environment=None):
        module = self.load(module_name)
        target = environment if environment is not None else {}
        target[alias or symbol] = module.get(symbol)
        return target[alias or symbol]

    def names(self):
        return sorted(self.modules.keys())


DEFAULT_MODULES = KModuleRegistry()
