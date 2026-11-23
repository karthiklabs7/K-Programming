import subprocess
import sys
import os
from pathlib import Path

checks = [
    ("K 1.0 foundation", [sys.executable, "tests/run_k10_foundation.py"]),
    ("Lexer engine", [sys.executable, "-m", "unittest", "tests.test_k10_lexer_engine"]),
    ("Lexer integration", [sys.executable, "-m", "unittest", "tests.test_k10_lexer_integration"]),
    ("Parser", [sys.executable, "-m", "unittest", "tests.test_k10_parser"]),
    ("Frontend", [sys.executable, "-m", "unittest", "tests.test_k10_frontend"]),
    ("Runtime bridge", [sys.executable, "-m", "unittest", "tests.test_k10_runtime_bridge"]),
    ("AST expressions", [sys.executable, "-m", "unittest", "tests.test_k10_ast_runtime"]),
    ("AST statements", [sys.executable, "-m", "unittest", "tests.test_k10_ast_statements"]),
    ("AST exceptions", [sys.executable, "-m", "unittest", "tests.test_k10_ast_exceptions"]),
    ("Collections", [sys.executable, "-m", "unittest", "tests.test_k10_collections"]),
    ("Modules", [sys.executable, "-m", "unittest", "tests.test_k10_modules"]),
    ("File handling", [sys.executable, "-m", "unittest", "tests.test_k10_files"]),
    ("Standard library", [sys.executable, "-m", "unittest", "tests.test_k10_stdlib"]),
    ("Diagnostics", [sys.executable, "-m", "unittest", "tests.test_k10_diagnostics"]),
    ("Optimizer", [sys.executable, "-m", "unittest", "tests.test_k10_optimizer"]),
    ("Runtime safety", [sys.executable, "-m", "unittest", "tests.test_k10_safety"]),
]

passed = failed = 0
env = os.environ.copy()
paths = [str(Path(__file__).resolve().parents[1] / "interpreter"),
         str(Path(__file__).resolve().parents[1])]
env["PYTHONPATH"] = os.pathsep.join(
    paths + ([env["PYTHONPATH"]] if env.get("PYTHONPATH") else [])
)
env["K_CI_IMPORT_PATH"] = "1"

for label, command in checks:
    result = subprocess.run(command, capture_output=True, text=True, env=env)
    if result.returncode == 0:
        print("[PASS] " + label)
        passed += 1
    else:
        print("[FAIL] " + label)
        details = (result.stdout + result.stderr).strip()
        print(details[-1200:] if details else "No error details")
        failed += 1

print("==============================")
print("K 1.0 FULL TEST SUITE SUMMARY")
print(f"Passed groups: {passed}")
print(f"Failed groups: {failed}")
if failed:
    print("FULL TEST SUITE NEEDS FIXES")
    sys.exit(1)
print("K 1.0 FULL TEST SUITE SUCCESS")
