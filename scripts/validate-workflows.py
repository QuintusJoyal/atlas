#!/usr/bin/env python3
"""Validate Atlas workflow presets and their indexes.

Usage:
    python3 scripts/validate-workflows.py

Checks:
1. Every workflows/*.md frontmatter is well formed and uses the allowed schema
   (name, type, variants, conditions, state-machine).
2. Every gate a preset declares is fed by at least one phase, and no phase
   feeds an undeclared gate.
3. `skip:` entries name real phases that carry a matching Skip-if line.
4. Conditions are known names; injected phases are limited to the two phases
   defined in workflows/README.md.
5. Every role named in a preset exists under agents/.
6. workflows/README.md's preset, gate, and condition tables match the presets
   and manifest.json.

Exit code: 0 = clean, 1 = issues found
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS_DIR = ROOT / "workflows"
AGENTS_DIR = ROOT / "agents"
MANIFEST_PATH = ROOT / "manifest.json"
README = WORKFLOWS_DIR / "README.md"

CANONICAL_STATE_MACHINE = [
    "pending",
    "active",
    "gated",
    "completed",
    "failed",
    "paused",
    "aborted",
]
KNOWN_GATES = {"token-budget", "requirements", "design", "final", "scope", "research"}
# Gates that are part of kickoff rather than a phase transition.
KICKOFF_GATES = {"token-budget"}
KNOWN_CONDITIONS = {"regulated", "data-changes", "security-sensitive", "technical-deep-dive"}
INJECTABLE_PHASES = {"security-review", "compliance"}
ALLOWED_TYPES = {"pipeline", "fast-lane", "assessment"}
VARIANT_KEYS = {"description", "gates", "token-estimate", "kickoff", "auto-approve", "tracking"}

ROLE_RE = re.compile(r"atlas-[a-z0-9-]+")

# Lite mode content is emitted from <!-- lite:start --> blocks and must not be
# scanned as real preset phases (e.g. self-assessment's lite block has its own
# `## Phases` heading). Strip marker blocks before parsing.
LITE_BLOCK_RE = re.compile(r"\n?<!-- lite:start -->.*?<!-- lite:end -->\s*", re.DOTALL)


def parse_value(raw):
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [part.strip().strip("'\"") for part in inner.split(",")]
    value = value.strip("'\"")
    if value == "true":
        return True
    if value == "false":
        return False
    return value


def strip_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def tokenize(fm_lines):
    tokens = []
    for line in fm_lines:
        if not line.strip() or line.strip().startswith("#"):
            continue
        indent = len(line) - len(line.lstrip(" "))
        tokens.append((indent, line.strip()))
    return tokens


def parse_block(tokens, idx, indent):
    if idx >= len(tokens):
        return None, idx
    if tokens[idx][1].startswith("- "):
        return parse_list(tokens, idx, indent)
    return parse_map(tokens, idx, indent)


def parse_list(tokens, idx, indent):
    result = []
    while idx < len(tokens) and tokens[idx][0] == indent and tokens[idx][1].startswith("- "):
        content = tokens[idx][1][2:].strip()
        if ":" in content:
            key, _, value = content.partition(":")
            item = {}
            if value.strip():
                item[key.strip()] = parse_value(value)
                idx += 1
            else:
                idx += 1
                nested, idx = parse_block(tokens, idx, tokens[idx][0])
                item[key.strip()] = nested
            while idx < len(tokens) and tokens[idx][0] > indent and not tokens[idx][1].startswith("- "):
                k2, _, v2 = tokens[idx][1].partition(":")
                if v2.strip():
                    item[k2.strip()] = parse_value(v2)
                    idx += 1
                else:
                    idx += 1
                    nested, idx = parse_block(tokens, idx, tokens[idx][0])
                    item[k2.strip()] = nested
            result.append(item)
        else:
            result.append(parse_value(content))
            idx += 1
    return result, idx


def parse_map(tokens, idx, indent):
    result = {}
    while idx < len(tokens) and tokens[idx][0] == indent and not tokens[idx][1].startswith("- "):
        key, sep, value = tokens[idx][1].partition(":")
        if not sep:
            idx += 1
            continue
        key = key.strip()
        if value.strip():
            result[key] = parse_value(value)
            idx += 1
        else:
            idx += 1
            if idx < len(tokens) and tokens[idx][0] > indent:
                nested, idx = parse_block(tokens, idx, tokens[idx][0])
                result[key] = nested
            else:
                result[key] = None
    return result, idx


def parse_frontmatter(text):
    fm_lines = strip_frontmatter(text)
    if fm_lines is None:
        return None
    tokens = tokenize(fm_lines)
    if not tokens:
        return None
    parsed, _ = parse_block(tokens, 0, tokens[0][0])
    return parsed


def extract_phases(body):
    """Return {phase_name: {'gate': str|None, 'skip_small': bool, 'roles': set}}."""
    phases = {}
    in_phases = False
    current = None
    for line in body.splitlines():
        if line.startswith("## "):
            in_phases = line.strip() == "## Phases"
            current = None
            continue
        if not in_phases:
            continue
        if line.startswith("### "):
            current = line[4:].strip()
            phases[current] = {"gate": None, "skip_small": False, "roles": set()}
            continue
        if current is None:
            continue
        if "- **Gate:**" in line:
            raw = line.split("**Gate:**", 1)[1].strip()
            base = raw.split()[0] if raw else ""
            phases[current]["gate"] = None if base.lower() == "null" else base
        if "- **Skip-if:**" in line and "variant=small" in line:
            phases[current]["skip_small"] = True
        if "- **Roles:**" in line:
            phases[current]["roles"].update(ROLE_RE.findall(line))
    return phases


def table_first_column(text, heading):
    """Read the first column of the first markdown table after `## heading`."""
    values = []
    lines = text.splitlines()
    in_section = False
    in_table = False
    for line in lines:
        if line.startswith("## "):
            if in_section:
                break
            in_section = line.strip() == heading
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if stripped.startswith("|"):
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if not cells:
                continue
            first = cells[0]
            if set(first) <= set("-: "):
                continue
            if first.lower() in ("condition", "preset", "gate"):
                in_table = True
                continue
            if in_table:
                values.append(first)
        elif in_table:
            break
    return values


def rel(path):
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main():
    print("Atlas Workflow Validator")
    print("=" * 50)

    issues = []
    warnings = []

    agent_roles = {p.stem for p in AGENTS_DIR.glob("*.md")}

    presets = {}
    for path in sorted(WORKFLOWS_DIR.glob("*.md")):
        if path.name == "README.md":
            continue
        text = LITE_BLOCK_RE.sub("\n", path.read_text(encoding="utf-8"))
        data = parse_frontmatter(text)
        if data is None:
            issues.append(f"{rel(path)}: missing or unparseable YAML frontmatter")
            continue
        presets[path.stem] = (path, data, text)

    if not presets:
        print("   FOUND no workflow presets")
        issues.append("no workflow presets found under workflows/")

    print(f"\n1. Checking {len(presets)} preset frontmatter...")
    for name, (path, data, text) in presets.items():
        where = rel(path)

        if data.get("name") != name:
            issues.append(f"{where}: frontmatter name {data.get('name')!r} != filename {name!r}")
        if data.get("type") not in ALLOWED_TYPES:
            issues.append(f"{where}: type {data.get('type')!r} not in {sorted(ALLOWED_TYPES)}")
        for key in ("description", "triggers", "variants", "state-machine"):
            if data.get(key) in (None, [], {}):
                issues.append(f"{where}: missing required frontmatter key {key!r}")
        if data.get("state-machine") != CANONICAL_STATE_MACHINE:
            issues.append(f"{where}: state-machine does not match the canonical list")
        if "conditions" not in data:
            issues.append(f"{where}: missing required frontmatter key 'conditions' (use [])")

        variants = data.get("variants") or {}
        for variant in ("small", "full"):
            if variant not in variants:
                issues.append(f"{where}: missing {variant!r} variant")
                continue
            block = variants[variant] or {}
            missing = VARIANT_KEYS - set(block)
            if missing:
                issues.append(f"{where}: {variant} variant missing keys {sorted(missing)}")

        small = variants.get("small") or {}
        full = variants.get("full") or {}
        if small:
            if small.get("token-estimate") != "light":
                issues.append(f"{where}: small token-estimate should be 'light'")
            if small.get("kickoff") != "lightweight":
                issues.append(f"{where}: small kickoff should be 'lightweight'")
            if small.get("auto-approve") is not True:
                issues.append(f"{where}: small auto-approve should be true")
            if small.get("tracking") != "none":
                issues.append(f"{where}: small tracking should be 'none'")
            if small.get("gates") not in ([], ["final"]):
                issues.append(f"{where}: small gates should be [] or ['final'], got {small.get('gates')!r}")
        if full:
            if full.get("kickoff") != "standard":
                issues.append(f"{where}: full kickoff should be 'standard'")
            if full.get("auto-approve") is not False:
                issues.append(f"{where}: full auto-approve should be false")
            if full.get("tracking") != "full":
                issues.append(f"{where}: full tracking should be 'full'")

        declared = set((small.get("gates") or []) + (full.get("gates") or []))
        for gate in declared:
            if gate not in KNOWN_GATES:
                issues.append(f"{where}: undeclared gate name {gate!r}")

        phases = extract_phases(text)
        fed = {p["gate"] for p in phases.values() if p.get("gate")}

        for gate in declared:
            if gate in KICKOFF_GATES:
                continue
            if gate not in fed:
                issues.append(f"{where}: gate {gate!r} is declared but no phase feeds it")

        for phase, info in phases.items():
            if info.get("gate") and info["gate"] not in declared:
                issues.append(
                    f"{where}: phase {phase!r} feeds gate {info['gate']!r}, which is not declared in variants"
                )
            for role in info["roles"]:
                if role not in agent_roles:
                    issues.append(f"{where}: phase {phase!r} names unknown role {role!r}")

        skipped = (small.get("skip") or []) if small else []
        for phase in skipped:
            if phase not in phases:
                issues.append(f"{where}: small skip names {phase!r}, which is not a phase in this preset")
            elif not phases[phase]["skip_small"]:
                issues.append(f"{where}: small skip names {phase!r} but that phase has no 'Skip-if: variant=small'")

        if "## Phase 0: Kickoff" not in text:
            issues.append(f"{where}: missing '## Phase 0: Kickoff' section")
        else:
            if "**Standard:**" not in text or "**Lightweight:**" not in text:
                issues.append(f"{where}: kickoff section must describe both Standard and Lightweight paths")
            if "estimation huddle" not in text:
                issues.append(f"{where}: standard kickoff must include the estimation huddle")
            if "token-budget if heavy" not in text:
                issues.append(f"{where}: standard kickoff must mention the token-budget gate")

        conditions = data.get("conditions") or []
        for cond in conditions:
            cname = cond.get("if")
            if cname not in KNOWN_CONDITIONS:
                issues.append(f"{where}: unknown condition {cname!r}")
            for injected in cond.get("add") or []:
                if injected not in INJECTABLE_PHASES:
                    issues.append(
                        f"{where}: condition {cname!r} injects undefined phase {injected!r} "
                        f"(allowed: {sorted(INJECTABLE_PHASES)})"
                    )
            for role in cond.get("add-roles") or []:
                if role not in agent_roles:
                    issues.append(f"{where}: condition {cname!r} names unknown role {role!r}")

    print(f"\n2. Checking workflows/README.md indexes...")
    readme_text = README.read_text(encoding="utf-8")
    listed_presets = set(table_first_column(readme_text, "## Presets"))
    missing = sorted(set(presets) - listed_presets)
    extra = sorted(listed_presets - set(presets))
    if missing:
        issues.append(f"workflows/README.md: preset table is missing {missing}")
    if extra:
        issues.append(f"workflows/README.md: preset table lists unknown presets {extra}")

    listed_gates = set(table_first_column(readme_text, "## Gates"))
    if listed_gates != KNOWN_GATES:
        issues.append(
            f"workflows/README.md: gate table {sorted(listed_gates)} != {sorted(KNOWN_GATES)}"
        )

    listed_conditions = set(table_first_column(readme_text, "## Conditions"))
    preset_conditions = set()
    for _, data, _ in presets.values():
        for cond in data.get("conditions") or []:
            preset_conditions.add(cond.get("if"))
    if preset_conditions - listed_conditions:
        issues.append(
            f"workflows/README.md: conditions table is missing {sorted(preset_conditions - listed_conditions)}"
        )

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        issues.append(f"manifest.json: invalid JSON ({exc})")
        manifest = {}
    meta = manifest.get("workflowMeta", {})
    manifest_gates = set(meta.get("gates", {}))
    if manifest_gates != KNOWN_GATES:
        issues.append(f"manifest.json: workflowMeta.gates {sorted(manifest_gates)} != {sorted(KNOWN_GATES)}")
    manifest_conditions = set(meta.get("conditions", {}))
    if manifest_conditions - listed_conditions:
        issues.append(
            f"manifest.json: workflowMeta.conditions has undocumented {sorted(manifest_conditions - listed_conditions)}"
        )

    print("\n" + "=" * 50)
    if issues:
        print(f"RESULT: {len(issues)} ISSUES FOUND")
        for issue in issues:
            print(f"   - {issue}")
        return 1
    for warning in warnings:
        print(f"   warn: {warning}")
    print(f"RESULT: CLEAN - {len(presets)} presets valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
