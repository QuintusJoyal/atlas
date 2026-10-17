#!/usr/bin/env python3
"""Lint agent-facing interfaces against the agent-interface contract.

Usage:
    python3 scripts/lint-interfaces.py

Checks every skills/<name>/SKILL.md against
knowledge/process/agent-interface-contract.md:

1. Frontmatter present, fully parseable, no unknown fields
2. Schema completeness: name, description, type, appliesTo, tags present;
   name kebab-case and equals the directory name; type in {playbook, skill}
3. Description quality: 20-300 chars, ends with a period,
   no banned filler words; playbook descriptions name their bound agent
4. Body contract: Route and Scope sections (Scope states a NOT boundary);
   playbooks add Delegation Examples; declared inputs/outputs are
   documented in the body
5. Reference consistency: every k/<stem> pointer resolves to a file under
   knowledge/

Exit code: 0 = clean, 1 = issues found
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
KNOWLEDGE_DIR = ROOT / "knowledge"

ALLOWED_KEYS = {
    "name", "description", "type", "version", "appliesTo", "tags",
    "capabilities", "permissions", "inputs", "outputs", "requires",
}
LIST_KEYS = ("capabilities", "permissions", "inputs", "outputs", "requires", "appliesTo", "tags")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
VALID_TYPES = {"playbook", "skill"}
BANNED_FILLER = ("various", "etc.", " and more", "stuff", "things", "as needed")
K_REF_RE = re.compile(r"\bk/([a-z0-9-]+)\b")
DESC_MIN, DESC_MAX = 20, 300


def parse_frontmatter(path):
    """Minimal frontmatter parser: scalars and inline lists. Returns dict or None."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    data = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return data
        if ":" not in line or line.startswith((" ", "\t", "#")):
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key or not value:
            continue
        if value.startswith("[") and value.endswith("]"):
            items = [v.strip().strip("'\"") for v in value[1:-1].split(",")]
            data[key] = [v for v in items if v]
        else:
            data[key] = value.strip("'\"")
    return None


def knowledge_stems():
    return {p.stem for p in KNOWLEDGE_DIR.rglob("*.md")}


def body_of(text):
    """Text after the closing frontmatter delimiter."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return text
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "---":
            return "\n".join(lines[i + 1:])
    return ""


def main():
    print("Atlas Interface Contract Linter")
    print("=" * 50)
    issues = 0
    stems = knowledge_stems()

    dirs = sorted(d for d in SKILLS_DIR.iterdir() if d.is_dir() and not d.name.startswith("."))
    print(f"\nLinting {len(dirs)} skill interfaces...")

    for entry in dirs:
        skill_file = entry / "SKILL.md"
        tag = f"skills/{entry.name}"

        if not skill_file.is_file():
            print(f"   FOUND {tag}: missing SKILL.md")
            issues += 1
            continue

        text = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(skill_file)
        if fm is None:
            print(f"   FOUND {tag}: missing or unparseable frontmatter")
            issues += 1
            continue

        # 1. Unknown fields
        for key in fm:
            if key not in ALLOWED_KEYS:
                print(f"   FOUND {tag}: unknown frontmatter field '{key}'")
                issues += 1

        # 2. Schema completeness
        for key in ("name", "description", "type", "appliesTo", "tags"):
            if key not in fm or not fm[key]:
                print(f"   FOUND {tag}: missing required field '{key}'")
                issues += 1

        for key in LIST_KEYS:
            if key in fm and not isinstance(fm[key], list):
                print(f"   FOUND {tag}: '{key}' must be a list")
                issues += 1

        name = fm.get("name", "")
        if name and not KEBAB_RE.match(name):
            print(f"   FOUND {tag}: name '{name}' is not kebab-case")
            issues += 1
        if name and name != entry.name:
            print(f"   FOUND {tag}: name '{name}' != directory name")
            issues += 1

        skill_type = fm.get("type", "")
        if skill_type and skill_type not in VALID_TYPES:
            print(f"   FOUND {tag}: type '{skill_type}' not in {sorted(VALID_TYPES)}")
            issues += 1

        for key in ("capabilities", "permissions", "inputs", "outputs", "requires"):
            if key in fm and isinstance(fm[key], list):
                for item in fm[key]:
                    if not KEBAB_RE.match(item.split("@")[0]):
                        print(f"   FOUND {tag}: {key} entry '{item}' is not kebab-case")
                        issues += 1

        # 3. Description quality
        desc = fm.get("description", "")
        if desc:
            if not (DESC_MIN <= len(desc) <= DESC_MAX):
                print(f"   FOUND {tag}: description length {len(desc)} outside {DESC_MIN}-{DESC_MAX}")
                issues += 1
            if not desc.endswith("."):
                print(f"   FOUND {tag}: description must end with a period")
                issues += 1
            lowered = desc.lower()
            for word in BANNED_FILLER:
                if word in lowered:
                    print(f"   FOUND {tag}: description contains banned filler '{word.strip()}'")
                    issues += 1
            if skill_type == "playbook":
                applies = fm.get("appliesTo") if isinstance(fm.get("appliesTo"), list) else []
                if applies and not any(agent in desc for agent in applies):
                    print(f"   FOUND {tag}: playbook description does not name its bound agent "
                          f"({', '.join(applies)})")
                    issues += 1

        # 4. Body contract
        body = body_of(text)
        headings = set(re.findall(r"^## (.+)$", body, re.MULTILINE))
        for required in ("Route", "Scope"):
            if required not in headings:
                print(f"   FOUND {tag}: body missing '## {required}' section")
                issues += 1
        if skill_type == "playbook" and "Delegation Examples" not in headings:
            print(f"   FOUND {tag}: playbook body missing '## Delegation Examples' section")
            issues += 1
        if "Scope" in headings:
            # Scope sections must state a boundary with NOT
            scope_match = re.search(r"^## Scope\n(.*?)(?=^## |\Z)", body, re.MULTILINE | re.DOTALL)
            if scope_match and "NOT" not in scope_match.group(1):
                print(f"   FOUND {tag}: Scope section states no NOT boundary")
                issues += 1

        # Declared inputs/outputs must be documented in the body
        for key in ("inputs", "outputs"):
            for item in fm.get(key) or []:
                if f"`{item}`" not in body:
                    print(f"   FOUND {tag}: declared {key} '{item}' not documented in body (use `{item}`)")
                    issues += 1

        # 5. Reference consistency
        for stem in sorted(set(K_REF_RE.findall(body))):
            if stem not in stems:
                print(f"   FOUND {tag}: k/{stem} does not resolve to any knowledge/ file")
                issues += 1

    print("\n" + "=" * 50)
    if issues == 0:
        print(f"RESULT: CLEAN - {len(dirs)} interfaces satisfy the contract")
        return 0
    print(f"RESULT: {issues} ISSUES FOUND")
    return 1


if __name__ == "__main__":
    sys.exit(main())
