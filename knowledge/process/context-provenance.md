---
name: context-provenance
category: process
load-when: Delegating across agent chains, debugging a suspected distorted handoff, compliance audit of a decision
skip-when: Single-role tasks, light small-variant handoffs without cross-agent context reuse
description: Signed context fragments with parent-hash attestation chains so every context element traces back to its source agent.
audience: [atlas-lead, all]
tags: [provenance, attestation, handoff, integrity, audit, jsonl]
---

# Context provenance

When context passes through multiple roles (lead → dev → reviewer), each hop can introduce subtle distortions ("hallucination-in-the-chain"). Provenance records make every context fragment attributable: each agent signs the fragments it emits, links them to their parent fragment with a hash, and every verification is logged. `scripts/provenance.py` implements this; agents shell out to it (LLMs cannot sign natively).

## Quick Reference
- Fragment schema: `source_agent`, `timestamp`, `content_hash`, `parent_hash`, `signature`
- Per-agent HMAC-SHA256 keys at `$ATLAS_DATA_DIR/keys/<agent>.key` (mode 0600)
- Parent linkage (`parent_hash`) forms an attestation chain back to the fragment's origin
- Audit log: append-only JSONL at `$ATLAS_DATA_DIR/provenance.jsonl`
- Broken chains are flagged and quarantined to `$ATLAS_DATA_DIR/quarantine/`
- **Signatures attest who emitted a fragment, not that it is true** — a compromised agent can re-sign distorted content. This is an attribution and debugging aid, not a truth proof.

## Fragment schema

```json
{
  "schema": "atlas-provenance/1",
  "source_agent": "atlas-dev",
  "run_id": "run-20260711-central-data-home",
  "timestamp": "2026-07-11T14:30:00Z",
  "content_hash": "e3b0c442…",
  "parent_hash": "9f86d081…",
  "signature": "1b2c…",
  "key_id": "atlas-dev"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `source_agent` | yes | Role that produced the fragment (must have a key in `$ATLAS_DATA_DIR/keys/`) |
| `timestamp` | yes | ISO 8601 UTC time of signing |
| `content_hash` | yes | SHA-256 of the exact content bytes handed off |
| `parent_hash` | no | `content_hash` of the fragment this one derives from; `null` for origin fragments |
| `signature` | yes | HMAC-SHA256 over `source_agent`, `run_id`, `timestamp`, `content_hash`, `parent_hash` |
| `run_id` | recommended | Run the fragment belongs to (enables `trace --run`) |

## Protocol

### 1. Key setup (once per machine)
```
python3 scripts/provenance.py init-key --agent atlas-dev
```
Creates `$ATLAS_DATA_DIR/keys/<agent>.key` (32 random bytes, hex, mode 0600). Never commit keys; they live only under `$ATLAS_DATA_DIR`.

### 2. Sign before handoff
```
python3 scripts/provenance.py sign --agent atlas-dev --file design.md \
    --parent <content_hash-of-input-fragment> --run <run-id> --out design.provenance.json
```
Signing appends a `sign` record (fragment included) to `provenance.jsonl`. The emitted fragment JSON travels with the handoff artifact.

### 3. Verify at reception
```
python3 scripts/provenance.py verify --fragment design.provenance.json --content design.md
```
The receiving agent runs this **before incorporating the context**. It checks three things:
- **hash** — `content_hash` matches the content actually received
- **signature** — the HMAC matches the sender's key
- **chain** — `parent_hash` resolves to a previously signed fragment in the audit log

Any failure quarantines the fragment to `$ATLAS_DATA_DIR/quarantine/`, logs a `verify` record with `status: quarantined`, and exits 1. **Quarantined context must not be used**; re-request it from the sender or escalate to atlas-lead.

### 4. Distortion detection (compaction / summarization)
```
python3 scripts/provenance.py check-distortion --original design.md --compacted design-summary.md
```
Compaction legitimately changes content, so a raw hash mismatch is expected — severity is assigned by content similarity (`difflib` ratio): ≥0.9 `low`, ≥0.5 `medium`, below that `high`. Result is logged to `provenance.jsonl` as a `distortion` record. `high` severity on decision-bearing context warrants re-deriving from the original rather than trusting the summary.

### 5. Trace (dashboard query)
```
python3 scripts/provenance.py trace --fragment <content_hash>   # walk chain to origin
python3 scripts/provenance.py trace --run <run-id>              # all fragments in a run
```
Given any decision in a run output that cites a fragment hash, `trace` walks `parent_hash` links back through every contributing fragment, printing source agent, timestamp, chain position, and latest verification status — answering "which agents' context influenced this decision, and was any link in the chain ever flagged?"

## Design note: HMAC keys vs asymmetric key pairs

The issue's signing criterion calls for per-agent key pairs; this implementation uses per-agent **HMAC-SHA256 secret keys** because Atlas scripts are Python-stdlib-only (no `cryptography`/`nacl` dependency), and the stdlib ships no asymmetric primitive. The practical consequence: verification must be able to read the sender's key file, so any process with access to `$ATLAS_DATA_DIR/keys/` can forge a signature for any agent. Within Atlas's single-machine, same-data-dir threat model this is equivalent; if fragment verification ever crosses machine boundaries, swap the HMAC in `scripts/provenance.py` for an ed25519 implementation — the fragment schema (`signature`, `key_id`) already accommodates that change.

## Audit log

Append-only JSONL at `$ATLAS_DATA_DIR/provenance.jsonl`; never rewrite existing lines (same rule as `trajectory.jsonl`). Record types: `sign` (full fragment), `verify` (checks + status), `quarantine` (via verify), `distortion` (severity + similarity). The log is the chain's ground truth: chain verification resolves `parent_hash` against `sign` records in this file.

## Handoff integration

Provenance is **additive** — handoff artifacts keep their 8 sections (4 in small variant) unchanged. Append one block at the end so existing consumers are unaffected:

```markdown
## Provenance
- Fragment: design.provenance.json (content_hash e3b0c442…)
- Parent: 9f86d081… (atlas-pm requirements fragment)
- Verify: python3 scripts/provenance.py verify --fragment design.provenance.json --content design.md
```

See `rules/handoff-protocol.md` (Context provenance section), `knowledge/process/trajectory-logging.md` (`provenanceHash` field links a trajectory decision to its fragment), and `knowledge/process/aci-enforcement.md` (tool provenance complements content provenance).
