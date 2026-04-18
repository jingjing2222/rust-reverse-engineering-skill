#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <head-sha> <output-dir>" >&2
  exit 1
fi

HEAD_SHA="$1"
OUT_DIR="$2"

SHORT_SHA="${HEAD_SHA:0:7}"
PACKAGE_ROOT="rust-reverse-engineering-skill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
STAGE_DIR="$(mktemp -d)"

cleanup() {
  rm -rf "$STAGE_DIR"
}
trap cleanup EXIT

mkdir -p "$STAGE_DIR/$PACKAGE_ROOT" "$OUT_DIR"

rsync -a \
  --exclude='.git/' \
  --exclude='.github/' \
  --exclude='.claude/settings.local.json' \
  "$REPO_ROOT/" "$STAGE_DIR/$PACKAGE_ROOT/"

tar -C "$STAGE_DIR" -czf "$OUT_DIR/${PACKAGE_ROOT}-${SHORT_SHA}.tar.gz" "$PACKAGE_ROOT"
(
  cd "$STAGE_DIR"
  zip -qr "$OUT_DIR/${PACKAGE_ROOT}-${SHORT_SHA}.zip" "$PACKAGE_ROOT"
)

(
  cd "$OUT_DIR"
  sha256sum "${PACKAGE_ROOT}-${SHORT_SHA}.tar.gz" "${PACKAGE_ROOT}-${SHORT_SHA}.zip" > SHA256SUMS.txt
)
