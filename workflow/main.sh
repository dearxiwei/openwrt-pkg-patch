#!/bin/bash
# Main orchestration script for pulling Docker images
# Usage: ./workflow/main.sh [czkawka-cn|krokiet-cn|all] [tag]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
IMAGES="${1:-all}"
TAG="${2:-latest}"

echo "=== OpenWrt Package Patch - Docker Image Puller ==="
echo "Images: ${IMAGES}"
echo "Tag: ${TAG}"
echo "Script Dir: ${SCRIPT_DIR}"
echo ""

case "${IMAGES}" in
  all)
    ./scripts/pull_image.sh "jlesage/czkawka" "${TAG}" "images/czkawka"
    ./scripts/pull_image.sh "jlesage/krokiet" "${TAG}" "images/krokiet"
    ;;
  czkawka-cn|czkawka)
    ./scripts/pull_image.sh "jlesage/czkawka" "${TAG}" "images/czkawka"
    ;;
  krokiet-cn|krokiet)
    ./scripts/pull_image.sh "jlesage/krokiet" "${TAG}" "images/krokiet"
    ;;
  *)
    echo "Unknown image: ${IMAGES}"
    echo "Available: all, czkawka-cn, krokiet-cn"
    exit 1
    ;;
esac

echo ""
echo "=== Pull complete ==="
ls -la images/
