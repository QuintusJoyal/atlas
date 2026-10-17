---
name: hybrid-reasoning
load-when: Designing or running a decision chain that mixes LLM output with rule engines, knowledge graphs, or deterministic validators
skip-when: Pure LLM drafting tasks with no symbolic checks, model training or evaluation (see model-cards)
---

# Hybrid reasoning reference

## Quick Reference
- Hybrid = LLM proposes, symbolic layer disposes. The LLM never has the final vote on a policy question.
- Four backend types: LLM (interpret, rank, weigh trade-offs), rule engine (policy verdicts), knowledge graph (relationship facts), validator (formats, invariants, re-verified claims)
- Every decision ships an explainability trace naming the component behind each step
- Rule violation = hard veto. Escalate to the orchestrator, never around the rule.

## Deep Dive

### Pluggable backend architecture
| Backend | Responsibility | Interface contract |
|---------|----------------|--------------------|
| LLM | Interpret the question, rank options, weigh trade-offs | Returns ranked options with reasons; never returns a policy verdict |
| Rule engine | Validate candidates against business policy | Input: candidate + rule set ID. Output: pass/fail per rule with rule ID |
| Knowledge graph | Answer relationship queries | Input: structured query (node type, edge type, direction). Output: nodes/edges with IDs, or empty |
| Deterministic validator | Re-check concrete claims and artifact shape | Input: claims + source references. Output: verified/unverified per claim |

Swap any backend by satisfying its contract; the orchestration and trace format stay identical. This is what keeps the architecture tool-agnostic: an organization plugs in its own rule engine (OPA, Drools, or a plain checklist) or graph store (Neo4j, a service catalog, a lineage table) behind the same interface.

### Rule engine conventions
- Rule sets are owned by the specialist accountable for the policy (security rules by atlas-security, compliance by atlas-compliance, change management by atlas-devops). The reasoner executes, it does not author.
- Name the rule set and version in the trace so a decision can be re-evaluated when policies change.
- Vacuous passes (rule set empty, input not matching any rule) are recorded as `pass (vacuous)`, not `pass`.

### Knowledge-graph lookup conventions
- Query by relationship, not by free text: `Service -[:DEPENDS_ON]-> Service`, `Dataset -[:PRODUCED_BY]-> Pipeline`, `Service -[:OWNED_BY]-> Team`.
- Every graph-backed claim cites the nodes and edges used. Empty result = `unvalidated`, never a guessed answer.
- Stale-graph guard: record the graph snapshot time; if the decision depends on data that churns (deployments, ownership), flag freshness.

### Deterministic validation checklist
- Counts: recompute from the source, compare
- Paths and identifiers: existence check against the filesystem or catalog
- Dates and thresholds: parse and range-check
- Final artifact: schema/required-fields check before handoff

### Explainability trace template
```
Decision: <question restated in one sentence>
Context: <constraints and data sources, one line each>
1. <step> - backend: LLM - verdict: ranked - reason: <one line, top option named>
2. <step> - backend: knowledge-graph - verdict: pass - reason: <nodes/edges cited>
3. <step> - backend: rule-engine - verdict: pass | fail - reason: <rule IDs>
4. <step> - backend: validator - verdict: pass - reason: <what was re-checked>
Rule results: <rule set name@version: pass/fail per rule, or "none applicable">
Validation: <claims verified: N/N or list of unverified>
Confidence: high | medium | low - <which steps were pure-LLM, if any>
Recommendation: proceed | veto | needs-human - <one sentence>
```

Trace rules: one line per step; every line names a component; no step without a backend; unvalidated steps are shown, not hidden. The trace is the audit artifact, written for a human reviewing the decision later, not for the model that produced it.

## Boundaries
- Authoring policies and rule sets: the accountable specialist (security, compliance, devops, architect), not atlas-reasoner
- Model selection and evaluation for the LLM backend: atlas-ai-eng
- Acting on the decision: atlas-dev or the orchestrator's gate
