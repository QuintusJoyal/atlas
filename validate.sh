#!/usr/bin/env bash
# Atlas self-validation (macOS/Linux).
# Checks:
#   - every agent has name, description, model in frontmatter
#   - agent name matches its filename and is atlas-prefixed
#   - model IDs are from the allowed set
#   - referenced <role>-playbook skills exist
#   - no em dashes or common AI tells in bundle text
# Exits non-zero on any failure.
set -uo pipefail

BUNDLE="$(cd "$(dirname "$0")" && pwd)"
ERRORS=0
err() { echo "  - $1"; ERRORS=$((ERRORS + 1)); }
ALLOWED="claude-opus-4-8-thinking-high composer-2.5 composer-2 inherit"

# 1. Agent frontmatter, name, model
for f in "$BUNDLE"/agents/*.md; do
  base="$(basename "$f" .md)"
  name="$(grep -m1 -E '^name:' "$f" | sed -E 's/^name:[[:space:]]*//')"
  if [ -z "$name" ]; then err "$base.md: missing name"; else
    [ "$name" != "$base" ] && err "$base.md: name '$name' does not match filename"
    case "$name" in atlas-*) ;; *) err "$base.md: name '$name' is not atlas-prefixed" ;; esac
  fi
  grep -qE '^description:[[:space:]]*\S' "$f" || err "$base.md: missing description"
  model="$(grep -m1 -E '^model:' "$f" | sed -E 's/^model:[[:space:]]*//')"
  if [ -z "$model" ]; then err "$base.md: missing model"; else
    echo "$ALLOWED" | grep -qw "$model" || err "$base.md: model '$model' not in allowed set"
  fi
done

# 2. Referenced playbooks exist
for f in "$BUNDLE"/agents/*.md; do
  for pb in $(grep -oE 'atlas-[a-z-]+-playbook' "$f" | sort -u); do
    [ -f "$BUNDLE/skills/$pb/SKILL.md" ] || err "$pb referenced but skills/$pb/SKILL.md not found"
  done
done

# 3. Em dashes and AI tells
TELLS=("as an AI" "delve" "tapestry" "in conclusion" "it is important to note" "it is worth noting")
while IFS= read -r f; do
  grep -q $'\xe2\x80\x94' "$f" && err "$(basename "$f"): contains an em dash"
  for t in "${TELLS[@]}"; do
    grep -qiF "$t" "$f" && err "$(basename "$f"): contains AI tell '$t'"
  done
done < <(find "$BUNDLE" -type f \( -name '*.md' -o -name '*.mdc' \) \
  -not -path '*/.git/*' -not -path '*/node_modules/*' -not -name 'writing-style.mdc')

if [ "$ERRORS" -gt 0 ]; then
  echo "Validation FAILED:"
  exit 1
fi
echo "Validation passed. Atlas looks consistent."
