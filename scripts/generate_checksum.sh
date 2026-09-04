#!/bin/bash
# Module: generate_checksum.sh
# Description: Generate checksums for image archives
# Usage: ./scripts/generate_checksum.sh [output_dir]

set -euo pipefail

OUTPUT_DIR="${1:-.}"

echo "=== Generating checksums ==="

find "${OUTPUT_DIR}" -name "*.tar" -o -name "*.tar.gz" | while read -r file; do
  sha256sum "${file}" >> "${OUTPUT_DIR}/sha256sum.txt"
done

echo "Checksums saved to: ${OUTPUT_DIR}/sha256sum.txt"
cat "${OUTPUT_DIR}/sha256sum.txt"
