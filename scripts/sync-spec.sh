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
#   - $BACKEND_ROOT (optional, default $OPENAGENT_ROOT/backend) — direct
#     path to the authoritative Backend checkout, used by cross-repo CI.
#   - $SYNC_PRESERVE_BANNER (optional) — preserve the existing sync time
#     and source SHA so drift checks compare contract content only.
#
# Outputs:
#   - openapi/beeos-platform-v1.yaml         (overwritten)
#   - openapi/beeos-agent-integration-v1.yaml (overwritten)
#   - openapi/runtime-error-codes-v4.generated.json (overwritten)
#
# Both language tabs render the same authoritative platform spec.
# ============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DOCS_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
OPENAGENT_ROOT="${OPENAGENT_ROOT:-$(cd "$DOCS_ROOT/.." && pwd)}"
BACKEND_ROOT="${BACKEND_ROOT:-$OPENAGENT_ROOT/backend}"
SRC="$BACKEND_ROOT/openapi"
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

  local timestamp source_sha
  timestamp="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  source_sha="$(cd "$BACKEND_ROOT" && git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
  if [[ "${SYNC_PRESERVE_BANNER:-0}" == "1" && -f "$dst_path" ]]; then
    timestamp="$(sed -n 's/^# Last synced: //p' "$dst_path" | head -n 1)"
    source_sha="$(sed -n 's/^# Source SHA: //p' "$dst_path" | head -n 1)"
    [[ -n "$timestamp" ]] || timestamp="unknown"
    [[ -n "$source_sha" ]] || source_sha="unknown"
  fi

  local banner
  banner="# ============================================================================
# AUTO-SYNCED FROM backend/openapi/${file}
# DO NOT EDIT HERE — edit the source in the openagent repo and run
#   cd beeos-docs && npm run sync-spec
# Last synced: ${timestamp}
# Source SHA: ${source_sha}
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
