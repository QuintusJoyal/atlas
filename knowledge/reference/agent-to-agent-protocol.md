---
name: agent-to-agent-protocol
load-when: Integrating with external agents, delegating tasks across frameworks, designing cross-vendor agent interoperability
skip-when: Single-agent workflows, internal-only delegation using existing handoff protocol, agent-to-tool operations (see MCP)
---

# Agent-to-Agent (A2A) Communication Protocol

The Agent-to-Agent (A2A) protocol enables Atlas agents to discover, delegate, and coordinate with external agents across frameworks (LangGraph, CrewAI, AutoGen). This document defines Atlas's approach to A2A integration, clarifying the distinction between A2A and MCP.

## Quick Reference

| Concept | Purpose | Atlas Integration Point |
|---|---|---|
| **Agent Card** | JSON description of agent capabilities, skills, tools, and metadata | Generated from agent definitions to expose Atlas capabilities externally |
| **Task** | A2A's unit of work with defined lifecycle states | Mapped to Atlas's gate system and handoff protocol |
| **Client** | Discovers and delegates to external A2A agents | Atlas roles can invoke external agents via A2A |
| **Server** | Exposes agent capabilities via A2A | Atlas agents can be exposed to external consumers |
| **Trust** | Policy-based access control for external agents | Enforced via pluggable trust provider |

## A2A vs MCP: Clear Separation

| Aspect | A2A (Agent-to-Agent) | MCP (Model Context Protocol) |
|---|---|---|
| **Purpose** | Agent-to-agent delegation and coordination | Agent-to-tool/resource access |
| **Scope** | Task delegation between autonomous agents | Function/tool invocation and data access |
| **Granularity** | High-level tasks with lifecycle management | Low-level tool calls and resource reads |
| **Who** | Autonomous agents (may span frameworks/vendors) | Agents accessing tools and data sources |
| **Lifecycle** | Long-running tasks with states (submitted, working, completed, failed) | Stateless or short-lived tool invocations |
| **In Atlas** | Cross-framework agent collaboration | Tool access with approval rules for write operations |

Atlas maintains strict separation: **A2A routes agent-to-agent traffic; MCP routes agent-to-tool traffic**. No tool execution flows through A2A endpoints, and no agent delegation flows through MCP servers.

## Agent Card Generation

Atlas agents expose capabilities via A2A agent cards derived from existing agent definitions.

### Card Structure

Agent cards follow A2A specification format and are generated from:
- **Agent frontmatter** (`agents/*.md`): name, role, description, tier, capabilities, permissions
- **Skill definitions** (`skills/atlas-*-playbook/SKILL.md`): skills, scope, delegation patterns
- **Tool registry** (`knowledge/process/tool-registry.md`): available tools and ACI constraints
- **Security posture**: tier classification and permission model

### Required Fields

| Field | Source | Notes |
|---|---|---|
| `name` | Agent frontmatter `name` | e.g., `atlas-dev` |
| `description` | Agent frontmatter `description` | Concise capability summary |
| `version` | Bundle version from `VERSION`/`manifest.json` | Tracks card compatibility |
| `capabilities` | Agent frontmatter `capabilities[]` | High-level abilities |
| `skills` | Mapped from skill definitions | Task patterns agent can perform |
| `tools` | Tool registry + role scoping | Available tools (non-sensitive) |
| `security` | Tier + permissions | Trust classification, read/write boundaries |
| `provider` | Atlas framework metadata | `{"organization": "Atlas", "url": "..."}` |

### Generation Guidelines

- **Derived, not duplicated**: Cards are generated from source of truth (agent markdown), avoiding schema drift.
- **Least disclosure**: Only expose capabilities and tools appropriate for external consumption; never expose internal run state or sensitive paths.
- **Versioned**: Card `version` must align with bundle version for compatibility tracking.
- **Deterministic**: Same agent definition yields identical card structure (stable for caching/validation).

## A2A Client

Atlas agents can discover and delegate tasks to external A2A-compliant agents.

### Discovery

1. **Card retrieval**: Fetch agent card from well-known endpoint (`/.well-known/agent.json` or specified URL)
2. **Card validation**: Validate schema, signature (if present), and trust status before use
3. **Capability matching**: Match requested task against card `skills`/`capabilities`
4. **Trust evaluation**: Apply trust policy (see Trust Framework) before delegation

### Task Delegation Flow

A2A task lifecycle maps to Atlas patterns:

| A2A State | Atlas Mapping | Notes |
|---|---|---|
| `submitted` | Handoff artifact created | Task request with inputs, constraints |
| `working` | Phase enters `active` | External agent executing; Atlas monitors progress |
| `input-required` | Phase remains `active`, escalate | External agent needs clarification; route via atlas-lead |
| `completed` | Phase becomes `gated` | Results validated against acceptance criteria |
| `failed` | Phase becomes `failed` | Apply retry policy per trust config |
| `cancelled` | Phase becomes `aborted` | Respect user abort or policy violation |

### Integration with Handoff Protocol

External A2A tasks produce results that flow into Atlas's existing handoff protocol:
1. External agent completes task → A2A `completed` with artifacts/outputs
2. Atlas A2A client transforms results into handoff artifact structure (per `rules/handoff-protocol.md`)
3. Handoff validated by atlas-lead before proceeding to next role
4. Gate approval follows standard flow (gated → user approval → completed)

This preserves Atlas's audit trail and DoD enforcement without reinventing lifecycle management.

## Task Lifecycle with Atlas Gates

Atlas gates (`requirements`, `design`, `final`, etc.) integrate cleanly with A2A task delegation:

1. **Gate preparation**: When a phase requires external capability, atlas-lead or assigned role initiates A2A delegation
2. **Task creation**: Map phase inputs to A2A task (include constraints, acceptance criteria, DoD)
3. **Execution monitoring**: Track A2A task state; update run state in `$ATLAS_DATA_DIR/runs/<run-id>/team.json`
4. **Completion validation**: On `completed`, validate outputs against gate criteria and DoD
5. **Gate transition**: Only proceed to next phase if outputs satisfy gate requirements

**Critical**: A2A delegation never bypasses gates. External work must still pass the relevant quality gate before advancing.

## Trust Framework

Atlas enforces policy-based controls determining which external A2A agents may be invoked.

### Trust Tiers

Aligned with `knowledge/process/role-trust-profiles.md` (experimental ARTS model):

| Tier | Trust Score | Allowed Operations | Requirements |
|---|---|---|---|
| `UNTRUSTED` | < 0.50 | None (blocked) | Must not delegate |
| `PROBATION` | 0.50–0.69 | Read-only tasks only | Explicit approval, full audit |
| `STANDARD` | 0.70–0.89 | Non-destructive tasks | Audit trail, rate limits |
| `TRUSTED` | ≥ 0.90 | Delegated per policy | Periodic revalidation |

### Trust Evaluation Criteria

| Criterion | Weight | Description |
|---|---|---|
| **Capability match** | High | Skills align with requested task; no scope creep |
| **Reputation** | High | Prior successful completions, known framework/vendor |
| **Security posture** | Critical | Card validation, TLS, auth, least-privilege claims |
| **Stability** | Medium | Version stability, uptime history |
| **Compliance** | Variable | Regulatory constraints (if regulated variant) |

### Trust Provider (Pluggable)

Trust evaluation is pluggable: default static policy + optional dynamic provider. Policies stored as configuration (not hardcoded in agents). Trust decisions are logged for audit.

## Security Controls

Cross-agent delegation expands the attack surface; Atlas applies defense-in-depth.

### Card Validation

- **Schema validation**: Agent cards must conform to expected A2A structure; reject malformed cards
- **Signature verification**: If signed cards provided, validate signatures before trusting
- **Source verification**: Cards fetched over HTTPS; validate endpoint authenticity
- **Least disclosure check**: Flag cards claiming excessive capabilities or tools
- **Version compatibility**: Reject cards with incompatible major versions

### Least-Privilege Access

- **Task-scoped delegation**: Delegate only the specific task/skill needed; never grant broad access
- **Input sanitization**: Treat external agent inputs/outputs as untrusted; validate against schemas
- **Output validation**: Validate returned artifacts match expected types and DoD criteria
- **No transitive delegation bypass**: External agents cannot delegate further on Atlas's behalf without explicit policy
- **Tool boundary**: A2A never grants MCP tool access to external agents; separation enforced

### Audit & Monitoring

- **Comprehensive audit trail**: All A2A operations logged (discovery, delegation, state changes, results)
- **Provenance**: Record card source, trust decision, request/response hashes, timestamps
- **Run workspace logging**: Audit entries persisted under `$ATLAS_DATA_DIR/runs/<run-id>/` (alongside gates, team.json)
- **Anomaly detection**: Flag unexpected task patterns, repeated failures, or policy violations
- **Non-repudiation**: Immutable audit records for compliance scenarios

### Threat Mitigations

| Threat | Mitigation |
|---|---|
| **Spoofed agent cards** | HTTPS only, signature verification, allowlist of trusted endpoints |
| **Prompt injection via task inputs/outputs** | Treat external content as untrusted; validate/sanitize; apply same security rules as user input |
| **Data exfiltration** | Least disclosure in cards; task-scoped inputs; deny delegation of tasks requesting sensitive data unless explicitly allowed |
| **Task hijacking/replay** | Nonce/timestamps, task IDs, TLS, short-lived delegation windows |
| **Denial of service** | Timeouts, retry backoff, rate limits per external agent/trust tier |
| **Scope creep** | Capability matching against requested skill; reject tasks outside delegated scope |

## Integration with MCP (No Conflict)

A2A and MCP coexist without conflict through explicit routing:

- **Routing rule**: If target is another agent → A2A. If target is a tool/resource → MCP.
- **Separation of concerns**: External agents cannot invoke Atlas MCP tools via A2A; MCP tool access remains controlled by Atlas's existing approval model (write-mode requires approval).
- **Shared audit**: Both A2A and MCP operations log to the same run audit trail for end-to-end traceability.
- **No shared auth context leakage**: A2A delegation tokens are distinct from MCP credentials.

## Configuration

A2A behavior is configured via policy (not inline in role bodies). Default conservative posture: deny external delegation unless explicitly allowed by trust policy and task type.

### Trust Policy Example (Conceptual)

```yaml
a2a:
  enabled: false  # opt-in by default for safety
  allowlist:
    - name: trusted-security-scanner
      endpoint: https://example.com/.well-known/agent.json
      trust_tier: TRUSTED
  denylist: []
  trust_provider: static  # or 'dynamic'
  require_signature: false
  audit_all: true
  max_retries: 3
  timeout_seconds: 120
```

**Note**: Actual configuration lives outside agent markdown (policy/config), consistent with Atlas's "separate policy from implementation" pattern.

## See Also

- **rules/handoff-protocol.md** — Artifact-based handoffs; A2A results map to handoff structure
- **knowledge/process/role-trust-profiles.md** — ARTS trust model and tiers
- **knowledge/process/tool-registry.md** — Tool categories; MCP vs A2A separation
- **knowledge/process/aci-enforcement.md** — ACI behavior rules (error handling, timeouts)
- **knowledge/reference/quality-gates.md** — Gate enforcement for delegated work
- **rules/atlas-core.md** — Core approval rules (MCP writes; A2A follows similar least-privilege)