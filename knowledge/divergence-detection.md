---
name: divergence-detection
category: process
load-when: After parallel phases complete, before advancing to next sequential stage
skip-when: Sequential-only workflows, single-role tasks
description: Detect semantic divergence between parallel agent outputs. Catches invisible contradictions before they compound.
audience: [atlas-lead]
tags: [divergence, parallel, conflict-detection, coordination, multi-agent]
---

# Divergence detection

When multiple agents work in parallel, their outputs may silently diverge. The code compiles, tests pass, but the codebase contains conflicting implementations of the same concept. This is the most expensive class of multi-agent failure.

## Quick Reference
- Run after all parallel phases complete, before next sequential stage
- Check: terminology, assumptions, ownership, interfaces
- If clean: advance. If conflicts: pause and present options to user
- Log results to trajectory.jsonl

## The problem

CooperBench (2026) found that agents achieve ~50% lower success rates when collaborating versus working solo. Invisible divergence is the signature failure mode: three agents solving different problems each independently implement dynamic model discovery with different class names, interfaces, and assumptions.

## Detection signals

### 1. Terminology divergence
Same concept named differently across parallel artifacts.
- Extract all noun phrases from parallel handoff artifacts
- Find synonyms or conflicting terms for the same concept
- Example: one role calls it "export job", another calls it "data extract"

### 2. Assumption divergence
Roles make incompatible assumptions about the system.
- Extract technology choices: protocol, framework, language, data format
- Find mismatches: one assumes REST, another assumes GraphQL
- One assumes PostgreSQL, another assumes MongoDB

### 3. Ownership overlap
Two roles claim the same file or artifact as their output.
- Extract file paths from parallel artifact outputs
- Find overlapping claims
- Two roles producing the same file = conflict

### 4. Interface mismatch
Role A's output schema doesn't match role B's expected input.
- Extract API contracts, function signatures, data models
- Check for incompatible request/response shapes
- One role defines `userId: string`, another expects `userId: number`

## Detection protocol

After all parallel phases in a stage complete:

1. **Collect** all parallel handoff artifacts
2. **Extract** from each: API contracts, data models, file paths, technology choices, noun phrases
3. **Compare** using the divergence checklist:
   - [ ] Terminology: any conflicting names for the same concept?
   - [ ] Assumptions: any incompatible technology choices?
   - [ ] Ownership: any overlapping output file claims?
   - [ ] Interfaces: any mismatched schemas or contracts?
4. **If clean:** advance to next phase
5. **If conflicts found:** pause, present to user with options

## Resolution options

When divergence is detected, present these options to the user:

| Option | When to use | Cost |
|--------|------------|------|
| **Reconcile** | Both choices are valid, user picks one | Low — one role adapts |
| **Re-run one role** | One role had incomplete context | Medium — re-delegate with merged context |
| **Override** | User has a strong preference | Low — one role adapts |
| **Accept divergence** | Known divergence, acceptable for now | Zero now, technical debt later |

## Integration with handoff protocol

The divergence check runs between parallel stage completion and the next sequential stage. It is performed by atlas-lead as a lightweight reasoning step (2-5 turns), not a separate delegation.

Add to gate approval flow after parallel phases:
```
After parallel phases complete:
  1. Collect all parallel handoff artifacts
  2. Run divergence checklist
  3. If clean: advance to next phase
  4. If conflicts: pause, present resolution options to user
  5. Log result to trajectory.jsonl
```

## Trajectory integration

Log divergence checks:
```jsonl
{
  "ts": "...",
  "role": "atlas-lead",
  "action": "divergence-check",
  "target": "design-stage",
  "why": "Checking parallel architect + UX outputs for conflicts",
  "outcome": "success",
  "divergenceFound": false,
  "tokens": 300
}
```

When divergence is found:
```jsonl
{
  "ts": "...",
  "role": "atlas-lead",
  "action": "divergence-check",
  "target": "design-stage",
  "outcome": "divergence-detected",
  "divergenceType": "terminology",
  "detail": "architect calls it 'export pipeline', UX calls it 'data flow'",
  "resolution": "reconcile",
  "tokens": 400
}
```
