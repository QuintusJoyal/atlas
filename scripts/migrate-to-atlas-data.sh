#!/usr/bin/env bash
# Migrate repo .atlas/ to central ATLAS_DATA_DIR.
# Default data dir: $HOME/.cursor/atlas-data (override with ATLAS_DATA_DIR).
# Dry-run by default; --apply to execute; --remove-legacy with --apply.

set -euo pipefail

APPLY=0
REMOVE_LEGACY=0
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DATA_DIR="${ATLAS_DATA_DIR:-$HOME/.cursor/atlas-data}"
WORKSPACE="${ATLAS_WORKSPACE:-$REPO_ROOT}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply) APPLY=1; shift ;;
    --remove-legacy) REMOVE_LEGACY=1; shift ;;
    --repo) REPO_ROOT="$2"; shift 2 ;;
    --data-dir) DATA_DIR="$2"; shift 2 ;;
    --workspace) WORKSPACE="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

LEGACY_ATLAS="$REPO_ROOT/.atlas"
TARGET_RUNS="$DATA_DIR/runs"
PREFIX=$([ "$APPLY" -eq 1 ] && echo '[APPLY]' || echo '[DRY-RUN]')

log() { echo "$PREFIX $*"; }

patch_meta() {
  local meta_path="$1" run_id="$2"
  [[ -f "$meta_path" ]] || return 0
  python3 - "$meta_path" "$run_id" "$WORKSPACE" "$APPLY" <<'PY'
import json, sys
path, run_id, workspace, apply = sys.argv[1:5]
with open(path, encoding="utf-8") as f:
    meta = json.load(f)
changed = False
if not meta.get("workspace"):
    meta["workspace"] = workspace
    changed = True
if not meta.get("slug"):
    meta["slug"] = run_id.split("-", 3)[-1] if run_id.count("-") >= 3 else run_id
    changed = True
if changed:
    print(f"patch meta.json for {run_id}", file=sys.stderr)
    if apply == "1":
        with open(path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
            f.write("\n")
PY
}

echo "Atlas migration to central data home"
echo "  Repo:      $REPO_ROOT"
echo "  Data dir:  $DATA_DIR"
echo "  Workspace: $WORKSPACE"
echo

[[ -d "$LEGACY_ATLAS" ]] || { echo "No legacy .atlas at $LEGACY_ATLAS"; exit 0; }

log "Ensure $TARGET_RUNS exists"
[[ "$APPLY" -eq 1 ]] && mkdir -p "$TARGET_RUNS"

if [[ -d "$LEGACY_ATLAS/runs" ]]; then
  for src in "$LEGACY_ATLAS/runs"/*; do
    [[ -d "$src" ]] || continue
    id="$(basename "$src")"
    dst="$TARGET_RUNS/$id"
    log "Copy run $id -> $dst"
    if [[ "$APPLY" -eq 1 ]]; then
      mkdir -p "$dst"
      cp -a "$src/." "$dst/"
      patch_meta "$dst/meta.json" "$id"
    else
      patch_meta "$src/meta.json" "$id"
    fi
  done
fi

for file in work-items.json config.json runner-jobs.json activity.jsonl; do
  src="$LEGACY_ATLAS/$file"
  dst="$DATA_DIR/$file"
  if [[ -f "$src" ]]; then
    log "Copy global $file -> $dst"
    [[ "$APPLY" -eq 1 ]] && mkdir -p "$DATA_DIR" && cp -a "$src" "$dst"
  fi
done

if [[ "$REMOVE_LEGACY" -eq 1 ]]; then
  if [[ "$APPLY" -eq 1 ]]; then
    log "Remove legacy $LEGACY_ATLAS"
    rm -rf "$LEGACY_ATLAS"
  else
    echo "Warning: --remove-legacy requires --apply" >&2
  fi
fi

if [[ "$APPLY" -eq 0 ]]; then
  echo
  echo "Dry-run complete. Re-run with --apply. Add --remove-legacy after verifying Control Center."
fi
