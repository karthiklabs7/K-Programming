from dataclasses import dataclass
try:
    from .k_1_0_lexer import tokenize
except ImportError:
    from k_1_0_lexer import tokenize

@dataclass
class Node:
    kind: str
    fields: dict

class ParserError(Exception):
    pass

class Parser:
    PRECEDENCE = {
        "=": 1, "or": 2, "OR": 2, "||": 2,
        "and": 3, "AND": 3, "&&": 3,
        "==": 4, "!=": 4, "<": 5, "<=": 5,
        ">": 5, ">=": 5, "+": 6, "-": 6,
        "*": 7, "/": 7, "%": 7
    }

    def __init__(self, source):
        source = source.replace(" AND ", " and ").replace(" OR ", " or ")
        self.tokens = tokenize(source)
        self.pos = 0

    def current(self):
        return self.tokens[self.pos]

    def check(self, value):
        return self.current().value == value

    def advance(self):
        token = self.current()
        if token.kind != "EOF":
            self.pos += 1
        return token

    def match(self, *values):
        if self.current().value in values:
            return self.advance()
        return None

    def expect(self, value):
        token = self.match(value)
        if token is None:
            t = self.current()
            raise ParserError(
                f"Expected {value!r} at {t.line}:{t.column}, got {t.value!r}"
            )
        return token

    def expect_kind(self, kind):
        token = self.current()
        if token.kind != kind:
            raise ParserError(
                f"Expected {kind} at {token.line}:{token.column}, got {token.value!r}"
            )
        return self.advance()

    def parse(self):
        body = []
        while self.current().kind != "EOF":
            body.append(self.statement())
        return Node("Program", {"body": body})

    def statement(self):
        if self.match("say"):
            value = self.expression()
            self.match(";")
            return Node("ExpressionStatement", {
                "expression": Node("Call", {
                    "callee": Node("Identifier", {"name": "say"}),
                    "arguments": [value]
                })
            })

        if self.match("import"):
            value = self.advance()
            if value.kind not in ("STRING", "IDENTIFIER"):
                raise ParserError("Expected module name after import")
            self.match(";")
            return Node("ImportStatement", {"module": value.value})

        if self.match("fun"):
            return self.function_decl()
        if self.match("class"):
            return self.class_decl()
        if self.match("if"):
            return self.if_stmt()
        if self.match("while"):
            return self.while_stmt()
        if self.match("for"):
            return self.for_stmt()
        if self.match("repeat"):
            return self.repeat_stmt()
        if self.match("try"):
            return self.try_stmt()
        if self.match("return"):
            return self.return_stmt()
        if self.match("break"):
            self.match(";")
            return Node("BreakStatement", {})
        if self.match("continue"):
            self.match(";")
            return Node("ContinueStatement", {})
        if self.match("{"):
            return self.block_after_open()

        expr = self.expression()
        self.match(";")
        return Node("ExpressionStatement", {"expression": expr})

    def block_after_open(self):
        body = []
        while not self.check("}") and self.current().kind != "EOF":
            body.append(self.statement())
        self.expect("}")
        return Node("Block", {"body": body})

    def block(self):
        self.expect("{")
        return self.block_after_open()

    def body_statement(self):
        if self.match("("):
            value = self.expression()
            self.expect(")")
            return value
        return self.expression()

    def parameters(self):
        self.expect("(")
        params = []
        if not self.check(")"):
            while True:
                params.append(self.expect_kind("IDENTIFIER").value)
                if not self.match(","):
                    break
        self.expect(")")
        return params

    def function_decl(self):
        name = self.expect_kind("IDENTIFIER").value
        params = self.parameters()
        body = self.block()
        return Node("FunctionDeclaration", {
            "name": name, "params": params, "body": body
        })

    def class_decl(self):
        name = self.expect_kind("IDENTIFIER").value
        self.expect("{")
        methods, fields = [], []
        while not self.check("}") and self.current().kind != "EOF":
            if self.match("fun"):
                methods.append(self.function_decl())
            else:
                fields.append(self.statement())
        self.expect("}")
        return Node("ClassDeclaration", {
            "name": name, "methods": methods, "fields": fields
        })

    def if_stmt(self):
        condition = self.body_statement()
        then_branch = self.statement()
        else_branch = None
        if self.match("else"):
            else_branch = self.statement()
        return Node("IfStatement", {
            "condition": condition,
            "then_branch": then_branch,
            "else_branch": else_branch
        })

    def while_stmt(self):
        condition = self.body_statement()
        body = self.statement()
        return Node("WhileStatement", {"condition": condition, "body": body})

    def for_stmt(self):
        name = self.expect_kind("IDENTIFIER").value
        self.expect("in")
        iterable = self.expression()
        body = self.statement()
        return Node("ForInStatement", {
            "name": name, "iterable": iterable, "body": body
        })

    def repeat_stmt(self):
        count = self.expression()
        body = self.statement()
        return Node("RepeatStatement", {"count": count, "body": body})

    def try_stmt(self):
        body = self.statement()
        self.expect("catch")
        handler = self.statement()
        return Node("TryCatchStatement", {
            "body": body, "handler": handler
        })

    def return_stmt(self):
        value = None
        if not self.check(";") and not self.check("}") and self.current().kind != "EOF":
            value = self.expression()
        self.match(";")
        return Node("ReturnStatement", {"value": value})

    def expression(self, minimum=1):
        left = self.prefix()
        while True:
            op = self.current().value

            if op == "(":
                self.advance()
                args = []
                if not self.check(")"):
                    while True:
                        args.append(self.expression())
                        if not self.match(","):
                            break
                self.expect(")")
                left = Node("Call", {"callee": left, "arguments": args})
                continue

            if op == ".":
                self.advance()
                name = self.expect_kind("IDENTIFIER").value
                left = Node("Member", {"object": left, "name": name})
                continue

            if op == "[":
                self.advance()
                index = self.expression()
                self.expect("]")
                left = Node("Index", {"object": left, "index": index})
                continue

            precedence = self.PRECEDENCE.get(op, 0)
            if precedence < minimum:
                break

            self.advance()
            right_minimum = precedence if op == "=" else precedence + 1
            right = self.expression(right_minimum)
            kind = "Assignment" if op == "=" else "Binary"
            left = Node(kind, {
                "operator": op, "left": left, "right": right
            })
        return left

    def prefix(self):
        token = self.advance()
        value = token.value

        if token.kind == "NUMBER":
            return Node("Number", {"value": value})
        if token.kind == "STRING":
            return Node("String", {"value": value})
        if token.kind == "IDENTIFIER":
            return Node("Identifier", {"name": value})

        if value in ("true", "false", "null"):
            return Node("Literal", {
                "value": {"true": True, "false": False, "null": None}[value]
            })

        if value in ("-", "+", "!", "not"):
            return Node("Unary", {
                "operator": value, "operand": self.expression(8)
            })

        if value == "(":
            expr = self.expression()
            self.expect(")")
            return Node("Grouping", {"expression": expr})

        if value == "[":
            elements = []
            if not self.check("]"):
                while True:
                    elements.append(self.expression())
                    if not self.match(","):
                        break
            self.expect("]")
            return Node("Array", {"elements": elements})

        if value == "{":
            pairs = []
            if not self.check("}"):
                while True:
                    key = self.expression()
                    self.expect(":")
                    val = self.expression()
                    pairs.append((key, val))
                    if not self.match(","):
                        break
            self.expect("}")
            return Node("Map", {"pairs": pairs})

        raise ParserError(
            f"Unexpected token {value!r} at {token.line}:{token.column}"
        )

def parse(source):
    return Parser(source).parse()
