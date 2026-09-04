#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
export PYTHONPATH="$PROJECT_DIR/src"
OUTPUT_DIR="${1:-$PROJECT_DIR/packages}"
mkdir -p "$OUTPUT_DIR"
echo "=== 离线镜像拉取 (IPv4 only) ==="
echo "输出目录: $OUTPUT_DIR"
for img in "jlesage/czkawka:latest" "jlesage/krokiet:latest"; do
    name="${img%%:*}"; out_file="$OUTPUT_DIR/${name//-cn/}.tar.gz"
    echo "--- $img ---"
    if $PROJECT_DIR/scripts/pull_images.py --source "$img" -o "$OUTPUT_DIR"; then echo "  OK"; else echo "  FAILED"; fi
done
echo ""
echo "=== 完成 ==="
ls -lh "$OUTPUT_DIR"/*.tar.gz 2>/dev/null || echo "(无输出)"
