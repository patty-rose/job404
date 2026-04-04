#!/bin/bash
# Run the conversational Claude TUI.
# Requires: pip install textual  (and the claude CLI in your PATH)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/tui.py"
