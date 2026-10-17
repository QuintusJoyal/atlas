#!/usr/bin/env python3
"""Validate Atlas skill manifests against the skill-registry schema.

Usage:
    python3 scripts/validate-skills.py

Checks (see knowledge/process/skill-registry.md for the schema):
1. Every skills/<name>/SKILL.md has frontmatter with name + description,
   and name matches its directory
2. Extended fields are well-formed: capabilities implies a valid semver
   version; permissions/inputs/outputs/requires are lists when present
3. Every requires entry ("name@X.Y.Z") names a registered skill, and the
   pinned MAJOR matches the dependency's current MAJOR (backward compat)
4. No dependency cycles
5. manifest.json skills[] matches the skill directories on disk
6. Prints the capability catalog (capability -> skills), the registry
   query surface for agents binding skills at runtime

Exit code: 0 = clean, 1 = issues found
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = ROOT / "skills"
MANIFEST_PATH = ROOT / "manifest.json"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRES_RE = re.compile(r"^([a-z0-9-]+)@(\d+\.\d+\.\d+)$")
LIST_KEYS = ("capabilities", "permissions", "inputs", "outputs", "requires", "appliesTo", "tags")


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
    return None  # unterminated frontmatter


def load_skills():
    """[(dir_name, frontmatter_dict_or_None)] for each skills/<name>/ dir."""
    skills = []
    for entry in sorted(SKILLS_DIR.iterdir()):
        if not entry.is_dir() or entry.name.startswith("."):
            continue
        skill_file = entry / "SKILL.md"
        if not skill_file.is_file():
            skills.append((entry.name, None))
            continue
        skills.append((entry.name, parse_frontmatter(skill_file)))
    return skills


def check_manifest():
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    listed = set(manifest.get("skills", []))
    on_disk = {name for name, _ in load_skills()}
    return listed - on_disk, on_disk - listed


def find_cycles(deps):
    """deps: {name: [dep_names]}. Returns list of cycles (each a list of names)."""
    cycles = []
    state = {}  # 0=unvisited, 1=on-stack, 2=done
    stack = []

    def visit(node):
        state[node] = 1
        stack.append(node)
        for dep in deps.get(node, []):
            if state.get(dep, 0) == 1:
                cycles.append(stack[stack.index(dep):] + [dep])
            elif state.get(dep, 0) == 0:
                visit(dep)
        stack.pop()
        state[node] = 2

    for node in deps:
        if state.get(node, 0) == 0:
            visit(node)
    return cycles


def main():
    print("Atlas Skill Registry Validator")
    print("=" * 50)

    issues = 0
    skills = load_skills()
    registry = {}  # name -> frontmatter (valid entries)
    deps = {}

    print("\n1. Checking skill manifests (name, description, schema)...")
    for dir_name, fm in skills:
        if fm is None:
            print(f"   FOUND skills/{dir_name}/SKILL.md missing or unparseable frontmatter")
            issues += 1
            continue

        name = fm.get("name", "")
        if name != dir_name:
            print(f"   FOUND skills/{dir_name}: frontmatter name '{name}' != directory name")
            issues += 1
        if not fm.get("description"):
            print(f"   FOUND skills/{dir_name}: missing description")
            issues += 1

        if "capabilities" in fm:
            if not fm["capabilities"]:
                print(f"   FOUND skills/{dir_name}: capabilities is empty")
                issues += 1
            version = fm.get("version", "")
            if not version:
                print(f"   FOUND skills/{dir_name}: capabilities without a version")
                issues += 1
            elif not SEMVER_RE.match(version):
                print(f"   FOUND skills/{dir_name}: version '{version}' is not MAJOR.MINOR.PATCH")
                issues += 1

        for key in LIST_KEYS:
            if key in fm and not isinstance(fm[key], list):
                print(f"   FOUND skills/{dir_name}: {key} must be a list")
                issues += 1

        requires = fm.get("requires") if isinstance(fm.get("requires"), list) else []
        dep_names = []
        for req in requires:
            match = REQUIRES_RE.match(req)
            if not match:
                print(f"   FOUND skills/{dir_name}: requires entry '{req}' not in name@X.Y.Z form")
                issues += 1
                continue
            dep_names.append((match.group(1), match.group(2)))
        deps[dir_name] = [d[0] for d in dep_names]
        # stash for later passes
        fm["_requires"] = dep_names
        registry[dir_name] = fm

    if issues == 0:
        print(f"   OK: {len(registry)} skill manifests valid")

    print("\n2. Checking dependency resolution and backward compatibility...")
    dep_issues = 0
    for name, fm in registry.items():
        for dep_name, dep_version in fm.get("_requires", []):
            if dep_name not in registry:
                print(f"   FOUND {name}: requires unknown skill '{dep_name}'")
                dep_issues += 1
                continue
            current = registry[dep_name].get("version", "0.0.0")
            if not SEMVER_RE.match(current):
                current = "0.0.0"
            if current.split(".")[0] != dep_version.split(".")[0]:
                print(f"   FOUND {name}: requires {dep_name}@{dep_version} "
                      f"but registry has {dep_name}@{current} (major mismatch)")
                dep_issues += 1
    cycles = find_cycles(deps)
    for cycle in cycles:
        print(f"   FOUND dependency cycle: {' -> '.join(cycle)}")
        dep_issues += 1
    if dep_issues == 0:
        print("   OK: all requires resolvable, majors compatible, no cycles")
    issues += dep_issues

    print("\n3. Checking manifest.json skills[] consistency...")
    missing_manifest, missing_disk = check_manifest()
    if missing_manifest:
        for f in sorted(missing_manifest):
            print(f"   FOUND in manifest but not on disk: skills/{f}")
            issues += 1
    if missing_disk:
        for f in sorted(missing_disk):
            print(f"   FOUND on disk but not in manifest: skills/{f}")
            issues += 1
    if not missing_manifest and not missing_disk:
        print("   OK: manifest skills[] matches disk")

    print("\n4. Capability catalog (registry query surface)...")
    catalog = {}
    for name, fm in registry.items():
        for cap in fm.get("capabilities") or []:
            catalog.setdefault(cap, []).append(f"{name}@{fm.get('version', '?')}")
    if catalog:
        for cap in sorted(catalog):
            print(f"   {cap}: {', '.join(sorted(catalog[cap]))}")
    else:
        print("   (no skills declare capabilities)")

    print("\n" + "=" * 50)
    if issues == 0:
        print("RESULT: CLEAN - No issues found")
        return 0
    print(f"RESULT: {issues} ISSUES FOUND")
    return 1


if __name__ == "__main__":
    sys.exit(main())
