# Workflow presets

atlas-lead picks a preset to right-size the pipeline. Each preset defines phases, roles, approval gates, and a Definition of Done per gate. Unknown task shapes fall back to `feature`. The user can override the preset at any time.

## Presets

| Preset | When to use | Variants |
| --- | --- | --- |
| feature | Net-new work, full pipeline with all three gates | small, full |
| bugfix | Defects and hotfixes, fast lane, single final gate | small, full |
| data-project | Data or analytics work, pulls the data roles | small, full |
| infra-change | Infrastructure, network, or cloud changes | small, full |
| security-audit | Read-only security and compliance assessment | small, full |
| discovery | Consulting: scope and proposal, no build | small, full |

## Variants

Every preset has two variants:

- **small:** lightweight path for simple tasks. Skips unnecessary gates, no estimation huddle, starts immediately. Auto-approves final gate if DoD is met. No tracking (no team.json, no budget.md).
- **full:** standard path with all gates, estimation huddle, and token-budget approval. Full tracking.

atlas-lead picks the variant based on scope and complexity. Tell the user which variant and why.

## Optimizations

### Auto-approve gates (small variant)
Small variant final gate is auto-approved when all DoD items pass. No user interaction needed. User can override: "I want to review before deploy."

### Skip tracking (small variant)
Small variants skip team.json and budget.md. Phase states tracked in memory only. No audit trail. Lead reports status verbally.

### Compressed handoff (small variant)
Small variant handoffs use 4 sections instead of 8: Summary, Outputs, Issues, Next. Saves ~200 tokens per handoff.

### Auto-detect conditions
Lead auto-detects conditions from task description:
| Keywords | Condition |
| --- | --- |
| auth, payment, secret, token, credential | security-sensitive |
| GDPR, SOC2, ISO, compliance, regulated | regulated |
| pipeline, data model, analytics, SQL, query | data-changes |

User can override at kickoff.

### Batch delegation
Parallel phases are delegated in a single turn. Lead sends multiple delegation calls in one message. Phases run concurrently.

### Auto-resume
When user says "continue" or "resume", lead auto-resumes from last completed phase. No confirmation needed. Skip completed phases, re-run failed/paused phases.

## Conditions

Workflows support conditional phase injection. When a condition is true, additional phases or roles are added:

| Condition | Effect |
| --- | --- |
| regulated | Adds compliance phase and atlas-compliance role |
| data-changes | Adds atlas-data-eng and atlas-dba roles |
| security-sensitive | Adds security-review phase and atlas-security role |
| security-impacting | Adds security-review phase and atlas-security role |
| technical-deep-dive | Adds atlas-architect role |

Conditions are evaluated at kickoff. Matched conditions inject phases into the workflow. Injected phases follow the same state machine as native phases.

## State machine

Every workflow follows a formal state machine:

```
pending → active → gated → completed
    ↓         ↓        ↓
  failed    paused   aborted
```

| State | Description |
| --- | --- |
| pending | Phase not started |
| active | Phase in progress (role delegated) |
| gated | Phase complete, waiting for gate approval |
| completed | Gate passed, phase done |
| failed | Phase or gate failed |
| paused | Scope change detected, re-evaluation in progress |
| aborted | Phase cancelled (user or lead decision) |

### Transitions

| From | To | Trigger |
| --- | --- | --- |
| pending | active | Lead delegates to role |
| active | gated | Role returns handoff |
| gated | completed | User approves gate (or auto-approve if small) |
| gated | failed | Gate criteria not met |
| active | failed | Role fails or model exhausted |
| any | aborted | User or lead cancels |
| active | paused | Scope change detected |
| paused | active | Re-evaluation complete, resume |
| paused | aborted | Re-evaluation determines restart needed |

## Scope changes

When requirements change mid-workflow:

1. Current phase pauses (state → paused)
2. Lead delegates re-evaluation to PM/BA
3. PM/BA assesses impact: which phases affected? re-estimate needed?
4. Lead presents re-evaluation to user
5. User decides: resume, restart from phase X, or abort
6. Lead executes decision

Scope changes can restart from any prior phase. Variant can be switched during re-evaluation.

## Abort and resume

- **Abort:** user or lead can abort at any time. All pending phases set to aborted. budget.md updated with reason (full only).
- **Resume:** resume from last completed phase. Re-run failed/paused phases. Skip completed phases (unless scope change invalidated them). Auto-resume on "continue" or "resume".
- **One workflow per run:** user must resume or abort a paused workflow before starting a new one.

## Phase composition

Phases can be added via conditions. Each phase has:
- **Gate:** which gate it feeds (or null)
- **Parallel:** whether it runs concurrently with other phases
- **Roles:** which roles participate
- **Skip-if:** when to skip (e.g., variant=small)
- **Input/Output:** what it receives and produces

Parallel phases run concurrently via parallel delegation (batched in one turn). Gate waits for all parallel phases to complete.

## Kickoff

Every pipeline run starts with Phase 0 kickoff:

### Standard kickoff (full variant)
1. atlas-lead: create run folder, seed `team.json`
2. Estimation huddle: participating roles return light | medium | heavy
3. atlas-lead writes `budget.md`
4. Gate: token-budget (user approves if heavy)

### Lightweight kickoff (small variant)
1. atlas-lead: create run folder
2. Start immediately (no tracking)

## Gates

Gates pause for user sign-off (full variant). Small variant auto-approves if DoD is met.

| Gate | Phase transition | Auto-approve |
| --- | --- | --- |
| requirements | Requirements → Design | full only |
| design | Design → Implementation | full only |
| final | Implementation → Delivery | small: auto, full: user |
| scope | Scoping → Audit (security-audit only) | full only |
| research | Research → Proposal (discovery only) | full only |

**Every pipeline run starts with Phase 0 kickoff:** workflow selection (lead announces + persists), estimation huddle (roles via Task, atlas-ai-eng aggregates), `budget.md` with Predicted and per-role estimates. See `knowledge/budget-template.md`.
