#!/usr/bin/env bash
set -e
REPO="https://github.com/karthiklabs7/K-Programming.git"
DEST="$HOME/.k-programming"
BIN="$HOME/.local/bin"
if ! command -v python3 >/dev/null 2>&1; then
  if command -v pkg >/dev/null 2>&1; then
    pkg install python git -y
  elif command -v apt >/dev/null 2>&1; then
    sudo apt update && sudo apt install -y python3 git
  else
    echo "Install Python 3 and Git first."
    exit 1
  fi
fi
command -v git >/dev/null 2>&1 || {
  echo "Git is required. Install Git and rerun."
  exit 1
}
if [ -e "$DEST" ]; then
  echo "Installation folder already exists: $DEST"
  echo "No files changed. Move or back up that folder before retrying."
  exit 1
fi
git clone --depth 1 "$REPO" "$DEST"
mkdir -p "$BIN"
cat > "$BIN/k" <<'LAUNCHER'
#!/usr/bin/env bash
ROOT="$HOME/.k-programming"
cd "$ROOT" || exit 1
for f in interpreter/k_1_0_dev.py interpreter/k_0_9_dev.py interpreter/k.py; do
  if [ -f "$ROOT/$f" ]; then
    exec python3 "$ROOT/$f" "$@"
  fi
done
echo "K interpreter entry point not found."
exit 1
LAUNCHER
chmod +x "$BIN/k"
echo 'Installation files created.'
echo "Add $BIN to PATH if the k command is not found."
echo 'Test with: k examples/hello.k'
