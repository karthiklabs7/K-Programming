class KRuntimeError(Exception):
    pass


class Environment:
    def __init__(self, parent=None):
        self.values = {}
        self.parent = parent

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise KRuntimeError(f"Undefined variable: {name}")

    def set(self, name, value):
        self.values[name] = value
        return value


def field(node, name, default=None):
    if isinstance(node, dict):
        return node.get(name, default)
    data = getattr(node, "fields", None)
    if isinstance(data, dict):
        return data.get(name, default)
    return getattr(node, name, default)


def kind_of(node):
    return str(field(node, "kind", field(node, "type", ""))).lower()


def evaluate(node, environment=None, builtins=None):
    env = environment or Environment()
    functions = builtins or {}
    kind = kind_of(node)

    if kind in ("number", "string", "literal"):
        return field(node, "value")

    if kind == "identifier":
        return env.get(field(node, "name"))

    if kind == "grouping":
        return evaluate(field(node, "expression"), env, functions)

    if kind == "array":
        return [evaluate(x, env, functions)
                for x in field(node, "elements", [])]

    if kind == "unary":
        value = evaluate(field(node, "operand"), env, functions)
        op = field(node, "operator")
        if op == "-":
            return -value
        if op == "+":
            return +value
        if op in ("!", "not"):
            return not value
        raise KRuntimeError(f"Unsupported unary operator: {op}")

    if kind == "binary":
        op = field(node, "operator")
        left = evaluate(field(node, "left"), env, functions)

        if op in ("and", "&&"):
            return bool(left) and bool(
                evaluate(field(node, "right"), env, functions))
        if op in ("or", "||"):
            return bool(left) or bool(
                evaluate(field(node, "right"), env, functions))

        right = evaluate(field(node, "right"), env, functions)
        operations = {
            "+": lambda: left + right,
            "-": lambda: left - right,
            "*": lambda: left * right,
            "/": lambda: left / right,
            "%": lambda: left % right,
            "==": lambda: left == right,
            "!=": lambda: left != right,
            "<": lambda: left < right,
            ">": lambda: left > right,
            "<=": lambda: left <= right,
            ">=": lambda: left >= right,
        }
        if op not in operations:
            raise KRuntimeError(f"Unsupported binary operator: {op}")
        try:
            return operations[op]()
        except (TypeError, ZeroDivisionError) as error:
            raise KRuntimeError(str(error)) from error

    if kind == "assignment":
        target = field(node, "left")
        if kind_of(target) != "identifier":
            raise KRuntimeError("Assignment target must be a variable")
        value = evaluate(field(node, "right"), env, functions)
        return env.set(field(target, "name"), value)

    if kind == "index":
        obj = evaluate(field(node, "object"), env, functions)
        index = evaluate(field(node, "index"), env, functions)
        try:
            return obj[index]
        except (IndexError, KeyError, TypeError) as error:
            raise KRuntimeError(str(error)) from error

    if kind == "call":
        callee = field(node, "callee")
        if kind_of(callee) == "identifier":
            name = field(callee, "name")
            function = functions.get(name)
            if function is None:
                try:
                    function = env.get(name)
                except KRuntimeError:
                    raise KRuntimeError(f"Unknown function: {name}")
        else:
            function = evaluate(callee, env, functions)

        args = [evaluate(x, env, functions)
                for x in field(node, "arguments", [])]
        if not callable(function):
            raise KRuntimeError("Value is not callable")
        return function(*args)

    raise KRuntimeError(f"Unsupported AST node: {kind or 'unknown'}")
