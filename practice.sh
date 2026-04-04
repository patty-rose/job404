#!/bin/bash
# Build if image doesn't exist, then run interactive
set -e

IMAGE="interview-practice"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$(docker images -q $IMAGE 2>/dev/null)" == "" ]]; then
  echo "Building image..."
  docker build -t $IMAGE "$SCRIPT_DIR"
fi

docker run --rm -it \
  -v "$SCRIPT_DIR/data:/app/data" \
  $IMAGE
