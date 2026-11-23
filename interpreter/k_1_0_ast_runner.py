"""K 1.0 AST execution pipeline."""
import sys
from pathlib import Path

MODULE_DIR = str(Path(__file__).resolve().parent)
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)

try:
    from .k_1_0_frontend import compile_source
    from .k_1_0_ast_statements import execute
except ImportError:
    from k_1_0_frontend import compile_source
    from k_1_0_ast_statements import execute


def run_ast(source, environment=None, builtins=None):
    compiled = compile_source(source)
    if not isinstance(compiled, dict) or "ast" not in compiled:
        raise RuntimeError("Frontend did not return an AST")
    return execute(
        compiled["ast"],
        environment=environment,
        builtins=builtins
    )
