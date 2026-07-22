#!/usr/bin/env python3
"""Generate lite/ from tier-marked blocks in the full bundle.

Atlas's lite mode (5 core agents for 3B-8B models) used to be a hand-maintained
parallel copy of agents/, skills/, and rules/atlas-core.md. That drifted from the
full bundle (see CHANGELOG 0.15.2 / 0.16.0). Instead, each source file that has a
lite mode embeds it verbatim inside a marked block:

    <!-- lite:start -->
    ...exact content for the generated lite/ file, including its own frontmatter...
    <!-- lite:end -->

This script extracts that block and writes it to the mapped lite/ path, with a
generated-file banner inserted (after frontmatter, if any, so `---` stays at byte
offset 0 for strict parsers). Edit the block in the source file; never hand-edit
a path under lite/agents/, lite/skills/, or lite/rules/atlas-core.md directly.

Usage:
    python3 scripts/build-lite.py          # regenerate lite/ from source
    python3 scripts/build-lite.py --check  # verify lite/ matches source; exit 1 on drift
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SOURCES = [
    ("agents/atlas-lead.md", "lite/agents/atlas-lead.md"),
    ("agents/atlas-dev.md", "lite/agents/atlas-dev.md"),
    ("agents/atlas-qa.md", "lite/agents/atlas-qa.md"),
    ("agents/atlas-architect.md", "lite/agents/atlas-architect.md"),
    ("agents/atlas-security.md", "lite/agents/atlas-security.md"),
    ("skills/atlas-lead-playbook/SKILL.md", "lite/skills/atlas-lead-playbook/SKILL.md"),
    ("skills/atlas-dev-playbook/SKILL.md", "lite/skills/atlas-dev-playbook/SKILL.md"),
    ("skills/atlas-qa-playbook/SKILL.md", "lite/skills/atlas-qa-playbook/SKILL.md"),
    ("skills/atlas-architect-playbook/SKILL.md", "lite/skills/atlas-architect-playbook/SKILL.md"),
    ("skills/atlas-security-playbook/SKILL.md", "lite/skills/atlas-security-playbook/SKILL.md"),
    ("rules/atlas-core.md", "lite/rules/atlas-core.md"),
]

MARKER_RE = re.compile(r"<!-- lite:start -->\s*\n(.*?)\n\s*<!-- lite:end -->", re.DOTALL)
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)

BANNER = (
    "<!-- GENERATED FILE. Do not edit directly.\n"
    "     Source: {src} (the <!-- lite:start --> block).\n"
    "     Regenerate with: python3 scripts/build-lite.py -->\n\n"
)


def extract(src_path: Path) -> str:
    text = src_path.read_text(encoding="utf-8")
    match = MARKER_RE.search(text)
    if not match:
        return None
    return match.group(1).strip() + "\n"


def insert_banner(body: str, banner: str) -> str:
    # Frontmatter must stay at byte offset 0 for strict parsers, so the banner goes after it, not before.
    fm_match = FRONTMATTER_RE.match(body)
    if fm_match:
        end = fm_match.end()
        return body[:end] + "\n" + banner + body[end:]
    return banner + body


def main():
    check_only = "--check" in sys.argv
    drift = []
    missing_markers = []

    for src_rel, out_rel in SOURCES:
        src_path = ROOT / src_rel
        out_path = ROOT / out_rel

        body = extract(src_path)
        if body is None:
            missing_markers.append(src_rel)
            continue

        generated = insert_banner(body, BANNER.format(src=src_rel))

        if check_only:
            existing = out_path.read_text(encoding="utf-8") if out_path.exists() else None
            if existing != generated:
                drift.append(out_rel)
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(generated, encoding="utf-8")
            print(f"generated: {out_rel}")

    if missing_markers:
        print("\nSources with no <!-- lite:start --> block (skipped):")
        for m in missing_markers:
            print(f"  - {m}")

    if check_only:
        if drift:
            print(f"\nDRIFT: {len(drift)} lite/ file(s) out of date with source:")
            for d in drift:
                print(f"  - {d}")
            return 1
        print("\nOK: lite/ matches source markers.")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
