"""Unified K 1.0 lexical and syntax frontend."""
try:
    from .k_1_0_lexer import tokenize, LexerError, Token
except ImportError:
    from k_1_0_lexer import tokenize, LexerError, Token
try:
    from .k_1_0_parser_engine import parse, Parser, ParserError
except ImportError:
    from k_1_0_parser_engine import parse, Parser, ParserError

def compile_source(source):
    if not isinstance(source, str):
        raise TypeError("K source must be a string")
    tokens = tokenize(source)
    syntax_tree = parse(source)
    return {
        "tokens": tokens,
        "ast": syntax_tree
    }

__all__ = [
    "tokenize", "parse", "compile_source",
    "LexerError", "ParserError", "Token", "Parser"
]
