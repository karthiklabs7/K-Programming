"""K 1.0 lexer integration interface.

The legacy interpreter remains unchanged. This module exposes the
new lexer through a stable interface for future parser integration.
"""
try:
    from .k_1_0_lexer_engine import Lexer, LexerError, Token, tokenize
except ImportError:
    from k_1_0_lexer_engine import Lexer, LexerError, Token, tokenize

def lex_source(source):
    if not isinstance(source, str):
        raise TypeError("K source must be a string")
    return tokenize(source)

__all__ = ["Lexer", "LexerError", "Token", "tokenize", "lex_source"]
