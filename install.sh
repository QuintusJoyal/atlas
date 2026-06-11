#!/usr/bin/env bash
# Atlas installer (macOS/Linux).
# Usage:
#   ./install.sh            # install (default)
#   ./install.sh install
#   ./install.sh update     # re-sync, preserves your knowledge base edits
#   ./install.sh uninstall
#   ./install.sh install --unprefixed
set -euo pipefail

MODE="${1:-install}"
UNPREFIXED=false
if [ "${2:-}" = "--unprefixed" ] || [ "${1:-}" = "--unprefixed" ]; then UNPREFIXED=true; fi
if [ "$MODE" = "--unprefixed" ]; then MODE="install"; UNPREFIXED=true; fi

BUNDLE="$(cd "$(dirname "$0")" && pwd)"
CURSOR="$HOME/.cursor"
AGENTS="$CURSOR/agents"
SKILLS="$CURSOR/skills"
RULES="$CURSOR/rules"
KB="$CURSOR/atlas-knowledge"

install_agent_name() {
  local a="$1"
  if [ "$UNPREFIXED" = true ]; then echo "$a" | sed -E 's/^atlas-(.+)\.md$/\1.md/'; else echo "$a"; fi
}

install_skill_name() {
  local s="$1"
  if [ "$UNPREFIXED" = true ]; then echo "$s" | sed -E 's/^atlas-(.+)-playbook$/\1-playbook/'; else echo "$s"; fi
}

AGENT_FILES=$(ls "$BUNDLE/agents")
SKILL_DIRS=$(ls "$BUNDLE/skills")
RULE_FILES=$(ls "$BUNDLE/rules")
PRESERVE="lessons.md proposed.md ways-of-working.md usage-insights.md"

if [ "$MODE" = "uninstall" ]; then
  echo "Uninstalling Atlas (knowledge base is preserved)..."
  for a in $AGENT_FILES; do
    rm -f "$AGENTS/$a" "$AGENTS/$(install_agent_name "$a")"
  done
  for s in $SKILL_DIRS; do
    rm -rf "$SKILLS/$s" "$SKILLS/$(install_skill_name "$s")"
  done
  for r in $RULE_FILES; do rm -f "$RULES/$r"; done
  echo "Done. Left $KB in place."
  exit 0
fi

echo "Atlas $MODE -> $CURSOR${UNPREFIXED:+ (unprefixed)}"
mkdir -p "$AGENTS" "$SKILLS" "$RULES" "$KB"

for a in $AGENT_FILES; do cp -f "$BUNDLE/agents/$a" "$AGENTS/$(install_agent_name "$a")"; done
for s in $SKILL_DIRS; do
  dst="$SKILLS/$(install_skill_name "$s")"
  mkdir -p "$dst"
  cp -Rf "$BUNDLE/skills/$s/." "$dst/"
done
for r in $RULE_FILES; do cp -f "$BUNDLE/rules/$r" "$RULES/$r"; done

for f in "$BUNDLE"/knowledge/*; do
  name="$(basename "$f")"
  target="$KB/$name"
  preserved=false
  for p in $PRESERVE; do [ "$p" = "$name" ] && preserved=true; done
  if [ "$MODE" = "install" ] || [ ! -f "$target" ] || [ "$preserved" = false ]; then
    cp -f "$f" "$target"
  else
    echo "  preserved $name"
  fi
done

if [ "$UNPREFIXED" = true ]; then echo "Atlas $MODE complete. Open Cursor and try: /lead help"
else echo "Atlas $MODE complete. Open Cursor and try: /atlas-lead help"; fi
