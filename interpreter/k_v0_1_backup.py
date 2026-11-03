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
}

def calculate(expression):
    tree = ast.parse(expression, mode="eval")

    def evaluate(node):
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float, str)):
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

        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = evaluate(node.operand)
            return -value if isinstance(node.op, ast.USub) else +value

        raise ValueError("Invalid expression")

    return evaluate(tree.body)

def run(source):
    for line_no, line in enumerate(source.splitlines(), 1):
        line = line.strip()

        if not line or line.startswith("#"):
            continue

        try:
            if line.startswith("say "):
                value = calculate(line[4:].strip())
                print(value)

            elif "=" in line:
                name, expression = line.split("=", 1)
                name = name.strip()

                if not name.isidentifier():
                    raise ValueError("Invalid variable name")

                variables[name] = calculate(expression.strip())

            else:
                raise ValueError("Unknown command")

        except Exception as error:
            print(f"K Error at line {line_no}: {error}")
            return

if len(sys.argv) != 2:
    print("K Programming 0.1.0")
    print("Usage: python interpreter/k.py filename.k")
else:
    try:
        with open(sys.argv[1], encoding="utf-8") as file:
            run(file.read())
    except FileNotFoundError:
        print("K Error: File not found")
