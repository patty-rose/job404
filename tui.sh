#!/bin/bash
# Run the conversational Claude TUI.
# Your ANTHROPIC_API_KEY is passed in from the host environment.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Load .env if present
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a
  source "$SCRIPT_DIR/.env"
  set +a
fi

if [[ -z "$ANTHROPIC_API_KEY" ]]; then
  echo "Error: ANTHROPIC_API_KEY is not set."
  echo "  Add it to .env or export it before running."
  exit 1
fi

IMAGE="interview-practice"

if [[ "$(docker images -q $IMAGE 2>/dev/null)" == "" ]]; then
  echo "Building image..."
  docker build -t $IMAGE "$SCRIPT_DIR"
fi

docker run --rm -it \
  -e ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY" \
  -e TERM="${TERM:-xterm-256color}" \
  -v "$SCRIPT_DIR/data:/app/data" \
  $IMAGE python tui.py
