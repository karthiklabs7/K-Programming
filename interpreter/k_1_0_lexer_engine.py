from dataclasses import dataclass

KEYWORDS = {
    "fun", "class", "return", "if", "else", "while", "for",
    "in", "break", "continue", "try", "catch", "finally",
    "throw", "new", "this", "super", "static", "true", "false",
    "null", "and", "or", "not", "import", "from", "as"
}

OPERATORS = (
    "==", "!=", "<=", ">=", "&&", "||", "++", "--",
    "+=", "-=", "*=", "/=", "%=", "->",
    "+", "-", "*", "/", "%", "=", "<", ">", "!",
    ".", ",", ":", ";", "(", ")", "{", "}", "[", "]"
)

@dataclass(frozen=True)
class Token:
    kind: str
    value: object
    line: int
    column: int

    def __repr__(self):
        return f"Token({self.kind!r}, {self.value!r}, {self.line}:{self.column})"


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, source):
        self.source = source
        self.index = 0
        self.line = 1
        self.column = 1
        self.tokens = []

    def peek(self, offset=0):
        pos = self.index + offset
        return self.source[pos] if pos < len(self.source) else ""

    def advance(self):
        char = self.peek()
        if char:
            self.index += 1
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
        return char

    def add(self, kind, value, line, column):
        self.tokens.append(Token(kind, value, line, column))

    def skip_space_and_comments(self):
        while self.peek():
            if self.peek().isspace():
                self.advance()
            elif self.peek() == "#":
                while self.peek() and self.peek() != "\n":
                    self.advance()
            elif self.peek() == "/" and self.peek(1) == "/":
                while self.peek() and self.peek() != "\n":
                    self.advance()
            else:
                break

    def read_identifier(self):
        line, col = self.line, self.column
        value = ""
        while self.peek() and (self.peek().isalnum() or self.peek() == "_"):
            value += self.advance()
        kind = "KEYWORD" if value in KEYWORDS else "IDENTIFIER"
        self.add(kind, value, line, col)

    def read_number(self):
        line, col = self.line, self.column
        value = ""
        while self.peek().isdigit():
            value += self.advance()

        if self.peek() == "." and self.peek(1).isdigit():
            value += self.advance()
            while self.peek().isdigit():
                value += self.advance()
            self.add("NUMBER", float(value), line, col)
        else:
            self.add("NUMBER", int(value), line, col)

    def read_string(self):
        line, col = self.line, self.column
        quote = self.advance()
        value = ""

        while self.peek() and self.peek() != quote:
            char = self.advance()
            if char == "\n":
                raise LexerError(f"Unterminated string at {line}:{col}")
            if char == "\\":
                escaped = self.advance()
                escapes = {
                    "n": "\n", "t": "\t", "r": "\r",
                    "\\": "\\", '"': '"', "'": "'"
                }
                if not escaped:
                    raise LexerError(f"Unterminated escape at {self.line}:{self.column}")
                value += escapes.get(escaped, escaped)
            else:
                value += char

        if self.peek() != quote:
            raise LexerError(f"Unterminated string at {line}:{col}")
        self.advance()
        self.add("STRING", value, line, col)

    def tokenize(self):
        while self.peek():
            self.skip_space_and_comments()
            if not self.peek():
                break

            char = self.peek()
            line, col = self.line, self.column

            if char.isalpha() or char == "_":
                self.read_identifier()
            elif char.isdigit():
                self.read_number()
            elif char in ("'", '"'):
                self.read_string()
            else:
                operator = next(
                    (op for op in OPERATORS if self.source.startswith(op, self.index)),
                    None
                )
                if operator is None:
                    raise LexerError(
                        f"Unexpected character {char!r} at {line}:{col}"
                    )
                for _ in operator:
                    self.advance()
                self.add("OPERATOR", operator, line, col)

        self.add("EOF", None, self.line, self.column)
        return self.tokens


def tokenize(source):
    return Lexer(source).tokenize()
