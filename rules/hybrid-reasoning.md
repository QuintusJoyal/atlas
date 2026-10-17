---
name: hybrid-reasoning
description: Hybrid reasoning discipline. Load when combining LLM output with symbolic checks, business rules, knowledge-graph lookups, or deterministic validation.
load: on-demand
---

# Hybrid reasoning

Applies when a decision mixes probabilistic (LLM) judgment with deterministic sources. The rule: the LLM proposes, the symbolic layer disposes.

## Pluggable backends
- Keep every backend behind a narrow adapter interface: inputs are plain facts and rules, outputs are verdicts with reasons. No backend sees another's prompts or internals.
- Default split: LLM ranks and interprets; rule engine checks policy; knowledge graph answers relationship questions; validators check formats, schemas, and invariants.
- A missing backend is a declared gap, never a silent LLM fallback for a check that was supposed to be symbolic.

## Rule engine checks
- Encode business policies (change management, refund limits, data residency, separation of duties) as rule sets owned by the relevant specialist.
- A rule violation is a hard veto. An LLM rationale never overrides a failed rule; escalation goes to atlas-lead, not around the rule.
- Record which rules ran and their verdicts; "no applicable rules" is itself a recorded result.

## Knowledge-graph lookups
- Relationship questions (what depends on this, who owns this, where did this data come from) are answered from the graph, not from model priors.
- Cite the node and edge used. If the graph has no answer, say so and downgrade the claim to unvalidated.
- Never invent graph facts to fill a gap; an empty result is a valid and useful finding.

## Deterministic output validation
- Re-verify every concrete claim in the output against sources: counts, file paths, identifiers, dates, thresholds. A claim that cannot be re-verified is labeled low confidence.
- Validate the final artifact shape (schema, required fields, enum values) before handoff, same as any other deliverable.

## Explainability trace
Every hybrid decision ships with a trace. Template (fuller version in `knowledge/ai/hybrid-reasoning.md`):

```
Decision: <question restated>
1. <step> - backend: LLM | rule-engine | knowledge-graph | validator - verdict: <pass|fail|unvalidated> - reason: <one line>
...
Rule results: <rules run, pass/fail per rule>
Validation: <what was re-checked, result>
Recommendation: proceed | veto | needs-human - <one sentence>
```

- One line per step, each line naming its backend. No step without a named component.
- Traces are evidence, not narrative: no hedging filler, no restating the prompt.
