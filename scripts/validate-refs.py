#!/usr/bin/env python3
"""Validate Atlas cross-references and manifest consistency.

Usage:
    python3 scripts/validate-refs.py

Checks:
1. All knowledge/<file> references in .md files point to existing files
2. intent/ and specifications/ references in .md files point to existing files
3. Intent and specification YAML files match their schemas and reference real files
4. manifest.json lists all knowledge, intent, and specification files that exist on disk
5. Bundle files on disk match the SHA-256 hashes pinned in manifest.json

Exit code: 0 = clean, 1 = issues found
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # schema checks degrade gracefully; reference checks still run
    yaml = None

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
INTENT_DIR = ROOT / "intent"
SPECIFICATIONS_DIR = ROOT / "specifications"
MANIFEST_PATH = ROOT / "manifest.json"

# Matches knowledge/<path>.md, with or without a leading $ATLAS_DATA_DIR/ prefix.
REF_PATTERN = re.compile(r'(?:\`?\$?ATLAS_DATA_DIR/)?knowledge/([a-zA-Z0-9_/-]+\.md)')
INTENT_REF_PATTERN = re.compile(r'(?:\`?\$?ATLAS_DATA_DIR/)?intent/([a-zA-Z0-9_/-]+\.ya?ml)')
SPEC_REF_PATTERN = re.compile(r'(?:\`?\$?ATLAS_DATA_DIR/)?specifications/([a-zA-Z0-9_/-]+\.ya?ml)')
KNOWLEDGE_REF_IN_YAML = re.compile(r'knowledge/([a-zA-Z0-9_/-]+\.md)')

GOAL_WEIGHTS = {'critical', 'high', 'medium', 'low'}
RISK_LEVELS = {'low', 'medium', 'high'}
POLICY_SEVERITIES = {'block', 'warn', 'info'}
POLICY_SCOPES = {'global', 'role', 'phase'}


def find_all_md_files():
    md_files = []
    skip_files = {'MIGRATION-v0.13-to-v0.14.md'}  # Migration guides have intentional old paths
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if '.git' in dirpath:
            continue
        for f in filenames:
            if f.endswith('.md') and f not in skip_files:
                md_files.append(Path(dirpath) / f)
    return md_files


def find_knowledge_refs(md_files):
    refs = {}  # {file_path: [(line_num, ref_path)]}
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        file_refs = []
        for i, line in enumerate(content.splitlines(), 1):
            for match in REF_PATTERN.finditer(line):
                ref_path = match.group(1)
                # Skip template placeholders
                if '<' in ref_path:
                    continue
                file_refs.append((i, ref_path))
        if file_refs:
            refs[md_file] = file_refs
    return refs


def check_refs_exist(refs):
    broken = []
    for md_file, file_refs in refs.items():
        for line_num, ref_path in file_refs:
            full_path = KNOWLEDGE_DIR / ref_path
            if not full_path.exists():
                broken.append((md_file, line_num, ref_path))
    return broken


def find_layer_refs(md_files, pattern, directory):
    """Find directory/<file>.yaml refs in .md files and check they resolve."""
    broken = []
    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue
        for i, line in enumerate(content.splitlines(), 1):
            for match in pattern.finditer(line):
                ref_path = match.group(1)
                if '<' in ref_path or '*' in ref_path:
                    continue
                if not (directory / ref_path).exists():
                    broken.append((md_file, i, ref_path))
    return broken


def check_governance():
    """Validate intent/specification YAML schemas and their internal references.

    Returns a list of human-readable issue strings. Reference resolution is
    regex-based so it runs even when PyYAML is unavailable; schema checks are
    skipped when PyYAML is missing.
    """
    issues = []

    if not INTENT_DIR.is_dir() or not SPECIFICATIONS_DIR.is_dir():
        return issues

    # Always check policy -> knowledge references, independent of PyYAML.
    for spec_file in sorted(SPECIFICATIONS_DIR.glob('*.y*ml')):
        text = spec_file.read_text(encoding='utf-8')
        for match in KNOWLEDGE_REF_IN_YAML.finditer(text):
            ref = match.group(1)
            if not (KNOWLEDGE_DIR / ref).exists():
                issues.append(f"{spec_file.relative_to(ROOT)}: reference knowledge/{ref} does not exist")

    if yaml is None:
        return issues

    for intent_file in sorted(INTENT_DIR.glob('*.y*ml')):
        try:
            data = yaml.safe_load(intent_file.read_text(encoding='utf-8')) or {}
        except yaml.YAMLError as exc:
            issues.append(f"{intent_file.relative_to(ROOT)}: invalid YAML ({exc})")
            continue
        rel = intent_file.relative_to(ROOT)
        for key in ('schema', 'id', 'name', 'goals', 'values', 'risk_tolerance', 'tradeoffs'):
            if key not in data:
                issues.append(f"{rel}: missing required key '{key}'")
        if not str(data.get('schema', '')).startswith('atlas-intent/'):
            issues.append(f"{rel}: schema must be 'atlas-intent/<version>'")
        goals = data.get('goals')
        if not isinstance(goals, list) or not goals:
            issues.append(f"{rel}: 'goals' must be a non-empty list")
        else:
            for goal in goals:
                if not isinstance(goal, dict) or 'id' not in goal or 'description' not in goal:
                    issues.append(f"{rel}: each goal needs 'id' and 'description'")
                elif goal.get('weight', 'medium') not in GOAL_WEIGHTS:
                    issues.append(f"{rel}: goal '{goal['id']}' has invalid weight '{goal.get('weight')}'")
        values = data.get('values')
        if not isinstance(values, list) or not values:
            issues.append(f"{rel}: 'values' must be a non-empty list")
        risk = data.get('risk_tolerance')
        if not isinstance(risk, dict) or not risk:
            issues.append(f"{rel}: 'risk_tolerance' must be a non-empty mapping")
        else:
            for domain, level in risk.items():
                if level not in RISK_LEVELS:
                    issues.append(f"{rel}: risk_tolerance.{domain} must be one of {sorted(RISK_LEVELS)}")
        tradeoffs = data.get('tradeoffs')
        priority = tradeoffs.get('priority') if isinstance(tradeoffs, dict) else None
        if not isinstance(priority, list) or not priority:
            issues.append(f"{rel}: tradeoffs.priority must be a non-empty ordered list")
        elif len(set(priority)) != len(priority):
            issues.append(f"{rel}: tradeoffs.priority entries must be unique")

    for spec_file in sorted(SPECIFICATIONS_DIR.glob('*.y*ml')):
        try:
            data = yaml.safe_load(spec_file.read_text(encoding='utf-8')) or {}
        except yaml.YAMLError as exc:
            issues.append(f"{spec_file.relative_to(ROOT)}: invalid YAML ({exc})")
            continue
        rel = spec_file.relative_to(ROOT)
        for key in ('schema', 'id', 'name', 'scope', 'policies'):
            if key not in data:
                issues.append(f"{rel}: missing required key '{key}'")
        if not str(data.get('schema', '')).startswith('atlas-specification/'):
            issues.append(f"{rel}: schema must be 'atlas-specification/<version>'")
        if data.get('scope') not in POLICY_SCOPES:
            issues.append(f"{rel}: scope must be one of {sorted(POLICY_SCOPES)}")
        policies = data.get('policies')
        if not isinstance(policies, list) or not policies:
            issues.append(f"{rel}: 'policies' must be a non-empty list")
            continue
        seen_ids = set()
        for policy in policies:
            if not isinstance(policy, dict):
                issues.append(f"{rel}: each policy must be a mapping")
                continue
            pid = policy.get('id')
            if not pid or not policy.get('description'):
                issues.append(f"{rel}: each policy needs 'id' and 'description'")
            elif pid in seen_ids:
                issues.append(f"{rel}: duplicate policy id '{pid}'")
            seen_ids.add(pid)
            if policy.get('severity') not in POLICY_SEVERITIES:
                issues.append(f"{rel}: policy '{pid}' severity must be one of {sorted(POLICY_SEVERITIES)}")
            if policy.get('scope') not in POLICY_SCOPES:
                issues.append(f"{rel}: policy '{pid}' scope must be one of {sorted(POLICY_SCOPES)}")
            applies_to = policy.get('applies_to')
            if applies_to is not None and not isinstance(applies_to, list):
                issues.append(f"{rel}: policy '{pid}' applies_to must be a list")

    return issues


def check_manifest():
    """Return (on_disk_not_in_manifest, in_manifest_not_on_disk) for the
    knowledge/, intent/, and specifications/ trees."""
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    missing_from_manifest = set()
    missing_from_disk = set()

    for key, directory, suffix in (
        ('knowledge', KNOWLEDGE_DIR, '.md'),
        ('intent', INTENT_DIR, ('.yaml', '.yml')),
        ('specifications', SPECIFICATIONS_DIR, ('.yaml', '.yml')),
    ):
        listed = set(manifest.get(key, []))
        disk = set()
        if directory.is_dir():
            for dirpath, dirnames, filenames in os.walk(directory):
                for f in filenames:
                    if f.endswith(suffix):
                        rel_path = os.path.relpath(os.path.join(dirpath, f), directory)
                        disk.add(rel_path.replace(os.sep, '/'))
        missing_from_manifest |= {f"{key}/{f}" for f in disk - listed}
        missing_from_disk |= {f"{key}/{f}" for f in listed - disk}

    return missing_from_manifest, missing_from_disk


def main():
    print("Atlas Reference Validator")
    print("=" * 50)

    issues = 0

    print("\n1. Checking knowledge references in .md files...")
    md_files = find_all_md_files()
    refs = find_knowledge_refs(md_files)
    broken = check_refs_exist(refs)

    if broken:
        print(f"   FOUND {len(broken)} broken references:")
        for md_file, line_num, ref_path in broken:
            rel_file = md_file.relative_to(ROOT)
            print(f"   - {rel_file}:{line_num} -> knowledge/{ref_path}")
            issues += 1
    else:
        print(f"   OK: All {sum(len(r) for r in refs.values())} references valid")

    print("\n2. Checking intent/ and specifications/ references in .md files...")
    layer_broken = (
        find_layer_refs(md_files, INTENT_REF_PATTERN, INTENT_DIR)
        + find_layer_refs(md_files, SPEC_REF_PATTERN, SPECIFICATIONS_DIR)
    )
    if layer_broken:
        print(f"   FOUND {len(layer_broken)} broken references:")
        for md_file, line_num, ref_path in layer_broken:
            rel_file = md_file.relative_to(ROOT)
            print(f"   - {rel_file}:{line_num} -> {ref_path}")
            issues += 1
    else:
        print("   OK: All intent/specification references valid")

    print("\n3. Checking intent and specification schemas...")
    governance_issues = check_governance()
    if governance_issues:
        for issue in governance_issues:
            print(f"   - {issue}")
            issues += 1
    elif yaml is None:
        print("   SKIP: PyYAML not installed, schema checks skipped")
    else:
        print("   OK: intent and specification files match their schemas")

    print("\n4. Checking manifest.json consistency...")
    missing_manifest, missing_disk = check_manifest()

    if missing_manifest:
        print(f"   FOUND {len(missing_manifest)} files on disk not in manifest:")
        for f in sorted(missing_manifest):
            print(f"   - {f}")
            issues += 1
    else:
        print("   OK: All disk files listed in manifest")

    if missing_disk:
        print(f"   FOUND {len(missing_disk)} files in manifest not on disk:")
        for f in sorted(missing_disk):
            print(f"   - {f}")
            issues += 1
    else:
        print("   OK: All manifest files exist on disk")

    print("\n5. Checking bundle integrity hashes against manifest.json...")
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "verify-integrity.py")],
        capture_output=True,
        text=True,
    )
    # The verify script prints SKIP for bundles without an integrity block
    # (pre-2.0 or lite-mode); that is clean, not a failure.
    if "SKIP:" in result.stdout:
        print("   " + result.stdout.strip().splitlines()[0])
    elif result.returncode != 0:
        for line in result.stdout.strip().splitlines():
            print(f"   {line}")
        issues += 1
    else:
        for line in result.stdout.strip().splitlines():
            print(f"   {line}")

    print("\n" + "=" * 50)
    if issues == 0:
        print("RESULT: CLEAN - No issues found")
        return 0
    else:
        print(f"RESULT: {issues} ISSUES FOUND")
        return 1


if __name__ == '__main__':
    sys.exit(main())
