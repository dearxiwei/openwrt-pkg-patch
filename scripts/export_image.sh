#!/bin/bash
# Module: export_image.sh
# Description: Export skopeo pulled image as tar archive for offline installation
# Usage: ./scripts/export_image.sh <image_name> [tag]

set -euo pipefail

IMAGE_NAME="${1:?Usage: export_image.sh <image_name> [tag]}"
TAG="${2:-latest}"
INPUT_DIR="images/${IMAGE_NAME}"
OUTPUT_TAR="${TAG}.tar"

if [ ! -d "${INPUT_DIR}" ]; then
  echo "Error: Image directory not found: ${INPUT_DIR}"
  echo "Please pull the image first: ./scripts/pull_image.sh ${IMAGE_NAME} ${TAG}"
  exit 1
fi

echo "=== Exporting ${IMAGE_NAME}:${TAG} to ${OUTPUT_TAR} ==="

# Convert dir to oci and then to tar
skopeo copy \
  --src dir://${INPUT_DIR} \
  --dest oci://${INPUT_DIR}.oci \
  "docker://${IMAGE_NAME}:${TAG}"

docker save "${IMAGE_NAME}:${TAG}" > "${OUTPUT_TAR}" 2>/dev/null || {
  # Fallback: create tar from OCI
  tar -czf "${OUTPUT_TAR}" -C "${INPUT_DIR}.oci" .
  echo "Fallback: Created tar from OCI format"
}

echo "=== Done ==="
echo "Archive saved: ${OUTPUT_TAR}"
ls -lh "${OUTPUT_TAR}"
