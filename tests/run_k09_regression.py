import ast
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
interpreter = root / "interpreter/k_0_9_1_dev.py"
example = root / "examples/classes_09.k"

tests = [
    ("Python syntax", lambda: ast.parse(interpreter.read_text(encoding="utf-8"))),
    ("Class example runtime", lambda: subprocess.run(
        [sys.executable, str(interpreter), str(example)],
        cwd=root, capture_output=True, text=True, check=True
    )),
]

failed = 0
for name, test in tests:
    try:
        result = test()
        if name == "Class example runtime" and result.stdout.strip().splitlines() != ["Karthik", "18", "19"]:
            raise AssertionError("Unexpected program output: " + result.stdout)
        print("[PASS]", name)
    except Exception as error:
        failed += 1
        print("[FAIL]", name, error)

print("Passed:", len(tests) - failed)
print("Failed:", failed)
print("K 0.9.1 REGRESSION SUCCESS" if failed == 0 else "K 0.9.1 NEEDS REVIEW")
sys.exit(1 if failed else 0)
