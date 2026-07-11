# Migration Guide: v0.13.0 to v0.14.0

## What's New

### Knowledge Reorganization
105 knowledge files moved from flat `knowledge/` directory into 18 subdirectories:

| Directory | Files | Purpose |
|-----------|-------|---------|
| `reference/` | 16 | Operational knowledge (lessons, resilience, collaboration) |
| `process/` | 16 | Process knowledge (ACI, critics, checkpoints, DAG, observability) |
| `context/` | 13 | Tactical knowledge (context-engineering, escalation, lead-routing) |
| `testing/` | 6 | Testing knowledge (pyramid, BDD, ISTQB, anti-patterns) |
| `security/` | 5 | Security knowledge (OWASP, STRIDE, NIST, CWE) |
| `architecture/` | 5 | Architecture knowledge (C4, ADR, DDD, trade-off) |
| `delivery/` | 7 | Delivery knowledge (DORA, GitOps, ITIL, PMBOK, SRE) |
| `data/` | 5 | Data knowledge (Kimball, dbt, Airflow, Great Expectations) |
| `craftsmanship/` | 5 | Craftsmanship knowledge (SOLID, clean code, TDD) |
| `decision/` | 5 | Decision knowledge (MECE, Socratic, SPIN, Minto) |
| `compliance/` | 4 | Compliance knowledge (GDPR, SOC2, ISO 27001, NIST CSF) |
| `cloud/` | 4 | Cloud knowledge (AWS, Azure, FinOps, CIS) |
| `ai/` | 4 | AI knowledge (NIST AI RMF, OWASP LLM, Anthropic) |
| `ux/` | 3 | UX knowledge (WCAG, Nielsen, Material Design) |
| `infra/` | 5 | Infrastructure knowledge (Kubernetes, API design, EDA) |
| `enterprise/` | 4 | Enterprise knowledge (TOGAF, Scrum, RAID, RACI) |
| `benchmark/` | 3 | Benchmark knowledge (frontier, performance, self-assessment) |
| `critic-prompts/` | 5 | Critic prompts (spec-integrity, oracle, implementation, etc.) |

### New Knowledge Files
- `process/runtime-execution.md` — Runtime execution protocol (minimal tool API)
- `process/dashboard-spec.md` — Observability dashboard specification
- `context/codebase-context.md` — Codebase-aware context loading
- `benchmark/performance-benchmarks.md` — Token usage measurements

### New Tools
- `scripts/validate-refs.py` — Validates all knowledge cross-references

### New Examples
- `examples/.cursorrules` — Cursor configuration
- `examples/.opencode.json` — OpenCode configuration
- `examples/CLAUDE.md` — Claude Code configuration
- `examples/.github/copilot-instructions.md` — VS Code Copilot configuration

### Lite Mode Updates
- `lite/rules/atlas-core.md` — Added structured errors and checkpoint rules
- `lite/workflows/self-assessment.md` — New simplified workflow

## Breaking Changes

### Knowledge File Paths Changed
All knowledge files moved to subdirectories. If you have custom configurations referencing `knowledge/<file>.md`, update to `knowledge/<subdir>/<file>.md`.

**Before:**
```
knowledge/lessons.md
knowledge/model-resilience.md
knowledge/aci-enforcement.md
```

**After:**
```
knowledge/reference/lessons.md
knowledge/reference/model-resilience.md
knowledge/process/aci-enforcement.md
```

### Manifest Updated
`manifest.json` now lists knowledge files with subdirectory paths.

## How to Update

### 1. Update Custom Configurations
If you have custom `.cursorrules`, `.opencode.json`, or `CLAUDE.md` files, update knowledge file paths.

### 2. Run Validation
```bash
python3 scripts/validate-refs.py
```

This checks all cross-references are valid.

### 3. Update Playbook Knowledge Index
Playbooks use `k/` prefix (not `knowledge/`), so they don't need path updates.

### 4. Update Agent Files
Agent files that reference knowledge files have been updated automatically.

## New Features to Try

### Runtime Execution Protocol
Read `knowledge/process/runtime-execution.md` to understand how agents make tool calls.

### Codebase-Aware Context
Read `knowledge/context/codebase-context.md` to learn about file discovery strategies.

### Dashboard
Read `knowledge/process/dashboard-spec.md` to understand the observability dashboard.

### Performance Benchmarks
Read `knowledge/benchmark/performance-benchmarks.md` to see token usage measurements.

## Version History

- v0.14.0 — Knowledge reorganization, runtime execution, codebase context, dashboard, benchmarks
- v0.13.0 — 8 innovations (ACI, critics, checkpoints, DAG, trust, compounding, self-assessment)
- v0.12.0 — Slim atlas-core, extracted knowledge files
- v0.11.0 — 10 workflows, lite mode, frontier comparison
