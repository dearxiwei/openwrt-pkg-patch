#!/bin/bash
# Module: import_image.sh
# Description: Import a Docker image tar archive (offline installation)
# Usage: ./scripts/import_image.sh <archive.tar> [image_name] [tag]

set -euo pipefail

ARCHIVE="${1:?Usage: import_image.sh <archive.tar> [image_name] [tag]}"
IMAGE_NAME="${2:-}"
TAG="${3:-latest}"

if [ ! -f "${ARCHIVE}" ]; then
  echo "Error: Archive not found: ${ARCHIVE}"
  exit 1
fi

echo "=== Importing ${ARCHIVE} ==="

if command -v docker &> /dev/null; then
  docker load -i "${ARCHIVE}"
  echo "Loaded with docker"
elif command -v podman &> /dev/null; then
  podman load -i "${ARCHIVE}"
  echo "Loaded with podman"
else
  echo "Warning: No Docker-compatible runtime found"
  echo "To use this archive, install Docker/Podman first:"
  echo "  apt-get install -y docker.io"
  echo "  then: docker load -i ${ARCHIVE}"
fi

echo "=== Done ==="
