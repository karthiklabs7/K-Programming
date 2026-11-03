import sys
import ast
import operator
import re

VERSION = "0.3.0"
variables = {}

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

        if isinstance(node, ast.Name):
            if node.id in variables:
                return variables[node.id]
            raise ValueError(f"Unknown variable: {node.id}")

        if isinstance(node, ast.BinOp):
            operation = OPERATORS.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator")
            return operation(evaluate(node.left), evaluate(node.right))

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.UAdd):
                return +value
            if isinstance(node.op, ast.Not):
                return not value
            raise ValueError("Unsupported unary operator")

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

        raise ValueError("Invalid expression")

    return evaluate(tree.body)


def parse_block(lines, index):
    statements = []

    while index < len(lines):
        line = lines[index].strip()

        if not line or line.startswith("#"):
            index += 1
            continue

        if line == "}":
            return statements, index + 1

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

        if line == "else {":
            raise ValueError("Unexpected else block")

        if line.startswith("say "):
            statements.append(("say", line[4:].strip()))
            index += 1
            continue

        if "=" in line and not any(op in line for op in ["==", "!=", ">=", "<="]):
            name, expression = line.split("=", 1)
            name = name.strip()

            if not name.isidentifier():
                raise ValueError("Invalid variable name")

            statements.append(("assign", name, expression.strip()))
            index += 1
            continue

        raise ValueError(f"Unknown command: {line}")

    return statements, index


def execute(statements):
    for statement in statements:
        kind = statement[0]

        if kind == "say":
            print(calculate(statement[1]))

        elif kind == "assign":
            variables[statement[1]] = calculate(statement[2])

        elif kind == "if":
            if calculate(statement[1]):
                execute(statement[2])
            else:
                execute(statement[3])

        elif kind == "repeat":
            count = calculate(statement[1])
            if not isinstance(count, int) or count < 0 or count > 100000:
                raise ValueError("repeat needs an integer from 0 to 100000")
            for _ in range(count):
                execute(statement[2])

        elif kind == "while":
            iterations = 0
            while calculate(statement[1]):
                if iterations >= 100000:
                    raise ValueError("while loop safety limit reached")
                execute(statement[2])
                iterations += 1


def run(source):
    lines = source.splitlines()

    # Support: } else {
    normalized = []
    for line in lines:
        if line.strip() == "} else {":
            normalized.extend(["}", "else {"])
        else:
            normalized.append(line)

    try:
        program, end = parse_block(normalized, 0)

        if end != len(normalized):
            raise ValueError("Unexpected closing brace")

        execute(program)

    except Exception as error:
        print(f"K Error: {error}")


if len(sys.argv) != 2:
    print(f"K Programming {VERSION}")
    print("Usage: python interpreter/k.py filename.k")
else:
    variables.clear()
    try:
        with open(sys.argv[1], encoding="utf-8") as file:
            run(file.read())
    except FileNotFoundError:
        print("K Error: File not found")
