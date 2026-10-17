---
name: artifact-governance
description: Agentic data governance for runtime artifacts (PII detection, redaction, retention). Load when handling trajectories, checkpoints, handoffs, tool inputs/outputs, or run artifacts.
load: on-demand
globs: "knowledge/process/**/*.md,rules/**/*.md,*.md"
---

# Artifact governance (runtime)

Applies to Atlas runtime artifacts, not user application data. Enforce governance at boundaries before persistence and before propagation.

## Scope
- Context loads: grep results, tool inputs/outputs, retrieved docs, tickets, snippets.
- Trajectory logs: `trajectory.jsonl` under `$ATLAS_DATA_DIR/runs/<run-id>/`.
- Checkpoints: checkpoint payloads under `$ATLAS_DATA_DIR/runs/<run-id>/` or `$ATLAS_DATA_DIR/checkpoints/`.
- Handoffs/delegation briefs, team.json, run artifacts under `$ATLAS_DATA_DIR/runs/<run-id>/`.
- OTel spans (when recorded): PII must not be written into span attributes/log bodies before persistence/export.

## Classification (artifact classes)
- Classify artifact fields by sensitivity: Public, Internal, Confidential, Restricted.
- PII/PHI/credentials/secrets are Restricted by default. Tokens, emails, names, phone, addresses, IDs, API keys, PEM, tokens in URLs/headers are sensitive.
- Tool outputs inherit classification from their source; reclassify if they merge sources.

## PII detection
- Use layered detection: regexes (email, phone, SSN-like, credit card patterns, IPs, UUIDs, AWS/GCP/Azure keys, auth tokens, private key blocks) plus NER conceptually.
- Assign severity tiers (low/med/high) per match; tie to redaction policy.
- Detection is required at context-load boundary. Lite-mode: redaction-only subset is acceptable (see Lite mode).

## Data-minimization (scoping)
- Scope by role: each role may load only the subset of fields needed for its contract (principle of least privilege).
- Before grep/load: filter result sets to minimal scope (files, regions, fields). Do not bulk-import entire repos/logs when a slice suffices.
- Strip or avoid inheriting unneeded sensitive context. See inheritance policy below.
- Avoid expanding context breadth to compensate for missing specificity; prefer targeted reads.

## Redaction policy
- Redact Restricted/sensitive values before persistence or propagation: replace with typed placeholders (e.g., `[REDACTED_EMAIL]`, `[REDACTED_KEY]`, `[REDACTED_TOKEN]`, `[REDACTED_PII]`).
- Apply redaction at these boundaries (pre-persistence):
  - Tool hooks pre/post: redact `toolInput` and `toolOutput` summaries before writing trajectory entries.
  - Checkpoint creation: redact sensitive fields in checkpoint context, artifacts, and metadata.
  - Delegation briefs: strip sensitive payloads; pass references/minimal summaries.
  - Handoff persistence: redact artifacts written under `$ATLAS_DATA_DIR/runs/<run-id>/`.
  - Trajectory append: never log raw secrets; log categories and placeholders.
- Preserve structure needed for debugging (type/category) without exposing values.

## Subagent context inheritance
- Do not inherit full parent context by default. Pass a scoped brief (task, constraints, minimal artifacts, required contracts only).
- Explicit allowlist: only fields/paths the child role needs per contract. Parent redacts before passing.
- No cross-boundary propagation of unneeded PII. Children must not request broad dumps to "be safe".
- Delegation entries record policy decision (scoped vs full) in action trail.

## Retention policies (per artifact class)
- Apply retention to `$ATLAS_DATA_DIR/runs/<run-id>/` and related artifacts. Backups follow same policy.
- Trajectory logs: retain for 30 days by default; deep runs may keep 90 days if justified; expired = auto-delete.
- Checkpoints: lightweight < 7 days, standard < 30 days, deep checkpoints tied to active runs; auto-delete expired per class.
- Handoffs/artifacts (run workspace): retain per phase; completed runs purge per classification (Public/Internal longer, Restricted shortest consistent with need).
- OTel spans (if present): per environment policy; redact before export; expiry aligned with trajectory.
- Automated expiry required where feasible; manual only when automation blocked (document blocker).

## Audit trail
- Record PII detection events: what detected (type/severity), where (boundary/file), action (redact/block/allow with justification), policy version, and issue reference.
- Log decisions in trajectory entries (`why`/metadata) without exposing values. Maintain auditable trail of governance decisions.
- Lite-mode: still record minimal audit markers when redaction occurs.

## Lite mode
- Lite-mode subset = redaction only (no full policy engine). Focus on deterministic redaction at append/persist boundaries.
- Detection may be regex-only in lite; still prefer typed placeholders and avoid logging secrets.
- Compatible with lite build blocks; see `scripts/build-lite.py` marker system.

## References
- `knowledge/process/trajectory-logging.md`, `knowledge/process/checkpoint-protocol.md`, `rules/handoff-protocol.md`, `rules/data-governance.md`, `k/gdpr-requirements.md`.
