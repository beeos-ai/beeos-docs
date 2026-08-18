#!/usr/bin/env bash
# ============================================================================
# beeos-docs OpenAPI spec sync helper
#
# Copies authoritative specs from the openagent meta repo's
# backend/openapi/*.yaml into beeos-docs/openapi/ with an anti-footgun
# banner prepended to each file.
#
# Usage (run from beeos-docs/ root):
#   npm run sync-spec
#   # or directly:
#   ./scripts/sync-spec.sh
#
# Inputs:
#   - $OPENAGENT_ROOT (optional, default ../) — root of the openagent
#     meta repo. The repo path matters because beeos-docs is a submodule
#     of openagent; locally, that submodule lives at openagent/beeos-docs.
#
# Outputs:
#   - openapi/beeos-platform-v1.yaml         (overwritten)
#   - openapi/beeos-agent-integration-v1.yaml (overwritten)
#   - openapi/runtime-error-codes-v4.generated.json (overwritten)
#
# Does NOT touch openapi/beeos-platform-v1-zh.yaml. That file is a
# historical localized snapshot and is not used by the API Reference.
# Both language tabs render the authoritative synced platform spec.
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OPENAGENT_ROOT="${OPENAGENT_ROOT:-$(cd "$DOCS_ROOT/.." && pwd)}"
SRC="$OPENAGENT_ROOT/backend/openapi"
DST="$DOCS_ROOT/openapi"

if [[ ! -d "$SRC" ]]; then
  echo "ERROR: cannot find backend/openapi at $SRC"
  echo "  Set OPENAGENT_ROOT env var to point at the openagent repo root."
  echo "  Hint: backend/ is a git submodule. If empty, run:"
  echo "    git submodule update --init --recursive"
  exit 1
fi

sync_one() {
  local file="$1"
  local src_path="$SRC/$file"
  local dst_path="$DST/$file"

  if [[ ! -f "$src_path" ]]; then
    echo "ERROR: source spec not found: $src_path"
    exit 1
  fi

  local timestamp
  timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"

  local banner
  banner="# ============================================================================
# AUTO-SYNCED FROM backend/openapi/${file}
# DO NOT EDIT HERE — edit the source in the openagent repo and run
#   cd beeos-docs && npm run sync-spec
# Last synced: ${timestamp}
# Source SHA: $(cd "$OPENAGENT_ROOT/backend" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')
# ============================================================================"

  mkdir -p "$DST"
  { echo "$banner"; cat "$src_path"; } > "${dst_path}.tmp"
  mv "${dst_path}.tmp" "$dst_path"

  printf "  synced %-45s -> %s lines\n" "$file" "$(wc -l < "$dst_path" | tr -d ' ')"
}

sync_support_file() {
  local file="$1"
  local src_path="$SRC/$file"
  local dst_path="$DST/$file"

  if [[ ! -f "$src_path" ]]; then
    echo "ERROR: support file not found: $src_path"
    exit 1
  fi

  cp "$src_path" "$dst_path"
  printf "  synced %-45s -> %s lines\n" "$file" "$(wc -l < "$dst_path" | tr -d ' ')"
}

echo "==> Syncing OpenAPI specs from $SRC"
echo "    Destination: $DST"
echo ""
sync_one beeos-platform-v1.yaml
sync_one beeos-agent-integration-v1.yaml
sync_support_file runtime-error-codes-v4.generated.json
node "$SCRIPT_DIR/inline-openapi-refs.mjs" \
  "$DST/beeos-platform-v1.yaml" \
  "$DST/runtime-error-codes-v4.generated.json"
echo ""
echo "DONE."
echo ""
echo "Note: both language tabs use openapi/beeos-platform-v1.yaml."
echo "      openapi/beeos-platform-v1-zh.yaml is a historical snapshot"
echo "      and is intentionally not updated by this script."
