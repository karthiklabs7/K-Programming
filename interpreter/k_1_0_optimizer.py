"""Safe, standalone AST optimizer for K 1.0."""

def _constant(node):
    if not isinstance(node, dict):
        return False, None
    kind = node.get("type", node.get("kind"))
    if kind in ("number", "string", "boolean", "literal"):
        return True, node.get("value")
    return False, None

def _literal(value, original):
    kind = "boolean" if isinstance(value, bool) else (
        "number" if isinstance(value, (int, float)) else
        "string" if isinstance(value, str) else "literal"
    )
    return {"type": kind, "value": value}

def _fold(op, a, b):
    operations = {
        "+": lambda: a + b,
        "-": lambda: a - b,
        "*": lambda: a * b,
        "/": lambda: a / b,
        "%": lambda: a % b,
        "==": lambda: a == b,
        "!=": lambda: a != b,
        ">": lambda: a > b,
        "<": lambda: a < b,
        ">=": lambda: a >= b,
        "<=": lambda: a <= b,
        "and": lambda: bool(a) and bool(b),
        "or": lambda: bool(a) or bool(b),
    }
    if op not in operations:
        raise ValueError("Unsupported operator")
    if op in ("/", "%") and b == 0:
        raise ZeroDivisionError
    return operations[op]()

def optimize(node):
    if isinstance(node, list):
        return [optimize(item) for item in node]
    if isinstance(node, tuple):
        return tuple(optimize(item) for item in node)
    if not isinstance(node, dict):
        return node

    result = {key: optimize(value) for key, value in node.items()}
    kind = result.get("type", result.get("kind"))

    if kind in ("binary", "binaryexpression", "binary_expression"):
        left_key = "left" if "left" in result else None
        right_key = "right" if "right" in result else None
        op = result.get("operator", result.get("op"))
        if left_key and right_key:
            left_ok, left = _constant(result[left_key])
            right_ok, right = _constant(result[right_key])
            if left_ok and right_ok:
                try:
                    return _literal(_fold(op, left, right), result)
                except (ArithmeticError, TypeError, ValueError, OverflowError):
                    pass
    return result

def optimize_program(program):
    return optimize(program)
