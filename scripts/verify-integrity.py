#!/usr/bin/env python3
"""Verify bundle integrity against manifest.json hashes.

Usage:
    python3 scripts/verify-integrity.py               # verify this tree
    python3 scripts/verify-integrity.py --root DIR    # verify an installed copy
    python3 scripts/verify-integrity.py --update      # regenerate hashes (resign)
    python3 scripts/verify-integrity.py --checksums   # print SHA256SUMS for release

manifest.json (schema atlas-bundle/2.0) pins a SHA-256 hash for every agent,
rule, skill playbook, and knowledge file under integrity.files. Verification
fails with a per-file report when any pinned file is modified, missing, or
unpinned, so a tampered bundle is caught before the orchestrator loads it.

Skips (exit 0) when no manifest is present (lite-mode installs) or the
manifest has no integrity block (pre-2.0 bundles).

Exit code: 0 = clean or skipped, 1 = integrity failure
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ALGORITHM = "sha256"


def collect_files(manifest):
    """Relative paths (forward slashes) of every hashable bundle file."""
    paths = []
    for name in manifest.get("agents", []):
        paths.append(f"agents/{name}")
    for name in manifest.get("rules", []):
        paths.append(f"rules/{name}")
    for name in manifest.get("skills", []):
        paths.append(f"skills/{name}/SKILL.md")
    for name in manifest.get("knowledge", []):
        paths.append(f"knowledge/{name}")
    return paths


def sha256_of(path):
    digest = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify(root, manifest):
    """Compare files on disk against the manifest's integrity block.

    Returns a list of (path, problem) tuples; empty means clean.
    """
    issues = []
    integrity = manifest.get("integrity") or {}
    pinned = integrity.get("files") or {}
    collected = collect_files(manifest)

    for rel in collected:
        if rel not in pinned:
            issues.append((rel, "not pinned in manifest integrity block"))
    for rel in sorted(pinned):
        if rel not in collected:
            issues.append((rel, "pinned but not listed in manifest"))
            continue
        full = root / rel
        if not full.is_file():
            issues.append((rel, "missing on disk"))
        else:
            actual = sha256_of(full)
            if actual != pinned[rel]:
                issues.append((rel, f"hash mismatch (expected {pinned[rel][:12]}..., got {actual[:12]}...)"))
    return issues


def update(root, manifest_path, manifest):
    """Recompute hashes from disk and write them back (resign path).

    Edits the manifest text surgically so the rest of the file keeps its
    original formatting.
    """
    files = {}
    for rel in collect_files(manifest):
        full = root / rel
        if not full.is_file():
            print(f"ERROR: cannot sign missing file: {rel}")
            return 1
        files[rel] = sha256_of(full)

    text = manifest_path.read_text(encoding="utf-8")
    # Drop any existing top-level integrity block before inserting the new one.
    text = re.sub(r',?\n  "integrity": \{.*?\n  \}', "", text, count=1, flags=re.DOTALL)
    block = '"integrity": ' + json.dumps({"algorithm": ALGORITHM, "files": files}, indent=2)
    block = "\n".join("  " + line if line else line for line in block.splitlines())
    close = text.rstrip()
    assert close.endswith("}"), "manifest.json does not end with a closing brace"
    text = close[:-1].rstrip() + ",\n" + block + "\n}\n"
    manifest_path.write_text(text, encoding="utf-8")
    print(f"Resigned {len(files)} files in {manifest_path}")
    return 0


def print_checksums(root, manifest):
    """Emit SHA256SUMS (hash and path per line) for release publishing."""
    for rel in collect_files(manifest):
        full = root / rel
        if not full.is_file():
            print(f"ERROR: missing file: {rel}", file=sys.stderr)
            return 1
        print(f"{sha256_of(full)}  {rel}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Verify Atlas bundle integrity against manifest.json")
    parser.add_argument("--root", default=None, help="bundle root to check (default: this repo)")
    parser.add_argument("--update", action="store_true", help="regenerate hashes from disk (resign)")
    parser.add_argument("--checksums", action="store_true", help="print SHA256SUMS for release publishing")
    args = parser.parse_args()

    root = Path(args.root).resolve() if args.root else Path(__file__).resolve().parent.parent
    manifest_path = root / "manifest.json"

    if not manifest_path.is_file():
        print("SKIP: no manifest.json present (lite-mode install?). Nothing to verify.")
        return 0

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    if not args.update and not (manifest.get("integrity") or {}).get("files"):
        print("SKIP: manifest has no integrity block (pre-2.0 bundle). Nothing to verify.")
        return 0

    if args.update:
        return update(root, manifest_path, manifest)
    if args.checksums:
        return print_checksums(root, manifest)

    print(f"Atlas Bundle Integrity ({manifest.get('integrity', {}).get('algorithm', ALGORITHM)})")
    print("=" * 50)

    issues = verify(root, manifest)
    if issues:
        print(f"FAILED: {len(issues)} file(s) failed verification:")
        for rel, problem in issues:
            print(f"  - {rel}: {problem}")
        print("\nDo not load this bundle. If the changes were intentional, re-pin with:")
        print("  python3 scripts/verify-integrity.py --update")
        return 1

    total = len(manifest["integrity"]["files"])
    print(f"OK: all {total} pinned files match the manifest")
    return 0


if __name__ == "__main__":
    sys.exit(main())
