#!/usr/bin/env bash
set -e
echo "=== skopeo installer ==="
if command -v skopeo &>/dev/null; then echo "skopeo already: $(skopeo --version)"; exit 0; fi
case "$(uname -s)" in
  Linux)
    if command -v apt-get &>/dev/null; then sudo apt-get update && sudo apt-get install -y skopeo
    elif command -v yum &>/dev/null; then sudo yum install -y skopeo
    elif command -v dnf &>/dev/null; then sudo dnf install -y skopeo
    elif command -v apk &>/dev/null; then sudo apk add skopeo
    else echo "ERROR: no package manager"; exit 1; fi ;;
  Darwin) brew install skopeo ;;
  *) echo "ERROR: unsupported OS"; exit 1 ;;
esac
echo "Done: $(skopeo --version)"
