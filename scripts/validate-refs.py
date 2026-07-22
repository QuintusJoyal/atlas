#!/usr/bin/env python3
"""Validate Atlas cross-references and manifest consistency.

Usage:
    python3 scripts/validate-refs.py

Checks:
1. All knowledge/<file> references in .md files point to existing files
2. manifest.json lists all knowledge files that exist on disk
3. No broken cross-references within knowledge files

Exit code: 0 = clean, 1 = issues found
"""

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
MANIFEST_PATH = ROOT / "manifest.json"

# Matches knowledge/<path>.md, with or without a leading $ATLAS_DATA_DIR/ prefix.
REF_PATTERN = re.compile(r'(?:\`?\$?ATLAS_DATA_DIR/)?knowledge/([a-zA-Z0-9_/-]+\.md)')


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


def check_manifest():
    with open(MANIFEST_PATH, 'r') as f:
        manifest = json.load(f)

    manifest_files = set(manifest.get('knowledge', []))

    disk_files = set()
    for dirpath, dirnames, filenames in os.walk(KNOWLEDGE_DIR):
        for f in filenames:
            if f.endswith('.md'):
                rel_path = os.path.relpath(os.path.join(dirpath, f), KNOWLEDGE_DIR)
                disk_files.add(rel_path.replace(os.sep, '/'))

    missing_from_manifest = disk_files - manifest_files
    missing_from_disk = manifest_files - disk_files

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

    print("\n2. Checking manifest.json consistency...")
    missing_manifest, missing_disk = check_manifest()

    if missing_manifest:
        print(f"   FOUND {len(missing_manifest)} files on disk not in manifest:")
        for f in sorted(missing_manifest):
            print(f"   - knowledge/{f}")
            issues += 1
    else:
        print("   OK: All disk files listed in manifest")

    if missing_disk:
        print(f"   FOUND {len(missing_disk)} files in manifest not on disk:")
        for f in sorted(missing_disk):
            print(f"   - knowledge/{f}")
            issues += 1
    else:
        print("   OK: All manifest files exist on disk")

    print("\n" + "=" * 50)
    if issues == 0:
        print("RESULT: CLEAN - No issues found")
        return 0
    else:
        print(f"RESULT: {issues} ISSUES FOUND")
        return 1


if __name__ == '__main__':
    sys.exit(main())
