import sys
import ast
import operator

variables = {}

operators = {
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
            operation = operators.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator")
            return operation(evaluate(node.left), evaluate(node.right))

        if isinstance(node, ast.Compare):
            left = evaluate(node.left)
            for op, comparator in zip(node.ops, node.comparators):
                right = evaluate(comparator)
                operation = operators.get(type(op))
                if operation is None or not operation(left, right):
                    return False
                left = right
            return True

        if isinstance(node, ast.BoolOp):
            values = [evaluate(value) for value in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)

        if isinstance(node, ast.UnaryOp):
            value = evaluate(node.operand)
            if isinstance(node.op, ast.USub):
                return -value
            if isinstance(node.op, ast.Not):
                return not value

        raise ValueError("Invalid expression")

    return evaluate(tree.body)


def run(source):
    lines = source.splitlines()
    i = 0

    def execute_block(start, end):
        i = start
        while i < end:
            line = lines[i].strip()

            if not line or line.startswith("#"):
                i += 1
                continue

            if line.startswith("if ") and line.endswith("{"):
                condition = calculate(line[3:-1].strip())
                depth = 1
                block_start = i + 1
                j = block_start

                while j < end and depth:
                    current = lines[j].strip()
                    if current.endswith("{"):
                        depth += 1
                    if current == "}":
                        depth -= 1
                    j += 1

                if depth:
                    raise ValueError(f"Missing closing brace at line {i+1}")

                true_end = j - 1
                else_start = None
                else_end = None

                if j < end and lines[j].strip() == "else {":
                    depth = 1
                    else_start = j + 1
                    k = else_start
                    while k < end and depth:
                        current = lines[k].strip()
                        if current.endswith("{"):
                            depth += 1
                        if current == "}":
                            depth -= 1
                        k += 1
                    if depth:
                        raise ValueError(f"Missing closing brace at line {j+1}")
                    else_end = k - 1
                    j = k

                if condition:
                    execute_block(block_start, true_end)
                elif else_start is not None:
                    execute_block(else_start, else_end)

                i = j
                continue

            if line.startswith("say "):
                print(calculate(line[4:].strip()))

            elif "=" in line and not any(op in line for op in ["==", "!=", ">=", "<="]):
                name, expression = line.split("=", 1)
                name = name.strip()
                if not name.isidentifier():
                    raise ValueError("Invalid variable name")
                variables[name] = calculate(expression.strip())

            else:
                raise ValueError(f"Unknown command: {line}")

            i += 1

    try:
        execute_block(0, len(lines))
    except Exception as error:
        print(f"K Error: {error}")


if len(sys.argv) != 2:
    print("K Programming 0.2.0")
    print("Usage: python interpreter/k.py filename.k")
else:
    variables.clear()
    try:
        with open(sys.argv[1], encoding="utf-8") as file:
            run(file.read())
    except FileNotFoundError:
        print("K Error: File not found")
