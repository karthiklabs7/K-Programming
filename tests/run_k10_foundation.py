from pathlib import Path
import ast
import subprocess
import sys

root = Path(__file__).resolve().parent.parent
interpreter = root / "interpreter/k_1_0_dev.py"
example = root / "examples/classes_09.k"
regression = root / "tests/run_k09_regression.py"

checks = 0

def passed(name):
    global checks
    checks += 1
    print("[PASS]", name)

ast.parse(interpreter.read_text(encoding="utf-8"))
passed("K 1.0 Python syntax")

result = subprocess.run(
    [sys.executable, str(regression)],
    cwd=root,
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(result.stdout)
    print(result.stderr)
    raise SystemExit("Regression suite failed")
passed("K 0.9.1 compatibility regression")

result = subprocess.run(
    [sys.executable, str(interpreter), str(example)],
    cwd=root,
    capture_output=True,
    text=True
)
if result.returncode != 0:
    print(result.stderr)
    raise SystemExit("Class example execution failed")

actual = result.stdout.strip().splitlines()
expected = ["Karthik", "18", "19"]

if actual != expected:
    print("Expected:", expected)
    print("Actual:", actual)
    raise SystemExit("Class example output mismatch")

passed("Class and object runtime compatibility")

print("==============================")
print("K 1.0 FOUNDATION TEST SUCCESS")
print("Passed:", checks)
print("Failed: 0")
print("==============================")
