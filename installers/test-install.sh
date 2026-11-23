#!/usr/bin/env bash
set -eu
echo "K INSTALLER PREFLIGHT"
command -v python3 >/dev/null 2>&1 && echo "Python 3: PASS" || echo "Python 3: MISSING"
command -v git >/dev/null 2>&1 && echo "Git: PASS" || echo "Git: MISSING"
for f in interpreter/k_1_0_dev.py interpreter/k_0_9_dev.py interpreter/k.py; do
  if [ -f "$f" ]; then echo "Interpreter candidate: $f"; fi
done
test -f installers/install.sh && echo "Shell installer: PASS"
test -f installers/install.ps1 && echo "Windows installer: PASS"
test -f installers/README.md && echo "Installer docs: PASS"
echo "Preflight complete. This does not replace real installation tests."
