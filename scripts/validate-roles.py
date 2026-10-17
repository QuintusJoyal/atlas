#!/usr/bin/env python3
"""Validate Atlas role definitions against the Agent Specialization Registry.

Usage:
    python3 scripts/validate-roles.py          # validate (exit 1 on issues)
    python3 scripts/validate-roles.py --json   # print the derived registry

The registry is derived from each agents/<role>.md frontmatter plus its
`## Role Boundaries` section; it is never hand-duplicated, so it cannot drift.
See knowledge/process/role-registry.md for the schema and the RBAC model.

Checks:
1. Every agents/*.md has well-formed frontmatter with the required role fields.
2. name matches the filename stem and the atlas-<slug> pattern.
3. tier is one of premium|standard|fast; capabilities is a non-empty list.
4. permissions has boolean read and write.
5. Specialist roles (every role except atlas-lead) declare a Role Boundaries
   section with both an I DO and an I DO NOT list.
6. Every agent on disk is listed in manifest.json agents and vice versa.

Exit code: 0 = clean, 1 = issues found
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AGENTS_DIR = ROOT / "agents"
MANIFEST_PATH = ROOT / "manifest.json"

SCHEMA = "atlas-role-registry/1.0"
VALID_TIERS = {"premium", "standard", "fast"}
REQUIRED_FIELDS = ["name", "role", "description", "tier", "capabilities", "permissions"]
ROLE_NAME_RE = re.compile(r"^atlas-[a-z0-9-]+$")
ORCHESTRATOR = "atlas-lead"


def split_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return None


def parse_frontmatter(lines):
    """Parse the small, predictable subset of YAML the agent files use.

    Supports `key: scalar`, `key: [a, b]`, `key:` followed by an indented
    `- item` list, and `key:` followed by indented `subkey: scalar` maps.
    """
    data = {}
    current = None
    current_kind = None
    for raw in lines:
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        stripped = raw.strip()
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.split(" #")[0].strip()
            if value == "":
                data[key] = None
                current, current_kind = key, None
            elif value.startswith("[") and value.endswith("]"):
                inner = value[1:-1].strip()
                data[key] = [p.strip().strip("'\"") for p in inner.split(",")] if inner else []
                current, current_kind = None, None
            else:
                data[key] = value.strip("'\"")
                current, current_kind = None, None
        elif indent > 0 and current:
            if stripped.startswith("- "):
                if current_kind in (None, "list"):
                    if not isinstance(data.get(current), list):
                        data[current] = []
                    current_kind = "list"
                data[current].append(stripped[2:].strip().strip("'\""))
            elif ":" in stripped:
                if current_kind in (None, "map"):
                    if not isinstance(data.get(current), dict):
                        data[current] = {}
                    current_kind = "map"
                subkey, _, subvalue = stripped.partition(":")
                data[current][subkey.strip()] = subvalue.split(" #")[0].strip().strip("'\"")
    return data


def validate_agent(path, manifest_agents, issues):
    text = path.read_text(encoding="utf-8")
    stem = path.stem
    fm_lines = split_frontmatter(text)
    if fm_lines is None:
        issues.append((path.name, "missing frontmatter block"))
        return None
    fm = parse_frontmatter(fm_lines)

    for field in REQUIRED_FIELDS:
        if field not in fm or fm[field] in (None, "", []):
            issues.append((path.name, f"missing required field '{field}'"))

    name = fm.get("name")
    if name != stem:
        issues.append((path.name, f"name '{name}' does not match filename '{stem}'"))
    if not isinstance(name, str) or not ROLE_NAME_RE.match(name or ""):
        issues.append((path.name, f"name '{name}' is not a valid atlas-<slug> role id"))

    tier = fm.get("tier")
    if tier not in VALID_TIERS:
        issues.append((path.name, f"tier '{tier}' not in {sorted(VALID_TIERS)}"))

    caps = fm.get("capabilities")
    if not isinstance(caps, list) or not caps:
        issues.append((path.name, "capabilities must be a non-empty list"))

    perms = fm.get("permissions")
    if not isinstance(perms, dict):
        issues.append((path.name, "permissions must be a map with read and write"))
    else:
        for key in ("read", "write"):
            if key not in perms:
                issues.append((path.name, f"permissions.{key} is required"))
            elif perms[key] not in ("true", "false"):
                issues.append((path.name, f"permissions.{key} must be true or false, got '{perms[key]}'"))

    if stem != ORCHESTRATOR:
        has_bounds = "## Role Boundaries" in text
        has_do = "### I DO" in text
        has_not = "### I DO NOT" in text
        if not (has_bounds and has_do and has_not):
            issues.append((path.name, "specialist role must declare Role Boundaries with I DO and I DO NOT"))

    if path.name not in manifest_agents:
        issues.append((path.name, "not listed in manifest.json agents"))

    return {
        "role": name,
        "label": fm.get("role"),
        "tier": tier,
        "capabilities": caps if isinstance(caps, list) else [],
        "permissions": {
            "read": perms.get("read") == "true" if isinstance(perms, dict) else False,
            "write": perms.get("write") == "true" if isinstance(perms, dict) else False,
        },
        "boundaries": stem != ORCHESTRATOR,
    }


def build_registry(agents):
    return {
        "schema": SCHEMA,
        "source": "agents/*.md",
        "roles": {role["role"]: {k: v for k, v in role.items() if k != "role"} for role in agents},
    }


def main():
    as_json = "--json" in sys.argv
    agent_paths = sorted(AGENTS_DIR.glob("*.md"))
    issues = []
    roles = []

    manifest_agents = set()
    if MANIFEST_PATH.is_file():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            manifest_agents = set(json.load(f).get("agents", []))
    else:
        issues.append(("manifest.json", "missing manifest.json"))

    for path in agent_paths:
        role = validate_agent(path, manifest_agents, issues)
        if role:
            roles.append(role)

    for listed in sorted(manifest_agents - {p.name for p in agent_paths}):
        issues.append(("manifest.json", f"'{listed}' listed in manifest but missing under agents/"))

    if as_json:
        print(json.dumps(build_registry(roles), indent=2, sort_keys=True))
        return 1 if issues else 0

    print("Atlas Role Registry Validator")
    print("=" * 50)
    if issues:
        print(f"FOUND {len(issues)} issue(s):")
        for name, detail in issues:
            print(f"   - {name}: {detail}")
        print("\nRESULT: FAILED")
        return 1
    print(f"OK: {len(roles)} role definition(s) valid against {SCHEMA}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
