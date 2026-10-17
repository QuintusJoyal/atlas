#!/usr/bin/env python3
"""Import a rule pack into an Atlas project, with conflict detection and review.

Companion to scripts/export-pack.py (format documented in
knowledge/process/rule-packs.md). Import never rewrites `lessons.md`: approved
lessons from the pack are appended to `knowledge/reference/proposed.md` as
checkbox review items, so the existing L1/L2/L3 approval pipeline stays the
only path into canonical knowledge. Skills and rules are merged into the full
bundle only under --apply, and a registry index records every ingested pack so
the same pack version is never ingested twice.

Lite mode is untouched by design: nothing is written under lite/, and lite
never loads knowledge/, so imported packs stay outside its token budget.

Usage:
    python3 scripts/import-pack.py dist/atlas-rulepack-0.17.4.tar.gz
    python3 scripts/import-pack.py pack.tar.gz --apply
    python3 scripts/import-pack.py pack.zip --root /path/to/target

Exit code: 0 = clean (merged, or dry run), 1 = error or duplicate pack
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PACK_SCHEMA = "atlas-rulepack/1"
REGISTRY_SCHEMA = "atlas-rulepack-registry/1"
PROPOSED_REL = "knowledge/reference/proposed.md"
REGISTRY_REL = "knowledge/reference/pack-registry.json"
REQUIRED_KEYS = ("schema", "id", "packVersion", "sourceProject", "domainTags",
                 "confidence", "lastValidated", "files")
FENCE_RE = re.compile(r"^\s*```")
TRAILING_META_RE = re.compile(r"(?:\s*\([^()]*\))+\s*$")


def parse_args():
    p = argparse.ArgumentParser(description="Import an Atlas rule pack (.tar.gz/.zip)")
    p.add_argument("archive", help="rule pack archive produced by scripts/export-pack.py")
    p.add_argument("--root", default=None, help="target bundle root (default: this repo)")
    p.add_argument("--registry", default=None,
                   help=f"pack registry index (default: <root>/{REGISTRY_REL})")
    p.add_argument("--apply", action="store_true",
                   help="merge the pack (default: report conflicts only)")
    return p.parse_args()


def extract_archive(archive):
    """Extract to a temp dir, rejecting absolute and parent-escaping paths."""
    tmp = tempfile.TemporaryDirectory(prefix="atlas-rulepack-")
    dest = Path(tmp.name)

    def check(name):
        if name.startswith("/") or ".." in Path(name).parts:
            sys.exit(f"ERROR: archive contains unsafe path {name!r}")

    if tarfile.is_tarfile(archive):
        with tarfile.open(archive, "r:*") as tar:
            for member in tar.getmembers():
                check(member.name)
            tar.extractall(dest)
    elif zipfile.is_zipfile(archive):
        with zipfile.ZipFile(archive) as zf:
            for name in zf.namelist():
                check(name)
            zf.extractall(dest)
    else:
        tmp.cleanup()
        sys.exit(f"ERROR: {archive} is not a tar or zip archive")
    return tmp


def find_pack_json(dest):
    dest = Path(dest)
    hits = sorted(dest.rglob("pack.json"))
    if not hits:
        sys.exit("ERROR: no pack.json in archive — not an Atlas rule pack")
    if len(hits) > 1:
        sys.exit("ERROR: archive holds more than one pack.json")
    return hits[0]


def load_pack(pack_json):
    pack = json.loads(pack_json.read_text(encoding="utf-8"))
    missing = [k for k in REQUIRED_KEYS if k not in pack]
    if missing:
        sys.exit(f"ERROR: pack.json is missing required keys: {', '.join(missing)}")
    if pack["schema"] != PACK_SCHEMA:
        sys.exit(f"ERROR: unsupported pack schema {pack['schema']!r} (expected {PACK_SCHEMA!r})")
    if not 0.0 <= float(pack["confidence"]) <= 1.0:
        sys.exit("ERROR: pack confidence must be between 0 and 1")
    return pack


def lesson_entries(text):
    """(topic, entry-text) for each lesson line outside code fences, checkboxes included."""
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
            body = re.sub(r"^\[[ xX]\]\s*", "", line[2:].strip())
            entries.append((topic, body))
    return entries


def normalize(entry_text):
    """Canonical form for conflict matching: drop trailing metadata, then slugify."""
    body = entry_text
    while TRAILING_META_RE.search(body):
        body = TRAILING_META_RE.sub("", body)
    return re.sub(r"[^a-z0-9]+", "", body.lower())


def entry_lesson(body):
    """Lesson body without its trailing (source: ..., approved: ...) metadata."""
    return TRAILING_META_RE.sub("", body).strip().rstrip(".")


def read_target_index(root):
    """normalized lesson -> human label, across both approval-queue files."""
    index = {}
    for rel in ("knowledge/reference/lessons.md", PROPOSED_REL):
        path = root / rel
        if not path.is_file():
            continue
        for topic, body in lesson_entries(path.read_text(encoding="utf-8")):
            key = normalize(body)
            if key:
                index.setdefault(key, f"{rel}: {topic or '(no topic)'}")
    return index


def load_registry(path):
    if path.is_file():
        registry = json.loads(path.read_text(encoding="utf-8"))
        if registry.get("schema") != REGISTRY_SCHEMA:
            sys.exit(f"ERROR: {path} has unsupported schema {registry.get('schema')!r}")
        return registry
    return {"schema": REGISTRY_SCHEMA,
            "description": "Rule packs already ingested into this project. "
                           "Index maintained by scripts/import-pack.py; duplicate "
                           "entries block re-ingestion of the same pack version.",
            "packs": []}


def plan(pack, pack_dir, root):
    """Classify every pack entry as new or conflicting against the target."""
    target_index = read_target_index(root)
    lessons_path = pack_dir / "lessons.md"
    new_lessons, seen, conflicts = [], set(), []
    if lessons_path.is_file():
        for topic, body in lesson_entries(lessons_path.read_text(encoding="utf-8")):
            key = normalize(body)
            if not key or key in seen:
                continue
            seen.add(key)
            if key in target_index:
                conflicts.append(("lesson", entry_lesson(body), target_index[key]))
            else:
                new_lessons.append((topic, entry_lesson(body)))

    def existing(kind, name, path):
        if path.exists():
            conflicts.append((kind, name, str(path.relative_to(root))))
            return False
        return True

    new_skills = [n for n in pack.get("skills", [])
                  if existing("skill", n, root / "skills" / n)]
    new_rules = [n for n in pack.get("rules", [])
                 if existing("rule", n, root / "rules" / f"{n}.md")]
    return new_lessons, new_skills, new_rules, conflicts


def collect_pack_files(pack, pack_dir):
    """Skill dirs and rule basenames declared by the pack, from its file list."""
    skills, rules = [], []
    for rel in pack.get("files", []):
        parts = Path(rel).parts
        if len(parts) == 3 and parts[0] == "skills" and parts[2] == "SKILL.md":
            if parts[1] not in skills:
                skills.append(parts[1])
        elif len(parts) == 2 and parts[0] == "rules" and parts[1].endswith(".md"):
            if parts[1][:-3] not in rules:
                rules.append(parts[1][:-3])
    # Fall back to the directory contents when the pack omits a file list.
    if not pack.get("files"):
        skills = [p.parent.name for p in sorted((pack_dir / "skills").glob("*/SKILL.md"))]
        rules = [p.stem for p in sorted((pack_dir / "rules").glob("*.md"))]
    return skills, rules


def merge(root, pack, pack_dir, new_lessons, new_skills, new_rules):
    """Write the pack into the target: review queue, skills, rules, registry."""
    today = date.today().isoformat()
    meta = (f"confidence {pack['confidence']}, last-validated {pack['lastValidated']}")

    if new_lessons:
        proposed_path = root / PROPOSED_REL
        lines = [f"- [ ] {body}. (role: imported-pack, "
                 f"rationale: from rule pack {pack['id']} ({meta}), "
                 f"source: rule pack {pack['id']}@{pack['packVersion']}, date: {today})"
                 for _, body in new_lessons]
        text = proposed_path.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        proposed_path.write_text(text + "\n".join(lines) + "\n", encoding="utf-8")

    for name in new_skills:
        src = pack_dir / "skills" / name / "SKILL.md"
        dst = root / "skills" / name / "SKILL.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)
    for name in new_rules:
        src = pack_dir / "rules" / f"{name}.md"
        dst = root / "rules" / f"{name}.md"
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, dst)

    # Register imported skills/rules in the manifest so integrity pinning covers them.
    manifest_path = root / "manifest.json"
    manifest = None
    if manifest_path.is_file():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        for key, names in (("skills", list(new_skills)),
                           ("rules", [f"{n}.md" for n in new_rules])):
            listed = manifest.get(key, [])
            for name in names:
                if name not in listed:
                    listed.append(name)
            manifest[key] = listed
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if manifest and (manifest.get("integrity") or {}).get("files"):
        result = subprocess.run(
            [sys.executable, str(root / "scripts" / "verify-integrity.py"), "--update"],
            capture_output=True, text=True)
        if result.returncode != 0:
            sys.exit("ERROR: re-pinning integrity hashes failed:\n" + result.stdout + result.stderr)
        print("Re-pinned manifest integrity hashes for the imported files.")


def report(args_apply, pack, lessons, skills, rules, conflicts, merged):
    state = "Apply" if args_apply else "Dry run"
    print("Atlas Rule Pack Import")
    print("=" * 60)
    print(f"Pack:     {pack['name']} @ {pack['packVersion']} ({pack['id']})")
    src = pack["sourceProject"]
    print(f"Source:   {src.get('name')} {src.get('version')} | "
          f"exported {pack.get('exportedAt')}")
    print(f"Meta:     tags: {', '.join(pack['domainTags']) or '(none)'} | "
          f"confidence {pack['confidence']} | last-validated {pack['lastValidated']}")
    print(f"Mode:     {state}")

    if lessons or skills or rules:
        print(f"\n1. Lessons: {len(lessons)} new"
              + (f" -> queued in {PROPOSED_REL} for approval" if merged and lessons else ""))
        for topic, body in lessons:
            print(f"   + [{topic or '(no topic)'}] {body[:100]}")
        print(f"2. Skills: {len(skills)} new"
              + (f" -> merged under skills/" if merged and skills else ""))
        for name in skills:
            print(f"   + skills/{name}/SKILL.md")
        print(f"3. Rules: {len(rules)} new"
              + (f" -> merged under rules/" if merged and rules else ""))
        for name in rules:
            print(f"   + rules/{name}.md")
    else:
        print("\nNo new entries: every pack lesson, skill, and rule already exists here.")

    if conflicts:
        print(f"\nConflicts ({len(conflicts)}) — kept as-is, not imported:")
        for kind, name, where in conflicts:
            print(f"   = {kind} {name!r} matches {where}")

    if not args_apply:
        print("\nDry run only. Re-run with --apply to merge.")


def main():
    args = parse_args()
    root = Path(args.root).resolve() if args.root else ROOT
    registry_path = Path(args.registry).resolve() if args.registry else root / REGISTRY_REL

    tmp = extract_archive(args.archive)
    try:
        pack_json = find_pack_json(tmp.name)
        pack = load_pack(pack_json)
        pack_dir = pack_json.parent

        registry = load_registry(registry_path)
        key = f"{pack['id']}@{pack['packVersion']}"
        if any(f"{e['id']}@{e['packVersion']}" == key for e in registry["packs"]):
            sys.exit(f"ERROR: pack {key} is already in {registry_path.name} — duplicate ingestion blocked")

        skills, rules = collect_pack_files(pack, pack_dir)
        pack["skills"], pack["rules"] = skills, rules
        new_lessons, new_skills, new_rules, conflicts = plan(pack, pack_dir, root)

        report(args.apply, pack, new_lessons, new_skills, new_rules, conflicts, merged=args.apply)
        if not args.apply:
            return 0

        merge(root, pack, pack_dir, new_lessons, new_skills, new_rules)
        registry["packs"].append({
            "id": pack["id"],
            "packVersion": pack["packVersion"],
            "name": pack["name"],
            "sourceProject": pack["sourceProject"],
            "importedAt": date.today().isoformat(),
            "domainTags": pack["domainTags"],
            "confidence": pack["confidence"],
            "lastValidated": pack["lastValidated"],
            "counts": {"lessons": len(new_lessons), "skills": len(new_skills),
                       "rules": len(new_rules), "conflicts": len(conflicts)},
            "loadInLite": False,
        })
        registry_path.parent.mkdir(parents=True, exist_ok=True)
        registry_path.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
        print(f"Recorded {key} in {registry_path.name}.")
        print("Lite mode: imported packs are never loaded in lite (token budget); "
              "only full-bundle knowledge/ sees them.")
        return 0
    finally:
        tmp.cleanup()


if __name__ == "__main__":
    sys.exit(main())
