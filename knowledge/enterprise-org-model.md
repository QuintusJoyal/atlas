# Enterprise org model → Atlas mappings

How familiar enterprise governance patterns map to Atlas roles, gates, and workflows. Atlas is not a replacement for your CAB or SOC; it gives each line of defense a named agent, artifact, and gate.

## RACI at a glance

| Activity | Responsible | Accountable | Consulted | Informed |
| --- | --- | --- | --- | --- |
| Scope and backlog | atlas-pm, atlas-ba | User (product owner) | atlas-consultant, atlas-delivery | atlas-lead |
| Architecture and NFRs | atlas-architect, atlas-ent-arch | User (gate 2) | atlas-security, atlas-cloud | atlas-lead |
| Implementation | atlas-dev | atlas-lead (orchestration) | atlas-architect, atlas-ux | atlas-qa |
| Test and release evidence | atlas-qa, atlas-devops | User (gate 3) | atlas-reviewer | atlas-maintenance |
| Security assurance | atlas-security | User (gate 3) | atlas-compliance (if regulated) | atlas-lead |
| Production change | atlas-devops | User | atlas-security, atlas-maintenance | atlas-delivery |
| Cross-system strategy | atlas-ent-arch | User (gate 2 on infra) | atlas-cloud, atlas-network | atlas-lead |

**Accountable** for delivery outcomes stays with the user at each approval gate. atlas-lead is accountable for **orchestration fidelity** (correct delegation, manifest, gate sequencing), not for substituting specialist judgment.

## Three lines of defense

| Line | Enterprise role | Atlas mapping | Artifact / gate |
| --- | --- | --- | --- |
| **First** (operations) | Build, run, fix day to day | atlas-dev, atlas-devops, atlas-maintenance, atlas-qa | `implementation.md`, `deploy.md`, `test-plan.md` |
| **Second** (risk oversight) | Security, compliance, architecture review | atlas-security, atlas-compliance, atlas-reviewer, atlas-architect | `security.md`, `review.md`, design gate |
| **Third** (audit) | Independent assurance | User final gate + optional atlas-compliance for regulated scope | Gate 3 sign-off; audit workflows use `security-audit` preset |

Second line runs **before** production deploy on feature and infra workflows. It is not optional on those paths; hotfix uses a lightweight second line (below), not a skip.

## CAB and change gates

Change Advisory Board discipline maps to Atlas **approval gates** and workflow presets.

| CAB concept | Atlas equivalent |
| --- | --- |
| Standard change | `feature` workflow: requirements → design → final |
| Normal change with infra blast radius | `infra-change`: mandatory atlas-security; design + final gates |
| Emergency change | `bugfix` / `hotfix`: final gate only; expedited deploy with rollback |
| Pre-approval of cost/risk envelope | Token-budget gate when `Predicted: heavy` |
| Change record | Run folder `$ATLAS_DATA_DIR/runs/<id>/` with artifacts, `team.json`, `gates/`, `budget.md` |
| Implementation window | atlas-devops `deploy.md` with rollback and verify steps |

Gate sidecars and chat approval are the CAB packet queue: review artifact, approve or reject, comment stored in `gates/<gate>.json`.

## PDCA (Plan–Do–Check–Act)

| Phase | Atlas phase | Roles |
| --- | --- | --- |
| **Plan** | Kickoff + requirements + design | atlas-lead, atlas-pm, atlas-ba, atlas-architect, atlas-ux |
| **Do** | Build + test | atlas-dev, atlas-docs, atlas-qa |
| **Check** | Review + security | atlas-reviewer, atlas-security, atlas-compliance |
| **Act** | Deploy + handoff + retro | atlas-devops, atlas-maintenance, retro in `retro.md` |

Proposals from Act feed `proposed.md`, `ways-of-working.md`, and `usage-insights.md` for the next Plan cycle.

## Escalation

Matches charter escalation path:

1. **Peer resolution**: roles consult directly (architect ↔ security, dev ↔ qa).
2. **Requirements owners**: unresolved items consolidate through atlas-pm or atlas-ba; one question to the user.
3. **Conflict arbitration**: atlas-lead applies charter order (simplicity, evidence, security first).
4. **User decision**: options plus recommendation; no silent overrides.

atlas-lead surfaces kickoff and gate blockers in chat (missing estimates, unapproved gates, premium overuse). Non-waivable: security, compliance, reviewer, user gates, MCP writes.

## Hotfix: lightweight second line

Hotfix and bugfix workflows (`workflows/bugfix.md`) shorten the pipeline but **do not eliminate** second-line oversight when risk is present.

| Step | Hotfix behavior |
| --- | --- |
| Kickoff | Lite profile: shorter estimation huddle, minimal manifest fields |
| Security / compliance | **Conditional pass**: engage atlas-security (and atlas-compliance if regulated) when the defect touches auth, data handling, payments, or policy controls. If scope is purely cosmetic or isolated, document the rationale in `review.md` |
| Review | atlas-reviewer on the fix diff; mandatory when risk is high |
| Deploy | atlas-devops expedited with rollback ready |
| Gate | Final delivery only (no requirements/design gates) |

**Not skipped**: evidence of root cause, regression test, review clearance or explicit risk acceptance, rollback plan for production hotfix.

Second line on hotfix is **lightweight** (focused threat check and diff review), not **absent**.

## Enterprise specialists (on demand)

Engage when domain requires; see `ROLES.md` and lead playbook enterprise section:

- Network, sysinfra, cloud, dba, data-eng, data-sci, ai-eng, data-analyst, ent-arch, delivery, consultant, compliance.

## References

- `rules/team-charter.mdc`
- `workflows/feature.md`, `workflows/bugfix.md`, `workflows/infra-change.md`
- `skills/atlas-lead-playbook/SKILL.md`
- `knowledge/collaboration.md`
