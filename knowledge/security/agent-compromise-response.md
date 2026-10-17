---
name: agent-compromise-response
category: security
load-when: Confirmed or strongly suspected agent compromise, poisoned memory/lessons, exposed role credentials, user asks to quarantine a role
skip-when: Preventive security review, routine audits, unconfirmed anomalies (triage first, see knowledge/delivery/incident-response.md)
description: Containment playbook for confirmed agent compromise: quarantine the role, revoke scoped credentials, export forensics, roll back artifacts, purge poisoned memory, downgrade trust, and produce a post-incident report.
audience: [atlas-security, atlas-lead]
tags: [incident-response, compromise, quarantine, forensics, containment, rollback, drill]
---

# Agent compromise response

Prevention lives in `rules/security.md` and failure recovery in `knowledge/process/checkpoint-protocol.md`. This playbook covers the third case: a compromise is **confirmed** and the agent that did it is still live. NIST and OWASP agentic guidance converge on the same core moves — isolate, preserve evidence, rotate credentials, recover from a trusted point — in that order.

## Quick Reference

- Order matters: **quarantine → revoke → export → rollback → purge → report.** Export before anything is destroyed; rollback before anything is rewritten.
- Confirm before containing: a false-positive purge destroys legitimate lessons and artifacts. Checkpoint and export first, containment second.
- Incident record: `$ATLAS_DATA_DIR/incidents/inc-<YYYYMMDD>-<slug>/` holds the export, hashes, purge list, and report.
- Trust downgrade is immediate on confirmation: compromised role → UNTRUSTED (`knowledge/process/role-trust-profiles.md`).
- Enforcement that protects the rest of the bundle lives outside the compromised role's context. See [Enforcement boundary](#enforcement-boundary).
- Drill the playbook with a simulated compromise (see [Red-team drill](#red-team-drill)).

## Confirm before containing

Containment is destructive, so confirmation comes first:

1. **Signal:** anomalous writes outside the role's owned artifacts, lessons/memories it authored that it cannot justify, out-of-scope tool use in its trajectory log, credential use it does not claim, or a direct report from another role or the user.
2. **Confirmation:** atlas-security traces the signal to a specific action in the trajectory log (`knowledge/process/trajectory-logging.md`) and the user authorizes containment. The compromised role is never asked to confirm its own compromise.
3. **Record T0:** the confirmation timestamp. Every export, purge, and rollback decision is scoped relative to T0 and to the last trusted checkpoint.

Suspected but unconfirmed → keep monitoring, do not purge. Unconfirmed anomalies are ordinary triage, not an incident.

## Step 1: Quarantine

- **Suspend the role.** atlas-lead stops delegating to it. In-flight phases it owns move to `paused`, then `aborted` or re-delegated to a role that is not implicated. No new briefs, no gate approvals, no handoffs accepted from it.
- **Isolate its scope.** Tighten its tool scope to nothing beyond read-only evidence gathering it will no longer be doing — drop Write/Edit/Bash/Task and MCP servers from any brief that names it, per `knowledge/process/role-tool-scoping.md`. Isolation is applied by the orchestrator in the delegation brief and by the harness's tool permissions, not by the role agreeing to stop.
- **Revoke scoped credentials.** Rotate every MCP server key, API token, and secret the role could reach — env vars, secrets manager entries, CI tokens — starting with anything used after T0. Rotation is performed by the user or the harness *outside* the role's context; the role's own file access cannot be trusted to perform it.
- **Announce.** One line to the user: role quarantined at T0, scope isolated, credentials rotating, forensics export starting.

## Step 2: Forensics export

Evidence first. Nothing is deleted, restored, or rewritten until the export exists and its hash is recorded.

- **Action log:** copy the run's append-only `trajectory.jsonl` (schema: `knowledge/process/trajectory-logging.md`) into the incident directory. Copy, never move or edit — the original stays append-only.
- **Context snapshot:** the compromised role's current context at containment time — agent file, skill playbook, delegation briefs it received, the checkpoint closest to T0, and every memory/lesson/knowledge entry it authored since the last trusted checkpoint.
- **Knowledge snapshot:** copy of the shared knowledge state it could write to (`knowledge/reference/lessons.md` and the run's memory files) at T0, so a purge can later be verified as scoped.
- **Hash everything.** SHA-256 per file into `SHA256SUMS`; the report cites these hashes.

```text
$ATLAS_DATA_DIR/incidents/inc-20260803-agent-poisoning/
  SHA256SUMS
  trajectory.jsonl          # immutable copy of the action log
  context/                  # agent, skill, briefs, checkpoint near T0
  knowledge/                 # lessons/memory snapshot at T0
  timeline.md               # detection → quarantine → export, with T0
```

## Step 3: Artifact rollback

Roll the workspace back to the last trusted checkpoint using the Atlas Checkpoint Protocol (`knowledge/process/checkpoint-protocol.md`):

1. **Find the last trusted checkpoint** — created before T0 by a role that is not implicated. If none exists, stop: there is no trusted point, escalate to the user rather than guessing.
2. **Validate it** (ACP checkpoint validation): file exists, JSON parses, referenced artifacts exist, trajectory references are consistent.
3. **Restore** with fork level 3 (resume). Use fork level 2 (branch) instead when the checkpoint's own artifacts may be tainted — branch from it, diff against the export, and let the user pick what survives.
4. **Record** the checkpoint id and fork level used in the incident directory.

Rollback restores artifacts, not memory: purge (Step 4) is a separate, separately verified action.

## Step 4: Memory/knowledge purge

Clear what the compromised role poisoned, and nothing else:

- **Scope:** entries the compromised role authored after the last trusted checkpoint and through T0 — lessons proposed to `knowledge/reference/lessons.md`, memory files, knowledge stubs, and any gate/checkpoint files it wrote. Entries from other roles and pre-checkpoint entries are untouched.
- **Precondition:** the Step 2 snapshot exists and its hashes verify. If the export is missing or corrupt, re-export before purging — never purge on an unverified snapshot.
- **Purge list:** write `purge-manifest.md` in the incident directory first (path, author, timestamp, reason per entry), then remove the entries. The record of what was deleted is never itself deleted.
- **Verify:** after purge, re-scan for entries authored by the quarantined role in the incident window. Zero remaining is the pass condition.

## Step 5: Trust downgrade and security gate

- **Trust profile:** on confirmation, force `trustScore` → 0.0, `tier` → UNTRUSTED, `driftAlerts` + 1, and record the incident id — independent of the ARTS formula, per `knowledge/process/role-trust-profiles.md`. The role is not delegated to again until the user restores it.
- **atlas-security gate:** containment is a blocking finding. No deploy or merge gate that touches the compromised role's artifacts passes until the containment Definition of Done below is met; atlas-security renders the verdict and verifies the forensics hash, rollback checkpoint, and purge scope itself rather than trusting the report.
- **Re-entry criteria:** post-incident report accepted by the user, trust profile reset explicitly by the user, credentials rotated, and a clean drill or review of the restored role. Restoration is a user decision, never automatic decay.

### Containment Definition of Done

- [ ] Role quarantined at a recorded T0, scope isolated, in-flight work reassigned
- [ ] Credentials rotated outside the role's context
- [ ] Forensics export complete with `SHA256SUMS` recorded
- [ ] Artifacts rolled back to a validated trusted checkpoint
- [ ] Purge scoped to the compromised role's post-checkpoint entries; purge-manifest written; rescan clean
- [ ] Trust profile forced to UNTRUSTED with the incident id
- [ ] Post-incident report delivered

## Step 6: Post-incident report

```markdown
# Post-incident report: <incident-id>

- **Incident:** inc-YYYYMMDD-<slug>   **Role:** <quarantined-role>
- **Detected:** <ts>   **T0 (confirmed):** <ts>   **Contained:** <ts>
- **Drill:** no (set `yes` for a simulated compromise)

## Root cause
<5 Whys or equivalent — how the role was compromised: injection vector, poisoned
input, tool misuse. Systems and process, not blame.>

## Blast radius
- Files touched by the role after the last trusted checkpoint: <list>
- Credentials it could reach: <list, all rotated: yes/no>
- Memory/lessons written: <list; purged: <list>  benign, kept: <list>>
- Data or code exfiltration indicators: <findings or none>

## Timeline
| Time | Event |
| ---- | ----- |
| <ts> | first signal |
| <T0> | confirmed, quarantine started |
| <ts> | forensics export + hashes |
| <ts> | rollback to <checkpoint-id> |
| <ts> | purge complete, rescan clean |
| <ts> | trust downgrade, containment DoD met |

## Response actions taken
- Quarantine / isolation / credential rotation: <what, by whom>
- Rollback: <checkpoint-id>, fork level, validation result
- Purge: <n> entries, verified against purge-manifest.md
- Trust: <role> → UNTRUSTED, incident id recorded

## Evidence
- `incidents/<incident-id>/SHA256SUMS` (trajectory copy, context, knowledge snapshot)

## Lessons promoted
- <lesson text → knowledge/reference/lessons.md, or "none">

## Follow-ups
- [ ] <owner, due date — prevention gap, scoping change, new rule>
```

Promote at most a few high-value lessons to `knowledge/reference/lessons.md`; the report keeps the full detail. A blameless report is mandatory: what happened and why the controls missed it, never who to blame.

## Red-team drill

The playbook is untested until it has run end to end against a simulated compromise. Drill after any change to this file and at least once per quarter.

1. **Sandbox.** Use a throwaway run under `$ATLAS_DATA_DIR` (or a copy of it). Never drill against live incident records or a real run's checkpoints.
2. **Inject.** Mark one non-critical role as compromised for the drill: it writes a marker "poisoned" lesson to the run's memory, touches one artifact outside its scope, and records ordinary trajectory entries. The injection is declared up front — no role is actually compromised.
3. **Execute steps 1–6 for real.** Confirm (against the marker), quarantine the role, rotate the sandbox credentials, export forensics, roll back to the last trusted checkpoint, purge the marker entries, downgrade trust, and write the report with `Drill: yes`.
4. **Score against the drill checklist:**
   - [ ] Quarantine reached every phase the role was running in; no new briefs to it
   - [ ] Export hash verifies; original trajectory unmodified (diff against copy)
   - [ ] Rollback validated and restored the tampered artifact
   - [ ] Purge removed exactly the marker entries — nothing written by other roles
   - [ ] Trust profile shows UNTRUSTED with the drill id
   - [ ] Report complete, including lessons promoted
   - [ ] Containment Definition of Done satisfied without human improvisation
5. **Failures are the output.** A step that required guessing gets a follow-up in the report and a fix to this playbook before the next drill. A runbook that does not work in a drill is worse than no runbook.

## Enforcement boundary

This playbook is advisory text inside the bundle. A compromised role can ignore instructions about its own containment, so the controls that protect everything else must not live in the role's context:

- **Credential rotation** is performed by the user or the harness, out-of-band.
- **Tool scope isolation** is enforced in the delegation brief and the harness's tool permissions (`knowledge/process/role-tool-scoping.md`), not by the role self-restricting.
- **Log integrity** comes from an append-only trajectory log plus an out-of-band copy at T0; the role's writes to its own history are evidence, not authority.
- **Quarantine** is the orchestrator refusing to delegate, which a role cannot override.

If the orchestrator or the user cannot perform these steps (single-role, unattended session), the correct action is to stop and escalate to the user, not to improvise containment from inside the compromised context.

## See Also

- `knowledge/process/checkpoint-protocol.md` — rollback, validation, fork levels
- `knowledge/process/trajectory-logging.md` — append-only action log schema
- `knowledge/process/role-tool-scoping.md` — phase-aware scope isolation
- `knowledge/process/role-trust-profiles.md` — trust tiers and forced downgrade
- `knowledge/delivery/incident-response.md` — general incident response, postmortems, blameless culture
- `knowledge/security/nist-800-53-controls.md` — IR and containment control references
