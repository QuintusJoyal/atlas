---
name: rule-packs
category: process
load-when: Exporting this project's lessons to another repo, importing a team rule pack, federation across repositories
skip-when: Normal operation, single-project work
description: Cross-project knowledge federation. Export approved lessons, skills, and rules as a portable rule pack; import with conflict detection, registry dedup, and human review.
audience: [atlas-lead, atlas-docs]
tags: [knowledge, federation, rule-pack, sharing, import, export, lessons]
---

# Rule packs (cross-project knowledge federation)

Approved lessons, custom skills, and rules can be exported from one Atlas project as a portable rule pack and imported into another, so organizational learning compounds across repositories instead of being siloed per repo.

## Quick Reference

- Export: `python3 scripts/export-pack.py [--skills a,b] [--rules x,y] [--tags t1,t2] [--confidence 0.9]`
- Import: `python3 scripts/import-pack.py <pack.tar.gz>` reports; add `--apply` to merge.
- Imported lessons land in `knowledge/reference/proposed.md` for the normal approval flow — never straight into `lessons.md`.
- `knowledge/reference/pack-registry.json` records every ingested `id@version` so the same pack is never ingested twice.
- Lite mode never loads packs: import writes nothing under `lite/`, and lite reads no external `knowledge/` (see `lite/rules/atlas-core.md`), so the 4K–8K token budget is untouched.
- Importing under `--apply` re-pins `manifest.json` integrity hashes; commit the manifest with the merge.

## Pack format

A rule pack is a `.tar.gz` (or `.zip`) holding one directory:

```
<pack-id>-rulepack-<version>/
  pack.json                  metadata manifest
  lessons.md                 approved lessons, same format as knowledge/reference/lessons.md
  skills/<name>/SKILL.md     optional custom skills
  rules/<name>.md            optional rules
```

`pack.json` (schema `atlas-rulepack/1`) carries the metadata a receiver needs to judge the pack:

| Field | Meaning |
| --- | --- |
| `id`, `packVersion` | Pack identity; `id@version` is the registry dedup key |
| `sourceProject` | Project the pack was exported from (name and version) |
| `domainTags` | Domain labels for the content (export defaults them to lesson topics) |
| `confidence` | 0-1 score for how likely the content still applies |
| `lastValidated` | Last date the content was confirmed (defaults to the latest `approved:` date in the lessons) |
| `counts`, `files` | Entry counts and the exact file list |

## Export

`scripts/export-pack.py` bundles `knowledge/reference/lessons.md` plus any `--skills` and `--rules` you name, and writes `<project>-rulepack-<version>.tar.gz` under `dist/` (gitignored). Only approved lessons are exported — `proposed.md` is a queue, not a source, so unvetted drafts never leave the project.

## Import

`scripts/import-pack.py` is read-only until `--apply`:

1. **Validate** — schema, required metadata, and archive paths (no absolute or `..` entries).
2. **Dedup** — if the pack's `id@version` is already in the registry, import stops. That is the duplicate-ingestion guard.
3. **Conflict detection** — every pack lesson is normalized (trailing metadata stripped, lowercased) and matched against both `lessons.md` and `proposed.md`. Matching skills and rules (same name on disk) are also conflicts. Conflicts are reported and skipped, never overwritten.
4. **Review** — new lessons are appended to `proposed.md` as `- [ ]` items tagged `role: imported-pack` with the pack's confidence and last-validated date in the rationale. The user approves them in the usual batch; only then do they move to `lessons.md`. Skills and rules merge under `skills/` and `rules/` with `--apply` only, so they are reviewable in the same diff.
5. **Record** — the registry entry and re-pinned `manifest.json` integrity hashes are written with the merge.

An import with no `--apply` changes nothing on disk: run it first as a dry run and read the conflict report.

## Lite mode

Lite mode respects its token budget by loading no external knowledge at all, and imported packs stay inside that rule: import never writes under `lite/`, and registry entries are marked `loadInLite: false`. Teams that want pack lessons in lite should promote the few that matter into a lite source block (see `lite mode` blocks in `rules/`), not load the pack.

## Storage

- Pack registry index: `knowledge/reference/pack-registry.json` (`schema: atlas-rulepack-registry/1`), one entry per ingested pack with source project, domain tags, confidence, last-validated date, and merge counts.
- Environment override for the registry path: `scripts/import-pack.py --registry <path>`, for projects whose knowledge lives in `$ATLAS_KNOWLEDGE_DIR`.
