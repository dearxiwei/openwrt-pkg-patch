#!/bin/bash
# Module: pull_image.sh
# Description: Use skopeo to pull a Docker image without Docker daemon
# Usage: ./scripts/pull_image.sh <source> <tag> <output_dir>

set -euo pipefail

SOURCE_REGISTRY="${DOCKER_SOURCE_REGISTRY:-docker.io}"
IMAGE_NAME="${1:?Usage: pull_image.sh <image_name> <tag> <output_dir>}"
TAG="${2:-latest}"
OUTPUT_DIR="${3:-images/${IMAGE_NAME}}"

FULL_SOURCE="${SOURCE_REGISTRY}/${IMAGE_NAME}"
FULL_DEST="dir://${OUTPUT_DIR}"

echo "=== Pulling ${FULL_SOURCE}:${TAG} ==="
echo "Source: ${FULL_SOURCE}:${TAG}"
echo "Output: ${OUTPUT_DIR}"

mkdir -p "${OUTPUT_DIR}"

skopeo copy \
  --src docker://${FULL_SOURCE}:${TAG} \
  --dest ${FULL_DEST} \
  docker://${FULL_SOURCE}:${TAG}

echo "=== Done ==="
echo "Image saved to: ${OUTPUT_DIR}"
ls -la "${OUTPUT_DIR}"
