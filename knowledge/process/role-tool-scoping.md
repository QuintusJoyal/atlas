---
name: role-tool-scoping
category: process
load-when: Delegating roles, designing workflows, debugging tool conflicts
skip-when: Single-role tasks, simple operations
description: Phase-aware tool scoping for Atlas multi-agent workflows. Defines which tools each role needs per phase.
audience: [atlas-lead]
tags: [tools, scoping, phases, delegation, multi-agent]
---

# Role tool scoping

Atlas is a multi-agent system. Not every role needs every tool at every time. Phase-aware tool scoping reduces context waste and prevents tool conflicts.

## Quick Reference
- Each phase has a permitted tool set
- Specialists request forbidden tools via escalation if needed
- Tool scope is included in delegation briefs, with a delegation token
- Delegated scope is always strictly attenuated from the delegator's
- Orchestration phases use a different scope than execution phases

## Tool Scope Matrix

| Phase | Read | Grep | Glob | Write | Edit | Bash | Task | WebFetch | WebSearch |
|-------|------|------|------|-------|------|------|------|----------|-----------|
| Discovery | Y | Y | Y | N | N | RO | Y | Y | Y |
| Design | Y | Y | Y | N | N | RO | Y | Y | N |
| Implementation | Y | Y | Y | Y | Y | Y | Y | N | N |
| Testing | Y | Y | Y | N | N | Y | Y | N | N |
| Review | Y | Y | Y | N | N | RO | Y | N | N |
| Documentation | Y | Y | Y | Y | N | N | N | N | N |

Y = permitted, N = forbidden, RO = read-only (Bash with read commands only)

## How to use

### In delegation briefs
When atlas-lead delegates to a role, include the tool scope and the delegation token:
```markdown
## Tool Scope (phase: implementation)
Primary: Read, Write, Edit, Bash
Secondary: Grep, Glob, Task
Forbidden: WebSearch, WebFetch
If you need a forbidden tool, escalate with justification.

## Delegation Token
id: d-002 | principal: user | authorizedBy: atlas-lead
chain: user > atlas-lead:d-001 → atlas-lead > <you>:d-002
Scope above is strictly attenuated from the delegator's scope.
You may not widen it. Escalate deviations to atlas-lead.
```

### Least-privilege attenuation (enforced)
Delegation is attenuating, never amplifying:
1. **Strict subset:** the delegated scope must be a strict subset of the delegator's effective scope — never equal, never greater. Role-specific overrides above apply before attenuation, not after.
2. **No re-broadening:** a spawned role never widens its own scope, never asks a peer to re-spawn it with more tools, and never reinterprets the brief as permission.
3. **Deviations route upward:** a needed forbidden tool is an escalation (T2 to atlas-lead, T3/user for anything that would match or exceed the delegator's own scope). The lead re-delegates the sub-task or the user grants a new, still-attenuated edge.
4. **Chain record:** every spawn appends one edge (principal, delegator, delegate, scope) to `$ATLAS_DATA_DIR/runs/<run-id>/delegation-chain.jsonl` — append-only, for post-hoc reconstruction of who authorized what.

Full token schema, chain record format, and reconstruction procedure: `knowledge/process/delegation-authority.md`. Validate a brief or a chain with `python3 scripts/validate-delegation.py`.

### When a role needs a forbidden tool
If a specialist role encounters a situation where it genuinely needs a forbidden tool:
1. Document what it needs and why
2. Escalate to atlas-lead (T2)
3. Lead either expands the scope or delegates the sub-task to a role with the right tools

### Orchestration scope
atlas-lead operates at the orchestration scope:
- Primary: Task (delegation), Read, Grep
- Secondary: Glob
- Forbidden: Edit, Write, Bash (lead does not implement)

This enforces the separation of orchestration from implementation.

## Tool conflict resolution

When two roles need to modify the same file in the same phase:
1. The first role to edit takes ownership (recorded in team.json)
2. The second role re-reads the file before editing (tool provenance check)
3. If both edits are independent (different sections), both proceed
4. If edits conflict, the second role escalates to lead for resolution

## Role-specific scope overrides

Some roles have permanent scope adjustments:
- **atlas-devops:** Bash is always permitted (even in Design phase for infrastructure validation)
- **atlas-docs:** Write is always permitted (documentation is their primary output)
- **atlas-compliance:** Read + Grep only across all phases (audit role, never modifies)
- **atlas-lead:** Never Edit, Write, or Bash (orchestration only)
