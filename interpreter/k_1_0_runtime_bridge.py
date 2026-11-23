"""Experimental K 1.0 frontend-to-legacy-runtime bridge."""
import sys
from pathlib import Path

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from k_1_0_frontend import compile_source

class RuntimeBridgeError(Exception):
    pass

def run_with_frontend(source, legacy_runner):
    """Validate source with the new frontend, then use legacy execution.

    The legacy runner remains responsible for execution until an AST
    evaluator is implemented and tested.
    """
    if not isinstance(source, str):
        raise TypeError("K source must be a string")

    try:
        frontend_result = compile_source(source)
    except Exception as error:
        raise RuntimeBridgeError(
            f"K frontend rejected source: {error}"
        ) from error

    legacy_result = legacy_runner(source)

    return {
        "frontend": frontend_result,
        "execution": legacy_result,
        "execution_engine": "legacy"
    }
