---
name: deterministic-guardrails
category: security
load-when: Wiring tool permissions, audit logging, injection scanning, MCP credentials, or compliance evidence in a host runtime
skip-when: Prompt-level security guidance only, no runtime enforcement needed
description: Runtime enforcement layer for Atlas security controls. Tool permission policy engine, prompt injection scanner, scoped MCP credential vault, hash-chained audit trail, and compliance report generator. Implemented in scripts/guardrails.py with declarative guardrails/policy.yaml.
audience: [all]
tags: [security, guardrails, permissions, audit, injection, mcp, compliance, runtime]
---

# Deterministic guardrails

Atlas security knowledge (OWASP, STRIDE, NIST 800-53) and the `atlas-security` gate are advisory: they are enforced by instruction-following. This engine makes the same controls enforceable as runtime code. A tool call is allowed or denied by evaluating a declarative policy, not by asking the agent to police itself.

## Quick Reference
- Engine: `scripts/guardrails.py` (Python 3.12, stdlib only)
- Policy: `guardrails/policy.yaml` (or JSON with the same shape)
- Pre-invocation check: `guardrails.py check` before every tool executes
- Injection scan: `guardrails.py scan` on agent output before it reaches external tools
- Credential vault: role/phase/tool scoping with revocation at phase boundaries
- Audit: append-only JSONL with a SHA-256 hash chain; `audit verify` detects tampering
- Report: `guardrails.py report` emits a per-run SOC2 / ISO 27001 evidence attestation

## 1. Tool permission policy engine

`guardrails/policy.yaml` maps roles and phases to allowed tools, argument rules, and filesystem scopes. The engine evaluates it as data.

| Section | Controls |
|---------|----------|
| `phases` | Phase x tool matrix, mirroring `knowledge/process/role-tool-scoping.md` (`allow`, `deny`, `readonly`) |
| `roles` | Permanent overrides: `deny` always wins, `allow` overrides a phase denial, `only` is a strict allowlist |
| `pathPolicy` | Allowed roots and denied globs (`.git/**`, `.env`, keys, `secrets/**`) for path-bearing tools |
| `shellReadonly` | Command allowlist used when a phase grants `bash: readonly` |
| `mcp` | Write indicators that force approval for MCP calls |

Unknown roles, phases, or tools fall back to `defaultDecision: deny`.

## 2. Pre-invocation hook

The host runtime routes every tool call through `check` before execution:

```sh
python3 scripts/guardrails.py check --role atlas-dev --phase implementation \
  --tool write --args '{"file_path": "src/app.py"}'
```

Exit `0` prints `{"decision": "allow", ...}`. Exit `1` prints an ACI structured error per `knowledge/process/aci-enforcement.md`:

```json
{"error": true, "errorCategory": "permission", "recoverable": false,
 "message": "role 'atlas-lead' may never use 'edit'",
 "suggestedAction": "Delegate to a role permitted to use 'edit' (escalate T2 if needed).",
 "context": {"role": "atlas-lead", "tool": "edit"}}
```

Every decision is written to the audit trail before the result is returned. The `tool.check` event is the same point `knowledge/process/trajectory-logging.md` calls the pre-action hook.

## 3. Prompt injection detection

`scan` runs regex patterns plus a Shannon-entropy check for encoded payloads on text before it is passed to an external tool or API:

```sh
python3 scripts/guardrails.py scan --text "$AGENT_OUTPUT"
```

Patterns cover instruction override, system-prompt exfiltration, role override, policy bypass, secrecy, exfiltration to URLs or addresses, shell injection, and encoded payloads (`base64`, `eval`). High-entropy tokens over the configured threshold are flagged as possible encoded payloads. Verdict `flagged` exits `1` and is recorded for the report. Tune `injection.minEntropy`, `minTokenLength`, and `patterns` in the policy to trade false positives against coverage.

## 4. MCP credential vault

Credentials are scoped to roles, phases, and tools; a caller only receives one whose scope matches. Values never appear in arguments or logs.

```sh
printf '%s' "$TOKEN" | python3 scripts/guardrails.py vault add --id github_token \
  --role atlas-dev --phase implementation
python3 scripts/guardrails.py vault get --id github_token --role atlas-dev --phase implementation
python3 scripts/guardrails.py vault revoke-phase --phase implementation
```

`revoke-phase` revokes at every phase boundary, so a credential granted for implementation is dead before review starts. The vault file is written `0600` under `$ATLAS_DATA_DIR/guardrails/`.

## 5. Immutable audit trail

Every check, scan, and vault action appends one JSONL line to `$ATLAS_DATA_DIR/runs/<run-id>/guardrails.jsonl`. Each event carries `seq`, `ts`, agent context, the decision, and a SHA-256 hash chained over the previous event:

```sh
python3 scripts/guardrails.py audit verify
```

`verify` recomputes the chain and fails (exit `1`) on a missing link or a modified event, so an edited or backfilled record is detectable. The event log is the runtime counterpart to the trajectory log.

## 6. Compliance report generator

`report` summarizes the audit trail into a per-run attestation, in markdown or JSON, suitable for a SOC2 / ISO 27001 evidence package:

```sh
python3 scripts/guardrails.py report --format md --out security-attestation.md
```

It reports the chain status, decision counts, checks by role and tool, policy violations, injection flags, and a control mapping to A01/A09/A03/A02 and their NIST families. It exits `1` if the chain is broken, so a tampered run cannot produce a clean attestation.

## Relationship to advisory controls

This engine enforces; the knowledge files still explain. `rules/security.md` and `knowledge/process/role-tool-scoping.md` define intent, `knowledge/process/aci-enforcement.md` defines the error contract, and `knowledge/ai/owasp-llm-top-10.md` names the threats (LLM01 prompt injection, LLM06 insecure plugin design, LLM08 excessive agency). Wire the engine into the host so the controls hold without relying on the agent to comply.
