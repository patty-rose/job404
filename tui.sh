#!/bin/bash
# Run the conversational Claude TUI.
# Requires: .venv/bin/pip install textual  (and the claude CLI in your PATH)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/.venv"

if [ ! -d "$VENV" ]; then
  echo "Creating venv..."
  python3 -m venv "$VENV"
fi

if ! "$VENV/bin/python" -c "import textual" 2>/dev/null; then
  echo "Installing textual..."
  "$VENV/bin/pip" install textual
fi

"$VENV/bin/python" "$SCRIPT_DIR/tui.py"
