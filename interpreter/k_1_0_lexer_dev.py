import sys
import ast
import operator
import re
from pathlib import Path

VERSION = "0.9.0"

variables = {}
functions = {}
classes = {}

class KObject:
    def __init__(self, class_name, attributes):
        self.class_name = class_name
        self.attributes = attributes
scopes = []
CURRENT_DIRS = []
IMPORTED_MODULES = set()

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


class BreakSignal(Exception):
    pass


class ContinueSignal(Exception):
    pass


def get_variable(name):
    for scope in reversed(scopes):
        if name in scope:
            return scope[name]

    if name in variables:
        return variables[name]

    raise ValueError(f"Unknown variable: {name}")


def has_private_access(obj):
    return any(scope.get("self") is obj for scope in reversed(scopes))


class KThrow(Exception):
    pass


class_parents = {}


@__import__('functools').lru_cache(maxsize=512)
def _cached_expression_ast(expression):
    return ast.parse(expression, mode='eval')


def calculate(expression):
    expression = re.sub(r'\bAND\b', 'and', expression)
    expression = re.sub(r'\bOR\b', 'or', expression)
    expression = re.sub(r'\bNOT\b', 'not', expression)

    try:
        tree = _cached_expression_ast(expression)
    except SyntaxError:
        print("K DEBUG: Invalid expression:", repr(expression))
        raise

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

        if isinstance(node, ast.Attribute):
            obj = evaluate(node.value)
            if isinstance(obj, KObject):
                if node.attr.startswith("_") and not has_private_access(obj):
                    raise ValueError("Private property access denied: " + node.attr)
                if node.attr not in obj.attributes:
                    raise ValueError(f"Unknown property: {node.attr}")
                return obj.attributes[node.attr]
            raise ValueError("Property access is supported only for K objects")

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

                if name == "assert_true":
                    if len(args) not in (1, 2):
                        raise ValueError("assert_true() requires one condition and optional message")
                    if not args[0]:
                        raise AssertionError(str(args[1]) if len(args) == 2 else "Assertion failed")
                    return True

                if name == "debug":
                    if len(args) != 1:
                        raise ValueError("debug() requires exactly one argument")
                    print("[DEBUG]", repr(args[0]))
                    return args[0]

                if name == "error_message":
                    if len(args) != 1:
                        raise ValueError("error_message() requires exactly one argument")
                    return str(args[0])

                if name == "input":
                    if len(args) > 1:
                        raise ValueError("input() accepts zero or one prompt")
                    return input(str(args[0]) if args else "")

                if name == "abs":
                    if len(args) != 1 or not isinstance(args[0], (int, float)):
                        raise ValueError("abs() requires one number")
                    return abs(args[0])

                if name in ("min", "max", "sum"):
                    if len(args) != 1 or not isinstance(args[0], (list, tuple)):
                        raise ValueError(name + "() requires one list or tuple")
                    if not args[0]:
                        raise ValueError(name + "() does not accept an empty sequence")
                    if not all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in args[0]):
                        raise ValueError(name + "() requires numeric values")
                    return {"min": min, "max": max, "sum": sum}[name](args[0])

                if name == "round":
                    if len(args) not in (1, 2):
                        raise ValueError("round() requires one or two arguments")
                    if not isinstance(args[0], (int, float)):
                        raise ValueError("round() requires a number")
                    if len(args) == 2 and not isinstance(args[1], int):
                        raise ValueError("round() digits must be an integer")
                    return round(*args)

                if name == "range":
                    if not 1 <= len(args) <= 3:
                        raise ValueError("range() requires one to three arguments")
                    if not all(isinstance(x, int) and not isinstance(x, bool) for x in args):
                        raise ValueError("range() arguments must be integers")
                    return list(range(*args))

                if name in ("keys", "values"):
                    if len(args) != 1 or not isinstance(args[0], dict):
                        raise ValueError(name + "() requires one dictionary")
                    return list(args[0].keys() if name == "keys" else args[0].values())

                if name == "contains":
                    if len(args) != 2:
                        raise ValueError("contains() requires two arguments")
                    try:
                        return args[1] in args[0]
                    except TypeError:
                        raise ValueError("contains() requires a searchable collection")

                if name in classes:
                    attributes = {}
                    scopes.append(attributes)
                    try:
                        for item in classes[name]:
                            if item[0] == "assign":
                                attributes[item[1]] = calculate(item[2])
                            elif item[0] == "function":
                                attributes[item[1]] = ("function", item[2], item[3])
                            elif item[0] == "static_function":
                                continue
                            else:
                                raise ValueError("Unsupported class member")
                    finally:
                        scopes.pop()

                    obj = KObject(name, attributes)
                    if "init" in attributes:
                        call_method(obj, "init", args)
                    elif args:
                        raise ValueError("This class has no init constructor")
                    return obj

                if name in ("read_file", "write_file", "append_file"):
                    expected = 1 if name == "read_file" else 2
                    if len(args) != expected:
                        raise ValueError(f"{name}() expects {expected} arguments")

                    base = CURRENT_DIRS[-1] if CURRENT_DIRS else Path.cwd()
                    file_path = (Path(base) / str(args[0])).resolve()

                    if name == "read_file":
                        return file_path.read_text(encoding="utf-8")

                    file_path.parent.mkdir(parents=True, exist_ok=True)
                    mode = "w" if name == "write_file" else "a"
                    with file_path.open(mode, encoding="utf-8") as file:
                        file.write(str(args[1]))
                    return None

                return call_function(name, args)

            if isinstance(node.func, ast.Attribute):
                method = node.func.attr

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id == "super"
                ):
                    current_scope = next(
                        (
                            scope for scope in reversed(scopes)
                            if "self" in scope and "__class__" in scope
                        ),
                        None
                    )
                    if current_scope is None:
                        raise ValueError("super() requires a class method")

                    current_class = current_scope["__class__"]
                    parent_class = class_parents.get(current_class)

                    if parent_class is None:
                        raise ValueError("No parent class available for super()")

                    return call_method(
                        current_scope["self"],
                        method,
                        args,
                        parent_class
                    )

                if (
                    isinstance(node.func.value, ast.Name)
                    and node.func.value.id in classes
                ):
                    return call_static_method(
                        node.func.value.id, method, args
                    )

                obj = evaluate(node.func.value)

                if isinstance(obj, KObject):
                    return call_method(obj, method, args)

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



def call_static_method(class_name, name, args):
    if name.startswith("_"):
        raise ValueError("Private static method access denied: " + name)

    for item in classes.get(class_name, []):
        if item[0] == "static_function" and item[1] == name:
            parameters = item[2]
            body = item[3]

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

    raise ValueError(f"Unknown static method: {name}")


def call_method(obj, name, args, owner_class=None):
    if name.startswith("_") and not has_private_access(obj):
        raise ValueError("Private method access denied: " + name)

    lookup_class = owner_class or obj.class_name

    for item in classes.get(lookup_class, []):
        if item[0] == "function" and item[1] == name:
            parameters = item[2]
            body = item[3]

            if not parameters or parameters[0] != "self":
                raise ValueError("First method parameter must be self")

            expected = len(parameters) - 1

            if len(args) != expected:
                raise ValueError(
                    f"{name} expects {expected} arguments, got {len(args)}"
                )

            local_scope = {
                "self": obj,
                "__class__": lookup_class
            }
            local_scope.update(zip(parameters[1:], args))
            scopes.append(local_scope)

            try:
                execute(body)
            except ReturnSignal as result:
                return result.value
            finally:
                scopes.pop()

            return None

    raise ValueError(f"Unknown method: {name}")



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

        if line == "catch {":
            return statements, index

        if line == "try {":
            body, index = parse_block(lines, index + 1)

            if index >= len(lines) or lines[index].strip() != "catch {":
                raise ValueError("try block requires catch block")

            catch_body, index = parse_block(lines, index + 1)
            finally_body = None

            if index < len(lines) and lines[index].strip() == "finally {":
                finally_body, index = parse_block(lines, index + 1)

            statements.append(("try", body, catch_body, finally_body))
            continue

        if line.startswith("import "):
            statements.append(("import", line[7:].strip()))
            index += 1
            continue

        if line.startswith("class ") and line.endswith("{") and len(line[:-1].split()) in (2, 4):
            header = line[:-1].strip().split()
            name = header[1]
            parent = None
            if len(header) == 4:
                if header[2] != "extends":
                    raise ValueError("Invalid class declaration")
                parent = header[3]
            if not name.isidentifier():
                raise ValueError("Invalid class name")
            if parent is not None and not parent.isidentifier():
                raise ValueError("Invalid parent class name")
            if not name.isidentifier():
                raise ValueError("Invalid class name")
            body, index = parse_block(lines, index + 1)
            statements.append(("class", name, body, parent))
            continue

        if line.startswith("static fun ") and line.endswith("{"):
            header = line[len("static fun "):-1].strip()

            if "(" not in header or not header.endswith(")"):
                raise ValueError("Invalid static method declaration")

            name, params_text = header.split("(", 1)
            name = name.strip()
            params_text = params_text[:-1].strip()
            params = [
                p.strip() for p in params_text.split(",") if p.strip()
            ]

            if not name.isidentifier():
                raise ValueError("Invalid static method name")
            if any(not p.isidentifier() for p in params):
                raise ValueError("Invalid static method parameter")
            if len(set(params)) != len(params):
                raise ValueError("Duplicate static method parameter")

            body, index = parse_block(lines, index + 1)
            statements.append(("static_function", name, params, body))
            continue

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

        if line.startswith("for ") and line.endswith("{"):
            header = line[4:-1].strip()
            variable, separator, expression = header.partition(" in ")
            variable = variable.strip()
            expression = expression.strip()

            if not separator or not variable.isidentifier() or not expression:
                raise ValueError("Invalid for loop syntax")

            body, index = parse_block(lines, index + 1)
            statements.append(("for", variable, expression, body))
            continue

        if line.startswith("throw "):
            expression = line[6:].strip()
            if not expression:
                raise ValueError("throw requires an expression")
            statements.append(("throw", expression))
            index += 1
            continue

        if line == "break":
            statements.append(("break",))
            index += 1
            continue

        if line == "continue":
            statements.append(("continue",))
            index += 1
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

            if "." in name:
                object_name, attribute = name.rsplit(".", 1)
                if not object_name.isidentifier() or not attribute.isidentifier():
                    raise ValueError("Invalid property assignment")
                statements.append(("set_attribute", object_name, attribute, expression.strip()))
            else:
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

        if kind == "class":
            parent = statement[3] if len(statement) > 3 else None
            members = []
            if parent is not None:
                if parent not in classes:
                    raise ValueError("Parent class not found: " + parent)
                members.extend(classes[parent])

            for member in statement[2]:
                if member[0] in ("function", "static_function"):
                    member_kind = member[0]
                    previous = next(
                        (
                            old_member for old_member in reversed(members)
                            if old_member[0] == member_kind
                            and old_member[1] == member[1]
                        ),
                        None
                    )

                    if (
                        member_kind == "function"
                        and previous is not None
                        and previous[2] != member[2]
                    ):
                        raise ValueError(
                            "Override parameter mismatch in method: "
                            + member[1]
                        )

                    members = [
                        old_member for old_member in members
                        if not (
                            old_member[0] == member_kind
                            and old_member[1] == member[1]
                        )
                    ]

                members.append(member)

            classes[statement[1]] = members
            class_parents[statement[1]] = parent

        elif kind == "try":
            try:
                execute(statement[1])
            except ReturnSignal:
                raise
            except Exception:
                execute(statement[2])
            finally:
                if len(statement) > 3 and statement[3] is not None:
                    execute(statement[3])

        elif kind == "throw":
            value = calculate(statement[1])
            raise KThrow(str(value))

        elif kind == "set_attribute":
            obj = get_variable(statement[1])
            if not isinstance(obj, KObject):
                raise ValueError("Property assignment requires a K object")
            if statement[2].startswith("_") and not has_private_access(obj):
                raise ValueError("Private property assignment denied: " + statement[2])
            obj.attributes[statement[2]] = calculate(statement[3])

        elif kind == "function":
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

        elif kind == "import":
            module_name = calculate(statement[1])
            if not isinstance(module_name, str):
                raise ValueError("Module name must be a string")

            base = CURRENT_DIRS[-1] if CURRENT_DIRS else Path.cwd()
            module_path = (Path(base) / module_name).resolve()

            if module_path in IMPORTED_MODULES:
                continue
            if not module_path.is_file():
                raise ValueError(f"Module not found: {module_name}")

            IMPORTED_MODULES.add(module_path)
            CURRENT_DIRS.append(module_path.parent)
            try:
                module_source = module_path.read_text(encoding="utf-8")
                module_lines = []
                for module_line in module_source.splitlines():
                    if module_line.strip() == "} else {":
                        module_lines.extend(["}", "else {"])
                    else:
                        module_lines.append(module_line)
                module_program, module_end = parse_block(module_lines, 0)
                if module_end != len(module_lines):
                    raise ValueError("Unexpected closing brace in module")
                execute(module_program)
            finally:
                CURRENT_DIRS.pop()

        elif kind == "try":
            try:
                execute(statement[1])
            except (ReturnSignal, BreakSignal, ContinueSignal):
                raise
            except Exception as error:
                if scopes:
                    scopes[-1]["error"] = str(error)
                else:
                    variables["error"] = str(error)
                execute(statement[2])

        elif kind == "break":
            raise BreakSignal()

        elif kind == "continue":
            raise ContinueSignal()

        elif kind == "for":
            variable, expression, body = statement[1:]
            iterable = calculate(expression)

            if not isinstance(iterable, (list, tuple, str)):
                raise ValueError("for loop requires a list, tuple or string")

            if len(iterable) > 100000:
                raise ValueError("for loop safety limit reached")

            for item in iterable:
                if scopes:
                    scopes[-1][variable] = item
                else:
                    variables[variable] = item

                try:
                    execute(body)
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

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
                try:
                    execute(statement[2])
                except ContinueSignal:
                    continue
                except BreakSignal:
                    break

        elif kind == "while":
            iterations = 0

            while calculate(statement[1]):
                if iterations >= 100000:
                    raise ValueError("While loop safety limit reached")

                try:
                    execute(statement[2])
                except ContinueSignal:
                    iterations += 1
                    continue
                except BreakSignal:
                    break

                iterations += 1


def run(source):
    lines = []

    for line in source.splitlines():
        if line.strip() == "} else {":
            lines.extend(["}", "else {"])
        elif line.strip() == "} catch {":
            lines.extend(["}", "catch {"])
        else:
            lines.append(line)

    try:
        program, end = parse_block(lines, 0)

        if end != len(lines):
            raise ValueError("Unexpected closing brace")

        execute(program)

    except ReturnSignal:
        print("K Error: return outside a function")
    except BreakSignal:
        print("K Error: break outside a loop")
    except ContinueSignal:
        print("K Error: continue outside a loop")
    except Exception as error:
        print(f"K Error: {error}")


if len(sys.argv) != 2:
    print(f"K Programming {VERSION}")
    print("Usage: python interpreter/k.py filename.k")
else:
    variables.clear()
    functions.clear()
    classes.clear()
    scopes.clear()
    IMPORTED_MODULES.clear()
    CURRENT_DIRS.clear()

    try:
        main_file = Path(sys.argv[1]).resolve()
        CURRENT_DIRS.append(main_file.parent)
        with main_file.open(encoding="utf-8") as file:
            run(file.read())
    except FileNotFoundError:
        print("K Error: File not found")
