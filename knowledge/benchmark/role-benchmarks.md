---
name: role-benchmarks
category: benchmark
load-when: Monthly self-assessment, calibrating role trust, measuring role quality across runs
skip-when: Normal operation, simple tasks, in-progress work
description: Role-level benchmark suites — 5-10 test cases per role category for consistent quality measurement across runs. Feeds pass^k gates and role trust profiles.
audience: [atlas-lead, atlas-ai-eng, atlas-ent-arch]
tags: [benchmark, roles, evaluation, pass-k, quality, self-assessment]
---

# Role benchmarks

A small, fixed suite of test cases per role category, so the same role is scored the same way across runs. Results feed the pass^k gate system (`workflows/README.md`), decision quality scoring (`knowledge/process/decision-quality-scoring.md`), and role trust profiles (`knowledge/process/role-trust-profiles.md`).

## Quick Reference
- 9 role categories covering all 24 roles (23 specialists + atlas-lead)
- 5-10 cases per category; each case is a prompt sketch plus pass criterion
- Each case is rated pass/fail against its criterion; the category score is the pass rate
- Default k per category: **k=2** for standard work, **k=3** for security, network, and compliance
- Like the rest of this bundle, a benchmark verdict is the agent's own judgment against these criteria unless the user supplies an external harness — state that caveat when reporting numbers

## How a benchmark run works

1. Pick the category for the role under test.
2. Run each case in a **fresh context** (no carry-over from the case before it).
3. Score each case pass/fail against its criterion. Record the failure signal when it fires.
4. `category_score = passing_cases / total_cases` (0.0-1.0).
5. A category passes a pass^k gate only when **every** case passes in **all k** runs.
6. Append results to `usage-insights.md`; feed failures into `knowledge/process/failure-mode-taxonomy.md` for pattern detection.

## Categories

### Orchestration — atlas-lead

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| ORC-1 | Route a mixed requirements + implementation request | Delegates to atlas-pm then atlas-dev; does not implement inline | Writes code itself |
| ORC-2 | Delegation naming check | Every `description` starts with `atlas-<role>:` and matches `role` | Generic or unnamed agent |
| ORC-3 | Parallel design phase (architect + UX) | Both delegated in one turn; gate waits for both | Serializes without reason |
| ORC-4 | Delegated agent fails once | Re-delegates same role on next tier in the same turn | Stops or takes over the work |
| ORC-5 | Scope change mid-run | Pauses phase, re-evaluates, presents options | Continues on stale scope |

### Requirements & analysis — atlas-pm, atlas-ba

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| REQ-1 | Draft stories for a feature | Each story has acceptance criteria and is testable | Vague, untestable stories |
| REQ-2 | Map edge cases for a refund flow | Finds partial refunds, currency, idempotency | Happy path only |
| REQ-3 | Ambiguous request ("make it faster") | Asks a clarifying question before proceeding | Guesses silently |
| REQ-4 | Out-of-scope request to atlas-ba | Defers design/implementation to owning role | Produces a design |
| REQ-5 | Non-functional requirements | Captures load, latency, security constraints | Omits NFRs |

### Design & architecture — atlas-architect, atlas-ux, atlas-ent-arch

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| DES-1 | Design a notifications service | Records an ADR with trade-offs and rejected options | Single option, no trade-offs |
| DES-2 | Onboarding flow UX | Accessibility and error states covered | Screens only, no edge states |
| DES-3 | Cross-system integration | Maps capability boundaries and coupling | Ignores enterprise constraints |
| DES-4 | Non-functional trade-off | Explicitly weighs simplicity vs scale | Over-engineers without need |
| DES-5 | Out-of-scope request to architect | Defers implementation details to atlas-dev | Writes production code |

### Implementation — atlas-dev

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| IMP-1 | Implement an endpoint against a plan | Follows the plan; changes stay in scope | Invents unrelated features |
| IMP-2 | Edit an existing file | Reads the file before editing | Blind edit from memory |
| IMP-3 | Bug fix | Adds or updates a regression test | Fix with no test |
| IMP-4 | Ambiguous interface | Surfaces the ambiguity rather than guessing | Silent assumption |
| IMP-5 | Security-relevant change | Flags the security path for atlas-security | Ships without flagging |

### Quality & verification — atlas-qa, atlas-reviewer

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| QUA-1 | Test plan for a feature | Covers acceptance criteria and edge cases | Happy path only |
| QUA-2 | Written tests | Assert observable behavior, not implementation | `mock.verify()`-style tests |
| QUA-3 | Review a diff | Finds a seeded defect | Rubber-stamps the change |
| QUA-4 | Charter conformance | Checks against the project charter | Ignores conventions |
| QUA-5 | Out-of-scope request to reviewer | Defers fixes to atlas-dev | Rewrites the code |

### Security, network & compliance — atlas-security, atlas-network, atlas-compliance

Default k: **3** (highest stakes)

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| SEC-1 | Audit an auth module | Maps findings to OWASP/STRIDE | Generic advice |
| SEC-2 | Secrets scan | Flags a seeded secret | Misses the secret |
| SEC-3 | VPC segmentation review | Identifies the over-permissive path | Approves as-is |
| SEC-4 | Data retention policy | Maps gaps to GDPR/SOC 2/ISO | No framework mapping |
| SEC-5 | Deploy gate decision | Blocks on a real high-severity finding | Passes despite the finding |

### Delivery & operations — atlas-devops, atlas-maintenance, atlas-sysinfra, atlas-cloud, atlas-dba, atlas-docs

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| OPS-1 | Deploy pipeline | Includes rollback path | No rollback |
| OPS-2 | Debug a latency regression | Follows evidence to root cause | Guesses from symptoms |
| OPS-3 | Harden a host | Applies baseline, documents changes | Ad-hoc hardening |
| OPS-4 | Slow query tuning | Proposes an index with trade-offs | Add index blindly |
| OPS-5 | Runbook for a service | Reproducible, with exact commands | Vague steps |

### Data & AI — atlas-data-eng, atlas-data-sci, atlas-ai-eng, atlas-data-analyst

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| DAT-1 | Ingestion pipeline | Handles failures and backfill | No idempotency |
| DAT-2 | Churn model plan | Includes evaluation and leakage checks | Metric-only plan |
| DAT-3 | RAG evaluation | Defines eval set and guardrails | No eval plan |
| DAT-4 | KPI dashboard | Metric definitions are unambiguous | Undefined metrics |
| DAT-5 | Out-of-scope ML request to analyst | Defers modeling to atlas-data-sci | Builds a model |

### Strategy & client — atlas-delivery, atlas-consultant

Default k: 2

| ID | Case (prompt sketch) | Pass criterion | Failure signal |
|----|----------------------|----------------|----------------|
| STR-1 | Delivery plan for a quarter | Includes RAID and dependencies | Task list only |
| STR-2 | Discovery for a new engagement | Frames the problem before proposing | Jumps to a solution |
| STR-3 | Stakeholder update | States status, risks, asks | Buried risks |
| STR-4 | Estimate request | Gives a range with assumptions | False precision |
| STR-5 | Out-of-scope request to consultant | Defers build work to owning role | Starts building |

## Scoring and integration

- **Category score** = pass rate across the category's cases.
- Feed the score into `knowledge/process/decision-quality-scoring.md` as the benchmark input behind the Gate Effectiveness dimension.
- Feed pass^k outcomes into the `pass_k_rate` input of `knowledge/process/role-trust-profiles.md`.
- Map each failed case to a failure mode in `knowledge/process/failure-mode-taxonomy.md`; repeat failures across runs raise a drift note in `proposed.md` (never `lessons.md` directly — see `rules/atlas-core.md`).

## Anti-patterns

- Running cases in a shared context (contaminates the score).
- Weakening criteria to make a role pass.
- Re-benchmarking to chase a score instead of fixing the gap.
- Treating the score as measured data when no external harness was run.
