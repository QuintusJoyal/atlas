#!/usr/bin/env python3
"""Generate lite/ from tier-marked blocks in the full bundle.

Atlas's lite mode (5 core agents for 3B-8B models) used to be a hand-maintained
parallel copy of agents/, skills/, rules/, and workflows/. That drifted from the
full bundle (see CHANGELOG 0.15.2 / 0.16.0). Instead, each source file that has a
lite mode embeds it verbatim inside a marked block:

    <!-- lite:start -->
    ...exact content for the generated lite/ file, including its own frontmatter...
    <!-- lite:end -->

This script extracts that block and writes it to the mapped lite/ path, with a
generated-file banner inserted (after frontmatter, if any, so `---` stays at byte
offset 0 for strict parsers). Edit the block in the source file; never hand-edit
a path under lite/ directly.

Every file under lite/ (5 agents, 5 playbooks, 5 rules, 5 workflows = 20) is
generated from a source marker block and covered by --check. --check also
enforces the lite system-prompt token budget: it sums the char/4 estimate of the
rules, agent, and playbook that make up each role's system prompt (excluding YAML
frontmatter and the generated-file banner, which are not prompt content) and
fails when a specialist exceeds ~1,300 tokens or the lead exceeds ~1,700.

Usage:
    python3 scripts/build-lite.py          # regenerate lite/ from source
    python3 scripts/build-lite.py --check  # verify lite/ matches source; exit 1 on drift
"""

import math
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
    ("rules/atlas-lead-orchestration.md", "lite/rules/atlas-lead-orchestration.md"),
    ("rules/engineering-standards.md", "lite/rules/engineering-standards.md"),
    ("rules/handoff-protocol.md", "lite/rules/handoff-protocol.md"),
    ("rules/team-charter.md", "lite/rules/team-charter.md"),
    ("workflows/bugfix.md", "lite/workflows/bugfix.md"),
    ("workflows/discovery.md", "lite/workflows/discovery.md"),
    ("workflows/feature.md", "lite/workflows/feature.md"),
    ("workflows/infra-change.md", "lite/workflows/infra-change.md"),
    ("workflows/self-assessment.md", "lite/workflows/self-assessment.md"),
]

# Lite system-prompt token budget. The estimate is chars/4 after stripping YAML
# frontmatter and the generated-file banner (neither is model-facing prompt text).
TOKEN_DIVISOR = 4
SPECIALIST_BUDGET = 1300
LEAD_BUDGET = 1700

MARKER_RE = re.compile(r"<!-- lite:start -->\s*\n(.*?)\n\s*<!-- lite:end -->", re.DOTALL)
FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)
BANNER_RE = re.compile(
    r"<!-- GENERATED FILE\..*?Regenerate with: python3 scripts/build-lite\.py -->", re.DOTALL
)
AGENT_NAME_RE = re.compile(r"^name:\s*(\S+)", re.M)
AGENT_RULES_RE = re.compile(r"^rules:\s*\n((?:[ \t]+-[ \t]+\S+[ \t]*\n)+)", re.M)

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


def detect_newline(path: Path) -> str:
    """Preserve the line-ending convention already used by an existing output file."""
    if path.exists() and b"\r\n" in path.read_bytes():
        return "\r\n"
    return "\n"


def estimate_tokens(path: Path) -> int:
    """chars/4 token estimate of a file's model-facing text (no frontmatter/banner)."""
    text = path.read_text(encoding="utf-8")
    text = FRONTMATTER_RE.sub("", text, count=1)
    text = BANNER_RE.sub("", text)
    return math.ceil(len(text.strip()) / TOKEN_DIVISOR)


def check_token_budget() -> list:
    """Return a list of over-budget roles; print per-file and per-role estimates."""
    print("\nLite system-prompt token budget (chars/%d):" % TOKEN_DIVISOR)
    issues = []
    for agent_path in sorted((ROOT / "lite/agents").glob("*.md")):
        text = agent_path.read_text(encoding="utf-8")
        name_match = AGENT_NAME_RE.search(text)
        rules_match = AGENT_RULES_RE.search(text)
        if not name_match or not rules_match:
            issues.append(f"{agent_path.name}: cannot read name/rules from frontmatter")
            continue
        name = name_match.group(1)
        rules = re.findall(r"-[ \t]+(\S+)", rules_match.group(1))
        budget = LEAD_BUDGET if name == "atlas-lead" else SPECIALIST_BUDGET
        kind = "lead" if name == "atlas-lead" else "specialist"

        parts = [(ROOT / "lite/rules" / f"{r}.md") for r in rules]
        parts.append(ROOT / "lite/skills" / f"{name}-playbook" / "SKILL.md")
        parts.append(agent_path)

        total = 0
        for part in parts:
            if not part.exists():
                issues.append(f"{name}: missing {part.relative_to(ROOT)}")
                continue
            tokens = estimate_tokens(part)
            total += tokens
            print(f"      {tokens:5d}  {part.relative_to(ROOT)}")
        status = "OVER" if total > budget else "ok"
        print(f"  {name} ({kind}): {total}/{budget} tokens [{status}]")
        if total > budget:
            issues.append(f"{name}: {total} tokens exceeds {kind} budget of {budget}")
    return issues


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
            newline = detect_newline(out_path)
            out_path.write_bytes(generated.replace("\n", newline).encode("utf-8"))
            print(f"generated: {out_rel}")

    if missing_markers:
        print("\nSources with no <!-- lite:start --> block (skipped):")
        for m in missing_markers:
            print(f"  - {m}")

    budget_issues = check_token_budget()

    if check_only:
        if drift:
            print(f"\nDRIFT: {len(drift)} lite/ file(s) out of date with source:")
            for d in drift:
                print(f"  - {d}")
        if budget_issues:
            print(f"\nTOKEN BUDGET: {len(budget_issues)} lite/ role(s) over budget:")
            for issue in budget_issues:
                print(f"  - {issue}")
        if drift or budget_issues:
            return 1
        print("\nOK: lite/ matches source markers; all roles within token budget.")
        return 0

    if budget_issues:
        print("\nWARNING: lite/ roles over token budget:")
        for issue in budget_issues:
            print(f"  - {issue}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
