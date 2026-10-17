#!/usr/bin/env python3
"""Export approved lessons, skills, and rules as a portable rule pack.

Rule packs are how one Atlas project shares proven knowledge with another
(see knowledge/process/rule-packs.md). This script bundles the canonical
approved lessons plus any explicitly selected custom skills and rules into
a single `.tar.gz` carrying a `pack.json` metadata manifest:

    source project, pack version, domain tags, confidence score,
    last-validated date, entry counts, and the file list.

Usage:
    python3 scripts/export-pack.py                          # lessons only
    python3 scripts/export-pack.py --skills my-skill --rules my-rule
    python3 scripts/export-pack.py --tags backend,ci --confidence 0.9
    python3 scripts/export-pack.py --out dist --root DIR

The pack is inert data: importing it (scripts/import-pack.py) merges nothing
into lessons.md directly — entries land in proposed.md for human approval.

Exit code: 0 = pack written, 1 = error
"""

import argparse
import io
import json
import re
import sys
import tarfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_SCHEMA = "atlas-rulepack/1"
LESSONS_REL = "knowledge/reference/lessons.md"
SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]*$")
APPROVED_RE = re.compile(r"approved:\s*(\d{4}-\d{2}-\d{2})")
FENCE_RE = re.compile(r"^\s*```")


def parse_args():
    p = argparse.ArgumentParser(description="Export an Atlas rule pack (.tar.gz)")
    p.add_argument("--root", default=None, help="bundle root (default: this repo)")
    p.add_argument("--project", default=None, help="source project name (default: manifest name)")
    p.add_argument("--pack-version", default=None, help="pack version (default: manifest version)")
    p.add_argument("--tags", default=None, help="comma-separated domain tags (default: lesson topics)")
    p.add_argument("--confidence", type=float, default=0.8,
                   help="confidence that the pack's lessons still apply, 0-1 (default: 0.8)")
    p.add_argument("--last-validated", default=None, help="YYYY-MM-DD (default: latest approved date in lessons)")
    p.add_argument("--skills", default="", help="comma-separated skill dirs under skills/ to include")
    p.add_argument("--rules", default="", help="comma-separated rule files under rules/ to include")
    p.add_argument("--out", default="dist", help="output directory (default: dist)")
    return p.parse_args()


def names(csv, flag):
    out = []
    for raw in csv.split(","):
        name = raw.strip()
        if not name:
            continue
        if not SLUG_RE.match(name):
            sys.exit(f"ERROR: invalid {flag} name {name!r} (expected lowercase letters, digits, hyphens)")
        out.append(name)
    return out


def lesson_entries(text):
    """(topic, entry-text) for each approved lesson line outside code fences."""
    entries, topic, in_fence = [], None, False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            topic = line[3:].strip()
        elif line.startswith("- "):
            entries.append((topic, line[2:].strip()))
    return entries


def domain_tags(lessons_text):
    topics = []
    for topic, _ in lesson_entries(lessons_text):
        slug = re.sub(r"[^a-z0-9]+", "-", (topic or "").lower()).strip("-")
        if slug and slug not in topics:
            topics.append(slug)
    return topics


def main():
    args = parse_args()
    root = Path(args.root).resolve() if args.root else ROOT

    manifest = {}
    manifest_path = root / "manifest.json"
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    project = args.project or manifest.get("name") or root.name
    pack_version = args.pack_version or manifest.get("version") or "0.0.0"

    lessons_path = root / LESSONS_REL
    if not lessons_path.is_file():
        sys.exit(f"ERROR: {LESSONS_REL} not found under {root} — nothing to export")
    lessons_text = lessons_path.read_text(encoding="utf-8")
    entries = lesson_entries(lessons_text)
    if not entries:
        sys.exit(f"ERROR: {LESSONS_REL} has no approved lesson entries")

    skill_names = names(args.skills, "--skills")
    rule_names = names(args.rules, "--rules")
    members = [("lessons.md", lessons_path)]
    for name in skill_names:
        skill_path = root / "skills" / name / "SKILL.md"
        if not skill_path.is_file():
            sys.exit(f"ERROR: skill {name!r} not found at skills/{name}/SKILL.md")
        members.append((f"skills/{name}/SKILL.md", skill_path))
    for name in rule_names:
        rule_path = root / "rules" / f"{name}.md"
        if not rule_path.is_file():
            sys.exit(f"ERROR: rule {name!r} not found at rules/{name}.md")
        members.append((f"rules/{name}.md", rule_path))

    if not 0.0 <= args.confidence <= 1.0:
        sys.exit("ERROR: --confidence must be between 0 and 1")

    approved_dates = APPROVED_RE.findall(lessons_text)
    last_validated = args.last_validated or (max(approved_dates) if approved_dates else date.today().isoformat())
    try:
        date.fromisoformat(last_validated)
    except ValueError:
        sys.exit(f"ERROR: --last-validated must be YYYY-MM-DD, got {last_validated!r}")

    tags = names(args.tags, "--tags") if args.tags else domain_tags(lessons_text)
    pack_id = re.sub(r"[^a-z0-9]+", "-", project.lower()).strip("-") or "atlas"

    pack = {
        "schema": PACK_SCHEMA,
        "id": pack_id,
        "name": f"{project} rule pack",
        "packVersion": pack_version,
        "sourceProject": {"name": project, "version": manifest.get("version", pack_version)},
        "exportedAt": date.today().isoformat(),
        "domainTags": tags,
        "confidence": args.confidence,
        "lastValidated": last_validated,
        "counts": {
            "lessons": len(entries),
            "skills": len(skill_names),
            "rules": len(rule_names),
        },
        "files": [rel for rel, _ in members],
        "generator": "scripts/export-pack.py",
    }

    out_dir = root / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    archive_path = out_dir / f"{pack_id}-rulepack-{pack_version}.tar.gz"
    prefix = f"{pack_id}-rulepack-{pack_version}/"

    with tarfile.open(archive_path, "w:gz") as tar:
        blob = io.BytesIO(json.dumps(pack, indent=2).encode("utf-8") + b"\n")
        info = tarfile.TarInfo(prefix + "pack.json")
        info.size, info.mtime = blob.getbuffer().nbytes, 0
        tar.addfile(info, blob)
        for rel, path in members:
            data = path.read_bytes()
            info = tarfile.TarInfo(prefix + rel)
            info.size, info.mtime = len(data), 0
            tar.addfile(info, io.BytesIO(data))

    print(f"Wrote {archive_path.relative_to(root)}")
    print(f"  project:  {project} ({pack_version})")
    print(f"  entries:  {pack['counts']['lessons']} lessons, "
          f"{pack['counts']['skills']} skills, {pack['counts']['rules']} rules")
    print(f"  tags:     {', '.join(tags) or '(none)'}")
    print(f"  confidence {pack['confidence']}, last-validated {last_validated}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
