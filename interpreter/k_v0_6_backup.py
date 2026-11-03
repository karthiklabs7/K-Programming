import sys
import ast
import operator
import re

VERSION = "0.6.0"

variables = {}
functions = {}
scopes = []

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Eq: operator.eq,
    ast.NotEq: operator.ne,
    ast.Gt: operator.gt,
    ast.GtE: operator.ge,
    ast.Lt: operator.lt,
    ast.LtE: operator.le,
}

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


def get_variable(name):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]

    if name in variables:
        return variables[name]

    raise ValueError(f"Unknown variable: {name}")


def calculate(expression):
    expression = re.sub(r'\bAND\b', 'and', expression)
    expression = re.sub(r'\bOR\b', 'or', expression)
    expression = re.sub(r'\bNOT\b', 'not', expression)

    tree = ast.parse(expression, mode="eval")

    def evaluate(node):

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str, bool)):
                return node.value
            raise ValueError("Unsupported value")

        if isinstance(node, ast.List):
            return [evaluate(item) for item in node.elts]

        if isinstance(node, ast.Tuple):
            return tuple(evaluate(item) for item in node.elts)

        if isinstance(node, ast.Dict):
            return {
                evaluate(key): evaluate(value)
                for key, value in zip(node.keys, node.values)
            }

        if isinstance(node, ast.Subscript):
            collection = evaluate(node.value)
            index = evaluate(node.slice)

            if isinstance(collection, dict):
                try:
                    return collection[index]
                except KeyError:
                    raise ValueError(f"Dictionary key not found: {index}")
                except TypeError:
                    raise ValueError("Invalid dictionary key")

            if isinstance(collection, (list, tuple, str)):
                if isinstance(index, bool) or not isinstance(index, int):
                    raise ValueError("List or string index must be an integer")
                try:
                    return collection[index]
                except IndexError:
                    raise ValueError("Index out of range")

            raise ValueError("Indexing is not supported for this value")

        if isinstance(node, ast.Name):
            return get_variable(node.id)

        if isinstance(node, ast.BinOp):
            operation = OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator")
            return operation(
                evaluate(node.left),
                evaluate(node.right)
            )

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)

            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.Not):
                return not value

        if isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(evaluate(v) for v in node.values)
            if isinstance(node.op, ast.Or):
                return any(evaluate(v) for v in node.values)

        if isinstance(node, ast.Compare):
            left = evaluate(node.left)

            for op, item in zip(node.ops, node.comparators):
                right = evaluate(item)
                operation = OPERATORS.get(type(op))

                if operation is None or not operation(left, right):
                    return False

                left = right

            return True

        if isinstance(node, ast.Call):
            args = [evaluate(arg) for arg in node.args]

            if isinstance(node.func, ast.Name):
                name = node.func.id

                if name == "length":
                    if len(args) != 1:
                        raise ValueError("length() requires exactly one argument")
                    if not isinstance(args[0], (str, list, tuple, dict)):
                        raise ValueError("length() supports strings, lists, tuples and dictionaries")
                    return len(args[0])

                if name == "type":
                    if len(args) != 1:
                        raise ValueError("type() requires exactly one argument")
                    value = args[0]
                    if isinstance(value, bool):
                        return "boolean"
                    if isinstance(value, (int, float)):
                        return "number"
                    if isinstance(value, str):
                        return "string"
                    if isinstance(value, list):
                        return "list"
                    if isinstance(value, dict):
                        return "dictionary"
                    if isinstance(value, tuple):
                        return "tuple"
                    if value is None:
                        return "none"
                    return "unknown"

                if name == "input":
                    if len(args) > 1:
                        raise ValueError("input() accepts zero or one prompt")
                    return input(str(args[0]) if args else "")

                return call_function(name, args)

            if isinstance(node.func, ast.Attribute):
                obj = evaluate(node.func.value)
                method = node.func.attr

                if isinstance(obj, list):
                    if method == "add" and len(args) == 1:
                        obj.append(args[0])
                        return None
                    if method == "remove" and len(args) == 1:
                        try:
                            obj.remove(args[0])
                        except ValueError:
                            raise ValueError("List value not found")
                        return None
                    if method == "sort" and len(args) == 0:
                        try:
                            obj.sort()
                        except TypeError:
                            raise ValueError("List items cannot be sorted together")
                        return None

                if isinstance(obj, str):
                    if method == "upper" and len(args) == 0:
                        return obj.upper()
                    if method == "lower" and len(args) == 0:
                        return obj.lower()
                    if method == "strip" and len(args) == 0:
                        return obj.strip()
                    if method == "replace" and len(args) == 2:
                        return obj.replace(str(args[0]), str(args[1]))

                raise ValueError("Unsupported method or incorrect arguments")

            raise ValueError("Invalid function call")

        raise ValueError("Invalid expression")

    return evaluate(tree.body)


def call_function(name, args):
    if name not in functions:
        raise ValueError(f"Unknown function: {name}")

    parameters, body = functions[name]

    if len(args) != len(parameters):
        raise ValueError(
            f"{name} expects {len(parameters)} arguments, got {len(args)}"
        )

    local_scope = dict(zip(parameters, args))
    scopes.append(local_scope)

    try:
        execute(body)
    except ReturnSignal as result:
        return result.value
    finally:
        scopes.pop()

    return None


def parse_block(lines, index):
    statements = []

    while index < len(lines):
        line = lines[index].strip()

        if not line or line.startswith("#"):
            index += 1
            continue

        if line == "}":
            return statements, index + 1

        if line.startswith("fun ") and line.endswith("{"):
            header = line[4:-1].strip()

            if "(" not in header or not header.endswith(")"):
                raise ValueError("Invalid function declaration")

            name, params_text = header.split("(", 1)
            name = name.strip()
            params_text = params_text[:-1].strip()

            if not name.isidentifier():
                raise ValueError("Invalid function name")

            params = [
                p.strip() for p in params_text.split(",") if p.strip()
            ]

            if any(not p.isidentifier() for p in params):
                raise ValueError("Invalid parameter name")

            if len(set(params)) != len(params):
                raise ValueError("Duplicate parameter")

            body, index = parse_block(lines, index + 1)
            statements.append(("function", name, params, body))
            continue

        if line.startswith("if ") and line.endswith("{"):
            condition = line[3:-1].strip()
            body, index = parse_block(lines, index + 1)
            else_body = []

            if index < len(lines) and lines[index].strip() == "else {":
                else_body, index = parse_block(lines, index + 1)

            statements.append(("if", condition, body, else_body))
            continue

        if line.startswith("repeat ") and line.endswith("{"):
            count = line[7:-1].strip()
            body, index = parse_block(lines, index + 1)
            statements.append(("repeat", count, body))
            continue

        if line.startswith("while ") and line.endswith("{"):
            condition = line[6:-1].strip()
            body, index = parse_block(lines, index + 1)
            statements.append(("while", condition, body))
            continue

        if line.startswith("say "):
            statements.append(("say", line[4:].strip()))
            index += 1
            continue

        if line.startswith("return "):
            statements.append(("return", line[7:].strip()))
            index += 1
            continue

        if line == "return":
            statements.append(("return", None))
            index += 1
            continue

        if "=" in line and not any(
            op in line for op in ["==", "!=", ">=", "<="]
        ):
            name, expression = line.split("=", 1)
            name = name.strip()

            if not name.isidentifier():
                raise ValueError("Invalid variable name")

            statements.append(("assign", name, expression.strip()))
            index += 1
            continue

        statements.append(("expression", line))
        index += 1

    return statements, index


def execute(statements):
    for statement in statements:
        kind = statement[0]

        if kind == "function":
            functions[statement[1]] = (
                statement[2],
                statement[3]
            )

        elif kind == "say":
            print(calculate(statement[1]))

        elif kind == "assign":
            value = calculate(statement[2])

            if scopes:
                scopes[-1][statement[1]] = value
            else:
                variables[statement[1]] = value

        elif kind == "return":
            if not scopes:
                raise ValueError("return can only be used inside a function")

            value = calculate(statement[1]) if statement[1] else None
            raise ReturnSignal(value)

        elif kind == "expression":
            calculate(statement[1])

        elif kind == "if":
            if calculate(statement[1]):
                execute(statement[2])
            else:
                execute(statement[3])

        elif kind == "repeat":
            count = calculate(statement[1])

            if not isinstance(count, int) or count < 0 or count > 100000:
                raise ValueError("Invalid repeat count")

            for _ in range(count):
                execute(statement[2])

        elif kind == "while":
            iterations = 0

            while calculate(statement[1]):
                if iterations >= 100000:
                    raise ValueError("While loop safety limit reached")

                execute(statement[2])
                iterations += 1


def run(source):
    lines = []

    for line in source.splitlines():
        if line.strip() == "} else {":
            lines.extend(["}", "else {"])
        else:
            lines.append(line)

    try:
        program, end = parse_block(lines, 0)

        if end != len(lines):
            raise ValueError("Unexpected closing brace")

        execute(program)

    except ReturnSignal:
        print("K Error: return outside a function")
    except Exception as error:
        print(f"K Error: {error}")


if len(sys.argv) != 2:
    print(f"K Programming {VERSION}")
    print("Usage: python interpreter/k.py filename.k")
else:
    variables.clear()
    functions.clear()
    scopes.clear()

    try:
        with open(sys.argv[1], encoding="utf-8") as file:
            run(file.read())
    except FileNotFoundError:
        print("K Error: File not found")
